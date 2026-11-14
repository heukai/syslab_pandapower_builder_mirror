"""Column maps (ticket 08): pairing rules, the carried commits, header spelling and the era-file writer."""

import datetime as dt
import json
import xml.etree.ElementTree as ET

import yaml

from syslab_pandapower_builder.column_maps import (
    Column, _block, carried_commits, header_names, match, norm, resolve_meters, write_era_maps,
)
from syslab_pandapower_builder.eras import ERAS_DIR, load_era
from syslab_pandapower_builder.hardware_parser import _parse_bay


def brk(name, bay, busbar, sb="117-2"):
    return Column(sb, "breaker", name, bay, busbar)


def meter(name, bay, sb="117-2"):
    return Column(sb, "meter", name, bay)


def test_norm_drops_spelling_differences():
    assert norm("Busbar A") == norm("busbar_a") == norm("BUSBAR-A") == norm("Busbar.A")
    assert norm("Busbar A") != norm("Busbar B")


class TestMatch:
    def test_breakers_pair_by_bay_and_busbar_and_equal_names_count_as_same(self):
        data = [brk("117_2_BRK_Grid_Grid", "Grid", "Grid"), brk("117_2_BRK_PV_Busbar A", "PV", "A")]
        model = [brk("117_2_BRK_Grid_Busbar_Grid", "Grid", "Grid"), brk("117_2_BRK_PV_Busbar A", "PV", "A")]
        m = match(data, model)
        assert m["pairs"] == [{"data": "117_2_BRK_Grid_Grid", "model": "117_2_BRK_Grid_Busbar_Grid",
                               "rule": "same bay and busbar"}]
        assert m["same"] == 1
        assert m["unmatched_data"] == m["unmatched_model"] == []

    def test_a_meter_pairs_by_bay_only_when_each_side_has_one(self):
        m = match([meter("P_Grid", "Grid")], [meter("P_Grid 117-4", "Grid")])
        assert m["pairs"] == [{"data": "P_Grid", "model": "P_Grid 117-4", "rule": "same bay"}]
        two = match([meter("P_A", "X"), meter("P_B", "X")], [meter("P_C", "X")])
        assert two["pairs"] == [] and two["unmatched_data"] == ["P_A", "P_B"]

    def test_a_renamed_bay_pairs_by_spelling_or_stays_unmatched(self):
        m = match([brk("117_2_BRK_Cable C1_Busbar A", "Cable C1", "A"), brk("117_2_BRK_Old_Busbar A", "Old", "A")],
                  [brk("117_2_BRK_CableC1_BusbarA", "CableC1", "Busbar A"), brk("117_2_BRK_New_Busbar A", "New", "A")])
        assert m["pairs"] == [{"data": "117_2_BRK_Cable C1_Busbar A", "model": "117_2_BRK_CableC1_BusbarA",
                               "rule": "same name after spelling"}]
        assert m["unmatched_data"] == ["117_2_BRK_Old_Busbar A"]      # never guessed
        assert m["unmatched_model"] == ["117_2_BRK_New_Busbar A"]


class TestCarriedCommits:
    def test_one_commit_for_all_switchboards_the_latest_counts(self):
        p = {"carries": "syslab abc123def then ebb1fb939 (committed 2023-06-23)", "switchboards": ["117-2", "117-5"]}
        assert carried_commits(p) == {"117-2": "ebb1fb939", "117-5": "ebb1fb939"}

    def test_one_commit_per_switchboard(self):
        p = {"carries": "319-2: syslab b5d64e3d4; 319-3: syslab f9d699cd5", "switchboards": ["319-2", "319-3"]}
        assert carried_commits(p) == {"319-2": "b5d64e3d4", "319-3": "f9d699cd5"}

    def test_none_and_free_text_carry_no_configuration(self):
        assert carried_commits({"carries": "none: E1/E2 busbars swapped against b736d2d87",
                                "switchboards": ["715-2"]}) is None
        assert carried_commits({"carries": "old meter names", "switchboards": ["117-4"]}) is None


def test_header_names_overlap_the_stretch_and_an_open_era_is_current(tmp_path):
    (tmp_path / "117_2.json").write_text(json.dumps({"eras": [
        {"valid_from": "2023-01-01T00:00:00", "valid_to": "2023-06-30T23:59:59", "columns": ["BRK_Old"]},
        {"valid_from": "2023-07-01T00:00:00", "valid_to": None, "columns": ["BRK_New"]},
    ]}))
    assert header_names(tmp_path, "117-2", dt.date(2023, 6, 1), dt.date(2023, 6, 10)) == {"BRK_Old"}
    assert header_names(tmp_path, "117-2", dt.date(2026, 1, 1), dt.date(2026, 1, 2)) == {"BRK_New"}
    assert header_names(tmp_path, "117-5", dt.date(2023, 6, 1), dt.date(2023, 6, 10)) is None


def test_meters_take_the_header_spelling_or_the_bay_name_for_a_lone_meter():
    cols = [meter("P_Cable C1A", "Cable C1A"), meter("P_Grid 117-4", "Grid"), brk("117_2_BRK_PV_Busbar A", "PV", "A")]
    out = resolve_meters(cols, {"P_CableC1A[kW]", "P_Grid[kW]", "BRK_PV_Busbar A"})
    assert [c.name for c in out] == ["P_CableC1A", "P_Grid", "117_2_BRK_PV_Busbar A"]


def test_interlocks_read_both_attribute_spellings():
    for a, b in (("breakerA", "breakerB"), ("brkA", "brkB")):
        bay = _parse_bay(ET.fromstring(f'<bay name="X"><interlock name="I" {a}="A1" {b}="B1"/></bay>'))
        assert (bay.interlocks[0].breaker_a, bay.interlocks[0].breaker_b) == ("A1", "B1")


MAPS = [{"status": "proposed", "from": dt.date(2023, 6, 16), "to": dt.date(2023, 6, 22),
         "targets": [{"from": dt.date(2023, 6, 16), "nodes": {"syslab-09": "29e3f21a0"}}],
         "switchboards": {"117-2": {"carried": "ebb1fb939",
                                    "pairs": [{"data": "a", "model": "b", "rule": "same bay"}],
                                    "same": 0, "unmatched_data": [], "unmatched_model": []}}}]


def test_block_has_no_anchors_and_one_line_per_pair():
    text = _block(MAPS)
    assert "&id" not in text and "*id" not in text
    assert "- {data: a, model: b, rule: same bay}" in text
    assert yaml.safe_load(text.replace("\n    ", "\n").lstrip()) == {"column_map": MAPS}


def test_writer_replaces_the_block_and_leaves_the_rest(tmp_path):
    path = tmp_path / "E9.yaml"
    path.write_text("header_periods:\n  - id: E9-H01\n    status: proposed\n  # a comment stays\n  - id: E9-H02\n"
                    "    status: proposed\nnext: 1\n")
    write_era_maps(path, {"E9-H01": MAPS})
    once = path.read_text()
    write_era_maps(path, {"E9-H01": MAPS})
    assert path.read_text() == once                                   # rerun gives the same file
    assert "# a comment stays" in once
    d = yaml.safe_load(once)
    assert d["header_periods"][0]["column_map"] == MAPS
    assert "column_map" not in d["header_periods"][1] and d["next"] == 1


def test_e6_carries_written_maps_without_anchors():
    text = (ERAS_DIR / "E6.yaml").read_text(encoding="utf-8")
    assert "&id" not in text
    periods = {h["id"]: h for h in load_era(ERAS_DIR / "E6.yaml").header_periods}
    h03 = periods["E6-H03"]["column_map"]
    assert [m["from"] for m in h03] == [dt.date(2023, 10, 23), dt.date(2023, 10, 31)]
    assert h03[0]["switchboards"]["117-2"]["unmatched_data"] == []
    for h in periods.values():
        for m in h.get("column_map", []):     # proposed, never confirmed by the bot; no map says why
            assert m["status"] == "proposed" or (m["status"] == "no map" and m["reason"])
    assert "b5d64e3d4" in periods["E6-H09"]["column_map"][0]["reason"]
