# What does each source say, and since when?

Type: research
Status: resolved
Blocked by: -

## Question

For every source of configuration knowledge, what does it state (switchboards, bays, breakers, cables, asset connections,
names), how are its versions dated, and how far back does it reach? First pass with what is available now: the column archive
(header eras, `syslab_data/metadata/column_archive/`), the device registry (`syslab_data/metadata/devices.py`), the builder's
git history and curated YAML, `hardware.xml` as of now, and the SVG versions 6 and 7
(`sample_data_SYSLAB-NAS/switchboard_overview_6(1).svg`, `_7.svg`; labels are visible text, ids carry no meaning). Second pass
after the access ticket: the SVG/Java repository history and the `syslab-master-conf` history.

Output: one table per source (what, dating, reach, naming), and the known changes each source shows (AirCon 715_2 -> 319_2,
the Gaia move, CEEx2 sockets, SVG 6 -> 7: 316-2, 119-10, Cable Q1, ...).

## Comments

**First pass done (2026-10-20, agent):** findings on the throwaway branch `research/source-inventory` (commit `fc5c6de`,
`.scratch/features/model-versions/research/source-inventory.md`, pushed to `kheu-home`, never merged). Gist:

- The column archive is the only dated source (header eras per device); a header date is when logging changed, not the
  physical change, so each physical change needs a second source.
- The registry has no validity dates and mixes eras (319_2 still `Solar`, `B2B`, `Cable1/2`, no `CEEx2`); the builder YAML
  holds only the current state (git dates are knowledge corrections); the published model's `valid_from` 2024-08-15 predates
  at least five later header eras; the `hardware.xml` snapshot looks like ~March 2026; the SVGs carry no date (Inkscape
  versions give lower bounds: v6 >= 2023-11-25, v7 >= 2026-05-05) and can lag the lab.
- Changes: Gaia on 715_2 until 2023-06-30, on 330_12 from 2024-06-10; CEEx2 on 117_2 from 2023-07-01, 319_2 from
  2023-12-01, meters split 2026-06-24; renames `Solar` -> `PV`, `Busbar 1/2` -> A/B (2023-07-01), NEVIC -> EVSE
  (2025-02-14); AirCon 715_2 -> 319_2 shown by no local source (only the 2026-10-18 registry statement).
- SVG 6 -> 7 (inferred from label positions): new 316-2 (P2XA, P2XB, Grid) on Cable M1 from 319-4's former P2X bay; 319-3
  `Spare` -> `PTX`; new 119-10 (fast charger site, batteries 1-5, EVSE 12) on Cable Q1 from 330-13's EVSE 12 bay;
  `Ext. 117-x` -> Cable X1/X2; 310-2 `Rock store` -> `Boiler`. None in hardware.xml, registry, archive or builder.
- Suspect: the 319_2 column-archive alias maps the old `Grid` busbar to `Busbar_A`; `hardware.xml` says `Busbar_B`.

**Second pass pending** the access ticket: the SVG/Java repository history and the `syslab-master-conf` history. The ticket
stays open until then.

## Answer

Both passes done (2026-10-20/21, agents). Findings: branch `research/source-inventory`, commits `fc5c6de` (local sources) and
`552eaed` (lab repositories), `.scratch/features/model-versions/research/source-inventory.md`; never merged.

**Which source dates what.** `syslab/conf` (`hardware.xml` history since 2015-08-03) dates configuration changes best: the
figure and the Java displet change on the same days, and the column archive's header eras follow later (a header date is when
logging changed, often months after). The registry has no dates; the builder YAML holds only the current state; the plain copy
in `syslab-master-conf/` is the repo state of some day between 2026-01-08 and 2026-04-07 (eight nodes exist only in the repo).

**Nodes.** syslab-01 = 319-2 (also 319-3 until 2023-04-13), -09 = 715-2, -11 = 117-2/4/5, -26 = 117-6, -29 = 716-2, -44 = 119-10
(added 2026-10-05: Cable_Q1, Battery_1..5, EVSE_12, one busbar A), -50 = 330-12, -51 = 330-13, -52 = 319-3/4, -53 = 310-2;
syslab-32 is a booster-heater load, not a switchboard. **316-2, PTX, P2XA/B and Cable M1 are in no `hardware.xml` at any commit
and not in the Java: they exist only in figure v7.**

**Dated changes (config / figure+Java / header):** 2023 rebuild 2023-06-14 (319-2) and 2023-06-23 (others), figure v6 and Java
2023-06-23 (Busbar 1/2 -> A/B, Solar -> PV, Gaia off 715-2, CEEx2 on 319-2 from 2023-04-13); Gaia on 330-12 drawn 2023-06-23,
config 2023-10-06, logged 2024-06-10; CEEx2 second meter: 117-2 config 2024-10-14, 319-2 config 2026-06-15, both headers
2026-06-24, no interlock in any version; NEVIC -> EVSE config 2023-11-14, header 2025-02-14; Boiler (310-2, takes the `Spare_1`
bay) all three 2026-08-13; 119-10 and Cable Q1 all three 2026-10-05.

**Against the first pass:**
- **AirCon 715_2 -> 319_2 is contradicted:** AirCon is on 319-2 in every config since 2015-08-03 and in the Java since 2018, never
  on 715-2. A move, if any, predates 2015 (open; the registry statement of 2026-10-18 needs the maintainer's check).
- **The `319_2.json` alias is swapped** (confirmed): config, comments and Java put the Grid busbar on B. Fix pending in `syslab_data`.
- The 2024-06-19 C1/C2 E1/E2 label swap: as-built vs as-planned; the config swapped only the 319-3 E pair on 2024-09-08, so 319-3
  E1/E2 breaker data logged 2023-12-01 to 2024-09-07 probably carry swapped names (inference).
- The sample figures date exactly: the NAS v6 is the repo version of 2024-10-25, v7 that of 2026-10-05.

**Open gaps:** AirCon before 2015; whether 316-2 is planned or not yet polled; the 330-13 end of Cable Q1 (config `EVSE_12`, Java
`Cable_Q1`); whether the rock store is still connected; 330-12 `Spare_6/7` (dropped from logging 2026-04-19, still in config);
configs before 2015 not examined.

**Third pass (2026-10-21, main session): the v6 -> v7 era change across the three lab sources** (script
`C:\Users\kheu\AppData\Local\Temp\v6v7\compare.py`; v6 end = conf `7c4a820a2^`, Java `5c6ee92`, figure `9c29ae3`, all
2026-08-13; v7 = conf `aeecde1bc`, Java `d407f7f`, figure `7979a0f`, all 2026-10-05):

- `hardware.xml`: one new grid node `syslab-44` (119-10) with 7 bays on one busbar (Battery_1..5, Cable_Q1, EVSE_12); nothing
  removed elsewhere; no interlock change. The 330-13 end keeps `EVSE_12`.
- Java: the same 7 breakers of 119-10 added; 330-13 `EVSE_12` A/B relabelled `Cable_Q1` A/B (same element ids); no element id
  changed; the figure loaded switches from v6 to v7.
- Figure: labels added 119-10, Battery 1-5, Fast charger site, Cable Q1, and the planned (greyed) 316-2, Building 316, P2XA/B,
  PTX, M1; Ext. 117-2/117-5 become Cable X1/X2; Rock store and P2X dropped; legend text changes.
- Not in any lab source: the cable Q1 itself (which bays it joins, type, length) is curated data for the builder.
- Within the v6 era, one earlier change on one day in all three sources: 310-2 `Spare_1` -> `Boiler` (2026-08-13).
- Builder side: its grid node list (`GRID_NODES`) lacks `syslab-44`, so a new node is itself part of a configuration change.
