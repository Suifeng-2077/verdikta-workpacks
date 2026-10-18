"""job-999 smoke-test - Analyse smoke test and report persistent anomalies. Replace this line with the job's own one-sentence summary..

Built from the Verdikta scaffold. The generic parts (CLI, robust loading, per-group runs,
markdown report, tests) are already correct; only the marked analysis section should need
editing for a new job. Keep the CLI flags and their defaults identical to the job's table.

Usage:
    python analyze.py data.csv [--threshold 30] [--min-scans 3] [--max-gap 300] [--out report.md]
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

# The columns every input must have. Widen only if the job's table says so.
REQUIRED = ("timestamp", "group", "value")


def load(path: str | Path, required: tuple[str, ...] = REQUIRED) -> tuple[pd.DataFrame, int]:
    """Read the CSV, coerce types, drop unparseable rows, and report how many were dropped."""
    df = pd.read_csv(path)
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise SystemExit(f"missing required column(s): {', '.join(missing)}")

    before = len(df)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["timestamp", "value"])
    skipped = before - len(df)
    df = df.sort_values("timestamp")
    return df.reset_index(drop=True), skipped


@dataclass
class Run:
    """One uninterrupted stretch of scans at or above the threshold."""

    group: str
    start: pd.Timestamp
    end: pd.Timestamp
    scans: int
    mean: float
    peak: float

    @property
    def duration_s(self) -> float:
        return (self.end - self.start).total_seconds()


def find_runs(
    df: pd.DataFrame, threshold: float, min_scans: int, max_gap_s: float
) -> list[Run]:
    """Runs of consecutive at-threshold scans per group, broken by a low scan or a long gap."""
    runs: list[Run] = []

    for group, g in df.groupby("group", sort=False):
        g = g.sort_values("timestamp")
        current: list[tuple[pd.Timestamp, float]] = []
        prev_t: pd.Timestamp | None = None

        def flush() -> None:
            if len(current) >= min_scans:
                values = [v for _, v in current]
                runs.append(
                    Run(
                        str(group),
                        current[0][0],
                        current[-1][0],
                        len(current),
                        sum(values) / len(values),
                        max(values),
                    )
                )

        for t, v in zip(g["timestamp"], g["value"]):
            if prev_t is not None and (t - prev_t).total_seconds() > max_gap_s:
                flush()
                current = []
            if float(v) >= threshold:
                current.append((t, float(v)))
            else:
                flush()
                current = []
            prev_t = t
        flush()

    runs.sort(key=lambda r: r.duration_s, reverse=True)
    return runs


def summarise(df: pd.DataFrame, threshold: float) -> list[dict[str, object]]:
    """Per-group statistics. Extend the dict here if the rubric asks for more columns."""
    rows: list[dict[str, object]] = []
    for group, g in df.groupby("group", sort=False):
        v = g["value"]
        rows.append(
            {
                "group": str(group),
                "rows": len(g),
                "start": g["timestamp"].min(),
                "end": g["timestamp"].max(),
                "pct_at_threshold": float((v >= threshold).mean() * 100.0),
                "median": float(v.median()),
                "p95": float(v.quantile(0.95)),
                "max": float(v.max()),
            }
        )
    return rows


def fmt_duration(seconds: float) -> str:
    total = int(round(seconds))
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    return f"{hours}h {minutes:02d}m" if hours else f"{minutes}m {secs:02d}s"


def render(csv_path: str, df: pd.DataFrame, skipped: int, args: argparse.Namespace, runs: list[Run]) -> str:
    stats = summarise(df, args.threshold)
    start, end = df["timestamp"].min(), df["timestamp"].max()
    lines: list[str] = []

    lines.append("# Anomaly persistence report")
    lines.append("")
    lines.append(f"- input: `{csv_path}`")
    lines.append(f"- window: {start:%Y-%m-%d %H:%M:%S} to {end:%Y-%m-%d %H:%M:%S} UTC")
    lines.append(
        f"- parameters: threshold {args.threshold}, min-scans {args.min_scans}, max-gap {args.max_gap}s"
    )
    lines.append(f"- rows used: {len(df)}; rows skipped: {skipped}")
    lines.append("")

    lines.append("## Per-group summary")
    lines.append("")
    lines.append("| group | rows | % at threshold | median | p95 | max |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for r in stats:
        lines.append(
            f"| {r['group']} | {r['rows']} | {r['pct_at_threshold']:.2f} | "
            f"{r['median']:.2f} | {r['p95']:.2f} | {r['max']:.2f} |"
        )
    lines.append("")

    lines.append("## Persistent runs")
    lines.append("")
    if not runs:
        lines.append("No run met the threshold for the required number of scans.")
    else:
        lines.append("| group | start | end | duration | scans | mean | peak |")
        lines.append("|---|---|---|---:|---:|---:|---:|")
        for r in runs:
            lines.append(
                f"| {r.group} | {r.start:%Y-%m-%d %H:%M:%S} | {r.end:%H:%M:%S} | "
                f"{fmt_duration(r.duration_s)} | {r.scans} | {r.mean:.2f} | {r.peak:.2f} |"
            )
    lines.append("")

    lines.append("## Findings")
    lines.append("")
    if runs:
        top = runs[0]
        lines.append(
            f"- {top.group}: the longest persistent run lasted {fmt_duration(top.duration_s)} "
            f"across {top.scans} scans, peaking at {top.peak:.2f} against a threshold of {args.threshold}."
        )
    busiest = max(stats, key=lambda r: r["pct_at_threshold"]) if stats else None
    if busiest:
        lines.append(
            f"- {busiest['group']}: at or above the threshold in {busiest['pct_at_threshold']:.1f}% "
            f"of its {busiest['rows']} rows, median {busiest['median']:.2f}."
        )
    lines.append(f"- {skipped} row(s) could not be parsed and were excluded, not silently kept.")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Analyse smoke test and report persistent anomalies. Replace this line with the job's own one-sentence summary.")
    p.add_argument("csv", help="input CSV")
    p.add_argument("--threshold", type=float, default=30.0)
    p.add_argument("--min-scans", type=int, default=3)
    p.add_argument("--max-gap", type=float, default=300.0)
    p.add_argument("--out", default=None, help="write the markdown report here instead of stdout")
    args = p.parse_args(argv)

    df, skipped = load(args.csv)
    runs = find_runs(df, args.threshold, args.min_scans, args.max_gap)
    report = render(args.csv, df, skipped, args, runs)

    if args.out:
        Path(args.out).write_text(report, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
