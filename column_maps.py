"""Column maps for data-name periods (auto-update ticket 08).

In a data-name period (era file ``header_periods``) the data files of some switchboards use the names of
another configuration than the master in force: the one they ``carries``. A column map translates those data
names into the model's names, per period and switchboard, derived automatically:

1. the data names come from the carried configuration's ``hardware.xml`` as the data logger writes them
   (``BRK_<bay>_<busbar>``, ``P_<instrument>``), the model names from the configuration in force, as the
   builder names its switches (:func:`~syslab_pandapower_builder.builder._derive_brk_name`) and bay meters;
2. a data breaker pairs with the model breaker of the same switchboard, bay and busbar; a data meter with
   the meter of the same switchboard and bay where each side has one;
3. what is left pairs where the names are equal after normalising spelling (case, ``_``, ``-``, ``.``,
   spaces);
4. the rest is listed as unmatched, never guessed; a person confirms the map (the bot's merge request).

A period that spans a master change of its switchboards gets one map per stretch with the same pairs; each
map names the target configurations (lab commit per node, from which day) it was derived against.
The maps are written into the era file next to their period (``column_map``); a published model version
later gets the name pairs only (``column_map.json``, without lab references).

    python -m syslab_pandapower_builder.column_maps --conf-repo syslab_lab --era E6          # print
    python -m syslab_pandapower_builder.column_maps --conf-repo syslab_lab --era E6 --write  # into E6.yaml
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

import yaml

from .builder import _bay_bus_name, _bb_bus_name, _derive_brk_name
from .conf_snapshot import _git, conf_in_force
from .eras import ERAS_DIR, Era, load_era
from .hardware_parser import GRID_NODES, SwitchboardDef, load_grid_switchboards

_COMMIT = re.compile(r"\b[0-9a-f]{9}\b")
_SB = re.compile(r"\b(\d{3}-\d{1,2}):")


@dataclass(frozen=True)
class Column:
    """One data column of a configuration: a breaker (``bay``, ``busbar``) or a bay meter."""

    switchboard: str
    kind: str          # "breaker" | "meter"
    name: str          # data name (carried configuration) or model name (configuration in force)
    bay: str
    busbar: str = ""


def norm(name: str) -> str:
    """A name with spelling differences removed (case, ``_``, ``-``, ``.``, spaces)."""
    return re.sub(r"[\s_\-.]", "", name).lower()


def data_columns(sw: SwitchboardDef) -> list[Column]:
    """The columns the data logger writes for *sw*: ``<sb>_BRK_<bay>_<busbar>``, ``P_<instrument>``."""
    p = sw.name.replace("-", "_")
    cols = [Column(sw.name, "breaker", f"{p}_BRK_{bay.name}_{b.busbar}", bay.name, b.busbar)
            for bay in sw.bays for b in bay.breakers]
    cols += [Column(sw.name, "meter", f"P_{i.name}", bay.name) for bay in sw.bays for i in bay.instruments]
    return cols


def model_columns(sw: SwitchboardDef) -> list[Column]:
    """The model's names for *sw*: its switch names (as the builder derives them) and its bay meters."""
    cols = []
    for bay in sw.bays:
        for b in bay.breakers:
            name = _derive_brk_name(_bb_bus_name(sw.name, b.busbar), _bay_bus_name(sw.name, bay.name))
            if name:
                cols.append(Column(sw.name, "breaker", name, bay.name, b.busbar))
        cols += [Column(sw.name, "meter", f"P_{i.name}", bay.name) for i in bay.instruments]
    return cols


def match(data: list[Column], model: list[Column]) -> dict:
    """Pair data columns with model columns (rules 2-4 of the module); returns pairs, same count, unmatched."""
    pairs, used, same = [], set(), [0]

    def take(d: Column, m: Column, rule: str) -> None:
        used.add(m)
        if d.name == m.name:
            same[0] += 1
        else:
            pairs.append({"data": d.name, "model": m.name, "rule": rule})

    left = []
    for d in data:
        if d.kind == "breaker":
            hits = [m for m in model if m.kind == "breaker" and m not in used
                    and (m.switchboard, m.bay, m.busbar) == (d.switchboard, d.bay, d.busbar)]
        else:
            mine = [x for x in data if x.kind == "meter" and (x.switchboard, x.bay) == (d.switchboard, d.bay)]
            hits = [m for m in model if m.kind == "meter" and m not in used
                    and (m.switchboard, m.bay) == (d.switchboard, d.bay)]
            hits = hits if len(hits) == 1 and len(mine) == 1 else []
        if len(hits) == 1:
            take(d, hits[0], "same bay and busbar" if d.kind == "breaker" else "same bay")
        else:
            left.append(d)
    unmatched = []
    for d in left:
        hits = [m for m in model if m.kind == d.kind and m not in used and norm(m.name) == norm(d.name)]
        if len(hits) == 1:
            take(d, hits[0], "same name after spelling")
        else:
            unmatched.append(d.name)
    return {"pairs": pairs, "same": same[0], "unmatched_data": sorted(unmatched),
            "unmatched_model": sorted(m.name for m in model if m not in used)}


def carried_commits(period: dict) -> dict[str, str] | None:
    """Per switchboard of *period* the lab commit whose configuration its data carry; None without one.

    ``carries`` names one or more commits (the latest counts) or, per switchboard, ``"<sb>: syslab <commit>"``
    parts separated by ``;``; ``none: ...`` (no configuration carries those names) gives None.
    """
    text = str(period.get("carries") or "")
    if text.startswith("none") or not _COMMIT.search(text):
        return None
    out = {}
    for part in text.split(";"):
        sb = _SB.search(part)
        commits = _COMMIT.findall(part)
        if sb and commits:
            out[sb.group(1)] = commits[-1]
    if not out:
        out = {sb: _COMMIT.findall(text)[-1] for sb in period["switchboards"]}
    return out


def switchboards_at(repo: Path, commit: str) -> dict[str, tuple[str, SwitchboardDef]]:
    """``{switchboard: (node, definition)}`` of the lab repository's configuration at *commit*."""
    out = {}
    with tempfile.TemporaryDirectory(prefix="syslab_conf_") as tmp:
        for node, d in GRID_NODES.items():
            show = subprocess.run(["git", "show", f"{commit}:conf/{d}/hardware.xml"], cwd=repo, capture_output=True)
            if show.returncode != 0:
                continue
            (Path(tmp) / d).mkdir()
            (Path(tmp) / d / "hardware.xml").write_bytes(show.stdout)
            for name, sw in load_grid_switchboards(tmp, {node: d}).items():
                out[name] = (node, sw)
    return out


def _known(repo: Path, commit: str) -> bool:
    return subprocess.run(["git", "cat-file", "-e", f"{commit}^{{commit}}"], cwd=repo, capture_output=True).returncode == 0


def _in_force(repo: Path, day: dt.date, switchboards: set[str]) -> tuple[dict[str, str], dict[str, SwitchboardDef]]:
    """The configuration in force on *day* for *switchboards*, wherever they are (a switchboard can move node):
    ``({node: commit}, {switchboard: definition})`` for the nodes that hold them."""
    target, sws = {}, {}
    for node, nc in conf_in_force(repo, day).items():
        found = {name: sw for name, (n, sw) in switchboards_at(repo, nc.commit).items()
                 if n == node and name in switchboards}
        if found:
            target[node] = nc.commit
            sws.update(found)
    return target, sws


def _change_days(repo: Path, start: dt.date, end: dt.date) -> list[dt.date]:
    days = set()
    for d in GRID_NODES.values():
        log = _git(repo, "log", "master", "--format=%ad", "--date=short", "--", f"conf/{d}/hardware.xml")
        days |= {x for x in (dt.date.fromisoformat(y) for y in log.split()) if start < x <= end}
    return sorted(days)


def header_names(archive: Path, switchboard: str, start: dt.date, end: dt.date) -> set[str] | None:
    """Column names in the data headers of *switchboard* between *start* and *end* (syslab_data column archive,
    ``<archive>/<sb>.json``); None without an archive file."""
    path = Path(archive) / f"{switchboard.replace('-', '_')}.json"
    if not path.exists():
        return None
    names: set[str] = set()
    for e in json.loads(path.read_text(encoding="utf-8"))["eras"]:
        until = dt.date.fromisoformat(e["valid_to"][:10]) if e.get("valid_to") else dt.date.max   # open: still in use
        if dt.date.fromisoformat(e["valid_from"][:10]) <= end and until >= start:
            names |= set(e["columns"])
    return names


def _header_form(switchboard: str, name: str) -> str:
    """A data name as it stands in the file header (``BRK_..`` without the board, ``P_<meter>[kW]``)."""
    prefix = switchboard.replace("-", "_") + "_"
    return name[len(prefix):] if name.startswith(prefix) else f"{name}[kW]"


def resolve_meters(columns: list[Column], headers: set[str]) -> list[Column]:
    """Meter names as the data headers spell them: the logger mostly drops the spaces of an instrument name
    (``Cable C1A`` -> ``P_CableC1A[kW]``), not always (``Flexhouse 3``); a derived meter name takes the header
    name equal to it after normalising spelling, where there is exactly one; else, for a bay with one meter,
    the header named after the bay (meters logged by their bay: ``Grid 117-4`` as ``P_Grid``)."""
    meters = {}
    for h in headers:
        if h.startswith("P_") and h.endswith("[kW]"):
            meters.setdefault(norm(h[2:-4]), []).append(h[:-4])
    per_bay = {}
    for c in columns:
        if c.kind == "meter":
            per_bay[c.bay] = per_bay.get(c.bay, 0) + 1
    out = []
    for c in columns:
        hits = meters.get(norm(c.name[2:]), []) if c.kind == "meter" else []
        if c.kind == "meter" and not hits and per_bay[c.bay] == 1:
            hits = meters.get(norm(c.bay), [])
        out.append(Column(c.switchboard, c.kind, hits[0], c.bay, c.busbar) if len(hits) == 1 else c)
    return out


def period_maps(repo: Path | str, period: dict, archive: Path | str | None = None) -> list[dict]:
    """The column maps of one data-name period: one per stretch with the same target configuration.

    With *archive* (the syslab_data column archive), meter names take the headers' spelling
    (:func:`resolve_meters`) and each map lists ``not_in_headers``: data names that no data header of the
    stretch has (a check on the carried configuration, for the person confirming).
    """
    repo = Path(repo)
    carried = carried_commits(period)
    if carried is None:
        return [{"status": "no map", "reason": f"carries no configuration: {period.get('carries')}"}]
    data: dict[str, list[Column]] = {}
    no_map: dict[str, str] = {}
    for sb in period["switchboards"]:
        if sb not in carried:
            no_map[sb] = "carries names no configuration has"
        elif not _known(repo, carried[sb]):
            no_map[sb] = f"commit {carried[sb]} not in the lab repository (another branch than master?)"
        elif (found := switchboards_at(repo, carried[sb]).get(sb)) is None:
            no_map[sb] = f"not in the configuration of {carried[sb]}"
        else:
            data[sb] = data_columns(found[1])
            headers = header_names(Path(archive), sb, period["from"], period["to"]) if archive is not None else None
            if headers:
                data[sb] = resolve_meters(data[sb], headers)
    if not data:
        return [{"status": "no map", "reason": "; ".join(f"{sb}: {r}" for sb, r in no_map.items())}]
    start, end = period["from"], period["to"]
    stretches, last = [], None
    for day in [start] + _change_days(repo, start, end):
        target, sws = _in_force(repo, day, set(data))
        if target == last:
            continue
        last = target
        maps = {}
        for sb, cols in data.items():
            m = match(cols, model_columns(sws[sb])) if sb in sws else {"pairs": [], "same": 0,
                                                                          "unmatched_data": [c.name for c in cols],
                                                                          "unmatched_model": []}
            maps[sb] = {"carried": carried[sb], **m}
        stretch = {"from": day, "target": dict(sorted(target.items())), "switchboards": maps}
        if no_map:
            stretch["no_map"] = no_map
        stretches.append(stretch)
    for i, s in enumerate(stretches):
        s["to"] = stretches[i + 1]["from"] - dt.timedelta(days=1) if i + 1 < len(stretches) else end
        for sb, m in s["switchboards"].items():
            seen = header_names(Path(archive), sb, s["from"], s["to"]) if archive is not None else None
            if seen is not None:
                m["not_in_headers"] = sorted(c.name for c in data[sb] if _header_form(sb, c.name) not in seen)
    merged: list[dict] = []
    for s in stretches:   # a target change that leaves the maps as they are does not start a new map
        if merged and merged[-1]["switchboards"] == s["switchboards"]:
            merged[-1]["to"] = s["to"]
            merged[-1]["targets"].append({"from": s["from"], "nodes": s["target"]})
            continue
        merged.append({"status": "proposed", "from": s["from"], "to": s["to"],
                       "targets": [{"from": s["from"], "nodes": s["target"]}],
                       **{k: v for k, v in s.items() if k in ("switchboards", "no_map")}})
    return merged


def era_maps(repo: Path | str, era: Era) -> dict[str, list[dict]]:
    """``{period id: maps}`` for every data-name period of *era*."""
    return {h["id"]: period_maps(repo, h) for h in era.header_periods}


class _Flow(dict):
    """A mapping written on one line (a pair)."""


class _Dumper(yaml.SafeDumper):
    """No ``&id``/``*id`` anchors: a date reused across keys is written out each time."""

    def ignore_aliases(self, data):
        return True


_Dumper.add_representer(_Flow, lambda d, v: d.represent_mapping("tag:yaml.org,2002:map", v, flow_style=True))


def _flow_pairs(maps: list[dict]) -> list[dict]:
    """A copy of *maps* with every pair as a one-line mapping."""
    return [{**m, "switchboards": {sb: {**s, "pairs": [_Flow(p) for p in s["pairs"]]}
                                   for sb, s in m["switchboards"].items()}}
            if "switchboards" in m else m for m in maps]


def _block(maps: list[dict]) -> str:
    """The ``column_map`` block of one period, indented for the era file (generated, so plain YAML)."""
    body = yaml.dump({"column_map": _flow_pairs(maps)}, Dumper=_Dumper, sort_keys=False,
                     allow_unicode=True, width=110)
    return "".join("    " + line + "\n" for line in body.splitlines())


def write_era_maps(path: Path | str, maps: dict[str, list[dict]]) -> None:
    """Put each period's ``column_map`` into the era file as its last key; the rest of the file stays as is.

    A period is the lines from its ``  - id:`` to the next line that is not indented deeper (the next
    period, a comment or the next section). An existing ``column_map`` (always last) is replaced, so
    rerunning gives the same file.
    """
    path = Path(path)
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    out, i = [], 0
    while i < len(lines):
        m = re.match(r"  - id: (\S+)", lines[i])
        if not m or m.group(1) not in maps:
            out.append(lines[i])
            i += 1
            continue
        j = i + 1
        while j < len(lines) and lines[j].startswith("    "):
            j += 1
        block = lines[i:j]
        cut = next((k for k, line in enumerate(block) if line.startswith("    column_map:")), len(block))
        out += block[:cut] + [_block(maps[m.group(1)])]
        i = j
    path.write_text("".join(out), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--conf-repo", required=True, help="lab repository syslab/ with its history (read-only)")
    p.add_argument("--era", required=True, help="era id, e.g. E6")
    p.add_argument("--period", help="one data-name period id, e.g. E6-H03")
    p.add_argument("--column-archive", help="syslab_data metadata/column_archive: check data names against the headers")
    p.add_argument("--write", action="store_true", help="write the maps into the era file")
    a = p.parse_args(argv)
    path = ERAS_DIR / f"{a.era}.yaml"
    era = load_era(path)
    periods = [h for h in era.header_periods if a.period in (None, h["id"])]
    maps = {h["id"]: period_maps(a.conf_repo, h, a.column_archive) for h in periods}
    for pid, ms in maps.items():
        for m in ms:
            if m["status"] != "proposed":
                print(f"{pid}: {m['status']} ({m['reason']})")
                continue
            for sb, s in m["switchboards"].items():
                print(f"{pid} {m['from']}..{m['to']} {sb}: {len(s['pairs'])} pairs, {s['same']} same, "
                      f"{len(s['unmatched_data'])} data and {len(s['unmatched_model'])} model names unmatched"
                      + (f", {len(s['not_in_headers'])} not in the headers" if "not_in_headers" in s else ""))
    if a.write:
        write_era_maps(path, maps)
        print(f"written into {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
