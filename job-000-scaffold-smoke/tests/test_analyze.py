"""Tests for analyze.py, built on synthetic fixtures so they need no network or real data."""

from __future__ import annotations

import pandas as pd
import pytest

from analyze import find_runs, load, main


def write_csv(tmp_path, rows, name="data.csv"):
    """rows: list of (timestamp, group, value) tuples, written with the required header."""
    path = tmp_path / name
    path.write_text(
        "timestamp,group,value\n" + "".join(f"{t},{g},{v}\n" for t, g, v in rows),
        encoding="utf-8",
    )
    return path


def minutes(*offsets: int, base="2026-10-17T16:00:00Z"):
    start = pd.Timestamp(base)
    return [(start + pd.Timedelta(minutes=m)).strftime("%Y-%m-%dT%H:%M:%SZ") for m in offsets]


def test_run_of_exactly_min_scans_counts_as_persistent(tmp_path):
    ts = minutes(0, 1, 2)
    df, _ = load(write_csv(tmp_path, [(t, "SOL/USDC", 40) for t in ts]))
    runs = find_runs(df, threshold=30, min_scans=3, max_gap_s=300)
    assert len(runs) == 1
    assert runs[0].scans == 3


def test_run_one_short_does_not_count(tmp_path):
    ts = minutes(0, 1)
    df, _ = load(write_csv(tmp_path, [(t, "SOL/USDC", 40) for t in ts]))
    assert find_runs(df, threshold=30, min_scans=3, max_gap_s=300) == []


def test_gap_breaks_the_run(tmp_path):
    ts = minutes(0, 1, 20, 21)
    df, _ = load(write_csv(tmp_path, [(t, "P", 40) for t in ts]))
    # 19 minutes between the second and third scan, max gap 5 minutes.
    assert find_runs(df, threshold=30, min_scans=3, max_gap_s=300) == []


def test_low_scan_splits_the_run(tmp_path):
    ts = minutes(0, 1, 2, 3, 4)
    rows = [(t, "P", v) for t, v in zip(ts, [40, 40, 5, 40, 40])]
    df, _ = load(write_csv(tmp_path, rows))
    assert find_runs(df, threshold=30, min_scans=3, max_gap_s=300) == []


def test_threshold_boundary_counts(tmp_path):
    ts = minutes(0, 1, 2)
    df, _ = load(write_csv(tmp_path, [(t, "P", 30) for t in ts]))
    assert len(find_runs(df, threshold=30, min_scans=3, max_gap_s=300)) == 1


def test_groups_are_independent(tmp_path):
    ts = minutes(0, 1, 2)
    rows = [(t, "A", 40) for t in ts] + [(t, "B", 1) for t in ts]
    df, _ = load(write_csv(tmp_path, rows))
    runs = find_runs(df, threshold=30, min_scans=3, max_gap_s=300)
    assert [r.group for r in runs] == ["A"]


def test_malformed_rows_are_skipped_and_counted(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text(
        "timestamp,group,value\n"
        "2026-10-17T16:00:00Z,P,40\n"
        "not-a-date,P,40\n"
        "2026-10-17T16:01:00Z,P,oops\n"
        "2026-10-17T16:02:00Z,P,40\n",
        encoding="utf-8",
    )
    df, skipped = load(path)
    assert skipped == 2
    assert len(df) == 2


def test_missing_column_fails_clearly(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("timestamp,group\n2026-10-17T16:00:00Z,P\n", encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        load(path)
    assert "value" in str(exc.value)


def test_cli_writes_report_file(tmp_path, capsys):
    ts = minutes(0, 1, 2)
    csv = write_csv(tmp_path, [(t, "P", 40) for t in ts])
    out = tmp_path / "report.md"
    assert main([str(csv), "--out", str(out)]) == 0
    text = out.read_text(encoding="utf-8")
    assert "# Anomaly persistence report" in text
    assert "Persistent runs" in text
    assert "rows skipped: 0" in text
    assert f"wrote {out}" in capsys.readouterr().out
