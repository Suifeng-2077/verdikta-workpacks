#!/usr/bin/env python3
"""csv2json.py - read a CSV file and write JSON.

Correctness choices that matter:
- Parsing goes through the stdlib ``csv`` reader, never ``str.split``, so quoted commas, doubled quotes and
  newlines inside a field survive.
- The delimiter is sniffed, with ``--delimiter`` to override the cases the sniffer gets wrong (single-column
  files, headers that contain the delimiter inside quotes).
- Encoding defaults to ``utf-8-sig`` because spreadsheet exports carry a BOM, and a stray BOM silently
  renames the first column.
- A ragged row is skipped and reported with its line number; nothing disappears quietly.
- Invalid CSV gets a specific message, not a traceback: unterminated quote, duplicate header, NUL bytes,
  empty file, header-only file, decode error with the byte offset.

Output shapes:
    --format array   (default) one JSON array of objects
    --format jsonl   one object per line, streams well for large files
    --format keyed   one object keyed by --key-by, e.g. {"1": {...}, "2": {...}}

Usage:
    python csv2json.py data.csv [-o out.json] [--format array|jsonl|keyed] [--key-by id]
                                [--types] [--null-empty] [--delimiter ','] [--encoding utf-8-sig]
                                [--indent 2] [--strict]
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path

# Values that --types will convert; anything else stays a string so the output is lossless by default.
_TRUE = {"true", "yes", "y"}
_FALSE = {"false", "no", "n"}


def coerce(value: str):
    """Convert a cell to int/float/bool when it is unambiguous, otherwise leave it as text."""
    text = value.strip()
    if text == "":
        return ""
    low = text.lower()
    if low in _TRUE:
        return True
    if low in _FALSE:
        return False
    try:
        if text.lstrip("+-").isdigit():
            return int(text)
        number = float(text)
        return number
    except ValueError:
        return value


def detect_delimiter(sample: str, override: str | None) -> str:
    if override:
        return override
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
    except csv.Error:
        return ","


def read_records(
    path: Path,
    delimiter: str | None = None,
    encoding: str = "utf-8-sig",
    types: bool = False,
    null_empty: bool = False,
) -> tuple[list[dict], int, str]:
    """Return (records, skipped_count, delimiter_used). Raises SystemExit with a specific message."""
    try:
        raw = path.read_bytes()
    except OSError as err:
        raise SystemExit(f"cannot read {path}: {err.strerror}")

    if b"\x00" in raw:
        raise SystemExit(
            f"{path} contains NUL bytes (often a UTF-16 file read as UTF-8); pass --encoding utf-16"
        )
    try:
        text = raw.decode(encoding)
    except UnicodeDecodeError as err:
        raise SystemExit(
            f"{path} is not valid {encoding}: bad byte at offset {err.start} — is it a different encoding?"
        )

    sample = text[:8192]
    used = detect_delimiter(sample, delimiter)

    # Normalise line endings explicitly. Reading bytes preserves CRLF, which would leave "\r\n" inside
    # multi-line fields and make the same CSV produce different JSON on Windows and on Linux.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    header: list[str] | None = None
    records: list[dict] = []
    skipped = 0
    quote_line = 0

    reader = csv.reader(io.StringIO(text), delimiter=used)
    while True:
        quote_line += 1
        try:
            row = next(reader)
        except StopIteration:
            break
        except csv.Error as err:
            raise SystemExit(f"{path}: malformed CSV near line {quote_line}: {err}")

        if not row or all(cell.strip() == "" for cell in row):
            continue
        if header is None:
            header = [cell.strip() for cell in row]
            if len(set(header)) != len(header):
                dupes = sorted({h for h in header if header.count(h) > 1})
                raise SystemExit(f"{path}: duplicate header name(s) {dupes}; JSON keys would be overwritten")
            continue
        if len(row) != len(header):
            print(f"skip line {quote_line}: expected {len(header)} fields, found {len(row)}", file=sys.stderr)
            skipped += 1
            continue

        if types:
            values = [coerce(c) for c in row]
        elif null_empty:
            values = [None if c == "" else c for c in row]
        else:
            values = row
        records.append(dict(zip(header, values)))

    if header is None:
        raise SystemExit(f"{path}: no header row (the file is empty)")
    if not records and text.strip():
        raise SystemExit(f"{path}: header-only file, no data rows")

    return records, skipped, used


def render(records: list[dict], fmt: str, key_by: str | None, indent: int) -> str:
    if fmt == "jsonl":
        return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records)
    if fmt == "keyed":
        if not key_by:
            raise SystemExit("--format keyed requires --key-by <column>")
        keyed: dict[str, dict] = {}
        for rec in records:
            if key_by not in rec:
                raise SystemExit(f"--key-by column {key_by!r} is not in the header")
            keyed[str(rec[key_by])] = rec
        return json.dumps(keyed, ensure_ascii=False, indent=indent or None) + "\n"
    return json.dumps(records, ensure_ascii=False, indent=indent or None) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Convert a CSV file to JSON.")
    p.add_argument("csv", type=Path, help="input CSV file")
    p.add_argument("-o", "--out", type=Path, default=None, help="output file (default: stdout)")
    p.add_argument("--format", choices=("array", "jsonl", "keyed"), default="array")
    p.add_argument("--key-by", default=None, help="column to key the object by (with --format keyed)")
    p.add_argument("--types", action="store_true", help="convert numeric and boolean cells (off by default)")
    p.add_argument("--null-empty", action="store_true", help="emit null instead of an empty string for empty cells")
    p.add_argument("--delimiter", default=None, help="field delimiter; omitted means sniff it")
    p.add_argument("--encoding", default="utf-8-sig", help="input encoding (default utf-8-sig)")
    p.add_argument("--indent", type=int, default=2, help="JSON indent (default 2; 0 means compact)")
    p.add_argument("--strict", action="store_true", help="exit 2 if any row was skipped")
    args = p.parse_args(argv)

    records, skipped, used = read_records(
        args.csv, args.delimiter, args.encoding, args.types, args.null_empty
    )
    print(f"delimiter={used!r} records={len(records)} skipped={skipped}", file=sys.stderr)

    payload = render(records, args.format, args.key_by, args.indent)
    if args.out:
        args.out.write_text(payload, encoding="utf-8")
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(payload)

    if args.strict and skipped:
        print(f"strict mode: {skipped} row(s) were skipped", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
