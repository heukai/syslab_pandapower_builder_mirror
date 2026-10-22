# SYSLAB grid: change log (PROTOTYPE, draft for the technical staff)

> Throwaway proposal for the ticket "What should a human-readable change log look like for the lab staff?".
> Built by hand from the research of 2026-10-20/21 (`research/source-inventory`, `research/figure-privacy`) and the
> v6 -> v7 comparison. **Please correct anything that is wrong or missing**: write in the margin, strike out, add a line.
> Newest first. One block per configuration era (named after the overview figure: E7, E7b, E8 ...); inside it, the
> changes of the era and the model versions published for it (7.1, 7.2 ...).

**How to read it**

- A **new era** opens only when `hardware.xml` brings a new switchboard (a new node), or when planned equipment becomes
  built. Renames, new bays and cables are changes *inside* an era. A new figure version is noted; it names the era.

- **Date** is the day the change entered `hardware.xml` (the lab's configuration), which is authoritative. Other sources
  (overview figure, display program, data files) are listed when they saw it, with their own date.
- **Certainty**: *confirmed* (configuration, figure and display agree), *config only*, *figure only*, *planned* (drawn
  greyed out, not built), *uncertain* (sources disagree or labels were mixed up for a while; not corrected).
- Names are the `hardware.xml` names. Where the figure or the display uses another name, it is shown in brackets.

---

## Planned, not built (would open era E7b, or E8 with a new figure)

| What | Seen in | Note |
|---|---|---|
| Switchboard **316-2** (bays PTX, P2XA, P2XB, Grid), **Cable M1** from 319-4 | figure v7 (greyed out), 2026-10-05 | Not in `hardware.xml`, not in the display program. |

## Era E7, from 2026-10-05: fast charger site 119-10 (overview figure v7)

Opened by: new switchboard 119-10 (node syslab-44) in `hardware.xml`.

**Model versions:** 7.1 *(to be built)*: 119-10 and Cable Q1; not validated yet.

**Changes:**

| Date | Switchboard | Change | Sources | Certainty |
|---|---|---|---|---|
| 2026-10-05 | **119-10** (new, node syslab-44) | New switchboard, Kempower fast charger: bays Battery 1-5, EVSE 12, Cable Q1, one busbar A | config, figure v7, display | confirmed |
| 2026-10-05 | 330-13 / 119-10 | New **Cable Q1** from 330-13 bay EVSE_12 to 119-10 bay Cable_Q1 | figure v7; cable data in the builder (declared) | confirmed |
| 2026-10-05 | 330-13 | Bay EVSE_12 is shown as "Cable_Q1" in the figure and display; `hardware.xml` still says EVSE_12 | display, figure | uncertain (may be renamed later) |
| 2026-10-05 | 117-2 / 117-5 | Figure labels "Ext. 117-2/117-5" now read "Cable X1/X2" (drawing only) | figure v7 | figure only |
| *pending* | 119-10 | First data file from the new node not yet checked (a node reads its configuration at restart) | data files | open |

## Era E6, 2023-06-23 to 2026-10-05: after the 2023 rebuild (overview figure v6)

Opened by: the 2023 rebuild (busbars A/B, PV), figure v6 and display program the same day.

**Model versions** (numbers illustrative):

| Model | Published | Accommodates | Validated on | Valid |
|---|---|---|---|---|
| 6.1 | 2026-10-13 | socket ports, equipment catalog | J1A inline converter test case, 2025-06-25 | the era |
| 6.2 | 2026-10-20 | CEEx2 bays as two sockets, one per busbar | 2026 J1A experiment, 2026-06-25 (310-2 island closes) | from 2026-06-15 (second CEEx2 meter on 319-2) |

Open in this era: the 319-3 island of 2026-06-25 does not close yet (being investigated).

**Changes:**

| Date | Switchboard | Change | Sources | Certainty |
|---|---|---|---|---|
| 2026-08-13 | 310-2 | Bay Spare_1 renamed **Boiler** | config, figure v6, display (same day) | confirmed |
| 2026-06-15 | 319-2 | Second meter on CEEx2 (one socket per busbar, each metered); data files from 2026-06-24 | config; data 2026-06-24 | confirmed (logging lag) |
| 2026-04-19 | 330-12 | Spare_6, Spare_7 no longer logged; still in `hardware.xml` | data files | uncertain (spare reallocated?) |
| 2024-10-25 | 117-4 | Naming fixes; manual D1 breaker drawn | figure v6 | figure only |
| 2024-10-14 | 117-2 | Second meter on CEEx2 (one socket per busbar, each metered); data files from 2026-06-24 | config; data 2026-06-24 | confirmed (logging lag) |
| 2024-09-08 | 319-3 | Cables E1/E2 swapped in the configuration (as built differed from as planned); figure swapped C1/C2 and E1/E2 labels on 2024-06-19 | config, figure | **uncertain 2023-12-01 to 2024-09-07**: E1/E2 breaker data of 319-3 may carry swapped names |
| 2023-11-14 | 117-6 | NEVIC bays renamed EVSE; data files use the new names from 2025-02-14 | config; data 2025-02-14 | confirmed (logging lag) |
| 2023-10-06 | 330-12 | **Gaia** wind turbine connected at 330-12 (drawn 2023-06-23; data from 2024-06-10) | config, figure v6, data | confirmed (dates differ by source) |
| 2023-06-23 | all | 2023 rebuild: busbars "Busbar 1/2" become A/B, "Solar" bays become PV, Gaia leaves 715-2; overview figure v6 and display program updated the same day | config, figure v6, display | confirmed |
| 2023-06-14 | 319-2 | 319-2 part of the rebuild | config | config only |
| 2023-04-13 | 319-2 / 319-3 | CEEx2 bay on 319-2; 319-3 moves from node syslab-01 to its own node | config | config only |

## Era E4, 2018 to 2023 (overview figure v4; figure v5 was never used)

**Changes:**

| Date | Switchboard | Change | Sources | Certainty |
|---|---|---|---|---|
| 2018-07-02 to 2020-06-23 | 8 switchboards, 116 breakers | Display program uses figure v4, busbars "Busbar 1/2" (319-2: "Grid"/"Local") | display, figure v4 | confirmed |
| since 2015-08-03 | 319-2 | AirCon wind turbine on 319-2 (never on 715-2 in any configuration since 2015) | config | confirmed |

## Before 2015

Not examined (first `hardware.xml` in the lab repository: 2015-08-03).

---

*Open questions for the staff:* Is the 330-13 bay EVSE_12 going to be renamed Cable_Q1? When was 119-10 first
powered and logged? Is the rock store gone for good? Were Spare_6/7 on 330-12 given to a named unit? Which E1/E2 labels
were right between December 2023 and September 2024?
