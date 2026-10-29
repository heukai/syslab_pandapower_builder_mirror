# SYSLAB grid: change log (PROTOTYPE, draft for the technical staff)

> Throwaway proposal for the ticket "What should a human-readable change log look like for the lab staff?", round 2
> (2026-10-23), aligned with the decisions of the map "dated model versions". Built by hand from the research of
> 2026-10-20/21 and the `syslab/conf` history. **Please correct anything that is wrong or missing**: strike out, add a line,
> write in the margin. The form itself is a proposal too.
>
> Round 3 (2026-10-25): cross-checked against the column archive (the column headers of every data file since 2009). It
> found twelve configuration changes of era 6 that were missing here, a start of era 6 one week earlier, and periods in
> which the data files use other names than the configuration. Entry numbers now follow the era file
> (`data/eras/E6.yaml`, branch `model-versions`).
>
> Round 4 (2026-10-25): the eras before 2023, from the data files and the history of the older figures (eras 0, 2, 3, 4;
> C13 to C15).

**How to read it**

- **Numbers.** `7` is a **configuration era**: it opens with a major change (a new switchboard, or a new layout of the
  overview figure). `7.2` is a **configuration revision**: the era's second set of smaller changes (renames, bays, meters).
  `7.2.3` is a **model version**: the third model of configuration 7.2, improved and validated over time;
  `7.2.3/summer-2027` is a scenario model derived from it. Each era starts at revision `.0`.
- **Change entries** (`E7-001`) are the lines of the log. Each says what changed, on which date, where it was seen
  (configuration = `hardware.xml` in master, figure, display program, data files, our cable data) and how sure we are.
- **Operational periods** split an era while its switchboards come into operation in stages (the commissioning period of
  2023), because experiments took place meanwhile.
- **Certainty:** *confirmed* (sources agree), *uncertain* (sources disagree, or labels were mixed up for a while: flagged,
  not corrected). *Not in force:* seen only in the figure or the display, or planned (drawn greyed out).
- Names are the `hardware.xml` names. Where the figure or the display uses another name, it is given in brackets.
- **Dates** are the dates a configuration change was written (its commit). It often reached master weeks later by a merge
  (Boiler: written 2026-08-13, on master 2026-09-12); the data files follow the written date.
- **Data-name periods** (`E6-H04`): times in which the data files use other names than the configuration in force,
  because a node had not been restarted, ran a configuration before it was committed, or ran one that was never committed.
  They do not change the grid; they say how to read the data of that time.

---

## Announced, not in force

| Entry | What | Seen in | Note |
|---|---|---|---|
| E7-010 | Switchboard **316-2** (bays PTX, P2XA, P2XB, Grid) and **Cable M1** from 319-4 | figure v7, greyed out (2026-10-05) | Planned. Would open era 7b, or era 8 with a new figure. |
| E7-009 | 330-13 bay EVSE_12 shown as "Cable_Q1" | display program, figure v7 (2026-10-05) | `hardware.xml` still says EVSE_12; the model keeps it. May be renamed later. |

---

## Era 7, from 2026-10-05: fast charger site 119-10 (overview figure v7)

**Major change:** new switchboard **119-10** (node syslab-44, Kempower fast charger). Announced by figure v7, materialized
by `hardware.xml` on 2026-10-05; first data files not yet checked (if 119-10 logged earlier from a feature-branch
configuration, the era starts then).

**Configuration 7.0**

| Entry | Date | Change | Seen in | Certainty |
|---|---|---|---|---|
| E7-001 | 2026-10-05 | New switchboard 119-10, one busbar A | configuration, figure v7, display | confirmed |
| E7-002 | 2026-10-05 | 119-10 bays Battery_1 ... Battery_5, EVSE_12, Cable_Q1 | configuration, display | confirmed |
| E7-003 | 2026-10-05 | New **Cable Q1**: 330-13 bay EVSE_12 to 119-10 bay Cable_Q1 | figure v7; our cable data (declared) | confirmed; **length and type unknown** |
| E7-004 | 2026-10-05 | Figure labels "Ext. 117-2 / 117-5" now read "Cable X1 / X2" | figure v7 | figure only |

**Model versions:** none yet. **7.0.1** to be developed. Open inquiries: Cable Q1 length and cable type; what is behind the
119-10 bays (charger and battery ratings).

---

## Era 6, 2023-06-16 (?) to 2026-10-05: after the 2023 rebuild (overview figure v6)

**Major change:** the 2023 rebuild (busbars renamed A/B, "Solar" bays renamed PV, 319-3 on its own node). Figure v6 and the
display program changed on 2023-06-23, the configurations on 2023-06-14 (319-2) and 2023-06-23. **But the data files of
117-2, 117-4, 117-5, 715-2 and 716-2 already use the rebuild names from 2023-06-16**, a week before the configuration was
committed. An era starts at its first operational evidence, so we propose 2023-06-16 (C7).

**Operational periods (commissioning period 2023)**

| Period | From | Switchboards in operation (in addition to 117-x, 319-2, 715-2, 716-2) | Note |
|---|---|---|---|
| 6-a | 2023-06-16 (?) | 319-3 (node syslab-52) | rebuild; 319-3 left syslab-01 on 2023-04-13 |
| 6-b | 2023-07-02 | + 319-4 | |
| 6-c | 2023-10-06 | + 330-12, 330-13 (with the **Gaia** wind turbine on 330-12) | figure v6 "as-built 330-12/330-13" on 2023-10-05 |
| 6-d | 2023-10-19 | + 310-2 | figure v6 "final configuration of 310-2" the same day; end of commissioning |

Data files of the new switchboards start later: 319-4 2023-12-01, 330-13 2023-12-19, 330-12 2024-06-10, 310-2 2025-02-24.

**Configuration revisions**

| Revision | Entry | Date | Change | Seen in | Certainty |
|---|---|---|---|---|---|
| 6.0 | E6-001 ... | 2023-06-23 | The rebuild configuration (all switchboards above, by operational period) | configuration, figure v6, display | confirmed |
| 6.1 | E6-007 | 2023-11-14 | 117-6: NEVIC bays renamed EVSE (data files use EVSE from 2025-02-14) | configuration; data | confirmed (logging lag) |
| 6.2 | E6-008 | 2024-09-08 | 319-3: cables E1/E2 swapped in the configuration (as built differed from as planned; figure swapped C1/C2 and E1/E2 labels on 2024-06-19) | configuration, figure | **uncertain 2023-12-01 to 2024-09-07**: 319-3 E1/E2 breaker data may carry swapped names |
| 6.3 | E6-009, E6-012 | 2024-10-14 | 117-2: second CEEx2 meter (two sockets, one per busbar; `CEEx2_2` on Busbar A, `CEEx2_1` on Busbar B, from the 2026-06-25 data) | configuration; data from 2026-06-24 | confirmed (logging lag) |
| 6.4 | E6-010 | 2026-06-15 | 319-2: second CEEx2 meter (two sockets, one per busbar) | configuration; data from 2026-06-24 | confirmed |
| 6.5 | E6-011 | 2026-08-13 | 310-2: bay Spare_1 renamed **Boiler** | configuration, figure v6, display (same day) | confirmed |

**Found in round 3, not yet in a revision** (all in the configuration and in the data; which revision each belongs to is
for you to say, question 12):

| Entry | Date | Change | Seen in | Certainty |
|---|---|---|---|---|
| E6-014 | 2023-08-13 | 715-2: Flexhouse renamed Flexhouse_1 | configuration; data from 2023-10-19 | confirmed (logging lag) |
| E6-015 | 2023-10-23 | 117-2: Grid renamed Grid_2, Cable X1 renamed Cable_X1_2 (117-5: Cable_X1_5), with the naming convention of all switchboards (2023-10-19 to 10-31) | configuration, display; data from 2024-02-27 | confirmed (logging lag) |
| E6-016 | 2023-10-27 | 716-2: cables E1 and E2 split into A/B bays; new bays Grid, HeatPump, PV, Spare_1 ... Spare_4 (16 to 32 breakers) | configuration, figure and display (2023-10-31); data from 2024-03-21 | confirmed (logging lag) |
| E6-017 | 2024-06-19 | 319-3: ABB primary meter and breaker (ABB_Pri) | configuration; data from 2024-03-06, on a busbar "Grid_Distribution" no configuration names | **uncertain** (C9) |
| E6-018 | 2024-09-08 | 319-3: supply side as built: manual breakers Supply, Spare, Amp_1, Amp_2, a Grid breaker | configuration, display, data (same day) | confirmed |
| E6-019 | 2024-09-08 | 319-4: meta crossbar split into Cross_A, Cross_B, Cross_C | configuration, display, data (same day) | confirmed |
| E6-020 | 2024-10-03 | 319-3: ABB_Pri breaker on the supply busbar, Grid breaker removed ("swapped breakers") | configuration, display, data (same day) | confirmed |
| E6-021 | 2024-10-08 | 117-5: new bays Booster_Heater, Heatpump, CEE_2 | configuration; data from 2024-10-09; display 2024-10-14 | confirmed |
| E6-022 | 2024-10-09 | 117-2 and 117-5: X cables as four bays with one breaker each (X1A/X1B on Busbar A, X2A/X2B on Busbar B) | configuration, data (same day); display fixed 2025-01-17 | confirmed |
| E6-023 | 2024-10-14 | 117-5: CEE_1, CEE_2 renamed CEEx1_1, CEEx1_2 | configuration, display, data (same day) | confirmed |
| E6-024 | 2023-10-31 | 117-4: Grid meter renamed Grid_4 (breakers unchanged) | configuration; data from 2026-06-24 | confirmed (logging lag) |
| E6-025 | 2026-01-07 | 117-4: manual breaker of cable D1 with feedback | configuration, display, data (same day) | confirmed |

**Data-name periods** (the data files of that time use other names than the configuration in force; question 8)

| Period | Switchboards | From | To | The data use | Why, as far as we can tell |
|---|---|---|---|---|---|
| E6-H01 | 117-2, 117-4, 117-5, 715-2, 716-2 | 2023-06-16 | 2023-06-22 | the rebuild names | configuration committed a week after it ran |
| E6-H02 | 117-2, 117-4, 117-5 | 2023-09-27 | 2023-09-27 | names committed only in October 2024 (Booster_Heater, CEEx1, split X cables) | one day, a test run? (C10) |
| E6-H03 | 117-2, 117-4, 117-5 | 2023-10-23 | 2024-02-26 | names before the naming convention | node not restarted |
| E6-H04 | 319-2, 319-3 | 2023-06-16 | 2023-11-30 | **pre-rebuild names** (319-2 Grid/Local busbars; 319-3 "A1 to 319-2" ...) | node not restarted? Covers operational periods 6-a to 6-c |
| E6-H05 | 319-3 | 2024-03-07 | 2024-09-07 | ABB_Pri on busbar "Grid_Distribution" | a configuration that was never committed? |
| E6-H06 | 319-3 | 2024-09-08 | 2024-09-08 | E1/E2 busbars swapped against the configuration | restart day |
| E6-H07 | 715-2 | 2023-08-13 | 2023-10-19 | Flexhouse (not Flexhouse_1) | node not restarted |
| E6-H08 | 716-2 | 2023-10-27 | 2024-03-20 | the June 2023 names (E1/E2 not split) | node not restarted |
| E6-H09 | 117-6 | 2023-11-14 | 2025-02-13 | NEVIC names | node not restarted |
| E6-H10 | 117-2, 117-4, 319-2 | 2023-10-31 | 2026-06-23 | old meter names (Grid, CEEx2) | all switch on 2026-06-24: a restart of syslab-11 and syslab-01? (C11) |

Also noted in this era, without a configuration revision: 330-12 Spare_6/7 no longer logged from 2026-04-19 (still in the
configuration; spare given to a unit?); 776-1 left the configuration on 2024-05-23 (node syslab-30 now runs EVSE18; not part
of the grid model); the rock store was cancelled.

**Model versions** (numbers illustrative until the first era file exists)

| Model | Published | Accommodates | Validated on | Note |
|---|---|---|---|---|
| 6.4.1 | 2026-10-20 | revisions up to 6.4 (CEEx2 as two sockets) | 2026 J1A experiment, 2026-06-25 (310-2 island closes) | superseded by 6.4.2 |
| 6.4.2 | 2026-10-24 | 6.4.1 + 117-2 CEEx2 meters corrected (`CEEx2_2` is the Busbar A socket, found in the data) | **2026-06-25, all islands close** (319-3 island RMSE 0.22 kW at 1 min; scenario 6.4.2/j1a-2026 for the converter) | **behind** from 2026-08-13 (Boiler, 6.5) |

---

## Era 4, 2015-07-29 to 2023-06-16: switchboard 716-2 in operation (overview figure v4)

**Major change:** a new figure layout (v4, 2015-08-11) with building 716 (switchboard 716-2, Flexhouse 2 and 3, CHP, heat
pumps). 716-2 logs its own data files from 2015-07-29, a year before its configuration is committed (2016-07-12). The
configurations of the other switchboards enter the lab repository on 2015-08-03. 319-3 is configured on syslab-01 with
319-2 throughout. Busbars "Busbar 1/2"; on 319-2 "Grid"/"Local"; on 319-3 A/B/C.

| Revision | Entry | Date | Change | Seen in | Certainty |
|---|---|---|---|---|---|
| 4.0 | E4-001 | 2015-08-03 | First configuration in the lab repository: 117-2/4/5, 117-6, 319-2, 319-3, 715-2 | configuration | confirmed |
| 4.0 | E4-002 | 2015-07-29 | 716-2: Grid, CEE, CHP, Cable E1, E2, F1, Flexhouse2/3, Heatpump1/2 | data; figure v4; configuration 2016-07-12 | confirmed (data ahead of configuration) |
| 4.0 | E4-003 | 2015-08-03 | AirCon wind turbine on 319-2 (in the data since 2012; never on 715-2 in any configuration) | configuration, data | confirmed |
| 4.1 | E4-004 | 2016-06-14 | 319-3: cables E1/E2 to 716-2 swap busbars (E1 from Busbar A/B to A/C, E2 from A/C to A/B), the same kind of swap as 6.2 in 2024 | data 2016-06-14; configuration 2016-07 (master 2016-07-13); 716-2 "swapped interlock E1+E2" fixed 2016-09-19 | **uncertain** (C13) |
| 4.1 | E4-005 | 2016-07-12 | 715-2: Cable1/Cable2 named CableB1/CableB2, cable F1 to 716-2 added | configuration; data from 2015-08-05 | confirmed (data ahead of configuration) |
| - | E4-006 | 2016-11-30 | Figure v4 names EDISON bays Container, NEVIC bays EVSE, Solar PV (the configuration only in 2023) | figure | figure only |
| - | E4-007 | 2018-07-02 | Display program moves to syslab-userspace, keeps figure v4 | display | display only |

Nothing else changes in the configuration of era 4: seven years without a breaker change on master. Figure v5
(2023-01-12) was a draft of v6, never displayed, so there is no era 5.

Open in this era: what the cables were before the rebuild (single cables A1, A2, ... or already the pairs A1A/A1B the
2023 configuration names), with length and type; the equipment behind the bays (C14).

## Before 2015: eras known from the data files and the figures only

No configuration history exists before 2015, but the data files go back to 2009 and the lab repository keeps the older
figures (dated in their file names). Models of these eras could only be rebuilt from the column names of the data and the
figures, and would stay unverified until checked against measurements (C15).

| Era | From | Figure | Major change | Then |
|---|---|---|---|---|
| **3** | 2013-07-31 | v3 "wide-20130101" (displayed from 2012-10-30) | "Extension Jan2013": cables E1, E2 from 319-3 and F1 to building 716 (716-2 not logged before 2015) | E3-001 cables E1/E2 on 319-3 in the data from 2013-07-31 (figure dated 2013-01-01: **built when?**) |
| **2** | 2012-02-18 | v2 "wide-20120101" (from 2012-01-13; v1 of 2011-12-21 is its narrow predecessor) | switchboard 117-6 for the NEVIC charging posts; Aircon turbine in place of Bonus on 319-2 | 2.0 Aircon (2012-02-18); 2.1 Solar bays on 117-2 (2012-03-14) and 319-2 (2012-04-03); 2.2 117-6 (2012-05-03, breakers from 06-27) with its feeder on 117-4 (2012-07-07); 2.3 319-3 logged (2013-05-19); 117-2 stops logging Ext117-5 (2013-01-30, cable still drawn) |
| **0** | 2009-12-16 | unnumbered figure of 2009-11-01 ("the additional switchboards installed for EDISON") | the EDISON switchboards 117-2/4/5, 319-2, 715-2, the 319-3 crossbar switch | 319-2 and 715-2 logged from 2009-12-16, 117-2/4/5 from May 2011 |

There is no era 1: figure v1 was replaced by its wide-screen variant v2 within three weeks, before any change it shows
reached the data. Figures v2 to v4 also carry an operator's login name in their access-control layer; that layer is never
published.

---

*Open questions for the staff* (numbered C1 to C15, apart from the handout's six questions; "so far" notes what we already know):

C1. Will the 330-13 bay EVSE_12 be renamed Cable_Q1 in the configuration?
   *So far:* the model keeps `EVSE_12` until the configuration renames it (maintainer, 2026-10-21).
C2. Cable Q1: length and cable type? What is behind the 119-10 bays?
C3. When was 119-10 first powered and logging (a feature-branch configuration before 2026-10-05)?
C4. 330-12 Spare_6/7: given to a named unit?
   *So far:* spares can disappear when they are given to a named unit (maintainer, 2026-10-21).
C5. 319-3 E1/E2 (and C1/C2): which labels were right between December 2023 and September 2024?
   *So far:* flagged as uncertain, not corrected: no consistent ground truth (maintainer, 2026-10-21).
C6. 117-2 CEEx2: is `CEEx2_2` the Busbar A socket, as the 2026-06-25 data shows?
   *So far:* yes by the data: with the swap every island of 2026-06-25 closes (maintainer agreed, 2026-10-24).
C7. **When did era 6 start?** The data files of five switchboards use the rebuild names from 2023-06-16; the configuration
   was committed on 2023-06-23 (on master 2023-06-30). Was the rebuild in operation from 2023-06-16? If experiments ran in
   that week, they would get the era-6 model.
C8. **Data-name periods:** is it right to keep these apart from the configuration changes (the grid did not change, only
   the names in the data)? Do you recognise the reasons we give? Are there restarts or test configurations we should know
   about? The longest one: 319-2 and 319-3 logged the pre-rebuild names until 2023-11-30, five months into era 6.
   *So far:* lags and feature-branch periods are flagged, not corrected (maintainer, 2026-10-21); a node reads
   hardware.xml only at a restart.
C9. 319-3 ABB_Pri, March to September 2024: the data name its breaker's busbar "Grid_Distribution", a name in no
   committed configuration. Which busbar was it?
C10. 2023-09-27: for one day, 117-2 and 117-5 logged names that were committed only in October 2024. A test of the new
     configuration? Was anything connected differently that day?
C11. 2026-06-24: the meter names of 117-2, 117-4 and 319-2 changed on the same day. Were syslab-11 and syslab-01 restarted
     then? Is there a record of node restarts?
C12. The twelve entries found in round 3 (E6-014 to E6-025): which belong together as one configuration revision (for
     example the 117-5 changes of 2024-10-08 to 2024-10-14)?
C13. 2016-06-14: was the E1/E2 swap on 319-3 a rewiring, or a correction of names after the data showed them swapped?
     (The same question as for 2024.)
C14. Before the 2023 rebuild: were cables A1 ... F1 single cables or pairs, and what length and type? Which equipment
     (Machine set, Battery, EDISON 1-3, CHP, heat pumps, Flexhouses, Bonus/Aircon) was behind the bays?
C15. Eras 0 to 3 (2009-2015): are models for them worth rebuilding from the data names and figures alone? Which past
     experiments would need them? When did 716-2 go into operation, with which bays (2013-2015)?
     *So far:* the yearly experiments (June; November or March) are the candidate days (staff, 2026-10-30).
