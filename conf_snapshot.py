"""The ``hardware.xml`` files in force on a day, exported from the lab repository ``syslab/conf``.

The model of a configuration revision is built from the configuration in force on its date (map "dated model
versions", ticket on consolidation, amended 2026-10-25): per node, the last ``hardware.xml`` on master whose commit
was **written** (author date) on or before that day. A change written on a branch reaches master's first-parent line
later by a merge; the data follow the written date, so the merge date does not count.

Only read-only git commands run in the lab repository (``log``, ``show``): never commit or push there.

US-24, US-25.
"""

from __future__ import annotations

import datetime as dt
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .hardware_parser import GRID_NODES


@dataclass(frozen=True)
class NodeConf:
    """The ``hardware.xml`` of one node in force on the day: which commit, written when."""

    node: str
    commit: str
    written: dt.date


def _git(repo: Path, *args: str) -> str:
    out = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, encoding="utf-8",
                         errors="replace")
    if out.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed in {repo}: {out.stderr.strip()}")
    return out.stdout


def conf_in_force(repo: Path | str, day: dt.date, nodes: dict[str, str] | None = None,
                  branch: str = "master") -> dict[str, NodeConf]:
    """Per node, the master commit of ``conf/<node>/hardware.xml`` with the latest author date on or before *day*.

    Nodes without such a commit (not configured yet on that day) are left out.
    """
    repo = Path(repo)
    found: dict[str, NodeConf] = {}
    for node, dir_name in (nodes or GRID_NODES).items():
        log = _git(repo, "log", branch, "--format=%H %ad", "--date=short", "--", f"conf/{dir_name}/hardware.xml")
        best = None
        for line in log.splitlines():
            commit, written = line.split()
            written = dt.date.fromisoformat(written)
            if written <= day and (best is None or written > best.written):
                best = NodeConf(node, commit[:9], written)
        if best:
            found[node] = best
    return found


def export_conf(repo: Path | str, day: dt.date, dest: Path | str,
                nodes: dict[str, str] | None = None) -> dict[str, NodeConf]:
    """Write ``dest/<node dir>/hardware.xml`` as in force on *day*; returns what was taken from where."""
    repo, dest = Path(repo), Path(dest)
    nodes = nodes or GRID_NODES
    taken = conf_in_force(repo, day, nodes)
    for node, nc in taken.items():
        target = dest / nodes[node] / "hardware.xml"
        target.parent.mkdir(parents=True, exist_ok=True)
        # bytes as stored: no newline translation, no decoding
        xml = subprocess.run(["git", "show", f"{nc.commit}:conf/{nodes[node]}/hardware.xml"], cwd=repo,
                             capture_output=True, check=True).stdout
        target.write_bytes(xml)
    return taken
