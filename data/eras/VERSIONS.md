# SYSLAB grid: versions log

Generated from `data/eras/E*.yaml` (`python -m syslab_pandapower_builder.eras`); edit the era files, not this.
Version numbers: era.revision.model, variants era.revision.model.CODE. Everything marked proposed waits for a person to confirm it.

## Era 7: Fast charger site 119-10

2026-10-05 to today · figure v7

| Revision | Date | Entry | Change | Certainty, status |
|---|---|---|---|---|
| 7.0 (from 2026-10-05) | 2026-10-05 | E7-001 | 119-10: added (node syslab-44, one busbar A) | confirmed, confirmed |
|  | 2026-10-05 | E7-002 | 119-10 Battery_1..Battery_5, EVSE_12, Cable_Q1: added | confirmed, confirmed |
|  | 2026-10-05 | E7-003 | Q1 330-13:EVSE_12 - 119-10:Cable_Q1: added (length and cable type unknown (inquiry to the staff)) | confirmed, confirmed |

Not in a revision:

- 2026-10-05 E7-004 330-13 EVSE_12: renamed (shown as "Cable_Q1" by the display program and figure v7; hardware.xml keeps EVSE_12 (the model follows it)) [no: evidence only]
- 2026-10-05 E7-005 316-2 PTX, P2XA, P2XB, Grid: added (drawn greyed out in figure v7; not in hardware.xml or the display program) [no: planned]

Model versions: none yet.

## Era 6: After the 2023 rebuild

2023-06-16 to 2026-10-05 · figure v6

| Revision | Date | Entry | Change | Certainty, status |
|---|---|---|---|---|
| 6.0 (from 2023-06-23) | 2023-06-23 | E6-001 | 319-3: moved (319-3 to its own node syslab-52 (new switchboard driver)) | confirmed, confirmed |
|  | 2023-07-02 | E6-002 | 319-4: added | confirmed, confirmed |
|  | 2023-08-13 | E6-014 | 715-2 Flexhouse: renamed (Flexhouse -> Flexhouse_1 (config written as a test case for the old Schneider PLCs)) | confirmed, proposed |
|  | 2023-10-06 | E6-003 | 330-13: added | confirmed, confirmed |
|  | 2023-10-06 | E6-004 | 330-12: added | confirmed, confirmed |
|  | 2023-10-06 | E6-005 | 330-12 Gaia: moved (Gaia wind turbine connected at 330-12 (left 715-2 in the rebuild); drawn 2023-06-23) | confirmed, proposed |
|  | 2023-10-19 | E6-006 | 310-2: added | confirmed, confirmed |
| 6.1 (from 2023-10-23) | 2023-10-23 | E6-015 | 117-2 Grid, Cable_X1: renamed (naming convention: Grid -> Grid_2, Cable X1 -> Cable_X1_2 (117-5: Cable_X1_5); the other renames of ...) | confirmed, proposed |
|  | 2023-10-27 | E6-016 | 716-2 Cable_E1A, Cable_E1B, Cable_E2A, Cable_E2B, Grid, HeatPump, PV, Spare_1..Spare_4: added (new PLC format and hardware changes: cables E1 and E2 split into A/B bays, new bays Grid, HeatPump (was ...) | confirmed, proposed |
|  | 2023-10-31 | E6-024 | 117-4 Grid: renamed (meter Grid_117-4 -> Grid_4 (breaker names unchanged); headers carry Grid_4 only from 2026-06-24) | confirmed, proposed |
|  | 2023-11-14 | E6-007 | 117-6 EVSE_01..EVSE_08: renamed (NEVIC bays renamed EVSE; data files use the new names from 2025-02-14) | confirmed, proposed |
| 6.2 (from 2024-06-19) | 2024-06-19 | E6-017 | 319-3 ABB_Pri: added (ABB primary-side meter and breaker (after the instrument check); the headers carry ABB_Pri from ...) | uncertain, proposed |
| 6.3 (from 2024-09-08) | 2024-09-08 | E6-008 | 319-3 Cable_E1A, Cable_E1B, Cable_E2A, Cable_E2B: renamed (E1/E2 swapped in the configuration (as built differed from as planned); figure swapped C1/C2 and E1/E2 ...) | uncertain, proposed |
|  | 2024-09-08 | E6-018 | 319-3 Supply, Spare, Amp_1, Amp_2, Grid: added (supply side of 319-3 as built: manual breakers Supply, Spare, Amp_1, Amp_2 on Busbar_Transformer; Grid ...) | confirmed, proposed |
|  | 2024-09-08 | E6-019 | 319-4 MetaCross -> Cross_A, Cross_B, Cross_C: retyped (meta-crossbar bay (3 breakers) split into three cross bays of two breakers each (A-B, B-C, A-C)) | confirmed, proposed |
|  | 2024-10-03 | E6-020 | 319-3 ABB_Pri, Grid: moved ("fixing swapped breakers and changed busbar names": ABB_Pri breaker on Busbar_Supply, the Grid breaker removed) | confirmed, proposed |
| 6.4 (from 2024-10-08) | 2024-10-08 | E6-021 | 117-5 Booster_Heater, Heatpump, CEE_2: added (three new bays on 117-5 (8 new breakers); one day of headers with these names already on 2023-09-27 (E6-H02)) | confirmed, proposed |
|  | 2024-10-09 | E6-022 | 117-2, 117-5 Cable_X1_2, Cable_X1_5 -> Cable_X1A/X1B/X2A/X2B: retyped (the X cables between 117-2 and 117-5 as four bays with one breaker each (X1A/X1B on Busbar A, X2A/X2B on ...) | confirmed, proposed |
|  | 2024-10-14 | E6-023 | 117-5 CEE_1, CEE_2: renamed (CEE_1, CEE_2 -> CEEx1_1, CEEx1_2) | confirmed, proposed |
|  | 2024-10-14 | E6-009 | 117-2 CEEx2: retyped (second CEEx2 meter (two sockets, one per busbar); data files from 2026-06-24) | confirmed, confirmed |
|  | 2024-10-14 | E6-012 | 117-2 CEEx2: retyped (meter-to-socket assignment: CEEx2_2 is the Busbar A socket, CEEx2_1 Busbar B (found in the 2026-06-25 data ...) | confirmed, confirmed |
| 6.5 (from 2026-01-07) | 2026-01-07 | E6-025 | 117-4 Cable_D1: added (manual breaker of cable D1 with feedback (Cable_D1_Manual, Busbar A); master by merge 947d603db on 2026-02-06) | confirmed, proposed |
| 6.6 (from 2026-06-15) | 2026-06-15 | E6-010 | 319-2 CEEx2: retyped (second CEEx2 instrument in the configuration (two sockets, one per busbar)) | confirmed, confirmed |
| 6.7 (from 2026-08-13) | 2026-08-13 | E6-011 | 310-2 Spare_1: renamed (Spare_1 -> Boiler) | confirmed, confirmed |

Not in a revision:

- 2026-04-19 E6-013 330-12 Spare_6, Spare_7: removed (no longer logged from 2026-04-19, still in hardware.xml; spare given to a named unit?) [no: evidence only]

| Model | Revision | Published | Status | Validated | Note |
|---|---|---|---|---|---|
| 6.6.1 | 6.6 | 2026-10-20 | superseded | - | CEEx2 sockets as two plugs (one bus and port per socket); numbered 6.4.1 until 2026-11-03 |
| 6.6.2 | 6.6 | 2026-10-24 | current | 2026-06-25: island_residuals, all islands; largest (319-3) RMSE 0.22 kW at 1 min | 117-2 CEEx2 meters corrected (CEEx2_2 is the Busbar A socket, found in the data); numbered 6.4.2 until 2026-11-03 |
| 6.6.2.J1A | 6.6 | 2026-10-24 | variant | - | variant for the 2026 J1A experiment (converter set-up); was written 6.4.2/j1a-2026 |
| 6.7.1 | 6.7 | built 2026-11-03, not published | superseded | - | first model built from the configuration in force on a day (build_model --conf-repo syslab --conf-date 2026-08-13); against 6.6.2 only 310-2 Spare_1 -> Boiler; not published; 2026-09-08 island_residuals: all islands with a slack meter close (largest RMSE 0.040 kW at 1 min), but 310-2 was idle that day, so the Boiler change is not tested by it |
| 6.7.2 | 6.7 | built 2026-11-07, not published | current | 2026-09-21: validate_day (island periods of at least 2 h, 06:00-18:00): every checkable grid-connected island closes; largest (319-3) RMSE 0.12 kW at 1 min, worst 716-2 0.32 kW; 310-2 with the Boiler 0.03 kW; the 12:45-16:08 grid-emulator island (slack 319-4 GridEmu, 7 boards) is converter-driven, not used (P mean -3.0 kW, RMSE 5.2 kW; the emulator's metering to be looked at); 2026-09-24: validate_day (island periods of at least 2 h, 06:00-18:00): every checkable island closes; largest (319-3) RMSE 0.09 kW at 1 min, worst 330-13 0.17 kW; 310-2 with the Boiler 0.07 kW | 6.7.1 with the meter names of all metered bays from hardware.xml (bay_meters, auto-update ticket 09; only 117-4 Grid -> Grid_4 differs from its bay); network, switch map, converters and catalog as 6.7.1; not published; on both days the published model misses the Boiler (310-2 island 16.9 and 36.7 kW RMSE) |

Data-name periods: E6-H01 117-2, 117-4, 117-5, 715-2, 716-2 2023-06-16 to 2023-06-22 (lead); E6-H02 117-2, 117-4, 117-5 2023-09-27 to 2023-09-27 (lead); E6-H03 117-2, 117-4, 117-5 2023-10-23 to 2024-02-26 (lag); E6-H04 319-2, 319-3 2023-06-16 to 2023-11-30 (lag); E6-H05 319-3 2024-03-07 to 2024-09-07 (unmatched); E6-H06 319-3 2024-09-08 to 2024-09-08 (transition); E6-H07 715-2 2023-08-13 to 2023-10-19 (lag); E6-H08 716-2 2023-10-27 to 2024-03-20 (lag); E6-H09 117-6 2023-11-14 to 2025-02-13 (lag); E6-H10 117-2, 117-4, 319-2 2023-10-31 to 2026-06-23 (meter-lag)

## Era 4: Switchboard 716-2 in operation

2015-07-29 to 2023-06-16 · figure v4

| Revision | Date | Entry | Change | Certainty, status |
|---|---|---|---|---|
| 4.0 (from 2015-07-29) | 2015-07-29 | E4-002 | 716-2: added (716-2 with bays Grid, CEE, CHP, Cable E1, Cable E2, Cable F1, Flexhouse2, Flexhouse3, Heatpump1, ...) | confirmed, proposed |
|  | 2015-08-03 | E4-001 | 117-2, 117-4, 117-5, 117-6, 319-2, 319-3, 715-2: added (first configuration in the lab repository (busbars "Busbar 1/2", on 319-2 "Grid"/"Local", on 319-3 A/B/C)) | confirmed, proposed |
|  | 2015-08-03 | E4-003 | 319-2 Aircon: added (AirCon wind turbine on 319-2 (never on 715-2 in any configuration since 2015)) | confirmed, proposed |
| 4.1 (from 2016-06-14) | 2016-06-14 | E4-004 | 319-3 E1 to 716-2, E2 to 716-2: moved (cables E1/E2 swap busbars on 319-3 (E1 from Busbar A/B to A/C, E2 from A/C to A/B); in the data from ...) | uncertain, proposed |
|  | 2016-07-12 | E4-005 | 715-2 Cable1, Cable2 -> CableB1, CableB2; CableF1: renamed (715-2 cables named after their route (B1, B2 to 319-3) and cable F1 to 716-2 added; the data use these ...) | confirmed, proposed |

Not in a revision:

- 2016-11-30 E4-006 117-4, 117-5, 117-6 Container 1-3, EVSE 1-8, PV: renamed (figure v4 names EDISON bays Container, NEVIC bays EVSE, Solar PV; the configuration keeps the old names ...) [no: figure only]
- 2018-07-02 E4-007 all: retyped (the display program moves to the syslab-userspace repository and keeps figure v4 (116 breakers on 8 ...) [no: display only]

Model versions: none yet.

Data-name periods: E4-H01 716-2 2015-07-29 to 2016-07-11 (lead); E4-H02 715-2 2015-08-05 to 2016-07-11 (lead); E4-H03 319-3 2016-06-14 to 2016-07-11 (lead)

## Era 3: Extension to building 716

2013-07-31 to 2015-07-29 · figure v3 · header-only

| Revision | Date | Entry | Change | Certainty, status |
|---|---|---|---|---|
| 3.0 (from 2013-07-31) | 2013-07-31 | E3-001 | 319-3 E1 to 716-2, E2 to 716-2: added (cables E1 (Busbar A/B) and E2 (Busbar A/C) to 716-2; the figure is dated 2013-01-01) | uncertain, proposed |

Not in a revision:

- 2013-07-31 E3-002 716-2: added (switchboard of building 716 (Flexhouse 2/3, CHP, heat pumps in figure v4); bays unknown until its data of 2015) [no: evidence only]

Model versions: none yet.

## Era 2: Switchboard 117-6 and the Aircon turbine

2012-02-18 to 2013-07-31 · figure v2 · header-only

| Revision | Date | Entry | Change | Certainty, status |
|---|---|---|---|---|
| 2.0 (from 2012-02-18) | 2012-02-18 | E2-001 | 319-2 Aircon: renamed (bay Bonus (wind turbine) becomes Aircon (wind turbine)) | confirmed, proposed |
| 2.1 (from 2012-03-14) | 2012-03-14 | E2-002 | 117-2 Solar: added | confirmed, proposed |
|  | 2012-04-03 | E2-003 | 319-2 Solar: added | confirmed, proposed |
| 2.2 (from 2012-05-03) | 2012-05-03 | E2-004 | 117-6 NEVIC1..NEVIC8: added (NEVIC charging posts, busbars Grid/SYSLAB; breaker columns from 2012-06-27) | confirmed, proposed |
|  | 2012-07-07 | E2-005 | 117-4 NEVIC: added (breaker of the feeder to 117-6) | confirmed, proposed |
| 2.3 (from 2013-05-19) | 2013-05-19 | E2-007 | 319-3 A1, A2 to 319-2; B1, B2 to 715-2; C1, C2 to 117-2; B2B-Ship; B2B-Shore: added (319-3 logged from 2013-05-19; drawn as the crossbar switch since 2009, so in operation before) | confirmed, proposed |

Not in a revision:

- 2013-01-30 E2-006 117-2 Ext117-5: removed (no longer logged on 117-2 (still drawn in figures v3 and v4, and logged on 117-5); meter removed?) [no: evidence only]

Model versions: none yet.

## Era 0: The EDISON switchboards

2009-12-16 to 2012-02-18 · figure v0 · header-only

| Revision | Date | Entry | Change | Certainty, status |
|---|---|---|---|---|
| 0.0 (from 2009-12-16) | 2009-12-16 | E0-001 | 319-2, 715-2: added (first data files; 319-2 bays Grid, Diesel, Dumpload, B2B, CEE, Bonus, Cable1, Cable2; 715-2 bays Grid, ...) | confirmed, proposed |
| 0.1 (from 2011-05-01) | 2011-05-01 | E0-002 | 117-2, 117-4, 117-5: added (first data files: 117-2 Grid, Battery, Machine, Cable1, Cable2, Ext117-5; 117-4 Transformer, EDISON3; ...) | confirmed, proposed |

Model versions: none yet.
