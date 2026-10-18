# python-converters

Two small, dependency-free converters with tests: `csv2json.py` and `json2csv.py`.

They exist because the common version of each has one specific bug that silently corrupts data, and the
fix is cheap if you decide to handle it up front.

## Setup

Standard library only. `pytest` is needed to run the tests.

```bash
pip install -r requirements.txt   # pytest, for the test suite only
```

## csv2json.py

```bash
python csv2json.py data.csv                       # JSON array to stdout
python csv2json.py data.csv -o out.json --indent 2
python csv2json.py data.csv --delimiter ';' --encoding utf-8
python csv2json.py big.csv --jsonl -o out.jsonl   # one object per line, streams well
python csv2json.py data.csv --strict              # exit 2 if any row was skipped
```

| option | default | meaning |
|---|---|---|
| `-o, --out` | stdout | output file |
| `--delimiter` | sniffed | force a field delimiter |
| `--encoding` | `utf-8-sig` | input encoding |
| `--indent` | `2` | JSON indent, `0` for compact |
| `--jsonl` | off | one JSON object per line instead of one array |
| `--strict` | off | non-zero exit if a row was skipped |

What it gets right:

- Parsing uses the stdlib `csv` reader, never `str.split`, so **quoted commas, doubled quotes and newlines
  inside a field survive**.
- The delimiter is sniffed (`csv.Sniffer` over `, ; \t |`) with `--delimiter` to override the cases the
  sniffer gets wrong.
- Encoding defaults to `utf-8-sig` because spreadsheet exports usually carry a BOM, and a stray BOM silently
  changes the first column's name.
- A **ragged row is skipped and reported with its line number**, and the count is always printed — nothing
  disappears quietly.

## json2csv.py

```bash
python json2csv.py data.json                      # CSV to stdout
python json2csv.py data.json -o out.csv --delimiter ';'
python json2csv.py data.json --columns id,name,email   # force column order
```

What it gets right:

- **The header is the union of keys across every record**, not the first record's keys. Taking the first
  record's keys is the classic bug: a record with an extra key loses it, and a record missing a key shifts
  every following column.
- Missing keys become an empty cell instead of being dropped.
- Nested objects and arrays are **JSON-encoded into the cell** rather than stringified with `repr`, so they
  parse back out.
- A malformed file fails with the line and column, not a bare traceback.

## Real output, not an illustration

Fixture `sample.csv`:

```csv
id,name,address,note
1,"Doe, John","1 Main St, Apt 2","said ""hi"""
2,Ann,"9b Side Rd","two
lines"
3,Bob,,empty address
```

```
$ python csv2json.py sample.csv --indent 2
delimiter=',' records=3 skipped=0
[
  {
    "id": "1",
    "name": "Doe, John",
    "address": "1 Main St, Apt 2",
    "note": "said \"hi\""
  },
  {
    "id": "2",
    "name": "Ann",
    "address": "9b Side Rd",
    "note": "two\nlines"
  },
  {
    "id": "3",
    "name": "Bob",
    "address": "",
    "note": "empty address"
  }
]
```

Round trip back to CSV:

```
$ python csv2json.py sample.csv -o sample.json && python json2csv.py sample.json
id,name,address,note
1,"Doe, John","1 Main St, Apt 2","said ""hi"""
2,Ann,9b Side Rd,"two
lines"
3,Bob,,empty address
```

Byte-for-byte the input, including the quoted comma, the doubled quote, the embedded newline and the empty
field.

## Tests

```
$ python -m pytest -q
.................                                                        [100%]
17 passed in 0.13s
```

Synthetic fixtures only, no network, no real data. Coverage includes: quoted comma, embedded newline,
doubled quote, BOM-prefixed header, semicolon detection, explicit delimiter override, ragged row skipped
and counted, empty file, CLI writing a file, `--strict` exit code, key union, missing key not shifting a
row, nested value JSON-encoded, empty array, malformed JSON naming the line, forced column order, and a
CSV→JSON→CSV round trip.
