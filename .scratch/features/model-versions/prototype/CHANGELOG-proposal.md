# SYSLAB grid: change log (PROTOTYPE, draft for the technical staff)

> Throwaway proposal for the ticket "What should a human-readable change log look like for the lab staff?", round 2
> (2026-10-23), aligned with the decisions of the map "dated model versions". Built by hand from the research of
> 2026-10-20/21 and the `syslab/conf` history. **Please correct anything that is wrong or missing**: strike out, add a line,
> write in the margin. The form itself is a proposal too.

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

## Era 6, 2023-06-23 to 2026-10-05: after the 2023 rebuild (overview figure v6)

**Major change:** the 2023 rebuild (busbars renamed A/B, "Solar" bays renamed PV, 319-3 on its own node). Figure v6 and the
display program changed on 2023-06-23, the configurations on 2023-06-14 (319-2) and 2023-06-23.

**Operational periods (commissioning period 2023)**

| Period | From | Switchboards in operation (in addition to 117-x, 319-2, 715-2, 716-2) | Note |
|---|---|---|---|
| 6-a | 2023-06-23 | 319-3 (node syslab-52) | rebuild; 319-3 left syslab-01 on 2023-04-13 |
| 6-b | 2023-07-02 | + 319-4 | |
| 6-c | 2023-10-06 | + 330-12, 330-13 (with the **Gaia** wind turbine on 330-12) | figure v6 "as-built 330-12/330-13" on 2023-10-05 |
| 6-d | 2023-10-19 | + 310-2 | figure v6 "final configuration of 310-2" the same day; end of commissioning |

Data files of the new switchboards start later: 319-4 2023-12-01, 330-13 2023-12-19, 330-12 2024-06-10, 310-2 2025-02-24.

**Configuration revisions**

| Revision | Entry | Date | Change | Seen in | Certainty |
|---|---|---|---|---|---|
| 6.0 | E6-001 ... | 2023-06-23 | The rebuild configuration (all switchboards above, by operational period) | configuration, figure v6, display | confirmed |
| 6.1 | E6-020 | 2023-11-14 | 117-6: NEVIC bays renamed EVSE (data files use EVSE from 2025-02-14) | configuration; data | confirmed (logging lag) |
| 6.2 | E6-021 | 2024-09-08 | 319-3: cables E1/E2 swapped in the configuration (as built differed from as planned; figure swapped C1/C2 and E1/E2 labels on 2024-06-19) | configuration, figure | **uncertain 2023-12-01 to 2024-09-07**: 319-3 E1/E2 breaker data may carry swapped names |
| 6.3 | E6-022 | 2024-10-14 | 117-2: second CEEx2 meter (two sockets, one per busbar) | configuration; data from 2026-06-24 | confirmed (logging lag) |
| 6.4 | E6-023 | 2026-06-15 | 319-2: second CEEx2 meter (two sockets, one per busbar) | configuration; data from 2026-06-24 | confirmed |
| 6.5 | E6-024 | 2026-08-13 | 310-2: bay Spare_1 renamed **Boiler** | configuration, figure v6, display (same day) | confirmed |

Also noted in this era, without a configuration revision: 330-12 Spare_6/7 no longer logged from 2026-04-19 (still in the
configuration; spare given to a unit?); 776-1 left the configuration on 2024-05-23 (node syslab-30 now runs EVSE18; not part
of the grid model); the rock store was cancelled.

**Model versions** (numbers illustrative until the first era file exists)

| Model | Published | Accommodates | Validated on | Note |
|---|---|---|---|---|
| 6.4.1 | 2026-10-20 | revisions up to 6.4 (CEEx2 as two sockets) | 2026 J1A experiment, 2026-06-25 (310-2 island closes) | **behind** from 2026-08-13 (Boiler, 6.5); the 319-3 island of 2026-06-25 does not close yet |

---

## Era 4, until the 2023 rebuild (overview figure v4)

| Entry | Date | Change | Seen in | Certainty |
|---|---|---|---|---|
| E4-001 | 2015-08-03 | First configuration in the lab repository: 117-2/4/5, 117-6, 319-2 and 319-3 (both on syslab-01), 715-2, 716-2 | configuration | confirmed |
| E4-002 | 2015-08-03 | AirCon wind turbine on 319-2 (never on 715-2 in any configuration since 2015) | configuration | confirmed |
| E4-003 | 2018-07-02 | Display program uses figure v4 (116 breakers on 8 switchboards, busbars "Busbar 1/2", on 319-2 "Grid"/"Local") | display, figure v4 | confirmed |

Figure v5 was never used by the display program.

## Before 2015

Not examined (first `hardware.xml` in the lab repository: 2015-08-03).

---

*Open questions for the staff:*

1. Will the 330-13 bay EVSE_12 be renamed Cable_Q1 in the configuration?
2. Cable Q1: length and cable type? What is behind the 119-10 bays?
3. When was 119-10 first powered and logging (a feature-branch configuration before 2026-10-05)?
4. 330-12 Spare_6/7: given to a named unit?
5. 319-3 E1/E2 (and C1/C2): which labels were right between December 2023 and September 2024?
6. 319-3: the breaker issue in the 2026-06-25 data (see the 319-3 island ticket).
