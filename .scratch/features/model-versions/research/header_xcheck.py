"""Cross-check the column-archive header eras against the hardware.xml and figure/Java history (research, throwaway).

Usage (from a folder outside the repos):
    python -I header_xcheck.py <syslab repo> <syslab-userspace repo> <column_archive dir> <out.csv> [boards]

Only read-only git commands (log, show, merge-base) run in the two lab repositories; never commit or push there.

For each header era of a switchboard, the breaker set (`BRK_<bay>_<busbar>`) is compared with the master
`hardware.xml` in force on `valid_from`, and with every version on any branch. Classes:

- ``header-only``: before the first hardware.xml of that switchboard
- ``ok``: identical to master in force
- ``alias``: same breakers as master in force, names differ in spelling only (case, space, underscore, dash)
- ``lag``: identical to an older master version (the node had not restarted yet)
- ``lead``: identical to a version committed later (data ahead of the repository)
- ``branch``: identical only to a version on a feature branch
- ``unmatched``: no version has this breaker set
- ``transition``: unmatched, and the era lasts at most one day (a restart mid-day)

Meter bays (``P_<bay>[kW]``) that appear or disappear against the previous header era are listed as well; the
hardware.xml check covers breakers only.
"""
import csv, json, os, re, subprocess, sys
from datetime import date

REPO, UREPO, ARCH, OUT = sys.argv[1:5]
BOARDS = (sys.argv[5].split(",") if len(sys.argv) > 5 else
          ["117_2", "117_4", "117_5", "117_6", "310_2", "319_2", "319_3", "319_4", "330_12", "330_13",
           "715_2", "716_2", "776_1"])
NODES = ["syslab-01", "syslab-09", "syslab-11", "syslab-26", "syslab-29", "syslab-30", "syslab-44", "syslab-50",
         "syslab-51", "syslab-52", "syslab-53"]
FIG_PATHS = ["src/main/resources/media/svg/",
             "src/main/java/risoe/syslab/gui/wall/displets/switchboard/SwitchboardsOverviewDisplet.java"]


def git(repo, *a):
    return subprocess.run(["git", *a], cwd=repo, capture_output=True, text=True, encoding="utf-8",
                          errors="replace").stdout


def log(repo, ref, path):
    """[(commit, 'YYYY-MM-DD', unix time)]; the time orders same-day commits."""
    out = git(repo, "log", *ref, "--format=%H %ad %ct", "--date=short", "--", path)
    return [(l.split()[0][:9], l.split()[1], int(l.split()[2])) for l in out.splitlines() if l.strip()]


def parse(xml):
    """{switchboard: (set('bay_busbar'), set(meter names))} from either hardware.xml format (2015 and 2023).

    A meter is known by its instrument name; old headers name it by its bay, so the bay name counts too."""
    res, sb, bay = {}, None, None
    for m in re.finditer(r'<(switchboard|bay|breaker|instrument)\b[^>]*?\bname="([^"]*)"([^>]*)', xml, re.S):
        tag, name, rest = m.groups()
        if tag == "switchboard":
            sb = name
            res.setdefault(sb, (set(), set()))
        elif tag == "bay":
            bay = name
        elif sb and tag == "instrument":
            res[sb][1].update({name, bay})
        elif sb:
            bb = re.search(r'busbar="([^"]*)"', rest)
            if bb:
                res[sb][0].add(f"{bay}_{bb.group(1)}")
    return res


def norm(s):
    return re.sub(r"[\s_\-]", "", s).lower()


def days(a, b):
    return (date.fromisoformat(a) - date.fromisoformat(b)).days


hist = {}  # switchboard -> [(date, commit, node, breakers, on_master)], in commit-time order
for node in NODES:
    master = {c for c, _, _ in log(REPO, ["master"], f"conf/{node}/hardware.xml")}
    for c, d, t in log(REPO, ["--all"], f"conf/{node}/hardware.xml"):
        for sb, (s, mt) in parse(git(REPO, "show", f"{c}:conf/{node}/hardware.xml")).items():
            if s:
                hist.setdefault(sb, []).append((t, d, c, node, frozenset(s), c in master, frozenset(mt)))
for k, v in hist.items():
    hist[k] = [h[1:] for h in sorted(v)]

fig = sorted({(d, c) for p in FIG_PATHS for c, d, _ in log(UREPO, ["--all"], p)})


def fig_near(d, k=3):
    return " ".join(f"{fd} {fc[:7]}" for fd, fc in fig if abs(days(fd, d)) <= k)


rows = []
for dev in BOARDS:
    sb = dev.replace("_", "-")
    j = json.load(open(os.path.join(ARCH, dev + ".json"), encoding="utf-8"))
    H = hist.get(sb, [])
    prev_bays = None
    for e in j["eras"]:
        vf, vt = e["valid_from"][:10], (e["valid_to"] or "")[:10]
        hs = frozenset(c[4:] for c in e["columns"] if c.startswith("BRK_"))
        bays = {m.group(1) for c in e["columns"] for m in [re.match(r"P_(.+)\[kW\]$", c)] if m}
        r = dict(board=sb, node=j.get("node", ""), valid_from=vf, valid_to=vt, source_file=e["source_file"],
                 n_brk=len(hs), cls="", master="", match="", offset_d="", stale_from="", stale_d="", diff="",
                 meter_bays="", meters_not_in_master="", meters_stale="", figure_java="")
        if prev_bays is not None and bays != prev_bays:
            r["meter_bays"] = " ".join([f"+{b}" for b in sorted(bays - prev_bays)] +
                                       [f"-{b}" for b in sorted(prev_bays - bays)])
        prev_bays = bays
        inforce = [h for h in H if h[4] and h[0] <= vf]
        exact = [h for h in H if h[3] == hs]
        if not hs:
            r["cls"] = "no-breakers"
        elif not inforce:
            r["cls"] = "header-only"
            if exact:
                r["match"] = f"{exact[0][0]} {exact[0][1]}"
        else:
            md, mc, _, ms, _, mm = inforce[-1]
            r["master"] = f"{md} {mc}"
            known = {norm(x) for x in mm}
            r["meters_not_in_master"] = " ".join(sorted(b for b in bays if norm(b) not in known))
            hn, cn = {norm(x) for x in hs}, {norm(x) for x in ms}
            if hs == ms:
                r["cls"] = "ok"
            elif hn == cn:
                r["cls"] = "alias"
            else:
                r["diff"] = " ".join([f"+{x}" for x in sorted(hn - cn)] + [f"-{x}" for x in sorted(cn - hn)])
                on_master = [h for h in exact if h[4]]
                older = [h for h in on_master if h[0] <= vf]
                if older:
                    h = older[-1]
                    r["cls"], r["match"], r["offset_d"] = "lag", f"{h[0]} {h[1]}", days(vf, h[0])
                elif on_master:
                    h = on_master[0]
                    r["cls"], r["match"], r["offset_d"] = "lead", f"{h[0]} {h[1]}", days(vf, h[0])
                elif exact:
                    h = exact[0]
                    r["cls"], r["match"], r["offset_d"] = "branch", f"{h[0]} {h[1]}", days(vf, h[0])
                else:
                    r["cls"] = "transition" if vt and days(vt, vf) <= 1 else "unmatched"
        # A master change during the era that the header did not follow: the node kept the older config.
        later = [h for h in H if h[4] and vf < h[0] <= (vt or "9999") and h[3] != hs]
        if hs and later:
            h = later[0]
            r["stale_from"], r["stale_d"] = f"{h[0]} {h[1]}", days(vt or date.today().isoformat(), h[0])
        # Same for meters: a master change during the era adds meters the header does not have yet.
        hb = {norm(b) for b in bays}
        mlater = [h for h in H if h[4] and vf < h[0] <= (vt or "9999") and
                  {norm(x) for x in h[5]} != {norm(x) for x in (inforce[-1][5] if inforce else h[5])}]
        new_meters = sorted({x for h in mlater for x in h[5] if norm(x) not in hb} -
                            (set(inforce[-1][5]) if inforce else set()))
        if new_meters:
            r["meters_stale"] = " ".join(new_meters)
        if (r["cls"] not in ("ok", "no-breakers") or r["meter_bays"] or r["stale_from"]
                or r.get("meters_not_in_master") or r.get("meters_stale")):
            r["figure_java"] = fig_near(vf)
        rows.append(r)

with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
for r in rows:
    print(f"{r['board']:7} {r['valid_from']}..{r['valid_to']:10} {r['cls']:11} {str(r['offset_d']):>6} "
          f"m={r['master']:20} x={r['match']:20} stale={r['stale_from']}({r['stale_d']}) "
          f"{r['meter_bays'][:50]} | {r['diff'][:70]} | M-{r['meters_not_in_master'][:60]} "
          f"M+{r['meters_stale'][:60]} | fig {r['figure_java']}")
