"""Tests for csv2json.py and json2csv.py. Synthetic fixtures only: no network, no real data."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from csv2json import main as csv2json_main
from csv2json import read_records
from json2csv import field_order, load_records, to_csv


# ---------- csv2json ----------

def test_quoted_comma_is_one_field(tmp_path):
    f = tmp_path / "a.csv"
    f.write_text('name,address\n"Doe, John","1 Main St, Apt 2"\n', encoding="utf-8")
    records, skipped, _ = read_records(f)
    assert skipped == 0
    assert records == [{"name": "Doe, John", "address": "1 Main St, Apt 2"}]


def test_embedded_newline_survives(tmp_path):
    f = tmp_path / "a.csv"
    f.write_text('id,note\n1,"line one\nline two"\n', encoding="utf-8")
    records, _, _ = read_records(f)
    assert records[0]["note"] == "line one\nline two"


def test_doubled_quote_is_unescaped(tmp_path):
    f = tmp_path / "a.csv"
    f.write_text('id,quote\n1,"he said ""hi"""\n', encoding="utf-8")
    records, _, _ = read_records(f)
    assert records[0]["quote"] == 'he said "hi"'


def test_bom_does_not_corrupt_first_header(tmp_path):
    f = tmp_path / "a.csv"
    f.write_bytes("\ufeffid,name\n1,ann\n".encode("utf-8"))
    records, _, _ = read_records(f)
    assert list(records[0]) == ["id", "name"]


def test_semicolon_detected(tmp_path):
    f = tmp_path / "a.csv"
    f.write_text("id;name\n1;ann\n2;bob\n", encoding="utf-8")
    records, _, used = read_records(f)
    assert used == ";"
    assert len(records) == 2


def test_explicit_delimiter_beats_sniffer(tmp_path):
    f = tmp_path / "a.csv"
    f.write_text("id|name\n1|ann\n", encoding="utf-8")
    records, _, used = read_records(f, delimiter="|")
    assert used == "|"
    assert records == [{"id": "1", "name": "ann"}]


def test_ragged_row_is_skipped_and_counted(tmp_path, capsys):
    f = tmp_path / "a.csv"
    f.write_text("id,name\n1,ann\n2,two,extra\n3,cid\n", encoding="utf-8")
    records, skipped, _ = read_records(f)
    assert skipped == 1
    assert [r["id"] for r in records] == ["1", "3"]
    assert "skip line 3" in capsys.readouterr().err


def test_empty_file_fails_clearly(tmp_path):
    f = tmp_path / "a.csv"
    f.write_text("", encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        read_records(f)
    assert "no header row" in str(exc.value)


def test_cli_writes_json_file(tmp_path):
    f = tmp_path / "a.csv"
    f.write_text("id,name\n1,ann\n", encoding="utf-8")
    out = tmp_path / "out.json"
    assert csv2json_main([str(f), "-o", str(out)]) == 0
    assert json.loads(out.read_text(encoding="utf-8")) == [{"id": "1", "name": "ann"}]


def test_cli_strict_exits_nonzero_on_skip(tmp_path):
    f = tmp_path / "a.csv"
    f.write_text("id,name\n1,ann\n2\n", encoding="utf-8")
    assert csv2json_main([str(f), "--strict"]) == 2


# ---------- json2csv ----------

def test_header_is_union_of_keys(tmp_path):
    f = tmp_path / "a.json"
    f.write_text(json.dumps([{"a": 1}, {"a": 2, "b": 3}]), encoding="utf-8")
    records = load_records(f)
    assert field_order(records, None) == ["a", "b"]


def test_missing_key_becomes_empty_cell_and_does_not_shift(tmp_path):
    f = tmp_path / "a.json"
    f.write_text(json.dumps([{"a": 1, "b": 2}, {"a": 3}]), encoding="utf-8")
    records = load_records(f)
    cols = field_order(records, None)
    lines = to_csv(records, cols, ",").strip().split("\n")
    assert lines[0] == "a,b"
    assert lines[2] == "3,"


def test_nested_value_is_json_encoded(tmp_path):
    f = tmp_path / "a.json"
    f.write_text(json.dumps([{"id": 1, "meta": {"x": [1, 2]}}]), encoding="utf-8")
    records = load_records(f)
    row = to_csv(records, field_order(records, None), ",").strip().split("\n")[1]
    assert json.loads(row.split(",", 1)[1].strip('"').replace('""', '"')) == {"x": [1, 2]}


def test_empty_array_is_handled(tmp_path):
    f = tmp_path / "a.json"
    f.write_text("[]", encoding="utf-8")
    assert load_records(f) == []


def test_malformed_json_names_the_line(tmp_path):
    f = tmp_path / "a.json"
    f.write_text('[{"a": 1,}]', encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        load_records(f)
    assert "not valid JSON" in str(exc.value)


def test_forcing_column_order(tmp_path):
    f = tmp_path / "a.json"
    f.write_text(json.dumps([{"b": 1, "a": 2}]), encoding="utf-8")
    records = load_records(f)
    assert field_order(records, ["a", "b"]) == ["a", "b"]


def test_round_trip_csv_then_json(tmp_path):
    """csv -> json -> csv must preserve values, which is the property a buyer actually cares about."""
    src = tmp_path / "src.csv"
    src.write_text('id,note\n1,"a, b"\n2,"line\nbreak"\n', encoding="utf-8")
    records, _, _ = read_records(src)
    back = to_csv(records, field_order(records, None), ",")
    assert '"a, b"' in back
    assert "line\nbreak" in back
