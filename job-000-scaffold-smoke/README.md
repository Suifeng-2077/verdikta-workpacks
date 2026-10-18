# job-999 smoke-test

Analyse smoke test and report persistent anomalies. Replace this line with the job's own one-sentence summary.

## Setup

```bash
python -m venv .venv && . .venv/Scripts/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python analyze.py data.csv
python analyze.py data.csv --threshold 30 --min-scans 3 --max-gap 300 --out report.md
pytest -q
```

| Option | Default | Meaning |
|---|---|---|
| `--threshold` | 30 | value at or above which a scan counts as anomalous |
| `--min-scans` | 3 | consecutive anomalous scans needed for a run to count as persistent |
| `--max-gap` | 300 | seconds between scans after which a run is broken |
| `--out` | stdout | write the markdown report here |

## Input format

One row per observation, with at least `timestamp` (ISO 8601, UTC), `group`, and `value`.
Unparseable rows are dropped and counted rather than silently kept, and a missing required
column fails with a message naming the column.

## Example output

```
$ python analyze.py sample.csv --threshold 30 --min-scans 3
# Anomaly persistence report

- input: `sample.csv`
- window: 2026-10-17 16:00:00 to 2026-10-17 16:07:30 UTC
- parameters: threshold 30.0, min-scans 3, max-gap 300.0s
- rows used: 10; rows skipped: 0

## Per-group summary
...
```

## What the tests cover

Synthetic fixtures only, no network and no real data: a run of exactly `min-scans` counts and one
scan fewer does not; a gap longer than `--max-gap` breaks a run; a single below-threshold scan
splits one; the threshold boundary is inclusive; groups are analysed independently; malformed rows
are skipped and counted; a missing column exits with a clear message; the CLI writes the report.
