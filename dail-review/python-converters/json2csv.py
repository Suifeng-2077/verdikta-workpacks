#!/usr/bin/env python3
"""json2csv.py - read a JSON file and write CSV.

Two details decide whether the output is usable:
- The header is the union of keys across every record, not the keys of the first record. Taking the first
  record's keys is the classic bug: any record that has an extra key loses it, and any record missing a key
  shifts every following column.
- Nested values are JSON-encoded into the cell instead of being stringified with ``repr``, so the data can
  be parsed back out of the CSV.

Missing keys write an empty cell. Encoding defaults to ``utf-8-sig`` so Excel reads non-ASCII correctly.

Usage:
    python json2csv.py data.json [-o out.csv] [--delimiter ','] [--encoding utf-8-sig] [--columns a,b]
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path


def load_records(path: Path, encoding: str = "utf-8-sig") -> list[dict]:
    """Read JSON and return a list of objects. Accepts a top-level array or a single object."""
    text = path.read_text(encoding=encoding)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as err:
        raise SystemExit(f"{path} is not valid JSON: {err.msg} at line {err.lineno} column {err.colno}")
    if isinstance(data, dict):
        return [data]
    if not isinstance(data, list):
        raise SystemExit("expected a JSON array of objects, or a single object")
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            raise SystemExit(f"record {i} is {type(item).__name__}, expected an object")
    return data


def field_order(records: list[dict], forced: list[str] | None) -> list[str]:
    """Union of keys in first-seen order, or the caller's explicit list."""
    if forced:
        return forced
    seen: dict[str, None] = {}
    for rec in records:
        for key in rec:
            seen.setdefault(str(key), None)
    return list(seen)


def cell(value) -> str:
    """Scalars as-is; objects and arrays JSON-encoded so they survive the round trip."""
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def to_csv(records: list[dict], columns: list[str], delimiter: str) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=delimiter, lineterminator="\n")
    writer.writerow(columns)
    for rec in records:
        writer.writerow([cell(rec.get(col, "")) for col in columns])
    return buf.getvalue()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Convert a JSON array of objects to CSV.")
    p.add_argument("json", type=Path, help="input JSON file")
    p.add_argument("-o", "--out", type=Path, default=None, help="output CSV file (default: stdout)")
    p.add_argument("--delimiter", default=",", help="field delimiter (default ',')")
    p.add_argument("--encoding", default="utf-8-sig", help="input encoding (default utf-8-sig)")
    p.add_argument("--columns", default=None, help="comma-separated column order; default is the union of keys")
    args = p.parse_args(argv)

    records = load_records(args.json, args.encoding)
    if not records:
        # An empty array still has to produce a usable file: header only, or nothing at all.
        print("0 records: writing nothing", file=sys.stderr)
        if args.out:
            args.out.write_text("", encoding="utf-8-sig")
        return 0

    forced = [c.strip() for c in args.columns.split(",")] if args.columns else None
    columns = field_order(records, forced)
    payload = to_csv(records, columns, args.delimiter)

    if args.out:
        args.out.write_text(payload, encoding="utf-8-sig")
        print(f"wrote {args.out} ({len(records)} records, {len(columns)} columns)", file=sys.stderr)
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
