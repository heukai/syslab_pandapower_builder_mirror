# What does each source say, and since when?

Type: research
Status: open
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
