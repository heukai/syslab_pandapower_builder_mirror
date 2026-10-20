# Source inventory: what each source says, and since when (first pass)

Research for ticket `02-what-each-source-says-and-since-when.md` (map: `../map.md`). First pass, 2026-10-20, local files
only (no FTP, no network). Terms follow `syslab_data/CONTEXT.md`.

**Pending (second pass, after ticket 01):** the history of the switchboard overview SVG and of the Java code that maps its labels
to breakers (own repository, not accessible yet), and the history of `syslab-master-conf` (the local copy is a plain folder, no
`.git`, so every `hardware.xml` statement below is "as of the local snapshot", not dated).

Marking: **F** = fact, with the file/line or command that shows it. **I** = inference (my reading; to be confirmed by the
maintainer or the second pass).

Helper scripts used (throwaway, not committed; run with `python -I` from a temp folder):

- `archive_summary.py`: per device in `syslab_data/metadata/column_archive/*.json`, lists eras (`valid_from`, `valid_to`,
  `source_file`) and the bays (`P_<bay>[kW]`) and breaker columns (`BRK_*`) added/removed between eras.
- `hw_summary.py`: per `syslab-master-conf/conf/syslab-*/hardware.xml`, lists switchboards, busbars, bays, breakers with busbar,
  interlocks, instruments and XML comments.
- `svg_text.py` / `svg_pos.py`: extract visible `<text>` labels of the two SVGs, diff them, and compute absolute positions (with
  transforms) to find each label's neighbours. Ids are ignored.

---

## 1. Column archive (header eras) — `syslab_data/metadata/column_archive/*.json`

| Aspect | Finding |
|---|---|
| What it states | Per device: the ordered CSV column set of each **header era**. For switchboards this gives the **bays** (`P_<Bay>[kW]` etc.), the **breakers** and the **busbar** each breaker closes onto (`BRK_<Bay>_<Busbar>`). Nothing about cables (only cable *bays*), nothing about which asset is behind a bay, nothing about switchboards without logging. **F** (file structure; `column_archive/__init__.py`). |
| How versions are dated | `valid_from` / `valid_to` per era, taken from the date in the first file name with that header (`source_file`, e.g. `715_2_20230701.csv`, `.csv.N` = header change on that day; US-23). Dates are **day of the first file with the new header**, i.e. when the logging changed, not necessarily the physical change. **F** (JSON fields). Knowledge of the archive itself is dated by `syslab_data` git commits (`git log -- metadata/column_archive`: first 2026-04-04, last 2026-10-19). **F** |
| Reach | Switchboards 117_2, 117_4, 117_5, 117_6, 715_2, 716_2, 776_1 from **2019-11-20**; 319_2 from **2021-01-01**; 716_h1 from 2021-05-01; 319_3 from **2022-03-02**; 319_4 from 2023-12-01; 330_13 from 2023-12-19; 330_12 from 2024-06-10; 310_2 from 2025-02-24. Control points from 2019-01-01 (gaia1, genset1, load1, meteo1) or 2019-11-20. **F** (`archive_summary.py`). Whether the start dates are the first data on FTP or just where the scan started is not stated. **I**: for 319_3/319_4/330_x/310_2 the start is plausibly the commissioning of the switchboard's logging. |
| Naming | Three generations of breaker column names: (a) to 2023-06-30: `BRK_<Bay>_Busbar 1/2`, `_Grid/_Local` (319_2), `_SYSLAB/_Grid` (117_6), bays like `Solar`, `Cable1`, `CableB1`, `Ext117-5`; (b) 2023-07-01..: `Busbar A/B` with a space, bays `CableB1A`, `CEE1`, `Container1`; (c) from 2023-09-27/2023-10-19/2023-12-01: `Busbar_A/B`, bays `Cable_B1A`, `Container_1`, matching `hardware.xml` names. A per-device `aliases` map exists only in `319_2.json` (lines 5-16: `P_Solar[kW]` -> `P_PV[kW]`, `BRK_Solar_Grid` -> `BRK_PV_Busbar_A`, `BRK_Solar_Local` -> `BRK_PV_Busbar_B`). **F** |
| Quirks | Same-day eras where `valid_to` < `valid_from` (two headers for one day: `117_2`/`117_4`/`117_5` around 2023-09-27..2023-10-01, `715_2` 2023-10-19, `319_3` 2024-09-08): the two variants alternate, so the archive cannot say which header is "real" on those days. **F** (`archive_summary.py` lines for those devices). |

Switchboard eras with structural content (bays/breakers added, removed, moved to another busbar), all **F** from
`archive_summary.py` unless marked:

- **117_2:** 2019-11-20 `Grid, Battery, Machine, Ext117-5, Cable1, Cable2, Solar` -> 2023-07-01 `Machine, Cable1, Cable2,
  Solar, Ext117-5` gone; `CEEx2, CableX1, CableC1A..C2B, PV` appear -> 2023-09-27 `Grid` -> `Grid_2` (with `BRK_Grid_2_Grid`),
  four X bays `Cable_X1A_2..X2B_2` -> 2024-02-27 X bays merged as `Cable_X1_2` (A/B) -> 2024-10-09 four X bays again ->
  2026-06-24 `CEEx2` meter split into `CEEx2_1`, `CEEx2_2`.
- **117_4:** 2019-11-20 `Transformer, EDISON3, NEVIC` (Busbar 1) -> 2023-07-01 `Grid, Container3, CableH1` -> 2026-01-07
  `Cable_D1_Manual` breaker appears -> 2026-06-24 `Grid` -> `Grid_4`.
- **117_5:** 2019-11-20 `D1, Ext117-2, CEE, EDISON1, EDISON2, Chg post` -> 2023-07-01 `CableD1, CableX1, CEE1, Container1,
  Container2, CableG1` -> 2023-09-27 `Booster_Heater, Heatpump, CEEx1_2` added, `CEE1` -> `CEEx1_1`, X bays split ->
  2024-02-27 `CEE_1` only, heater/heat pump/CEE x1_2 gone, X merged -> 2024-10-09 `Booster_Heater, Heatpump, CEE_2` back ->
  2024-10-14 `CEE_1/CEE_2` -> `CEEx1_1/CEEx1_2`.
- **117_6:** `NEVIC1..8` with breakers `_SYSLAB`/`_Grid` -> 2025-02-14 `EVSE_01..08` with `Busbar_A`/`Busbar_B`.
- **319_2:** 2021-01-01 `Grid, Diesel, Dumpload, B2B, CEE, Aircon, Cable1, Cable2, Solar` (`_Grid`/`_Local`) -> 2023-12-01
  `B2B, Cable1, Cable2, Solar` gone; `CEEx2, Cable_A1A..A2B, PV` appear; Grid has one breaker `BRK_Grid_Busbar_B` ->
  2026-06-24 `CEEx2` meter split into `CEEx2.A`, `CEEx2.B`. `Aircon` is present in **every** 319_2 era.
- **319_3:** 2022-03-02 bays named by destination (`A1 to 319-2`, `B1 to 715-2`, `C1 to 117-2`, `E1 to 716-2`, `B2B-Ship`,
  `B2B-Shore`) -> 2023-12-01 `Cable_<X><n><A/B>` bays, `Grid`, `ABB_Sec` -> 2024-03-06 `ABB_Pri` meter -> 2024-03-07
  `BRK_ABB_Pri_Busbar_Grid_Distribution` -> 2024-09-08 Transformer busbar breakers `Supply, Spare, Amp_1, Amp_2` +
  `BRK_Grid_Busbar_Grid` -> 2024-09-08 (`.csv.2`) Cable E busbars swapped (E1 now A/B, E2 now A/C) -> 2024-10-03
  `BRK_ABB_Pri_Busbar_Supply` replaces `BRK_Grid_Busbar_Grid`. Cable C busbars also differ between 2022 (`C1` A/C, `C2` A/B)
  and 2023-12-01 (`C1A` A/B, `C2A` A/C).
- **319_4:** 2023-12-01 `BRK_MetaCross_*` (duplicate names) -> 2024-09-08 `BRK_Cross_A/B/C_*`. `P2X` bay present throughout.
- **330_12:** 2024-06-10 23 bays incl. `Gaia`, `Spare_1..7` -> 2026-04-19 `Spare_6`, `Spare_7` gone.
- **715_2:** 2019-11-20 `Grid, Gaia, Flexhouse, Solar, CableF1, CableB2, CableB1` -> 2023-07-01 `Gaia, Solar, CableB1,
  CableB2` gone; `Spare, PV, CableB1A/B, CableB2A/B` appear -> 2023-10-19 `Flexhouse` -> `Flexhouse_1`. No `Aircon` bay in
  any 715_2 era.
- **716_2:** 2019-11-20 `CEE, CableE1, Cable E2, Cable F1, Flexhouse2, Flexhouse3, Heatpump1, Heatpump2, CHP` -> 2023-07-01
  `Heatpump2, CHP` gone, `BoosterHeater` appears -> 2024-03-21 `Grid, PV, Spare_1..4`, cable bays split into
  `Cable_E1A..E2B`.
- **310_2** (one era from 2025-02-24, incl. `RockStorage`, `CHP`), **330_13** (one era from 2023-12-19, incl. `EVSE_12`),
  **776_1** (no breakers), **716_h1** (heat, no breakers; pump columns of bay 6 come and go).

## 2. Device registry — `syslab_data/metadata/devices.py`

| Aspect | Finding |
|---|---|
| What it states | Per device: node (`syslab-XX`), category, description, bay list (`measurement_prefixes`), optional `valid_from`/`valid_to` (none set). Asset links in `ASSET_CONNECTIONS` (lines 400-406): `pv319` -> 319_2 `PV` (data check), `pv330` -> 330_12 `PV_1`, `pvbatt2/3` -> 330_12 `PVBatt_2/3` (registry text). No cables, no busbars, no breakers. **F** |
| Dating | No dates in content: `valid_from/valid_to` fields exist but are unset for every device; `AssetConnection` validity unset for all four links. Only dating is the `syslab_data` git history (e.g. `3f6c51a` 2026-10-18 "Registry: AirCon is now on 319_2, formerly on 715_2"; `e118740` 2026-10-18 asset connections). **F** (`git log -- metadata/devices.py`) |
| Reach | Claims to describe the "post-2024 topology era" (comment lines 182-185), but mixes eras: **F** 319_2 bays (lines 225-229) are the **2021-2023** header names `B2B, Cable1, Cable2, Solar` without `CEEx2`/`Cable_A*`; 117_2 (lines 197-202) has `CEEx2` but not the 2026-06-24 `CEEx2_1/_2`; 117_4 has `Grid` not `Grid_4`; 330_12 lists `Spare_1..4` (no 5..7). Archive since 2026-04-19 still has `Spare_5`. |
| Naming | Bay names as in `hardware.xml`/current headers (underscore style), except 319_2. Devices named `<building>_<n>` (`319_2`), CPs by lowercase id (`pv319`, `gaia1`, `aircon`). |
| Statements on moves | `aircon` (lines 324-326): "now on 319_2 bay Aircon, formerly on 715_2; dates: US-50", node `syslab-25`. 117_6: "former syslab-27, now syslab-26" (line 215). **F** |

## 3. Builder curated YAML and git history — `syslab_pandapower_builder/data/`

| Aspect | Finding |
|---|---|
| What it states | `cables.yaml`: 33 cables (A..L, X; D1 single; G1/H1 land on 117-6 busbars, no bay there) with endpoints as bus names, length, cable type; source line 12 "SYSLAB campus cable installation records". `breaker_groups.yaml`: one group per switchboard (description, switch list, default state, `logged`, interlocks) plus the 319-3/319-4 Crossbar and 24 inline ports (lines 775-933). `converter_connections.yaml`: ABB B2B 319-3, Grid Emu B2B 319-3/319-4. `socket_meters.yaml` (2026-10-20): meter per socket port incl. the two CEEx2 sockets of 319-2 and 117-2. `equipment_catalog.yaml`: mobile loads, inline impedance, mobile converter (placeholders). `non_breaker_connections.yaml`: empty. **F** |
| Dating | Only git commit dates (knowledge dates, not physical dates). No per-entry validity. The published model carries one validity range: `syslab_pandapower/model_data/model_version.json` `valid_from: 2024-08-15`, `valid_to: null`, build 2026-10-20. **F** |
| Reach | Current configuration only. Git history 2026-03-30 (`517a364`) .. 2026-10-20 (`6aad0bc`), 20 commits. `cables.yaml` and `cable_types.yaml` unchanged since the initial commit (`git diff 517a364 HEAD --stat -- data/cables.yaml data/cable_types.yaml` is empty). **F** |
| Naming | Bus names `{sw}_{bay}` / `{sw}_Busbar-{letter}` with dash switchboard ids (`319-2_Cable_A1A`); switch names `{sw_underscore}_BRK_{bay}_Busbar_{X}` (`319_2_BRK_PV_Busbar_A`); socket ports `"319-2 CEEx2.A"`; cables `Cable A1A`. **F** |
| Changes in history | `517a364` (2026-03-30) had a non-breaker connection "Grid 319-3" -> `319-3_Busbar-Supply` citing `switchboard_overview_6.svg`; removed by `abb0f10` (2026-04-04). `ed45e16` (2026-04-05) adds the per-switchboard groups incl. `CEEx2` interlocks; `dc056cf` (2026-04-19) marks unlogged switches; `3d584c8` (2026-10-20) drops the CEEx2 `max_closed: 1` groups ("no basis in hardware.xml"); `c2c913f`..`a3ea12f` (2026-10-20) socket meters. **F** (`git show`) None of these is a physical change; all are corrections of knowledge. **I** |
| Model vs. its own validity | `valid_from 2024-08-15` predates header changes that the model already reflects (319_3 Transformer breakers 2024-09-08, `ABB_Pri` on Supply 2024-10-03, 117_5 `CEEx1_*` 2024-10-14, 117_6 EVSE 2025-02-14, 310_2 from 2025-02-24). **F** (dates) / **I** (the model is not valid from 2024-08-15). |

## 4. `hardware.xml` (local snapshot) — `syslab-master-conf/conf/syslab-XX/hardware.xml`

| Aspect | Finding |
|---|---|
| What it states | Per node: switchboard(s) with location, busbars, bays, breakers with busbar, interlocks, instruments (meters), PLC registers, instrument buses (IP). Assets only implicitly by bay name. No cables between switchboards. Non-switchboard nodes describe one device (`syslab-03` "Gaia turbine", `turbine name="gaia1"`, location "Test stand I"). **F** (`hw_summary.py`) |
| Dating | None in the files; no `.git` in `syslab-master-conf` (`Test-Path .git` = False). All files have mtime 2026-03-18 12:58 (copy time). **F** The snapshot is older than some header changes: it still has 330-12 `Spare_5..7` (syslab-50 lines 155-169) although the header dropped `Spare_6/7` on 2026-04-19, but it already has the `CEEx2_1/_2` instruments of 117-2 (syslab-11 lines 26-27) and `Grid_4` (lines 77-78) that the header shows only from 2026-06-24. **F** **I**: the snapshot is from about March 2026; the 2026-06-24 header changes on 117_2, 117_4 and 319_2 came from a logging-software deployment that started to use instrument names already in `hardware.xml`. |
| Reach | One version (the current one as of the snapshot). Some history survives in XML comments: 715-2 "NB: Real order" lists old bay names `CableB1, Gaia, Solar, CableB2, CableF1` (syslab-09 lines 11-18); 319-2 `Busbar_A` "old local busbar", `Busbar_B` "old grid busbar" (syslab-01 lines 7-8); 117-6 `Busbar_A` "old SYSLAB busbar", `Busbar_B` "old Grid busbar"; 117-4 "TODO: Rename D1_Manual to D1"; 319-4 "is called AMP on the Switchboard cabinet". **F** |
| Naming | `conf/_naming_conventions.txt`: underscore separates category and instance (`Cable_E1A`, `Busbar_A`), dash structures non-word sequences (`Cable_C1B-A`, `319-3A-4B`), CamelCaps for multi-word names (`BoosterHeater_1`, `PVBatt_2`). Breakers `<Bay>-<A/B/C>`; cross breakers `319-3A-4B`. **F** |
| Odd entries | 330-12 `location="Turbine hall (319)"` (syslab-50 line 7; it is in building 330 per registry/SVG). `syslab-25` is "Ship to shore", empty (line 3), but the registry gives `aircon` node `syslab-25`. **F** |

## 5. Switchboard overview SVG, versions 6 and 7 — `sample_data_SYSLAB-NAS/`

| Aspect | Finding |
|---|---|
| What it states | A drawing of all switchboards (buildings, switchboard ids, busbars, bays, transformer ratings, cables as labels such as `Cable A1` with sub-labels `A1.A`, `A1.B`) and a legend. Only visible text carries meaning. It shows switchboards that no other source has. **F** |
| Dating | No content date. `inkscape:version` line 8: v6 "1.3.2 (091e20ef0f, 2023-11-25, custom)", v7 "1.4.4 (dcaf3e7d9e, 2026-05-05)"; `sodipodi:docname` `switchboard_overview_6.svg` / `_7.svg`. **F** **I**: these are Inkscape build dates, so v6 was last saved on or after 2023-11-25 and v7 on or after 2026-05-05 (lower bounds only). File mtimes (2026-03-16 / 2026-10-19) are download times. Minor versions (git) are pending. |
| Reach | Two snapshots. v6 still labels 117-2/117-5 cable bays `Ext. 117-5`/`Ext. 117-2`, names gone from the headers since 2023-07-01, so the drawing can lag the lab. **F**/**I** |
| Naming | Spaces instead of underscores (`Cable A1`, `EVSE 1`, `Container 1`, `CEE x2`), one cable label per pair with `.A/.B` sub-labels, short forms (`HP 1`, `Emu`, `PTX`, `Rock store`), `Flexhouse` for `Flexhouse_1`, `EVSE 1` for `EVSE_01`. **F** (`svg_text.py`) |

Label differences v6 -> v7 (**F** from `svg_text.py`; placement from `svg_pos.py`):

| v6 only | v7 only | Where (neighbouring labels in v7) |
|---|---|---|
| — | `316-2`, `Building 316`, `P2XA`, `P2XB`, `Grid` (+1), `CableM1` (x2) | new switchboard 316-2 with busbars A/B; second `CableM1` sits on 319-4 next to `GridEmulator`, `CableK1` |
| `P2X` (319-4, between `Spare 2` and `K1.A`) | — | 319-4 now has `CableM1` instead |
| `Spare` (319-3 Transformer busbar, next to `Amp 2`) | `PTX` (319-3 Transformer row, under `Building 316`) | |
| — | `119-10`, `Fast charger site`, `Battery 1..5`, `Cable Q1` (x2) | new switchboard 119-10; one `Cable Q1` on 330-13 at the x position where v6 had `EVSE 12`; `EVSE 12` now next to 119-10 |
| `Ext. 117-5`, `Ext. 117-2` | `Cable X1`, `Cable X2` | 117-2 / 117-5 |
| `Rock store` (310-2) | `Boiler` (310-2) | `Spare 1` also changed position on 310-2 |
| `PV 2/Bat`, `PV 3/Bat` | `PV 2/Batt`, `PV 3/Batt` | 330-12; `Spare 1` moved from between `Demolab 2`/`Gaia` to after `Cable K2` |
| `No data /Out of use` | `Noconnection`, `Nodata` | legend |

## 6. Context documents (not sources of configuration, but of declared facts)

- US-50 (`syslab_data/user_stories.md` line 461): "the AirCon wind turbine was at 715_2 and is now at 319_2; the Gaia turbine
  moved too", "between 2022 and 2024 there were major changes". Aliases `Solar` -> `PV`, `Busbar 1` -> `Busbar_A`. **F**
- ADR-0005 repeats "AirCon from 715_2 to 319_2" as an example. ADR-0002: `hardware.xml` authoritative for breakers/bays,
  curated YAML for cables. ADR-0004: CEE bays are socket ports. **F**
- None of these give a date for any move. **F**

---

## 7. Known configuration changes, by source

Legend: date = first day a source shows the new state; "—" = source silent; "agrees"/"disagrees" refers to the current state.

| Change | Column archive | Registry | Builder YAML (git) | hardware.xml (snapshot) | SVG 6 / 7 | Verdict |
|---|---|---|---|---|---|---|
| **AirCon 715_2 -> 319_2** | 319_2 has `Aircon` in every era since 2021-01-01; 715_2 has no `Aircon` bay since 2019-11-20 (**F**) | "formerly on 715_2", no date (declared 2026-10-18, `3f6c51a`) | 319-2 only | 319-2 bay `Aircon` (syslab-01 line 42) | 319-2 in both | Current state agrees everywhere. The move itself is **not visible** in any local source: either before 2019-11-20 for 715_2 / 2021-01-01 for 319_2, or AirCon fed 715_2 through a bay with another name (e.g. `Gaia`, `Solar`) (**I**). Open; needs declaration or flow-partner evidence. |
| **Gaia 715_2 -> 330_12** | 715_2 `Gaia` bay until 2023-06-30, `Spare` from 2023-07-01; 330_12 `Gaia` from its first file 2024-06-10; `gaia1` CP continuous since 2019-01-01 (**F**) | 330_12 bay `Gaia`, no asset link for `gaia1` | 330-12 `Gaia` | 330-12 `Gaia` (syslab-50 line 106); 715-2 comment keeps `Gaia` in "Real order" (syslab-09 line 15) | 330-12 in both | Agree on the current state. Bay gone from 715_2 header on 2023-07-01; arrival on 330_12 dated only by the start of 330_12 logging (2024-06-10). Gap 2023-07 .. 2024-06 unknown (**I**: the turbine may not have been connected). |
| **Solar -> PV (319_2, 715_2, 117_2)** | 715_2 and 117_2: `Solar` -> `PV` on 2023-07-01; 319_2 on 2023-12-01; alias map only for 319_2 (**F**) | 319_2 still `Solar`; 715_2/117_2 `PV` | `PV` | `PV` | `PV` | Rename (same bay). Registry 319_2 is stale. |
| **319_2 busbars `Grid`/`Local` -> `Busbar_B`/`Busbar_A`** | 2023-12-01; alias map says `BRK_Solar_Grid` -> `Busbar_A`, `BRK_Solar_Local` -> `Busbar_B` (`319_2.json` lines 14-15) | — | Grid only on Busbar-B | `Busbar_A` "old local", `Busbar_B` "old grid" (syslab-01 lines 7-8) | — | **Disagreement:** the archive alias maps Grid->A, `hardware.xml` says Grid->B (and the Grid bay has only `Grid-B`). **I**: the alias in `319_2.json` is swapped. |
| **Busbar 1/2 -> A/B, SYSLAB/Grid -> A/B** | 2023-07-01 (117_x, 715_2, 716_2), 2025-02-14 (117_6) (**F**) | — | — | 117-6 comments: A = old SYSLAB, B = old Grid | — | Mapping 1->A, 2->B is assumed by US-50, not stated by any source (**I**). |
| **CEEx2 bays with two sockets** (319-2, 117-2) | 117_2 `CEEx2` from 2023-07-01, split `CEEx2_1/_2` on 2026-06-24; 319_2 `CEEx2` from 2023-12-01, split `CEEx2.A/.B` on 2026-06-24 (**F**) | 117_2 `CEEx2` (single), 319_2 none | Interlock `max_closed: 1` from `ed45e16` (2026-04-05) to `3d584c8` (2026-10-20); two sockets declared 2026-10-20 (`socket_meters.yaml`) | No interlock on either CEEx2 bay; 117-2 two instruments `CEEx2_1/_2`, 319-2 one instrument `CEEx2` (syslab-01 line 32) | one `CEE x2` label each, both versions | Two breakers without interlock agree since the first header. Meter split dated 2026-06-24 by headers; 319-2 meter split **not** in `hardware.xml` snapshot (disagreement, or the snapshot predates it). Physical date of the second socket/meter unknown. |
| **SVG 7: switchboard 316-2 + Cable M1; P2X leaves 319-4** | 319_4 `P2X` bay in all eras, nothing on 316-2 (**F**) | — | 319-4 `P2X`, no 316-2 | 319-4 `P2X` (syslab-52 line 200), no 316-2 | v6: 319-4 `P2X`; v7: 316-2 with `P2XA`, `P2XB`, `Grid`, `CableM1`; 319-4 `CableM1` instead of `P2X` | Only SVG 7 shows it. **I**: P2X moved to new switchboard 316-2, fed by Cable M1 from the former 319-4 P2X bay; dated between v6 (>= 2023-11-25) and v7 (>= 2026-05-05), and after the last archive refresh of 319_4 (no new 319_4 era seen). |
| **SVG 7: 319-3 `Spare` -> `PTX`** | 319_3 `BRK_Spare_Busbar_Transformer` from 2024-09-08, still current | 319_3 bay `Spare` | `319_3_BRK_Spare_Busbar_Transformer` (`breaker_groups.yaml` line 134) | 319-3 bay `Spare` (syslab-52 line 21) | v6 `Spare`, v7 `PTX` | **I**: the Transformer-busbar spare now feeds P2X/316-2 (`PTX`, drawn under `Building 316`). Rename or new use; SVG only. |
| **SVG 7: switchboard 119-10 + Cable Q1; EVSE 12 leaves 330-13** | 330_13 `EVSE_12` current since 2023-12-19 (**F**) | 330_13 `EVSE_12` | 330-13 `EVSE_12` | 330-13 `EVSE_12` (syslab-51 line 33) | v6: `EVSE 12` on 330-13; v7: `Cable Q1` in that position, 119-10 "Fast charger site" with `Battery 1..5`, `EVSE 12`, `Cable Q1` | Only SVG 7. **I**: the 330-13 EVSE_12 bay now feeds Cable Q1 to 119-10. Map: "exist but are in neither hardware.xml nor the model". |
| **117-2/117-5 `Ext.` -> Cable X** | `Ext117-5`/`Ext117-2` breakers until 2023-06-30; `CableX1` 2023-07-01; four X bays 2023-09-27, merged 2024-02-27, split 2024-10-09 (**F**) | four X bays per side | four X cables in `cables.yaml` | four single-breaker X bays per side, no instruments | v6 `Ext. 117-5/-2` (stale), v7 `Cable X1`, `Cable X2` | Agree on current; SVG 6 lagged the headers by at least 5 months. 2024-02-27..2024-10-08 header era with merged X bays is unexplained (**I**: logging config, not wiring). |
| **310-2 `Rock store` -> `Boiler`** | `RockStorage` (only era, from 2025-02-24) | `RockStorage` | `RockStorage` | `RockStorage` (syslab-53 line 49) | v6 `Rock store`, v7 `Boiler`, and `Spare 1` moved | Only SVG 7. **I**: either the RockStorage bay was renamed Boiler, or the Spare_1 bay now serves a boiler and RockStorage became spare (positions favour the second). |
| **330-12 `Spare_6/7` removed** | 2026-04-19 (**F**; `Spare_5` stays) | `Spare_1..4` | `Spare_1..7` (`breaker_groups.yaml` lines 568-574) | `Spare_1..7` | `Spare 1..4` in both | Disagree; `hardware.xml` snapshot predates the change. SVG never drew 5..7. |
| **117_5 CEE bays** | `CEE` -> `CEE1` (2023-07-01) -> `CEEx1_1`+`CEEx1_2` (2023-09-27) -> `CEE_1` (2024-02-27) -> `CEE_1/_2` (2024-10-09) -> `CEEx1_1/_2` (2024-10-14) | `CEEx1_1/_2` | sockets `117-5 CEEx1_1/_2` | `CEEx1_1/_2` | `CEE 1`, `CEE 2` | Agree on current. Several header eras within a year (**I**: mostly renames). |
| **319_3 cable busbar assignments** | Cable C pair busbars swap between 2022-03-02 and 2023-12-01; Cable E pair swaps on 2024-09-08 (`.csv.2`) (**F**) | — | follows hardware.xml | E1A/E1B on A/B, E2A/E2B on A/C, C1 on A/B, C2 on A/C — matches the latest header | not resolvable from labels | Physical rewiring or relabelling; to be checked with staff (**I**). |
| **319_3 Transformer busbar, ABB_Pri** | `ABB_Pri` 2024-03-06; on `Grid_Distribution` 2024-03-07; Transformer breakers 2024-09-08; `ABB_Pri` on `Supply` 2024-10-03 (**F**) | `Transformer, Supply, Spare, Amp_1, Amp_2, ABB_Pri` | ABB B2B in `converter_connections.yaml` | `ABB_Pri-Grid@Busbar_Supply` | `ABBPri`, `Supply`, `Transformer`, `Amp 1/2` in both | Agree on current; history only in headers. |
| **117_6 NEVIC -> EVSE** | 2025-02-14 (**F**) | EVSE_01..08; node syslab-27 -> syslab-26 | EVSE, unlogged | EVSE_01..08 | `EVSE 1..8` | Agree; rename + busbar rename (A = old SYSLAB, B = old Grid). |
| **716_2 rebuild** | `Heatpump2`, `CHP` gone 2023-07-01; `Grid`, `PV`, `Spare_1..4`, split E cables 2024-03-21 (**F**) | current list | current | current | current | Agree on current. **I**: CHP reappears on 310_2 (from 2025-02-24): possibly a move. |
| **New switchboards** | 319_3 2022-03-02, 319_4 2023-12-01, 330_13 2023-12-19, 330_12 2024-06-10, 310_2 2025-02-24 (first header) | no dates | no dates | no dates | v6 has all of them | Header start is the only date; **I**: commissioning may be earlier. |

## 8. Open gaps

1. **No local source dates the AirCon move**, and the column archive contradicts "formerly on 715_2" for 2019-11-20 onwards
   unless AirCon used a differently named bay. Needs the maintainer's declaration or a flow-partner check (US-43) on 715_2
   `Gaia`/`Solar` against an AirCon signal (there is no AirCon CP data; `syslab-25` is "Ship to shore").
2. **`hardware.xml` is undated**: the second pass (git history of `syslab-master-conf`) is needed to date every bay/instrument
   change and to settle whether 316-2, 119-10, Cable Q1/M1, PTX and Boiler are in a newer `hardware.xml`.
3. **SVG minor versions** and the Java label-to-breaker mapping (pending, ticket 01) would narrow the 316-2/119-10 dates, which
   now lie only between >= 2023-11-25 and >= 2026-05-05.
4. **Header era vs. physical change:** a header era date is when logging changed. The 2023-07-01 changes hit five switchboards on
   one day and the 2026-06-24 changes three, which looks like software deployments (**I**). Each physical change needs a
   second source.
5. **The 319_2 alias** (`Grid` -> `Busbar_A`) contradicts `hardware.xml` comments; fix or confirm before eras are built on it.
6. **Registry is stale** for 319_2 (old bay list), 117_2/117_4 (pre-2026-06-24 names) and 330_12 (spares); `valid_from/to`
   unset everywhere.
7. **Model validity claim** (`valid_from 2024-08-15`) is earlier than at least five later header eras the model reflects.
8. Pre-2021 319_2 and pre-2022 319_3 data are not in the archive (the archive does not say whether files exist).

---

## Second pass (lab repositories)

2026-10-21, after ticket 01. Sources, both read-only (only `git log`, `git show`, file reads; nothing committed, branched or
configured there):

- `syslab/` at `0760fc29b` (2026-10-15): `conf/syslab-XX/hardware.xml`, 148 commits from `affe00650` (2015-08-03) to
  `7c4a820a2` (2026-10-05).
- `syslab-userspace/` at its 2026-10-05 head: `src/main/resources/media/svg/switchboard_overview_4..7.svg` and
  `src/main/java/risoe/syslab/gui/wall/displets/switchboard/SwitchboardsOverviewDisplet.java` (40 commits, 2018-07-02 to
  2026-10-05).

Commits are cited by hash and date only. Marking as in the first pass (**F** fact with hash/file, **I** inference).

Helper scripts (throwaway, not committed; run with `python -I` from a temp folder):

- `hwhist.py`: for every commit touching `conf/*/hardware.xml`, parses the new and parent version (XML comments stripped,
  regex, tolerant of malformed files) into switchboards, busbars, bays, breakers with busbar, interlocks and instruments, and
  prints what was added and removed.
- `svghist.py`: for every commit of `switchboard_overview_{4,5,6,7}.svg`, extracts the visible `<text>` labels (tspans
  joined, ids ignored) and diffs the label multiset against the previous version; also compares two given versions, or a local
  file against a commit.

### S2.1 Which node is which switchboard (`syslab` HEAD `0760fc29b`)

Switchboard nodes (**F**, device name and `<switchboard name>` at HEAD; first/last commit touching the node's `hardware.xml`):

| Node | Switchboard(s) | First `hardware.xml` | Last change |
|---|---|---|---|
| syslab-01 | 319-2 (until `196774659` 2023-04-13 also 319-3) | `affe00650` 2015-08-03 | `dfb7b96c1` 2026-06-15 |
| syslab-09 | 715-2 | `affe00650` 2015-08-03 | `c4b552870` 2025-01-17 |
| syslab-11 | 117-2, 117-4, 117-5 | `affe00650` 2015-08-03 | `9137e426b` 2026-01-08 |
| syslab-26 | 117-6 (device "NEVIC substation" until `d2aff19b5` 2023-11-14) | `affe00650` 2015-08-03 | `01c9f0bfc` 2025-02-07 |
| syslab-29 | 716-2 | `f9d699cd5` 2016-07-12 | `9309c12f8` 2025-02-05 |
| syslab-30 | 776-1 until `da0e6a9a3` 2024-05-23, then only "EVSE_18" (no switchboard) | `affe00650` 2015-08-03 | `bbc65ecc7` 2024-05-26 |
| syslab-44 | **119-10** (one busbar `Busbar_A`; bays `Cable_Q1`, `Battery_1..5`, `EVSE_12`; one breaker per bay, no interlocks) | `7c4a820a2` 2026-10-05 | same |
| syslab-50 | 330-12 | `cf92b2f15` 2023-10-06 | `4423b8677` 2025-09-12 |
| syslab-51 | 330-13 | `317257c1e` 2023-10-06 | `1835c442a` 2025-02-07 |
| syslab-52 | 319-3 and 319-4 (device name "Substation 319-2" until `74959b439` 2024-10-03, a copy slip) | `ebb1fb939` 2023-06-23 | `bb934bf48` 2025-01-28 |
| syslab-53 | 310-2 | `92ce040cb` 2023-10-19 | `627b0011c` 2026-08-13 |

Other nodes relevant to configuration (**F**): syslab-03 "Gaia turbine", syslab-24 "PV 319" (location "Aircon hut"),
syslab-25 "Ship to shore" (empty since 2015), syslab-27 "Flexhouse 3", syslab-33 716-h1 (heat), and the 2026 additions
syslab-32 "Booster heater" (`589e7f702` 2026-04-24, a load in building 716, **not** a switchboard), syslab-34/42/43 heat dump
loads (2026-09-13), syslab-40 "EVSE_06" (2026-09-10), syslab-41 "boiler-310" (2026-09-14), syslab-60 "HeatNetwork"
(2026-09-12), syslab-61 "330-D" heat substation (2026-09-16).

- **316-2**: in **no** `hardware.xml`, at any commit (`grep` of `conf/` for `316-2`, `PTX`, `P2XA`, `Cable_M1`: no hit), and
  not in the Java displet. It exists only in SVG v7. 319-4 still has bay `P2X` (A/C, interlocked) at HEAD. **F**
- **119-10 and Cable Q1**: node syslab-44, added `7c4a820a2` 2026-10-05; the 330-13 end of Cable Q1 is **not** in
  `hardware.xml`: syslab-51 still has bay `EVSE_12` (A/B) at HEAD, so `EVSE_12` is now a bay on both 330-13 and 119-10. **F**
- The registry note "117-6: former syslab-27, now syslab-26" (first pass, section 2) is contradicted: 117-6 has been on
  syslab-26 since 2015-08-03 and syslab-27 is "Flexhouse 3". **F**

### S2.2 The plain copy in `syslab-master-conf/` versus the repository

Each copied `hardware.xml` was matched (line endings ignored) against the history of its node (**F**):

| Node | Copy equals commit | Repo changes missing from the copy |
|---|---|---|
| syslab-01 (319-2) | `98c670a16` 2025-01-29 | `dfb7b96c1` 2026-06-15: instrument `CEEx2` split into `CEEx2.A`, `CEEx2.B` |
| syslab-11 (117-2/4/5) | `9137e426b` 2026-01-08 (= HEAD) | none |
| syslab-33 (716-h1) | `d9b8d5e3f` 2025-03-13 | `9a7760ff1` 2026-04-08: pumps and heat meters removed from the driver |
| syslab-53 (310-2) | `32f7454e9` 2025-02-03 | `627b0011c` 2026-08-13: bay `Spare_1` renamed `Boiler` |
| syslab-50, -52 | HEAD | none |
| repo only | — | syslab-32, -34, -40, -41, -42, -43, **-44 (119-10)**, -60, -61 (the copy has a `syslab-32` folder with `software.xml` only) |

So the copy is the repository state of some day between 2026-01-08 and 2026-04-07 (**F**, from the two bounding commits),
consistent with the file times of 2026-03-18 (first pass). Ticket 01 lists four differing files; the eight further repo-only
nodes (2026-09/10 additions) were missed there, probably because they were added after its comparison (**I**). For switchboards
the copy lacks: 319-2 `CEEx2.A/.B`, 310-2 `Boiler`, and 119-10.

### S2.3 Dated `hardware.xml` changes to switchboards

From `hwhist.py` (**F** for what changed; the date is the commit date, i.e. when the change was recorded in the repository).
Commits that changed only addresses, CT factors, PLC registers or formats are left out unless noted.

| Date | Commit | Switchboard | Structural change |
|---|---|---|---|
| 2015-08-03 | `affe00650` | all of 2015 | First state: 319-2 busbars `Grid`/`Local`, bays `Grid` (one breaker on `Grid`), `Diesel, Dumpload, B2B, CEE, Aircon, Cable1, Cable2, Solar`; 319-3 on syslab-01 with bays by destination (`C1 to 117-2` A/C, `C2 to 117-2` A/B, `E1 to 716-2` A/B, `E2 to 716-2` A/C, `B2B-Ship`, `B2B-Shore`, ...); 715-2 `Grid, Cable1, Flexhouse, Gaia, Solar, Cable2` on `Busbar 1/2` (+`Grid` busbar); 117-2 `Grid, Battery, Machine, Ext117-5, Cable1, Cable2, Solar`; 117-4 `Transformer, EDISON3, NEVIC`; 117-5 `D1, Ext117-2, CEE, EDISON1, EDISON2, Chg post`; 117-6 `NEVIC1..8` on `SYSLAB`/`Grid`; 776-1. |
| 2018-01-19 | `740c6a103` | 776-1 | bays `ChgPost 1/2` removed |
| 2021-04-14 | `86b170567` | 117-2 | Grid interlock removed |
| 2023-03-13 | `29e3f21a0` | 715-2 | bay `Flexhouse` -> `Spare` (format change commit) |
| 2023-04-13 | `196774659` | 319-2 | `B2B`, `Cable1`, `Cable2` removed; `CEEx2` (two breakers, **no interlock**), `CableA1`, `CableA2` added; 319-3 removed from syslab-01 |
| 2023-06-14 | `86f2e627d` | 319-2 | "new (tested)" config: busbars `Grid`/`Local` -> `Busbar A`/`Busbar B`; bay `Grid` breaker moves from busbar `Grid` to **`Busbar B`** (`Grid-B`); `Solar` -> `PV`; cable bays split `CableA1A..A2B`; comments "Busbar_A old local busbar", "Busbar_B old grid busbar" added |
| 2023-06-23 | `ebb1fb939` | 715-2, 117-2/4/5, 716-2, 319-3 | "after lab rebuild": `Busbar 1/2` -> `Busbar A/B` everywhere; 715-2 `Gaia`, `Solar` gone, `PV`, `Flexhouse` (back), `CableB1A..B2B` added; 117-2 `Machine, Ext117-5, Cable1/2, Solar` gone, `CEEx2` (no interlock), `CableC1A..C2B`, `CableX1`, `PV` added; 117-4 -> `Grid, Container3, CableH1`; 117-5 -> `CableD1, CableX1, CEE1, Container1/2, CableG1`; 716-2 `CHP`, `Heatpump2` gone, `BoosterHeater` added (`Cable E2`, `Cable F1`, `Flexhouse3` renamed without space); 319-3 on syslab-52 with `Cable_<X><n><A/B>` bays: C1A/C1B on A/B, C2A/C2B on A/C, **E1A/E1B on A/C, E2A/E2B on A/B** |
| 2023-07-02 | `e15deb9cc` | 319-4 | first config (J, K cables, `GridEmu`, `P2X`, `MetaCross`) |
| 2023-08-11 | `d916a0c14` | 319-4 | interlock fixes: `P2X` B/C -> A/C, `Cable_K2B` |
| 2023-08-13 | `f3e088dc7` | 715-2 | naming convention (`Cable_B1A`, `Flexhouse_1`, `Busbar_A`) |
| 2023-10-06 | `cf92b2f15` | 330-12 | first config: 23 bays incl. **`Gaia`**, `Spare_1..7` |
| 2023-10-06 | `317257c1e` | 330-13 | first config: `Grid, Cable_L1, EVSE_11..18` (A/B) |
| 2023-10-19 | `92ce040cb` | 310-2 | first config: incl. `RockStorage`, `CHP`, `Spare_1..3` |
| 2023-10-19..23 | `6e24ea334`, `2c865897f`, `34004a2e3`, `2a54a1449` | 319-4, 330-12, 319-2, 117-x | naming convention renames only |
| 2023-10-27 | `20271a203` | 716-2 | rebuild: `Grid`, `PV`, `HeatPump`, `Spare_1..4`, `Cable_E1A..E2B`, `Flexhouse_2/3` |
| 2023-10-31 | `a61c8f814` | 117-2, 117-4, 117-5 | `Grid` -> `Grid_2` (117-2), instrument `Grid_4` (117-4), `Cable_X1` -> `Cable_X1_2` / `Cable_X1_5` |
| 2023-11-14 | `a6107864b` | 117-6 | `NEVIC1..8` on `SYSLAB`/`Grid` -> `EVSE_01..08` on `Busbar_A`/`Busbar_B`; NEVIC interlocks dropped |
| 2024-05-23 | `da0e6a9a3` | 776-1 | switchboard removed from syslab-30 (node now controls EVSE_18) |
| 2024-06-19 | `58404461b` | 319-3 | after an instrument check: `ABB_Pri` bay on new busbar `Busbar_Grid` |
| 2024-09-08 | `b736d2d87` | 319-3, 319-4 | "adapting to reality": `Busbar_Transformer` with `Supply, Spare, Amp_1, Amp_2, Transformer`; **E1A/E1B now A/B, E2A/E2B now A/C** (swap); 319-4 `MetaCross` -> `Cross_A/B/C` |
| 2024-10-03 | `74959b439` | 319-3 | "swapped breakers": `ABB_Pri` on `Busbar_Supply` (busbar `Busbar_Grid` -> `Busbar_Supply`) |
| 2024-10-08 | `69de9a862` | 117-5 | `Booster_Heater`, `Heatpump`, `CEE_2` added |
| 2024-10-09 | `777e5f1a4` | 117-2, 117-5 | X cables: one two-breaker bay -> four one-breaker bays per side (`Cable_X1A_2`, ... A or B only) |
| 2024-10-14 | `a96c88172` | 117-2, 117-5 | 117-2 `CEEx2` instrument -> `CEEx2_1`, `CEEx2_2`; 117-5 `CEE_1/_2` -> `CEEx1_1/_2` |
| 2026-01-07 | `5e50ea348` | 117-4 | `Cable_D1_Manual` (feedback-only breaker) added |
| 2026-06-15 | `dfb7b96c1` | 319-2 | `CEEx2` instrument -> `CEEx2.A`, `CEEx2.B` ("not sure why it was missing") |
| 2026-08-13 | `627b0011c` | 310-2 | bay `Spare_1` -> `Boiler` (`RockStorage` stays) |
| 2026-10-05 | `7c4a820a2` | 119-10 | new switchboard (see S2.1) |

Never in `hardware.xml` (**F**): an interlock on either `CEEx2` bay (no `IL CEEx2` in any version); an `Aircon` bay on 715-2
(715-2 bays in 2015: `Grid, Cable1, Flexhouse, Gaia, Solar, Cable2`); removal of 330-12 `Spare_6/7` (still at HEAD);
316-2, `PTX`, `Cable_M1`.

### S2.4 Figure and Java history (`syslab-userspace`)

Figures (**F**, `svghist.py` and `git log --name-status`):

| File | Commits | Notes |
|---|---|---|
| `switchboard_overview_4.svg` | `90b0511` 2018-12-11 .. `1a9066b` 2021-09-18 | pre-rebuild; 715-2 busbar label fix 2019-04-17; busbar labels and transformer ratings 2021-09-18 |
| `switchboard_overview_5.svg` | `c2047c6` 2023-06-23 only | same as v6 except legend "Out of service" |
| `switchboard_overview_6.svg` | `c2047c6` 2023-06-23 .. `9c29ae3` 2026-08-13 (11 commits) | the post-rebuild figure; displayed until 2026-10-05 |
| `switchboard_overview_7.svg` | `910fb87`, `c32720d`, `7979a0f`, all 2026-10-05 | `c32720d` switches the displet to v7 |

The local samples are exact repository versions (line endings ignored, md5): `switchboard_overview_6(1).svg` = v6 at
`0ecd4ea` (2024-10-25), so it is the v6 state valid 2024-10-25 .. 2026-08-12; `switchboard_overview_7.svg` = v7 at `7979a0f`
(2026-10-05, current). **F** The Inkscape-version lower bounds of the first pass are superseded by these commit dates.

Label changes over the v6 history (**F**): 2023-10-05 `a503581` 330-12/330-13 as built (+`Cable L1`, `Grid`); 2023-10-19
`b6656a1` 310-2 final configuration (no label change); 2023-10-31 `01de4af` 716-2 (`HP 1`, `Spare`, two `Grid` -> `Heat pump`,
`Spare 1`, `Spare 2`); 2024-06-19 `7c64e9a` C1/C2 and E1/E2 labels swapped ("as-built deviated from as-planned"; the label
multiset is unchanged, labels moved); 2024-09-08 `21412bd` 319-3 supply side (+`Amp 1`, `Amp 2`, `Spare`, `Supply`,
`Transformer`); 2024-10-03 `667a306` (+`ABB Pri`, `Supply`); 2024-10-25 `0ecd4ea` (+`Cable D1` on 117-4); 2026-08-13 `9c29ae3`
one `Spare 1` -> `Boiler` (310-2), legend text, `Building 319`.

v6 at `9c29ae3` -> v7 at `910fb87` (**F**): removed `Ext. 117-2`, `Ext. 117-5`, `P2X`, `PV 2/Bat`, `PV 3/Bat`, `Rock store`,
one `Spare`, legend; added `316-2`, `Building 316`, `P2XA`, `P2XB`, `Grid`, two `Busbar A` + one `Busbar B`, `Cable M1` (x2),
`PTX`, `119-10`, `Fast charger site`, `Battery 1..5`, `Cable Q1` (x2), `Cable X1`, `Cable X2`, `PV 2/Batt`, `PV 3/Batt`,
`Spare 1`, legend. The new `Spare 1` is the former `Rock store` text element, same position (310-2). **F**

Java displet, dated mapping changes (**F**, `git show <hash> -- SwitchboardsOverviewDisplet.java`):

- 2018-07-02 .. 2023-06-22: 319-2 `Aircon` and `Solar` on `Local`/`Grid`; 715-2 `Gaia`, `Solar` on `Busbar 1/2`; 117-6
  `NEVIC1..8` on `SYSLAB`/`Grid`.
- 2023-06-23 `73b29d2` (new diagram, 116 -> 276 breaker bindings): `Gaia` mapped on **330-12**; 319-2 `Grid` breaker on
  **`Busbar B`**, `PV` on A/B, `CEEx2` on A/B (two independent breakers), `Aircon` on A/B; 117-2 `CEEx2`; 117-6 `EVSE1..8`
  on A/B.
- 2023-08-11 `5563837` names synchronized with syslab-52; 2023-10-05 `a503581` 330-12/13 as built; 2023-10-19 `b6656a1`
  310-2, `db9aa8e` meta-crossbar, `2740208` 330-12 names; 2023-10-31 `01de4af`, `4b9e2ed`, `5d7d42a` 716 and 117 names.
- 2024-03-26 `0d8f6d4`: 117-6 `EVSE1` -> `EVSE_01` (bay names).
- 2024-06-19 `0f779ce`: breaker bindings of C1<->C2 (117-2 and 319-3) and E1<->E2 (319-3, 716-2) swapped; 319-3 E1 now on
  A/B, E2 on A/C.
- 2024-09-08 `353e492`, `7d062cf`, `21412bd`: crossbar as three bays, 319-3 supply-side manual breakers; 2024-10-03
  `667a306`, `adac4f3`: supply and transformer breakers of 319-3.
- 2024-10-14 `bff0176`, 2024-10-25 `de087fd`, `0ecd4ea`: 117-4/5 names, manual D1 breaker; 2025-01-17 `eda6aac`: 117-2
  X-line bay names; 2025-02-18 `0f881d5`: 117-5 `Cable_D1-A` was bound to busbar B; 2026-01-07 `3c0ea91`: 117-4 D1 feedback.
- 2026-08-13 `5c6ee92`: 310-2 `Spare_1` -> `Boiler`. `RockStorage` stays bound (to the line now labelled `Spare 1` in v7).
- 2026-10-05 `c32720d`: switch to v7, 119-10 bays bound; `330-13_EVSE_12` line commented out; `d407f7f`: 119-10 polled,
  330-13 breakers rebound from bay `EVSE_12` to bay **`Cable_Q1`** (A/B), which does not exist in syslab-51's `hardware.xml`.
- Not in the Java at any commit: 316-2, `P2XA/B`, `PTX`, `Cable_M1` (319-4 `P2X` is still bound to A/C). **F**

### S2.5 Cross-check of the first-pass change table

"Agree" = the sources agree on the state; the date columns are first commit/era showing the new state.

| Change | `hardware.xml` (repo) | Figure / Java | Header era (first pass) | Verdict |
|---|---|---|---|---|
| **AirCon 715_2 -> 319_2** | `Aircon` bay on 319-2 in every version since `affe00650` 2015-08-03; never on 715-2 | Java: 319-2 `Aircon` since `02de357` 2018-07-02; figures v4..v7 one `Aircon` label (319-2) | 319_2 `Aircon` every era since 2021-01-01 | **Contradicted for 2015-2026**: no lab source shows AirCon on 715-2. If it ever was there, it was before 2015-08-03 (or via a bay named otherwise, e.g. `Gaia`/`Solar`, **I**). The registry's "formerly on 715_2" (`3f6c51a`) has no support; the move is not a configuration change of any modelled era. |
| **Gaia 715_2 -> 330_12** | 715-2 `Gaia` until `ebb1fb939` 2023-06-23 (removed "after lab rebuild"); 330-12 `Gaia` from `cf92b2f15` 2023-10-06 | Java: 715-2 until 2023-06-22, 330-12 from `73b29d2` 2023-06-23 (drawn on 330-12 from the first v6) | 715_2 `Gaia` until 2023-06-30; 330_12 from 2024-06-10 | **Confirmed and narrowed**: off 715-2 in the 2023 rebuild (2023-06-23 config, 2023-07-01 header). On 330-12 the drawing (2023-06-23) and config (2023-10-06) predate logging (2024-06-10). Physical connection date on 330-12: between 2023-06-23 (planned) and 2024-06-10 (logged) (**I**: the 330-12 config commit 2023-10-06 is the best estimate of commissioning). |
| **CEEx2 bays with two sockets** | 319-2 `CEEx2` from `196774659` 2023-04-13, 117-2 from `ebb1fb939` 2023-06-23; two breakers (A, B), **never an interlock**; second instrument: 117-2 `a96c88172` 2024-10-14 (`CEEx2_1/_2`), 319-2 `dfb7b96c1` 2026-06-15 (`CEEx2.A/.B`) | Java: two independent breakers on both since 2023-06-23; one `CEE x2` label each | 117_2 from 2023-07-01, 319_2 from 2023-12-01; meters split 2026-06-24 on both | **Confirmed, dated**: bays since the rebuild; no interlock ever (supports `3d584c8`). Meter split: config 2024-10-14 (117-2) and 2026-06-15 (319-2), header for both 2026-06-24. **I**: the 117-2 split was deployed to logging only on 2026-06-24; the 319-2 commit says the instrument "was missing", so the second 319-2 meter likely existed before 2026-06-15. |
| **Solar -> PV** | 319-2 `86f2e627d` 2023-06-14; 715-2, 117-2 `ebb1fb939` 2023-06-23 | Java `73b29d2` 2023-06-23 | 715_2/117_2 2023-07-01, 319_2 2023-12-01 | **Confirmed**: one rename in the 2023 rebuild; header lag on 319_2 is logging (319_2 kept its old header until 2023-11-30). |
| **319_2 `Grid`/`Local` -> `Busbar_B`/`Busbar_A` (the suspect alias)** | `86f2e627d` 2023-06-14: the `Grid` bay's only breaker moves from busbar `Grid` to `Busbar B`; comments "Busbar_A old local", "Busbar_B old grid" added in the same commit | Java `73b29d2`: `Grid` breaker bound to `Busbar B`; the drawn breaker of `Solar`@`Local` is bound as `PV`@`Busbar A`, `Solar`@`Grid` as `PV`@`Busbar B` | header 2023-12-01 `BRK_Grid_Busbar_B` | **The `319_2.json` alias is swapped** (`BRK_Solar_Grid` must map to `BRK_PV_Busbar_B`, `BRK_Solar_Local` to `BRK_PV_Busbar_A`). Three independent sources agree (**F**); the Java element continuity is supporting evidence only (v6 is a redrawn figure that reuses some ids for other bays, **I**). |
| **Busbar 1/2 -> A/B** | `ebb1fb939` 2023-06-23 (715-2, 117-2/5, 716-2); 117-4 `Busbar 1` -> `Busbar A` | Java `73b29d2`: 117-2 drawn breakers of `Solar`@`Busbar 1`/`2` rebound as `PV`@`Busbar A`/`B` | 2023-07-01 | **Confirmed for 117-2** (1 -> A, 2 -> B) by Java continuity (**I**-strong); for 715-2/716-2 the order of breakers per bay is unchanged (`-BB1`/`-A` first) but no source states 1 = A explicitly. |
| **117-6 NEVIC -> EVSE, SYSLAB/Grid -> A/B** | `a6107864b` 2023-11-14 | Java `73b29d2` 2023-06-23 (`EVSE1`), `0d8f6d4` 2024-03-26 (`EVSE_01`) | 2025-02-14 | **Confirmed; header lags config by 15 months.** The drawing renamed first (2023-06-23). **I**: physical relabelling (if any) happened in the 2023 rebuild; 2025-02-14 is a logging deployment. |
| **SVG 6 -> 7: 316-2, Cable M1, P2XA/B, PTX** | absent (319-4 `P2X`, 319-3 `Spare` at HEAD) | v7 `910fb87` 2026-10-05 only; not in Java | none | **Dated 2026-10-05 (figure only).** Inference of the first pass (P2X fed from 319-4 over Cable M1, PTX from 319-3 Transformer busbar `Spare`) stands as **I**; no config or mapping exists yet, so 316-2 is planned or unpolled. |
| **SVG 6 -> 7: 119-10, Cable Q1, EVSE 12 moves** | syslab-44 `7c4a820a2` 2026-10-05: 119-10 with `Cable_Q1`, `EVSE_12`; 330-13 still `EVSE_12` | v7 `910fb87`, Java `c32720d`/`d407f7f` 2026-10-05: 330-13 breakers rebound to bay `Cable_Q1` | 330_13 `EVSE_12` (archive up to 2026-06-24 at least) | **Confirmed and dated 2026-10-05** (config, figure, Java, same day). **Disagreement**: syslab-51 (330-13) not updated, so the 330-13 end of Cable Q1 is still named `EVSE_12` in `hardware.xml` and logging, but `Cable_Q1` in the Java. **I**: the 330-13 bay `EVSE_12` was repurposed to feed Cable Q1; the EVSE 12 charger moved behind 119-10. |
| **`Ext. 117-x` -> Cable X** | `CableX1` 2023-06-23; `Cable_X1_2/_5` 2023-10-31; four one-breaker bays 2024-10-09 | v6 kept `Ext. 117-2/-5` until v7 (2026-10-05); Java X bay names 2025-01-17 | 2023-07-01, ... | **Confirmed**: v6 label lag of 3.3 years. The header era 2024-02-27 (merged X bays) matches the config era 2023-10-31 .. 2024-10-08 (`Cable_X1_2`, one two-breaker bay), so the header merge is a late logging deployment, and the 2023-09-27 four-bay header predates the config (**F** dates / **I** reading). |
| **310-2 `Rock store` -> `Boiler`** | `627b0011c` 2026-08-13: **`Spare_1` -> `Boiler`**; `RockStorage` unchanged at HEAD | v6 `9c29ae3` and Java `5c6ee92` 2026-08-13: `Spare 1` -> `Boiler`; v7 2026-10-05 relabels the `Rock store` element `Spare 1`, Java still binds `RockStorage` to it | one era (`RockStorage`, `Spare_1`) from 2025-02-24 | **First-pass reading corrected**: the Boiler took the former `Spare_1` bay (2026-08-13). The v7 label `Spare 1` on the `RockStorage` bay disagrees with `hardware.xml` and the Java (**F**); **I**: either the rock store is out of use or the label is a drawing slip. |
| **C1/C2, E1/E2 label swap 2024-06-19** | 319-3 E pair: A/B, A/C in 2015; **A/C, A/B** from `ebb1fb939` 2023-06-23; back to **A/B, A/C** in `b736d2d87` 2024-09-08. C pair: A/C, A/B in 2015; A/B, A/C from 2023-06-23, unchanged since | `7c64e9a` (labels) and `0f779ce` (Java) 2024-06-19: C1<->C2 and E1<->E2 swapped; Java 319-3 E1 A/B, E2 A/C from 2024-06-19 | 319_3 C pair swap between 2022-03-02 and 2023-12-01; E pair swap 2024-09-08 (`.csv.2`) | **Confirmed and explained**: the as-built cables differ from the plan; the figure and Java were corrected 2024-06-19, the config (and with it logging) for the E pair on 2024-09-08. **I**: 319-3 E1/E2 breaker data between 2023-06-23 (or 2023-12-01 in logging) and 2024-09-07 carry swapped E1/E2 names; for the C pair the config already matched as-built from 2023-06-23 and only the drawing was wrong. Physical wiring itself likely dates from the 2023 rebuild. |
| **319-3 ABB_Pri / Transformer busbar** | `ABB_Pri` 2024-06-19 (on `Busbar_Grid`), Transformer busbar 2024-09-08, `ABB_Pri` on `Busbar_Supply` 2024-10-03 | v6/Java 2024-09-08 and 2024-10-03 | `ABB_Pri` 2024-03-06/07, Transformer 2024-09-08, Supply 2024-10-03 | **Agree from 2024-09-08**; `ABB_Pri` was logged 3.5 months **before** it was committed (header 2024-03-06 vs config 2024-06-19), so the deployed config can precede the repository. |
| **330-12 `Spare_6/7` removed** | not removed (HEAD has `Spare_1..7`) | figures never drew 5..7 | removed 2026-04-19 | **Disagreement persists**: logging changed, `hardware.xml` did not. |

### S2.6 Which source dates a physical change best

- **`hardware.xml` commit dates** are the best single dating source for *what the lab says exists* from 2015-08-03 on: they
  cover every switchboard, are fine-grained, and often say why ("after lab rebuild", "adapting to reality", "after plumbing
  work"). Limits (**F** examples): the deployed config can run ahead of the commit (`ABB_Pri` logged 2024-03-06, committed
  2024-06-19; 117-2 `Grid_2` logged 2023-09-27, committed 2023-10-31), and config can describe hardware before it is logged
  (330-12 config 2023-10-06, logged 2024-06-10; 117-6 EVSE 2023-11-14 vs 2025-02-14).
- **Header eras** date when logging changed; they lag config by days to 2.5 years (117-4 `Grid_4`: config 2023-10-31, header
  2026-06-24) and sometimes lead it. They remain the only proof that a configuration was live.
- **Figure and Java** date when the operators' view changed. They lead config for the 2023 rebuild (Gaia on 330-12 drawn
  2023-06-23) and for corrections (C/E swap 2024-06-19), and lag it for labels (`Ext. 117-x` until 2026-10-05). The Java binding
  of breakers to busbars is a second, independent statement of busbar assignments (it settled the 319-2 alias).
- **Rule of thumb (I):** physical change date = earliest of (config commit, figure/Java commit, header era) when the commit
  message says the change reflects reality; otherwise bracket it between the first statement and the first header era that
  shows it.

### S2.7 Open gaps after the second pass

1. **AirCon on 715-2** is not in any lab source since 2015-08-03; needs the maintainer to retract or date it (pre-2015?).
2. **316-2 / PTX / Cable M1** exist only in figure v7 (2026-10-05); no node, no breakers, no mapping. Planned or unpolled; ask
   the lab.
3. **330-13 end of Cable Q1**: `hardware.xml` (syslab-51) still says `EVSE_12`, Java says `Cable_Q1`; logging will keep the old
   name until syslab-51 is updated. The model needs one declared name.
4. **310-2 `RockStorage` vs v7 label `Spare 1`**: is the rock store still connected?
5. **330-12 `Spare_6/7`**: logging dropped them 2026-04-19, config did not.
6. **Pre-2015**: the `conf/` history starts 2008-10-29 but the first `hardware.xml` is 2015-08-03; older configs (other file
   names) were not examined.
7. **Column archive reach**: the latest era starts 2026-06-24; whether the archive was scanned past 2026-08-13 (Boiler) and
   2026-10-05 (119-10) is not stated, so the absence of those eras is not evidence.
8. **`319_2.json` alias** must be fixed (swap A/B for the `Solar` breakers) in `syslab_data` before eras are built on it; and the
   319-3 E1/E2 breaker columns for 2023-12-01 .. 2024-09-07 need a declared correction.
