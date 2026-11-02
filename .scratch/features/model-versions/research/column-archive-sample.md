# Column archive vs hardware.xml vs figure: sample cross-check (2026-10-25)

Sample: 117-2, 117-5, 319-3, 715-2, 716-2. Method: for each header era in `syslab_data/metadata/column_archive/*.json`,
compare its `BRK_*` set with the master `hardware.xml` in force on `valid_from` (exact / spelling only / structural), and
find the first commit on any branch whose breaker set matches the header exactly. The lab repos were only read.
Scripts: `$CLAUDE_JOB_DIR/tmp/ca_summary.py`, `xcheck.py` (not versioned).

## Coverage

- Headers: 2009-12 (319-2, 715-2) to today. `hardware.xml`: from 2015-03. Figure and Java history: from 2018-12.
- Anything before 2015 is header-only evidence (eras 1 to 3 at most).

## Findings (candidate change entries, all *proposed*)

| # | Board | Header date | Observation | Class |
|---|---|---|---|---|
| 1 | 117-x, 715-2, 716-2 | 2023-06-16 | rebuild names in data 7 d **before** master `ebb1fb939` (2023-06-23) | config committed after deploy; era 6 starts 2023-06-16 on these nodes |
| 2 | 117-2, 117-5 | 2023-09-27 (1 day) | names match configs committed **2024-10-09/14** (X1A/X1B, Booster_Heater, CEEx1) | test run of a future config; uncertain day |
| 3 | 117-x | 2023-09-28 to 2024-02-26 | old names, although master renamed on 2023-10-23/31 | logging lag 119 d (node restart) |
| 4 | 319-2, 319-3 | to 2023-11-30 | **old layout names** (A1..E2 "to 716-2", Busbar A/B/C, Grid/Local) until 2023-11-30, master new since 2023-06 | lag ~5 months; covers operational periods 6-a to 6-c: data of that time carries pre-rebuild names |
| 5 | 319-3 | 2016-06-14 | E1/E2 busbars swapped in data; master gets it 2016-07-12; 716-2 interlock fix 2016-09-19 | an earlier E1/E2 swap (era 4), config lead 28 d |
| 6 | 319-3 | 2024-03-07 to 2024-09-08 | `ABB_Pri_Busbar_Grid_Distribution` matches **no** hardware.xml version | uncommitted node config; flag |
| 7 | 319-3 | 2024-09-08 (1 day) | intermediate E1/E2 state, no version matches; same-day `b736d2d87` exact | transition day |
| 8 | 715-2 | 2015-08-05 to 2023-06-15 | CableB1/B2 + CableF1 match only a **branch** commit (`97fa34f04`, PVModbusConvertion, 2016-04-26); master said Cable1/Cable2 | node ran a branch config ~8 years; master names lose (keep as aliases, ticket 07) |
| 9 | 715-2 | 2023-10-19 (1 day) | Flexhouse vs Flexhouse1, no match | transition day |
| 10 | 716-2 | 2024-03-21 | matches master of 2023-10-27 | lag 146 d |
| ok | 117-2/5, 319-3/4, 117-4, 310-2 | 2024-09-08, 2024-10-03/09/14, 2026-01-07, 2026-08-13 | header = master same day; Java/figure same day | positive controls |

Also: one-day "eras" (`.csv.1`/`.csv.2` files) are restarts mid-day, not configurations; 117-6 header names follow
master `EVSE` 2025-02-14 (config 2023-11-14, lag 15 months, known as E6-020).

## Strategy proposed

1. **Run the cross-check for all boards** and emit *proposed* change entries into the era YAML files (origin
   `discovered`, evidence = header file + commit), classes as above: `lag`, `lead`, `branch`, `unmatched`, `transition`.
   Normalised-equal sets are aliases, not changes.
2. **Eras before 2015** from headers only: 2009-2013 changes (319-2 Bonus→Aircon 2012-02-18, Solar bays 2012, 319-3
   from 2013-05, E1/E2 2013-07-31, 117-2 Ext117-5 removed 2013-01-30) form a header-only era (or eras); model versions there
   are "unverified, header-only", built from the 2015 hardware.xml + header diffs. Proposal: one era E4 2013-07-31 to
   2023-06-15 (with revisions at 2015-08-05, 2016-06-14, ...) and E3 or "pre-E4" before it; decision for the staff/maintainer.
3. **Model per operational period, labels per header era:** the model follows master hardware.xml (ticket 07); the
   header era gives the **label map** data→model for that period (e.g. finding 4: old names must map onto the era-6 model).
   This is what `syslab_data` needs to select a model *and* translate columns.
4. **Selection in `syslab_data`:** date → era → operational period → newest validated model version; the header era of
   the files on that day must have a label map into that model, otherwise warn ("headers not covered"). Uncertain
   windows (findings 2, 4, 6, 7) give a warning, not a refusal.
5. **Expected model versions in `syslab_pandapower`** (draft): E6 6.x.y (now), E7 7.0.1 (next); historical E4 4.x.1
   (2015-2023, figure v4, verify on one experiment day per revision); pre-2015 only on request.

Open: run steps 1-2 for all 13 boards; decide pre-2015 era names; figure v4/v5 dates for era 4 (figure history from 2018 only).

---

# Full run, all 13 switchboards (2026-10-25)

Scripts in this folder (run with `python -I` from a folder outside the repos; read-only git in the lab repos):

- `header_xcheck.py`: every header era against the hardware.xml history; output `header_xcheck.csv`
  (one row per header era: class, master in force, matching version, offset, stale-from, meter checks, figure/Java
  commits within 3 days).
- `config_diffs.py`: breaker and meter changes between consecutive versions on master's first-parent line (dates
  there are the dates a change **reached master**, often a merge).

Not covered: 776-1 (no breaker columns), 330-12/330-13/310-2/319-4 (one header era each, all `ok`).

## Added by the full run

1. **Stale eras** (the header stays on an older config while master moves on during the era):
   117-2/4/5 2023-10-23 to 2024-02-26 (126 d), 319-2 2023-04-13 to 2023-11-30, 319-3 2023-06-23 to 2023-11-30 (160 d),
   715-2 2023-08-13 to 2023-10-18 (67 d), 716-2 2023-10-27 to 2024-03-20 (145 d), 117-6 2023-11-14 to 2025-02-13 (457 d).
2. **Meter names lag apart from breakers:** 117-4 `Grid_4` in hardware.xml from 2023-10-31, in headers from 2026-06-24;
   117-2 `CEEx2_1/_2` from 2024-10-14, headers 2026-06-24; 319-2 `CEEx2.A/B` from 2026-06-15, headers 2026-06-24.
   2026-06-24 looks like a restart of syslab-11 and syslab-01.
3. **The date of a change: author date or merge date.** On master's first-parent line, changes arrive by merges, often
   weeks later: 310-2 Boiler written 2026-08-13, merged 2026-09-12; 117-4 Cable_D1_Manual 2026-01-07 / 2026-02-06;
   319-2 CEEx2.A/B 2026-06-15 / 2026-06-25; rebuild 2023-06-23 / 2023-06-30; naming convention 2023-10-19..31 / 2023-11-01.
   The headers follow the **author date** (nodes run the branch before the merge). Ticket 07 says "the last master
   commit inside the period": it should say which date. Proposal: the author date, with the merge date as evidence.
4. **E6 misses real configuration changes** (now proposed entries on branch `model-versions`):
   117-5 Booster_Heater, Heatpump, CEE_2 bays (2024-10-08); X-cables 117-2/117-5 split into X1A/X1B/X2A/X2B, one
   breaker each (2024-10-09); 117-5 CEE_1/CEE_2 renamed CEEx1_1/_2 (2024-10-14); 117-4 Cable_D1_Manual (2026-01-07);
   319-3 ABB_Pri (2024-06-19; in headers since 2024-03-07 on a busbar no config names), supply-side manual breakers
   (2024-09-08) and the swapped supply breakers (2024-10-03); 319-4 MetaCross split into Cross_A/B/C (2024-09-08);
   716-2 E-cables split into A/B with Grid, HeatPump, PV, Spare_1..4 bays (2023-10-27); 715-2 Flexhouse renamed
   Flexhouse_1 (2023-08-13); renames 117-2 Grid→Grid_2 and X1→X1_2/X1_5 (2023-10-23/31).
5. **Era 6 start:** the first operational evidence is 2023-06-16 (headers of five switchboards), not 2023-06-23
   (ticket 05: an era starts at the first operational evidence).

---

# Step 2: eras before 2023 (2026-10-25)

Era files on branch `model-versions` (`ab31d0f`): `data/eras/E0.yaml`, `E2.yaml`, `E3.yaml`, `E4.yaml`, all proposed.

**Figure history found.** The older overview figures are in the history of the `syslab` repository (`media/`, deleted
there 2018-12-12, continued in `syslab-userspace`). The renames of 2015-08-11 (`9f0c83e0e`) give the numbering:

| Figure | File before 2015 | Added | Displayed from | Shows (new against the one before) |
|---|---|---|---|---|
| (none) | `swbdrawing.svg` | 2009-09-19 | 2009-09-19 | before EDISON; precedes all data files |
| (unnumbered) | `swbdrawing-qmarks.svg` | 2009-11-01 | 2009-11-01 | EDISON 117-2/4/5, 319-2 Grid/Local, 715-2, 319-3 crossbar A/B/C, Bonus |
| v1 | `swbdrawing-qmarks-20120101.svg` | 2011-12-04 | 2011-12-21 | Aircon, NEVIC, D1 to 117-4, B2B as Ship/Shore |
| v2 | `swbdrawing-qmarks-wide-20120101.svg` | 2012-01-13 | 2012-01-13 | wide-screen v1 with NEVIC 1-8 (117-6) |
| v3 | `swbdrawing-qmarks-wide-20130101.svg` | 2012-10-30 | 2012-10-30 | "Extension Jan2013": cables D1, E1, E2, F1, heat pumps, CHP, houses 417/418, test bays |
| v4 | `switchboard_overview_4.svg` | 2015-08-11 | 2015-08-11 | building 716, Flexhouse 2/3; from 2016-11-30 Container/EVSE/PV labels, 319-3 label 2016-07-15 |
| v5 | `switchboard_overview_5.svg` | 2023-01-12 | never | draft of v6 |

Figures v2 to v4 have an operator's login name in the access-control layer (ticket 12: such layers are stripped).

**Eras drafted** (named after the figure, starting at the first operational evidence):

| Era | From | To | Basis | Major change | First operational evidence |
|---|---|---|---|---|---|
| E0 | 2009-12-16 | 2012-02-18 | header-only | EDISON switchboards (unnumbered figure) | first data files |
| E2 | 2012-02-18 | 2013-07-31 | header-only | 117-6 NEVIC; Aircon replaces Bonus (v1/v2) | 319-2 Aircon in the data |
| E3 | 2013-07-31 | 2015-07-29 | header-only | extension to building 716 (v3) | 319-3 logs cables E1/E2 to 716-2 |
| E4 | 2015-07-29 | 2023-06-16 | configuration | 716-2, figure v4, hardware.xml from 2015-08-03 | 716-2 data files |

No E1 (v1 superseded by v2 in three weeks, no data change in between); no E5 (v5 never displayed). Era 4 is very
quiet: on master only the 2016 E1/E2 swap and the 715-2 cable names change in seven years.

**Data ahead of the configuration, already in 2015-2016:** 716-2 (a year), 715-2 cable names (a year), the E1/E2 swap
(a month). Same pattern as in era 6: the node runs a configuration before it is committed.

## Expected model versions (draft for syslab_pandapower)

| Era | Base model | Built from | Status it can reach |
|---|---|---|---|
| E7 | 7.0.1 | hardware.xml 2026-10 + cable data + Cable Q1 inquiry | validated (after Q1 answered) |
| E6 | 6.0.1 ... 6.5.x (today 6.4.2) | hardware.xml per operational period + E6 entries | validated on 2026-06-25 (6.4.2); earlier revisions need their own day |
| E4 | 4.0.1, 4.1.1 | hardware.xml 2015-08-03 / 2016-07 + **pre-rebuild cable data (missing: E4-Q1)** | validated if a suitable day with data exists (island_residuals) |
| E3, E2, E0 | 3.0.1, 2.x.1, 0.x.1 | breaker and meter names of the data headers + figure + E4 cable data as a guess | **unverified, header-only**; only on request (staff question 15) |

## How syslab_data would select one (outline)

1. Day -> era (`eras.era_at`), operational period (`period_at`), configuration revision in force.
2. Newest model version of that revision that is validated, else the newest one marked "fewer guarantees"; a model
   lacking newer confirmed entries of its era is marked "behind" (ticket 07/08 rules, handout).
3. Warnings: the era is header-only; the day lies in a header period (`header_periods_at(day, switchboard)`), so the
   column names of that day are translated with that period's names (`carries`); an entry in force that day is uncertain.
4. Data files whose names match no model of the day are reported, not guessed (the "unmatched" class).

What `syslab_pandapower` must publish for this: per model version its era, revision, validity, validation days and a
column map per header period (data names -> model breakers and meters). The column maps are new: they are the
public, data-side counterpart of the header periods (to settle in the publishing-and-selection ticket).
