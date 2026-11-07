"""Configuration era files: the era files (E0 to E7) load and pass their checks; the checks catch errors."""

import datetime as dt

import pytest

from syslab_pandapower_builder.eras import Era, check_era, check_eras, era_at, load_eras, version_log


@pytest.fixture(scope="module")
def eras():
    return load_eras()


def by_id(eras, name):
    return next(e for e in eras if e.era == name)


def test_eras_are_present_in_order_and_clean(eras):
    assert [e.era for e in eras] == ["E0", "E2", "E3", "E4", "E6", "E7"]   # no E1, no E5
    assert check_eras(eras) == []


def test_era_of_a_day(eras):
    assert era_at(eras, dt.date(2009, 12, 1)) is None              # before the first data files
    assert era_at(eras, dt.date(2014, 1, 1)).era == "E3"
    assert era_at(eras, dt.date(2023, 6, 16)).era == "E6"
    assert era_at(eras, dt.date(2026, 10, 25)).era == "E7"
    assert [e.basis for e in eras[:4]] == ["header-only"] * 3 + ["configuration"]


def test_operational_period_of_a_day(eras):
    e6 = by_id(eras, "E6")
    assert e6.period_at(dt.date(2023, 6, 30))["id"] == "6-a"
    assert e6.period_at(dt.date(2023, 10, 10))["id"] == "6-c"
    assert "310-2" in e6.period_at(dt.date(2026, 6, 25))["switchboards"]
    assert e6.period_at(dt.date(2026, 10, 5)) is None          # E7 from then


def test_revisions_list_only_entries_in_force(eras):
    e7 = by_id(eras, "E7")
    assert not e7.in_force(e7.entry("E7-005"))                 # 316-2 is planned
    assert all(e7.in_force(e7.entry(i)) for r in e7.configuration_revisions for i in r["entries"])


def _era(**changes) -> Era:
    base = {"id": "E9-001", "date": dt.date(2030, 1, 2), "element": {"switchboard": "999-1"}, "change": "added",
            "evidence": [{"role": "materialized", "source": "hardware.xml", "ref": "x"}], "origin": "built",
            "certainty": "confirmed", "in_force": True, "status": "confirmed"}
    base.update(changes)
    return Era("E9", "test", 9, dt.date(2030, 1, 1), None, {}, [{"id": "9-a", "from": dt.date(2030, 1, 1)}],
               [base], [{"revision": "9.0", "entries": ["E9-001"]}])


def test_header_periods_of_a_day(eras):
    e6 = by_id(eras, "E6")
    assert e6.start == dt.date(2023, 6, 16)                    # first operational evidence: headers
    assert [h["id"] for h in e6.header_periods_at(dt.date(2023, 8, 1), "319-3")] == ["E6-H04"]
    assert e6.header_periods_at(dt.date(2025, 6, 1), "319-3") == []
    assert {h["kind"] for h in e6.header_periods_at(dt.date(2023, 12, 1))} == {"lag", "meter-lag"}


@pytest.mark.parametrize("period, msg", [
    ({"kind": "late"}, "kind"),
    ({"id": "E9-001"}, "must start with E9-H"),
    ({"to": dt.date(2029, 12, 1)}, "after to"),
    ({"carries": ""}, "carries missing"),
])
def test_header_period_checks(period, msg):
    era = _era()
    h = {"id": "E9-H01", "switchboards": ["999-1"], "from": dt.date(2030, 1, 1), "to": dt.date(2030, 2, 1),
         "kind": "lag", "carries": "x", "status": "proposed"}
    h.update(period)
    era.header_periods = [h]
    msgs = check_era(era)
    assert any(msg in m for m in msgs), msgs


@pytest.mark.parametrize("changes, msg", [
    ({"change": "teleported"}, "change"),
    ({"in_force": "maybe"}, "in_force"),
    ({"evidence": []}, "no evidence"),
    ({"certainty": "uncertain"}, "flag or note"),
    ({"id": "E8-001"}, "must start with E9-"),
    ({"date": dt.date(2029, 1, 1)}, "outside the era"),
])
def test_checks_name_the_entry_to_fix(changes, msg):
    msgs = check_era(_era(**changes))
    assert any(msg in m for m in msgs), msgs


def test_version_log_lists_revisions_models_and_open_entries(eras):
    log = version_log(eras)
    assert log.index("## Era 7") < log.index("## Era 6") < log.index("## Era 0")      # newest era first
    assert "| 6.7 (from 2026-08-13) | 2026-08-13 | E6-011 |" in log
    assert "| 6.6.2 | 6.6 | 2026-10-24 | current | 2026-06-25:" in log
    assert "| 6.7.1 | 6.7 | built 2026-11-03, not published | superseded |" in log
    assert "| 6.7.2 | 6.7 | built 2026-11-07, not published | current |" in log
    assert "| 6.5 (from 2026-01-07) | 2026-01-07 | E6-025 | 117-4 Cable_D1: added" in log
    assert "E6-013 330-12 Spare_6, Spare_7: removed" in log and "[no: evidence only]" in log   # not in a revision
    assert "E7-005" in log and "[no: planned]" in log


def test_model_version_checks():
    era = _era()
    era.model_versions = [{"version": "9.1.1", "revision": "9.1", "status": "current"},
                          {"version": "8.0.1", "revision": "9.0", "status": "old"}]
    msgs = check_era(era)
    assert any("revision 9.1 is not" in m for m in msgs)
    assert any("must be numbered 9.0.N" in m for m in msgs)
    assert any("status 'old'" in m for m in msgs)


def test_header_only_era_rejects_configuration_evidence():
    era = _era()
    era.basis = "header-only"
    assert any("header-only era" in m for m in check_era(era))


def test_versions_log_file_is_up_to_date(eras):
    """data/eras/VERSIONS.md is generated; regenerate it with `python -m syslab_pandapower_builder.eras`."""
    path = eras[0].path.parent / "VERSIONS.md"
    assert path.read_text(encoding="utf-8").replace("\r\n", "\n") == version_log(eras)
