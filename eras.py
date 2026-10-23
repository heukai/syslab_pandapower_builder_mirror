"""Configuration era files (``data/eras/E*.yaml``): load and check them.

One file per configuration era: its major change, operational periods, change entries and
configuration revisions (map "dated model versions" in ``.scratch/features/model-versions/``,
decisions of the tickets on configuration changes, consolidation and forward builds).
This module only reads and checks; proposing entries and model development come later.

US-24, US-50.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ERAS_DIR = Path(__file__).resolve().parent / "data" / "eras"

CHANGES = {"added", "removed", "renamed", "moved", "retyped"}
ROLES = {"announced", "evidenced", "materialized", "displayed", "declared"}
ORIGINS = {"built", "discovered", "declared"}
CERTAINTY = {"confirmed", "uncertain"}
STATUS = {"proposed", "confirmed"}


@dataclass
class Era:
    """One configuration era as written in its file."""

    era: str
    title: str
    figure: int
    start: dt.date
    end: dt.date | None
    major_change: dict
    operational_periods: list[dict]
    changes: list[dict]
    configuration_revisions: list[dict] = field(default_factory=list)
    inquiries: list[dict] = field(default_factory=list)
    path: Path | None = None

    def entry(self, entry_id: str) -> dict:
        return next(c for c in self.changes if c["id"] == entry_id)

    def in_force(self, entry: dict) -> bool:
        return entry.get("in_force") is True

    def period_at(self, day: dt.date) -> dict | None:
        """The operational period in force on ``day`` (None outside the era)."""
        if day < self.start or (self.end and day >= self.end):
            return None
        return [p for p in self.operational_periods if p["from"] <= day][-1]


def load_era(path: Path | str) -> Era:
    with open(path, encoding="utf-8") as f:
        d = yaml.safe_load(f)
    return Era(
        era=d["era"], title=d["title"], figure=int(d["figure"]), start=d["start"], end=d.get("end"),
        major_change=d["major_change"], operational_periods=d["operational_periods"],
        changes=d.get("changes") or [], configuration_revisions=d.get("configuration_revisions") or [],
        inquiries=d.get("inquiries") or [], path=Path(path),
    )


def load_eras(folder: Path | str = ERAS_DIR) -> list[Era]:
    """All era files, ordered by start date."""
    return sorted((load_era(p) for p in Path(folder).glob("E*.yaml")), key=lambda e: e.start)


def check_era(era: Era) -> list[str]:
    """Problems in one era file, as messages naming the entry to fix (empty list: fine)."""
    msgs: list[str] = []
    ids = [c.get("id") for c in era.changes]
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        msgs.append(f"{era.era}: change entry id {dup} used twice")
    for c in era.changes:
        cid = c.get("id", "?")
        if not str(cid).startswith(f"{era.era}-"):
            msgs.append(f"{cid}: id must start with {era.era}-")
        for key, allowed in (("change", CHANGES), ("origin", ORIGINS), ("certainty", CERTAINTY), ("status", STATUS)):
            if c.get(key) not in allowed:
                msgs.append(f"{cid}: {key} {c.get(key)!r} is not one of {sorted(allowed)}")
        if not isinstance(c.get("date"), dt.date):
            msgs.append(f"{cid}: date missing or not a date")
        elif c["date"] < era.start or (era.end and c["date"] >= era.end):
            if c.get("in_force") is True:
                msgs.append(f"{cid}: date {c['date']} outside the era ({era.start} to {era.end})")
        inf = c.get("in_force")
        if inf is not True and not (isinstance(inf, str) and inf.startswith("no:")):
            msgs.append(f"{cid}: in_force must be yes, or 'no: <reason>'")
        if not c.get("evidence"):
            msgs.append(f"{cid}: no evidence")
        for ev in c.get("evidence") or []:
            if ev.get("role") not in ROLES:
                msgs.append(f"{cid}: evidence role {ev.get('role')!r} is not one of {sorted(ROLES)}")
            if not ev.get("ref"):
                msgs.append(f"{cid}: evidence without a ref")
        if c.get("certainty") == "uncertain" and not (c.get("flag") or c.get("note")):
            msgs.append(f"{cid}: uncertain entries need a flag or note saying why")
    starts = [p["from"] for p in era.operational_periods]
    if not starts or starts[0] != era.start:
        msgs.append(f"{era.era}: the first operational period must start on the era start {era.start}")
    if starts != sorted(starts):
        msgs.append(f"{era.era}: operational periods out of order")
    revs = [r["revision"] for r in era.configuration_revisions]
    num = era.era[1:]
    for r in era.configuration_revisions:
        if not str(r["revision"]).startswith(f"{num}."):
            msgs.append(f"{era.era}: revision {r['revision']} must be numbered {num}.N")
        for eid in r.get("entries", []):
            if eid not in ids:
                msgs.append(f"{era.era}: revision {r['revision']} lists unknown entry {eid}")
            elif era.entry(eid).get("in_force") is not True:
                msgs.append(f"{era.era}: revision {r['revision']} lists {eid}, which is not in force")
    if len(set(revs)) != len(revs):
        msgs.append(f"{era.era}: a configuration revision number is used twice")
    return msgs


def check_eras(eras: list[Era]) -> list[str]:
    """Checks per era plus the sequence: each era ends where the next starts."""
    msgs = [m for e in eras for m in check_era(e)]
    for a, b in zip(eras, eras[1:]):
        if a.end != b.start:
            msgs.append(f"{a.era} ends {a.end}, but {b.era} starts {b.start}")
    return msgs
