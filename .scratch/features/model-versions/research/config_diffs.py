"""Breaker and meter changes between consecutive master hardware.xml versions per switchboard (research, throwaway).

Usage: python -I config_diffs.py <syslab repo> <from YYYY-MM-DD> [<to>]
Read-only git (log, show) in the lab repository. Names are compared after normalising spelling (case, space,
underscore, dash), so a pure naming-convention commit shows as "spelling only".
"""
import re, subprocess, sys

NODES = ["syslab-01", "syslab-09", "syslab-11", "syslab-26", "syslab-29", "syslab-30", "syslab-44", "syslab-50",
         "syslab-51", "syslab-52", "syslab-53"]


def git(repo, *a):
    return subprocess.run(["git", *a], cwd=repo, capture_output=True, text=True, encoding="utf-8",
                          errors="replace").stdout


def log(repo, ref, path):
    out = git(repo, "log", *ref, "--format=%H %ad %ct", "--date=short", "--", path)
    return [(l.split()[0][:9], l.split()[1], int(l.split()[2])) for l in out.splitlines() if l.strip()]


def parse(xml):
    """{switchboard: (set('bay_busbar'), set(instrument names))}, as in header_xcheck.py but without bay names."""
    res, sb, bay = {}, None, None
    for m in re.finditer(r'<(switchboard|bay|breaker|instrument)\b[^>]*?\bname="([^"]*)"([^>]*)', xml, re.S):
        tag, name, rest = m.groups()
        if tag == "switchboard":
            sb = name
            res.setdefault(sb, (set(), set()))
        elif tag == "bay":
            bay = name
        elif sb and tag == "instrument":
            res[sb][1].add(name)
        elif sb:
            bb = re.search(r'busbar="([^"]*)"', rest)
            if bb:
                res[sb][0].add(f"{bay}_{bb.group(1)}")
    return res


def norm(s):
    return re.sub(r"[\s_\-]", "", s).lower()


REPO, FROM = sys.argv[1], sys.argv[2]
TO = sys.argv[3] if len(sys.argv) > 3 else "9999"

seq = {}
for node in NODES:
    for c, d, t in log(REPO, ["--first-parent", "master"], f"conf/{node}/hardware.xml"):
        for sb, (b, m) in parse(git(REPO, "show", f"{c}:conf/{node}/hardware.xml")).items():
            if b:
                seq.setdefault(sb, []).append((t, d, c, node, b, m))
for sb in sorted(seq):
    vs = sorted(seq[sb])
    for (_, _, _, _, b0, m0), (_, d, c, node, b1, m1) in zip(vs, vs[1:]):
        if not (FROM <= d < TO):
            continue
        nb0, nb1 = {norm(x) for x in b0}, {norm(x) for x in b1}
        nm0, nm1 = {norm(x) for x in m0}, {norm(x) for x in m1}
        if b0 == b1 and m0 == m1:
            continue
        subj = git(REPO, "log", "-1", "--format=%s", c).strip()[:70]
        print(f"{sb:7} {d} {c} {node}: {subj}")
        if nb0 == nb1 and nm0 == nm1:
            print("        spelling only")
            continue
        for tag, a, z in (("brk", nb0, nb1), ("meter", nm0, nm1)):
            if a != z:
                print(f"        {tag} +{sorted(z - a)}")
                print(f"        {tag} -{sorted(a - z)}")
