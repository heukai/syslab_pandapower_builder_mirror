"""Configuration era files: the E6 and E7 files load and pass their checks; the checks catch errors."""

import datetime as dt

import pytest

from syslab_pandapower_builder.eras import Era, check_era, check_eras, load_eras


@pytest.fixture(scope="module")
def eras():
    return load_eras()


def test_e6_and_e7_are_present_and_clean(eras):
    assert [e.era for e in eras][:2] == ["E6", "E7"]
    assert check_eras(eras) == []


def test_operational_period_of_a_day(eras):
    e6 = eras[0]
    assert e6.period_at(dt.date(2023, 6, 30))["id"] == "6-a"
    assert e6.period_at(dt.date(2023, 10, 10))["id"] == "6-c"
    assert "310-2" in e6.period_at(dt.date(2026, 6, 25))["switchboards"]
    assert e6.period_at(dt.date(2026, 10, 5)) is None          # E7 from then


def test_revisions_list_only_entries_in_force(eras):
    e7 = eras[1]
    assert not e7.in_force(e7.entry("E7-005"))                 # 316-2 is planned
    assert all(e7.in_force(e7.entry(i)) for r in e7.configuration_revisions for i in r["entries"])


def _era(**changes) -> Era:
    base = {"id": "E9-001", "date": dt.date(2030, 1, 2), "element": {"switchboard": "999-1"}, "change": "added",
            "evidence": [{"role": "materialized", "source": "hardware.xml", "ref": "x"}], "origin": "built",
            "certainty": "confirmed", "in_force": True, "status": "confirmed"}
    base.update(changes)
    return Era("E9", "test", 9, dt.date(2030, 1, 1), None, {}, [{"id": "9-a", "from": dt.date(2030, 1, 1)}],
               [base], [{"revision": "9.0", "entries": ["E9-001"]}])


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
