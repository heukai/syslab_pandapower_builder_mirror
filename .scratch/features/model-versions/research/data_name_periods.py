"""Chronological log of data-name periods, as a Markdown table (research, throwaway).

Usage (from a folder outside the repos):
    python -I data_name_periods.py <syslab repo> <column_archive dir> <builder repo> <era branch>

Only read-only git commands run in the lab repository. Each header era of a switchboard (column archive) is cut at every
master hardware.xml change inside it; each piece is compared with the master version in force then:

- breakers: ok, alias (other spelling), lag (an older master version), lead (a version committed later; "branch" if it
  never reached master), unmatched (no version), transition (unmatched, at most one day);
- meters, where the breakers agree: meter-lag (master names a meter that the data still call otherwise).

Pieces that agree are left out; neighbouring pieces with the same finding are merged. Rows overlapping an era file's
`header_periods` (on the era branch) carry its id.
"""
import json, os, re, subprocess, sys
from datetime import date, timedelta

import yaml

REPO, ARCH, BUILDER, BRANCH = sys.argv[1:5]
BOARDS = ["117_2", "117_4", "117_5", "117_6", "310_2", "319_2", "319_3", "319_4", "330_12", "330_13", "715_2", "716_2"]
NODES = ["syslab-01", "syslab-09", "syslab-11", "syslab-26", "syslab-29", "syslab-50", "syslab-51", "syslab-52",
         "syslab-53"]
TODAY = date.today()


def git(repo, *a):
    return subprocess.run(["git", *a], cwd=repo, capture_output=True, text=True, encoding="utf-8",
                          errors="replace").stdout


def log(ref, path):
    out = git(REPO, "log", *ref, "--format=%H %ad %ct", "--date=short", "--", path)
    return [(l.split()[0][:9], date.fromisoformat(l.split()[1]), int(l.split()[2])) for l in out.splitlines() if l.strip()]


def parse(xml):
    """{switchboard: (breakers 'bay_busbar', instrument names)}; both hardware.xml formats."""
    res, sb, bay = {}, None, None
    for m in re.finditer(r'</switchboard>|<(switchboard|bay|breaker|instrument)\b[^>]*?\bname="([^"]*)"([^>]*)', xml, re.S):
        tag, name, rest = m.groups()
        if tag is None:                      # the 2023 format lists driver instruments again after the switchboards
            sb = None
        elif tag == "switchboard":
            sb = name
            res.setdefault(sb, (set(), set()))
        elif tag == "bay":
            bay = name
        elif sb and tag == "instrument":
            res[sb][1].add((name, bay))      # before 2023 the data name a meter by its bay
        elif sb:
            bb = re.search(r'busbar="([^"]*)"', rest)
            if bb:
                res[sb][0].add(f"{bay}_{bb.group(1)}")
    return res


def norm(s):
    return re.sub(r"[\s_\-]", "", s).lower()


hist = {}  # switchboard -> [(time, date, commit, breakers, instruments, on_master)] in commit-time order
for node in NODES:
    master = {c for c, _, _ in log(["master"], f"conf/{node}/hardware.xml")}
    for c, d, t in log(["--all"], f"conf/{node}/hardware.xml"):
        for sb, (b, m) in parse(git(REPO, "show", f"{c}:conf/{node}/hardware.xml")).items():
            if b:
                # IMB-* instruments are not power meters; they never appear as P_ columns.
                # The bay name stands in for the meter only in the old configuration format (before the move to the
                # switchboard format in 2023); since then the data use the instrument name (Grid_4, CEEx2_1).
                old = d < date(2023, 4, 1)
                meters = frozenset((n, bay if old else None) for n, bay in m if not n.startswith("IMB"))
                hist.setdefault(sb, []).append((t, d, c, frozenset(b), meters, c in master))
for v in hist.values():
    v.sort()

periods = []
for n in git(BUILDER, "ls-tree", "--name-only", f"{BRANCH}:data/eras").split():
    if n.startswith("E") and n.endswith(".yaml"):
        e = yaml.safe_load(git(BUILDER, "show", f"{BRANCH}:data/eras/{n}"))
        periods += e.get("header_periods") or []


def era_ids(board, a, b):
    return ", ".join(h["id"] for h in periods if board in h["switchboards"] and h["from"] <= b and a <= h["to"]) or "-"


def classify(hs, hm, a, b, master_now, versions):
    """Finding for one piece: (kind, what the data use) or None when the data agree with master."""
    ms, mm = master_now[3], master_now[4]
    if hs != ms:
        if {norm(x) for x in hs} == {norm(x) for x in ms}:
            return "alias", "same breakers, other spelling"
        exact = [v for v in versions if v[3] == hs]
        older = [v for v in exact if v[5] and v[1] <= a]
        later = [v for v in exact if v[1] > a]
        if older:
            v = older[-1]
            return "lag", f"breaker names of the configuration of {v[1]} ({v[2]})"
        if later:
            v = later[0]
            return ("lead" if v[5] else "branch"), \
                f"breaker names of the configuration of {v[1]} ({v[2]}{'' if v[5] else ', branch only'})"
        return ("transition" if (b - a).days < 1 else "unmatched"), "breaker names of no configuration"
    have = {norm(x) for x in hm}
    missing = sorted(name for name, bay in mm if norm(name) not in have and norm(bay or "") not in have)
    if missing:
        return "meter-lag", f"old names for the meters {', '.join(missing)}"
    return None


rows = []
for dev in BOARDS:
    sb = dev.replace("_", "-")
    H = hist.get(sb, [])
    eras = json.load(open(os.path.join(ARCH, dev + ".json"), encoding="utf-8"))["eras"]
    for e in eras:
        hs = frozenset(c[4:] for c in e["columns"] if c.startswith("BRK_"))
        hm = {m.group(1) for c in e["columns"] for m in [re.match(r"P_(.+)\[kW\]$", c)] if m}
        a0 = date.fromisoformat(e["valid_from"][:10])
        b0 = date.fromisoformat(e["valid_to"][:10]) if e["valid_to"] else TODAY
        if not hs:
            continue
        # cut points: master changes strictly inside the era
        cuts = sorted({v[1] for v in H if v[5] and a0 < v[1] <= b0})
        starts = [a0] + cuts
        for i, a in enumerate(starts):
            b = (starts[i + 1] - timedelta(days=1)) if i + 1 < len(starts) else b0
            if b < a:
                continue
            inforce = [v for v in H if v[5] and v[1] <= a]
            if not inforce:
                continue          # before the first hardware.xml: header-only
            f = classify(hs, hm, a, b, inforce[-1], H)
            # A master change and the restart that follows it on the same day: not a period.
            if f and f[0] in ("lag", "meter-lag") and a in cuts and (b - a).days < 1:
                continue
            if f:
                m = inforce[-1]
                rows.append([a, b, sb, f[0], f[1], e["source_file"], f"{m[1]} {m[2]}"])

# merge neighbours with the same board, kind and data names; keep the first master in force
rows.sort(key=lambda r: (r[2], r[0]))
merged = []
for r in rows:
    if merged and merged[-1][2:5] == r[2:5] and (r[0] - merged[-1][1]).days <= 2:   # bridges a dropped restart day
        merged[-1][1] = r[1]
        if r[5] not in merged[-1][5]:
            merged[-1][5] += f", {r[5]}"
    else:
        merged.append(r)
merged.sort(key=lambda r: (r[0], r[2]))

print("| # | From | To | Days | Switchboard | Kind | What the data files use | Master in force (first) | Data file "
      "| Era file | Status |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for i, (a, b, sb, kind, text, src, mref) in enumerate(merged, 1):
    print(f"| D{i:02d} | {a} | {b} | {(b - a).days + 1} | {sb} | {kind} | {text} | {mref} | `{src}` | "
          f"{era_ids(sb, a, b)} | open |")
