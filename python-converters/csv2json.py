#!/usr/bin/env python3
"""csv2json.py - read a CSV file and write JSON.

Design choices that matter for correctness rather than convenience:
- Parsing goes through the stdlib ``csv`` reader, never ``str.split``, so quoted commas, doubled quotes
  and newlines inside a field survive.
- The delimiter is sniffed, with an explicit ``--delimiter`` override for the cases the sniffer gets wrong
  (single-column files, or files whose header rows confuse it).
- Encoding defaults to ``utf-8-sig`` because spreadsheet exports usually carry a BOM, and a stray BOM
  silently corrupts the first header name.
- A malformed row is skipped and reported with its line number instead of aborting the run, and the count
  is always reported so nothing disappears quietly.

Usage:
    python csv2json.py data.csv [-o out.json] [--delimiter ','] [--encoding utf-8-sig]
                                [--indent 2] [--jsonl] [--strict]
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path


def detect_delimiter(sample: str, override: str | None) -> str:
    """Return the field delimiter: an explicit one if given, otherwise the sniffer's best guess."""
    if override:
        return override
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
    except csv.Error:
        return ","


def read_records(
    path: Path, delimiter: str | None = None, encoding: str = "utf-8-sig"
) -> tuple[list[dict[str, str]], int, str]:
    """Return (records, skipped_count, delimiter_used). Header comes from the first non-empty line."""
    text = path.read_text(encoding=encoding)
    sample = text[:8192]
    used = detect_delimiter(sample, delimiter)

    reader = csv.reader(io.StringIO(text), delimiter=used)
    header: list[str] | None = None
    records: list[dict[str, str]] = []
    skipped = 0

    for line_no, row in enumerate(reader, start=1):
        if not row or all(cell.strip() == "" for cell in row):
            continue
        if header is None:
            header = [cell.strip() for cell in row]
            continue
        if len(row) != len(header):
            # Ragged row: keep it visible rather than letting it shift columns silently.
            print(
                f"skip line {line_no}: expected {len(header)} fields, found {len(row)}",
                file=sys.stderr,
            )
            skipped += 1
            continue
        records.append(dict(zip(header, row)))

    if header is None:
        raise SystemExit("no header row found: the file is empty or has no data")

    return records, skipped, used


def write_output(records: list[dict[str, str]], out: Path | None, indent: int, jsonl: bool) -> None:
    if jsonl:
        payload = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records)
    else:
        payload = json.dumps(records, ensure_ascii=False, indent=indent) + "\n"
    if out:
        out.write_text(payload, encoding="utf-8")
        print(f"wrote {out} ({len(records)} records)", file=sys.stderr)
    else:
        sys.stdout.write(payload)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Convert a CSV file to JSON.")
    p.add_argument("csv", type=Path, help="input CSV file")
    p.add_argument("-o", "--out", type=Path, default=None, help="output JSON file (default: stdout)")
    p.add_argument("--delimiter", default=None, help="field delimiter; omitted means sniff it")
    p.add_argument("--encoding", default="utf-8-sig", help="input encoding (default utf-8-sig)")
    p.add_argument("--indent", type=int, default=2, help="JSON indent (default 2, 0 for compact)")
    p.add_argument(
        "--jsonl",
        action="store_true",
        help="write one JSON object per line instead of one array; better for very large files",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        help="exit non-zero if any row was skipped (default: skip and report)",
    )
    args = p.parse_args(argv)

    records, skipped, used = read_records(args.csv, args.delimiter, args.encoding)
    print(f"delimiter={used!r} records={len(records)} skipped={skipped}", file=sys.stderr)
    write_output(records, args.out, args.indent, args.jsonl)

    if args.strict and skipped:
        print(f"strict mode: {skipped} row(s) were skipped", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
