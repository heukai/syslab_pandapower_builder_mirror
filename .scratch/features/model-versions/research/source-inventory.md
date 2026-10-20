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
