# Access to the figure repository and the hardware.xml history

Type: task
Status: resolved
Blocked by: -

## Question

Give the agent read access to (a) the repository that holds the switchboard overview SVG and the Java code that maps its
text labels to breakers, and (b) the history of `syslab-master-conf` (the local copy is a plain folder, no git history). The
backward direction of the mechanism depends on dated versions of both.

HITL: the maintainer provides the access; the answer records where the repositories live, how to read them, and how far back
their history goes.

## Answer

Done by the maintainer, 2026-10-20. Both lab repositories are cloned into the workspace, read-only.

**NEVER PUSH, NEVER COMMIT to either repository.** Read, diff and `git log` only. Every agent that touches them is told this
rule (workspace `AGENTS.md`, this map's Notes).

- **`syslab/`** (`git.elektro.dtu.dk/syslab/syslab`, 3 220 commits, last 2026-10-15): `conf/syslab-XX/hardware.xml` for 50
  nodes. The `conf/` history starts 2008-10-29; the first `hardware.xml` appears 2015-08-03; 148 commits touch a
  `hardware.xml`, the last on 2026-10-05. Compared with the plain copy in `syslab-master-conf/` (ignoring line endings), four
  `hardware.xml` differ: `syslab-01` (319-2), `syslab-33`, `syslab-53` (310-2), and `syslab-32` exists only in the repo (a new
  node, candidate for 316-2 or 119-10). The plain copy is therefore stale; the builder should read the repo's `conf/`.
- **`syslab-userspace/`** (`git.elektro.dtu.dk/syslab/syslab-userspace`, 191 commits, since 2018-07-02, last 2026-10-05):
  the figures in `src/main/resources/media/svg/` (`switchboard_overview_4.svg` to `_7.svg`, plus `heatswitchboard_overview_2`,
  `flexhouse`, `vis_418`, ...), and the label-to-breaker mappings in
  `src/main/java/risoe/syslab/gui/wall/displets/switchboard/SwitchboardsOverviewDisplet.java` (1 258 lines, 40 commits; per the
  maintainer it holds all mappings, including those of the version 7 era). The figure history is dated by commit, e.g.
  2023-08-11 bay and busbar names synchronized with syslab-52, 2024-06-19 C1/C2 and E1/E2 labels swapped (as-built vs
  as-planned), 2026-08-13 310-2 `Spare_1` -> `Boiler`, 2026-10-05 PTX, the fast charging site and 119-10.

Consequences: the second passes of the source inventory and of the figure-privacy research can run; the safe-pipe ticket and
the first-new-reference-era ticket lose this blocker.

## Comments

**Correction (2026-10-21, from the source inventory):** `syslab-32` is a booster-heater load, not a switchboard; 119-10 is
`syslab-44` (added 2026-10-05). Eight nodes exist only in the repo, not only `syslab-32`.
