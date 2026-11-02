# Pick-up log: data-name periods (C8) and configuration revisions of era 6 (C12)

Working list to pick up from later; not part of the staff draft. Each row has a status: `open`, then `confirmed`,
`corrected` or `dropped` with a date and who said so. Generated parts can be regenerated; hand edits go in the Status
and Notes columns only.

## C8: data-name periods, all switchboards, 2015 to today

Stretches in which the data files of a switchboard use other names than the master `hardware.xml` in force. Built by
`research/data_name_periods.py` from the column archive (`syslab_data/metadata/column_archive`, header eras since 2009)
and the `hardware.xml` history (read-only, all branches). Each header era is cut at every master change inside it and
each piece compared with the master version then in force. Left out: pieces that agree; a master change and the restart
that follows it on the same day; meters before 2023 named by their bay (the old configuration format did that).
Before 2015-08-03 there is no master configuration to compare with.

Kinds: **lag** (names of an older configuration: node not restarted), **lead** (names of a configuration committed
later), **branch** (names of a configuration that never reached master as such), **unmatched** (names of no
configuration), **transition** (unmatched for one day: a restart), **alias** (same breakers, other spelling),
**meter-lag** (breakers agree, but master names a meter the data still call otherwise).

Regenerate (from a folder outside the repos, workspace root as `W`):
`python -I W/syslab_pandapower_builder/.scratch/features/model-versions/research/data_name_periods.py W/syslab W/syslab_data/metadata/column_archive W/syslab_pandapower_builder model-versions`

| # | From | To | Days | Switchboard | Kind | What the data files use | Master in force (first) | Data file | Era file | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| D01 | 2015-08-05 | 2016-06-14 | 315 | 715-2 | branch | breaker names of the configuration of 2016-04-26 (97fa34f04, branch only) | 2015-08-03 affe00650 | `715_2_20150805_v02.csv.1, 715_2_20150805_v02.csv.2` | E4-H02 | open |
| D02 | 2016-06-14 | 2016-07-11 | 28 | 319-3 | lead | breaker names of the configuration of 2016-07-12 (f9d699cd5) | 2015-08-03 affe00650 | `319_3_20160614.csv.1` | E4-H03 | open |
| D03 | 2016-06-14 | 2016-06-14 | 1 | 715-2 | transition | breaker names of no configuration | 2015-08-03 affe00650 | `715_2_20160614_v02.csv.1` | E4-H02 | open |
| D04 | 2016-06-15 | 2016-07-11 | 27 | 715-2 | lead | breaker names of the configuration of 2016-07-12 (f9d699cd5) | 2015-08-03 affe00650 | `715_2_20160615_v02.csv.gz` | E4-H02 | open |
| D05 | 2023-03-13 | 2023-06-15 | 95 | 715-2 | lag | breaker names of the configuration of 2018-02-15 (dd4ff3f6c) | 2023-03-13 29e3f21a0 | `715_2_20160615_v02.csv.gz` | - | open |
| D06 | 2023-04-13 | 2023-11-30 | 232 | 319-2 | lag | breaker names of the configuration of 2021-01-21 (0d4e63848) | 2023-04-13 196774659 | `319_2_20120403.csv.gz` | E6-H04, E6-H10 | open |
| D07 | 2023-06-16 | 2023-06-22 | 7 | 117-2 | lead | breaker names of the configuration of 2023-06-23 (ebb1fb939) | 2022-03-08 948f15ef1 | `117_2_20230616.csv` | E6-H01 | open |
| D08 | 2023-06-16 | 2023-06-22 | 7 | 117-4 | lead | breaker names of the configuration of 2023-06-23 (ebb1fb939) | 2022-03-08 948f15ef1 | `117_4_20230616.csv` | E6-H01 | open |
| D09 | 2023-06-16 | 2023-06-22 | 7 | 117-5 | lead | breaker names of the configuration of 2023-06-23 (ebb1fb939) | 2022-03-08 948f15ef1 | `117_5_20230616.csv` | E6-H01 | open |
| D10 | 2023-06-16 | 2023-06-22 | 7 | 715-2 | lead | breaker names of the configuration of 2023-06-23 (ebb1fb939) | 2023-03-13 29e3f21a0 | `715_2_20230616.csv` | E6-H01 | open |
| D11 | 2023-06-16 | 2023-06-22 | 7 | 716-2 | lead | breaker names of the configuration of 2023-06-23 (ebb1fb939) | 2018-02-15 b9d04a949 | `716_2_20230616.csv` | E6-H01 | open |
| D12 | 2023-06-23 | 2023-09-27 | 97 | 117-4 | meter-lag | old names for the meters Grid 117-4 | 2023-06-23 ebb1fb939 | `117_4_20230616.csv` | E6-H02 | open |
| D13 | 2023-06-23 | 2023-11-30 | 161 | 319-3 | lag | breaker names of the configuration of 2021-01-21 (0d4e63848) | 2023-06-23 ebb1fb939 | `319_3_20160614.csv.1` | E6-H04 | open |
| D14 | 2023-08-13 | 2023-10-18 | 67 | 715-2 | lag | breaker names of the configuration of 2023-06-23 (ebb1fb939) | 2023-08-13 f3e088dc7 | `715_2_20230616.csv` | E6-H07 | open |
| D15 | 2023-09-27 | 2023-09-27 | 1 | 117-2 | lead | breaker names of the configuration of 2024-10-09 (777e5f1a4) | 2023-06-23 ebb1fb939 | `117_2_20230927.csv.1` | E6-H02 | open |
| D16 | 2023-09-27 | 2023-09-27 | 1 | 117-4 | alias | same breakers, other spelling | 2023-06-23 ebb1fb939 | `117_4_20230927.csv.1` | E6-H02 | open |
| D17 | 2023-09-27 | 2023-09-27 | 1 | 117-5 | lead | breaker names of the configuration of 2024-10-14 (a96c88172) | 2023-06-23 ebb1fb939 | `117_5_20230927.csv.1` | E6-H02 | open |
| D18 | 2023-09-28 | 2023-10-22 | 25 | 117-4 | meter-lag | old names for the meters Grid 117-4 | 2023-06-23 ebb1fb939 | `117_4_20230928.csv` | - | open |
| D19 | 2023-10-19 | 2023-10-19 | 1 | 715-2 | transition | breaker names of no configuration | 2023-10-19 fce9dd0eb | `715_2_20231019.csv.1` | E6-H07 | open |
| D20 | 2023-10-23 | 2023-10-30 | 8 | 117-2 | alias | same breakers, other spelling | 2023-10-23 2a54a1449 | `117_2_20230928.csv` | E6-H03 | open |
| D21 | 2023-10-23 | 2024-02-26 | 127 | 117-4 | alias | same breakers, other spelling | 2023-10-23 2a54a1449 | `117_4_20230928.csv` | E6-H03, E6-H10 | open |
| D22 | 2023-10-23 | 2023-10-30 | 8 | 117-5 | alias | same breakers, other spelling | 2023-10-23 2a54a1449 | `117_5_20230928.csv` | E6-H03 | open |
| D23 | 2023-10-27 | 2024-03-20 | 146 | 716-2 | lag | breaker names of the configuration of 2023-06-23 (ebb1fb939) | 2023-10-27 20271a203 | `716_2_20230616.csv` | E6-H08 | open |
| D24 | 2023-10-31 | 2024-02-26 | 119 | 117-2 | lag | breaker names of the configuration of 2023-06-23 (ebb1fb939) | 2023-10-31 a61c8f814 | `117_2_20230928.csv` | E6-H03, E6-H10 | open |
| D25 | 2023-10-31 | 2024-02-26 | 119 | 117-5 | lag | breaker names of the configuration of 2023-06-23 (ebb1fb939) | 2023-10-31 a61c8f814 | `117_5_20230928.csv` | E6-H03 | open |
| D26 | 2023-11-14 | 2025-02-13 | 458 | 117-6 | lag | breaker names of the configuration of 2018-01-19 (6bc9fe055) | 2023-11-14 d2aff19b5 | `117_6_20120627_v02.csv` | E6-H09 | open |
| D27 | 2024-02-27 | 2026-06-24 | 849 | 117-4 | meter-lag | old names for the meters Grid_4 | 2023-10-31 a61c8f814 | `117_4_20240227.csv, 117_4_20260107.csv.1` | E6-H10 | open |
| D28 | 2024-03-07 | 2024-09-07 | 185 | 319-3 | unmatched | breaker names of no configuration | 2023-12-01 c857263a5 | `319_3_20240307-old.csv` | E6-H05 | open |
| D29 | 2024-09-08 | 2024-09-08 | 1 | 319-3 | transition | breaker names of no configuration | 2024-09-08 b736d2d87 | `319_3_20240307-old.csv, 319_3_20240908.csv.1` | E6-H06 | open |
| D30 | 2024-09-08 | 2024-10-02 | 25 | 319-3 | meter-lag | old names for the meters ABB_Pri | 2024-09-08 b736d2d87 | `319_3_20240908.csv.2` | E6-H06 | open |
| D31 | 2024-10-14 | 2026-06-24 | 619 | 117-2 | meter-lag | old names for the meters CEEx2_1, CEEx2_2 | 2024-10-14 a96c88172 | `117_2_20241009.csv.1` | E6-H10 | open |
| D32 | 2026-06-15 | 2026-06-24 | 10 | 319-2 | meter-lag | old names for the meters CEEx2.A, CEEx2.B | 2026-06-15 dfb7b96c1 | `319_2_20231201.csv` | E6-H10 | open |

**Against the era files** (`header_periods` on branch `model-versions`), to pick up:

- D05 (715-2, 2023-03-13 to 06-15) and D06 before 2023-06-16 (319-2 from 2023-04-13) fall in era 4 and have no
  era-file period yet: candidates E4-H04, E4-H05.
- D18 (117-4, 2023-09-28 to 10-22, meter "Grid 117-4" logged as Grid) has no period; with D12 and D27 the 117-4 grid meter
  is logged as "Grid" from 2023-06-23 to 2026-06-24 under two master names ("Grid 117-4", then "Grid_4"). E6-H10 starts on
  2023-10-31 for it; it should start on 2023-06-23.
- D30 (319-3, ABB_Pri meter missing in the data 2024-09-08 to 10-02) is wider than E6-H06 (one day).
- E6-H01 to E6-H09 match rows here; E6-H10 bundles D27, D31, D32.

## C12: configuration revisions of era 6

Twelve entries found on 2026-10-25 (E6-014 to E6-025) have no revision yet. Proposal: group by date and by the
configuration commit they share, and number the revisions in time order. The current numbers (6.0 to 6.5) were marked
illustrative in the change-log draft and are not published anywhere, so renumbering is still cheap; the validated model
6.4.2 would become 6.6.1 (it accommodates everything up to the 319-2 CEEx2 meter).

| Proposed | Dates | Entries (new in bold) | What | Today | Status |
|---|---|---|---|---|---|
| 6.0 | 2023-06-16 to 10-19 | E6-001 ... E6-006, **E6-014** | the rebuild and its commissioning; 715-2 Flexhouse_1 (2023-08-13) | 6.0 | open |
| 6.1 | 2023-10-23 to 11-14 | **E6-015, E6-016, E6-024**, E6-007 | naming convention on all switchboards; 716-2 E-cables split, new bays; 117-4 Grid_4; 117-6 EVSE | 6.1 | open |
| 6.2 | 2024-06-19 | **E6-017** | 319-3 ABB_Pri (instrument check) | (new) | open |
| 6.3 | 2024-09-08 to 10-03 | E6-008, **E6-018, E6-019, E6-020** | 319-3 and 319-4 as built: E1/E2, supply side, cross bays, supply breakers (same commit `b736d2d87` for three of them) | 6.2 | open |
| 6.4 | 2024-10-08 to 10-14 | **E6-021, E6-022, E6-023**, E6-009, E6-012 | "validated syslab-11 configuration": 117-5 new bays, X cables split, CEEx1, 117-2 CEEx2 | 6.3 | open |
| 6.5 | 2026-01-07 | **E6-025** | 117-4 manual breaker of cable D1 | (new) | open |
| 6.6 | 2026-06-15 | E6-010 | 319-2 CEEx2 (two sockets) | 6.4 | open |
| 6.7 | 2026-08-13 | E6-011 | 310-2 Boiler | 6.5 | open |

Alternatives: keep 6.0 to 6.5 and put the new entries into the nearest existing revision (no new numbers, but 6.2 would
then hold changes from June and October 2024); or open the new revisions as 6.6 and 6.7 out of time order (no
renumbering, but the numbers no longer follow the calendar).
