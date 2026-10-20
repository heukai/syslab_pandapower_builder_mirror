# Research: what in the switchboard overview figure is private or operator-only (ticket 12, first pass)

Ticket: `.scratch/features/model-versions/issues/12-what-in-the-figure-is-private.md` (map: `../map.md`).
Date: 2026-10-20. Status: **first pass** (figure, `hardware.xml`, model files). The Java code that reads the figure is not
yet accessible; the second pass (what the Java code reads) waits for the access ticket (01).

Inputs (read only, local, not committed): `sample_data_SYSLAB-NAS/switchboard_overview_6(1).svg` (511 846 B, docname
`switchboard_overview_6.svg`) and `switchboard_overview_7.svg` (546 622 B). Cross-checked against
`syslab-master-conf/conf/syslab-{01,11,52,53}/hardware.xml` and `syslab_pandapower/model_data/switch_name_map.json` (297 switches)
and `breaker_groups.json`.

**Legend.** **[F]** fact, followed by how it was verified. **[I]** inference, not verified. "Parsed" = Python
`xml.etree.ElementTree` with transforms composed down the tree (throwaway scripts in a temp folder, run with
`python -I`; not committed). Coordinates are user units after transforms, v7 unless stated.

## Summary

- Nothing in either file names a person, host, IP address, email or absolute path, and neither file embeds images, fonts,
  scripts, `<style>` elements or XML comments **[F: regex scan of the raw text]**. What needs to go is (a) Inkscape/sodipodi
  editor state: a relative export path that points into an internal source tree, the namedview with id
  `risoe.syslab.config.base`, window geometry and the Inkscape build; (b) the operator UI: the `Login` layer and its four
  sub-layers, the `Emstop` and `OutOfService` overlays and the `Xbar-CEE-Plugs` layer; (c) junk: empty and off-canvas texts.
- A label map is **feasible but not fully automatic**. Breakers are plain grey `<circle>`s in one flat `Breakers` layer, and
  labels are loose `<text>` elements, mostly at the document root. Nothing in the file groups a circle with its label or its
  switchboard. Geometry carries everything: the switchboard is a `Buildings`-layer box, the bay is a label in line with the
  circle's column or row, and the busbar is the circle's row or column. Where the label exists, the geometry matches
  `hardware.xml` busbar assignments exactly (all of 319-4, 310-2, 319-2, 117-2 CEE x2). Unlabelled breakers (Grid bays,
  the 319-3/319-4 crossbar), renamed bays (Boiler = RockStorage, Cable M1 = P2X) and switchboards absent from the model
  (316-2, 119-10) need a small curated alias/override table per figure version.

## (1) What must not reach the public package, or only matters to the operator UI

| # | Location (XPath-ish) | Content seen (v6 / v7) | Why | Strip rule |
|---|---|---|---|---|
| 1 | `/svg/@inkscape:export-filename` | `../../extensions/Unilab_2021/switchboard_overview_unilab_sketch.png` (both) **[F]** | Relative path into an internal source tree (`extensions/Unilab_2021`), and an internal project name | Remove the attribute |
| 2 | `/svg/@inkscape:export-xdpi`, `@inkscape:export-ydpi` | `199.99011` **[F]** | Editor export state | Remove |
| 3 | `/svg/@sodipodi:docname` | `switchboard_overview_6.svg` / `_7.svg` **[F]** | Internal file name, not secret; the published name is set by the builder | Remove (the builder sets its own file name) |
| 4 | `/svg/@inkscape:version`, `@sodipodi:version`, `@inkscape:output_extension` | `1.3.2 (091e20ef0f, 2023-11-25, custom)` / `1.4.4 (dcaf3e7d9e, 2026-05-05)`; `0.32` **[F]** | Fingerprints the maintainer's tool build; no value to the public | Remove |
| 5 | `/svg/sodipodi:namedview[@id='risoe.syslab.config.base']` and child `inkscape:grid` | zoom, cx/cy, `window-width=1920`, `window-height` 978 / 1098, `window-x/y=0`, `current-layer` `layer5` / `g4883`, page colours **[F]** | Editor window geometry and session state. Its id is a Java-package-like internal name **[F: attribute value]**; that the Java code looks it up is **[I]** | Remove the whole element |
| 6 | `/svg/metadata/rdf:RDF/cc:Work` | only `dc:format=image/svg+xml`, `dc:type=StillImage`; no title, creator, rights or date **[F]** | Harmless, but carries no licence or attribution | Remove; the builder may write its own `<metadata>`/`<title>` (owner, licence, era) once the figure owner has given permission (map: publishing needs the owner's permission) |
| 7 | `//g[@inkscape:label='Login']` (`id=layer6`, displayed) and its sub-layers `LayerLoginButton` (`layer4-1`, shown), `LayerLogoutButton` (`layer7`, hidden), `LayerControlWarning` (`layer3-2`, hidden), `LayerAccessDenied` (`layer6-7`, hidden) | Texts `Login`, `Logout`, `Username: ----` (`id=textUser`), `Auto logout in: --:--` (`id=textTime`), `Breaker control enabled`, `--- ACCESS DENIED ---`; button groups `id=btnLogin`, `btnLogout`; panel `rect4911` **[F]** | Operator UI only. The placeholders hold no real user name in either file **[F]**, but the runtime UI fills them **[I]**, so a figure captured from a running UI could carry one | Remove the whole `Login` layer (by label, not by id) |
| 8 | Ids `btnLogin`, `btnLogout`, `textUser`, `textTime` | The only hand-written ids besides defs (`Strips1_*`, `Arrow*`) **[F: id scan]** | Hooks for the operator UI **[I: strongly suggested by the names; confirm in the Java pass]** | Disappear with rule 7; afterwards assert that no element id matches `^(btn|text)(Login|Logout|User|Time)$` |
| 9 | `//g[@inkscape:label='Emstop']` (`layer10`) | 12 emergency-stop markers (red circle r≈20, `!`, `ES`). **Displayed in v6, `display:none` in v7** **[F]** | Live state shown by the UI (emergency stop pressed); a static copy would show a false alarm or nothing | Remove the layer. Keep the `Legend` entry only if Emstop is kept; otherwise also remove the `Emergency stop` legend group in `layer9` (`text24481`, `g4151`, …) |
| 10 | `//g[@inkscape:label='OutOfService']` (`layer2`, hidden) | 12–14 hatched rects/paths, one per switchboard box, filled with `url(#pattern…)` **[F]** | Per-switchboard out-of-service overlay toggled by the UI **[I]** | Remove the layer, then garbage-collect `defs/pattern` elements no longer referenced |
| 11 | `//g[@inkscape:label='Xbar-CEE-Plugs']` (`layer1`, hidden) | 24 unlabelled paths (plug symbols), identical in v6 and v7 **[F]** | Temporary equipment on CEE sockets is recorded per experiment, not in the model (ADR-0004) | Remove the layer |
| 12 | Legend states `layer9` | `Breaker closed/open/tripped`, `Set to manual`, `Cannot actuate`, `Did not actuate`, `No data / Out of use` (v6) → `No connection`, `No data` (v7) **[F]** | Operator state colours; harmless, partly useful to a viewer of a coloured figure | Keep, or keep only closed/open (the states a static or data-driven figure can show). A decision for the spec, not private |
| 13 | Breaker fill `#e4e4e4` on all 295 circles in `Breakers` **[F]** | A neutral placeholder the UI recolours **[I]** | Not private | Keep |
| 14 | Empty texts: `text7` (Droid Sans), `text4876` (off-canvas at x=-248), `text24485`, `text18` (v7 only) **[F]** | Editor leftovers | Remove texts whose `itertext()` is blank |
| 15 | Editor-only attributes on every element: `sodipodi:nodetypes`, `sodipodi:role`, `inkscape:connector-curvature`, `inkscape:collect`, `inkscape:stockid`, `inkscape:label` on non-layers (`#text6833`, `#text5505-0`) **[F: attribute census, ~1 100 occurrences]** | Noise, not private | Remove all `sodipodi:*` and `inkscape:*` attributes and elements **after** the layer rules above have used `inkscape:label`/`groupmode` to find the layers. Keep `xml:space` |
| 16 | Fonts | `font-family` Luxi Sans (~410–440 uses), Noto Sans, Droid Sans, Bitstream Vera Sans Mono, sans-serif; **none embedded** **[F]** | Not private. Luxi Sans is rarely installed, so a PNG render substitutes it **[I]** | Keep the names; append a `sans-serif` fallback when rendering. Not a privacy item |

Not found in either file, by full-text regex scan **[F]**: IPv4 addresses, `http(s)` URLs other than XML namespace URIs, email
addresses, drive letters or `/home`/`/Users` paths, `sodipodi:absref`, `<image>`, `data:` URIs, `@font-face`, `<script>`,
`on*` event attributes, `<title>`/`<desc>`, XML comments. Names of people: none. (The internal IPs and serials sit in
`hardware.xml`, not in the figure; the label map must not copy anything from `hardware.xml` beyond bay, breaker and busbar
names.)

Visible content that is **not** private but is a policy choice for the owner: the title `SYSLAB breaker overview`
(`g239924`), building names (`Building 319`, …), equipment names (`Gaia`, `Flexhouse`, `Demolab 1`, `EVSE 11`, `Fast charger
site`, …), transformer ratings (`630 kVA`, …). These describe the public lab and appear in the public model's switch names
already **[F for the switch names: `switch_name_map.json`]**.

**Recommended sanitizer shape [I]:** an allow-list rather than a block-list. Keep only the layers `Buildings`, `Lines`,
`Busbars`, `Breakers`, `Legend` (minus Emstop) and the root-level texts and paths; drop every other layer; strip all
`inkscape:`/`sodipodi:` attributes and the namedview/metadata; garbage-collect unreferenced `defs`; then assert that no
string from a deny-list (`Login`, `Logout`, `Username`, `ACCESS DENIED`, `export-filename`, `risoe.`, `../`) is left. A new
layer in a future figure version is then dropped by default and flagged, not leaked.

## (2) What the figure must keep for a label map

### Structure **[F: parsed]**

- 15 `inkscape:label`led groups: 13 `groupmode="layer"` (9 top-level: `Buildings`, `Lines`, `Xbar-CEE-Plugs`, `Busbars`,
  `Breakers`, `Legend`, `Emstop`, `OutOfService`, `Login`; 4 sub-layers in `Login`) and 2 labelled texts.
- **Breakers:** 295 `<circle>`s (v7; r=6.087, fill `#e4e4e4`) directly under `Breakers` (`layer5`), with no group per
  breaker. Some carry ids `path…` (circles converted from arcs); ids are auto-generated. One breaker-like circle
  (`circle3-1`, at the ABB Pri feeder) sits in `Lines`, so layer membership is a good filter but not a perfect one.
  The other circles in the file are legend swatches (14), Emstop markers (12) and one in `Lines`.
- **Switchboards:** text `NNN-N` in `Buildings` (`319-2`, `310-2`, …, 16 in v7). Most have a `Buildings` `<rect>` box that
  contains exactly one such text (330-12, 330-13, 716-2, 715-2, 117-2, 117-4, 117-5, 117-6, 310-2, and in v7 316-2,
  119-10). **319-2, 319-3, 319-4 have no rect box** (drawn with paths), so they need a nearest-label or curated box rule.
- **Busbars:** texts `Busbar A/B/C` in `Busbars`, one per busbar per switchboard (26 in v7). Busbars are rows (horizontal
  switchboards) or columns (vertical switchboards 310-2, 319-2, 715-2).
- **Bay labels**, two kinds:
  - Feeder/equipment names, mostly **root-level texts outside any layer** (`Workshop`, `HP 1`, `CEE x2`, `Boiler`, `Cable |
    K1` split over tspans, …), rotated −90° under/over vertical columns or horizontal beside rows.
  - Cable conductor labels `X1.A`/`X1.B` in `Lines`: a cable with two parallel bays (`Cable_J1A`, `Cable_J1B` in
    `hardware.xml`) is drawn as one `Cable J1` label plus `J1.A`, `J1.B` sub-labels at both ends. `Combined` texts
    (`Lines/g…`) mark the merged A+B conductor and are not bays.
  - In v7, 316-2's bays are labelled by texts **inside the `Breakers` layer** (`Grid`, `P2XA`, `P2XB`, `Cable | M1`), unlike
    every other switchboard.
- Labels are never grouped with their circles, and nothing in the file ties a label to a switchboard but position.

### How a breaker resolves to (switchboard, bay, busbar) **[F for the examples; method I]**

1. Switchboard = the `Buildings` box containing the circle (fallback: curated boxes for 319-2/3/4).
2. Bay = the label aligned with the circle across the busbars: for a vertical column the −90° label with |label.x −
   circle.x| ≲ 8 (A-conductor labels sit about 2.5 left of the circle, B about 7 right); for a horizontal row the label
   whose y is within the row. Choose the nearest along the column/row inside the same box.
3. Busbar = rank of the circle's row (or column) in that switchboard, named by the `Busbar X` texts.
4. Model name = `{swbd with _}_BRK_{hardware bay}_Busbar_{X}`, with the figure label normalised (`J1.A` → `Cable_J1A`,
   `CEE x2` → `CEEx2`) and an alias table for the rest.

A naive nearest-label pass (temp script `pair.py`) gave a label to 290 of the 295 v7 circles; it is right on the clean
switchboards (117-6, 330-13, 310-2, 319-2, most of 330-12 and 716-2) and wrong where horizontal multi-line labels sit beside
columns (316-2, the 319 complex). Making it exact needs the orientation-aware rule above and an override table.

### Worked examples (v7) **[F: coordinates parsed; names from `hardware.xml` and `switch_name_map.json`]**

| Figure label (id, position) | Circles (id, x, y) | Busbar by geometry | `hardware.xml` | Model switch |
|---|---|---|---|---|
| `J1.A` on **310-2** (`text61914`, 1155, 327, horizontal; `Lines`) | `circle61904` (1179.7, 329.2), `circle61906` (1207.4, 329.5) | columns: 1179.7 = A, 1207.4 = B (`Busbar A` text at x 1152, `Busbar B` at 1200) | syslab-53, switchboard 310-2, bay `Cable_J1A`, breakers `Cable_J1A-A` (Busbar_A), `Cable_J1A-B` (Busbar_B) | `310_2_BRK_Cable_J1A_Busbar_A`, `…_Busbar_B` |
| `J1.A` on **319-4** (`text61890`, 1023, 422, −90°; `Lines`) | `circle40876` (1026.1, 467.1), `circle40874` (1026.1, 501.1) | rows: 433 = A, 467 = B, 501 = C | syslab-52, 319-4, bay `Cable_J1A`, breakers `Cable_J1A-B` (Busbar_B), `Cable_J1A-C` (Busbar_C) | `319_4_BRK_Cable_J1A_Busbar_B`, `…_Busbar_C` |
| `CEE x2` on **319-2** (`text9506-1`, 1236, 514, horizontal; root) | `path10659` (1179.6, 502.0), `path10696` (1207.3, 516.1) | columns: 1179.6 = A, 1207.3 = B (`Busbar A` text at x 1152, `Busbar B` at 1196) | syslab-01, 319-2, bay `CEEx2`, `CEEx2-A` (Busbar_A), `CEEx2-B` (Busbar_B) | `319_2_BRK_CEEx2_Busbar_A`, `…_Busbar_B` |
| `CEE x2` on **117-2** (`text85221`, 282, 785, −90°; root) | `circle7041` (270.9, 688.3), `circle7039` (284.9, 716.8) | rows: 688.8 = A, 716.8 = B (`Busbar A` text y 682, `Busbar B` y 709) | syslab-11, 117-2, bay `CEEx2`, `CEEx2-A` (Busbar_A), `CEEx2-B` (Busbar_B) | `117_2_BRK_CEEx2_Busbar_A`, `…_Busbar_B` |

Note that both CEE x2 pairs are **staggered** (the two circles are 14 units apart across the bay axis, not in line), so the
alignment tolerance must allow about 12 units **[F]**.

Whole-switchboard check, 319-4 (rows A 433, B 467, C 501) **[F]**: geometry gives K1A B/C, K1B B/C, K2A A/B, K2B A/B, J1A
B/C, J1B B/C, J2A A/C, J2B A/C, Spare_1 A/C (x 846), Spare_2 A/B (961), Spare_3 A/B (995), GridEmu B/C (773, label `Grid |
Emulator`), P2X A/C (809, label `Cable | M1`). These are exactly the busbar pairs in syslab-52 and in the model's 319_4
switch names. **The busbar row is reliable evidence; only the bay name needs care.**

### Ambiguities and gaps

- **Unlabelled breakers [F]:** Grid bays (310-2 top row at y 47; 319-2 bottom at (1207.8, 762.5), B only, which matches
  `Grid-B` being the only Grid breaker in syslab-01; 715-2 two circles near (90, 766) and (116, 782); 117-2 three circles
  near x 217–240, which fits `Grid_2` A/B/Grid **[I]**); the six 319-3/319-4 crossbar circles at x 653–733, y 366–470
  (= `Cross_A/B/C` × 2 **[I: count matches `breaker_groups.json`]**); the 319-3 Supply/Transformer/Amp circles. These need
  overrides keyed by switchboard and position, ideally by stable ids once the owner adds them.
- **Renamed or different labels [F for the labels, I for the pairing]:** `Boiler` (v7) / `Rock store` (v6) = `RockStorage`
  (310-2); `Cable | M1` (v7) / `P2X` (v6) = `P2X` (319-4, which in v7 feeds the new 316-2); `HP 1` = `HeatPump_1`; `PV 2/Batt`
  = `PVBatt_2`; `Booster | Heater` = `BoosterHeater`/`Booster_Heater`; `Heat pump` = `Heatpump`/`HeatPump`; `CEE 1`, `CEE 2` on
  117-5 = `CEEx1_1`, `CEEx1_2`; `Grid | Emulator` = `GridEmu`; `ABB | Pri`/`ABB Sec` = `ABB_Pri`/`ABB_Sec`. Labels that occur
  many times (`Spare 1`, `PV`, `CEE`, `Grid`) only become unique together with the switchboard.
- **One symbol, several model breakers [F: counts; I: meaning]:** 117-2 has 19 circles against 21 model switches, and 117-5
  has 18 against 20. The figure draws `Cable X1` and `Cable X2` as one breaker each per switchboard, while the model has
  `Cable_X1A_2` + `Cable_X1B_2` and so on. The label map must allow 1 → n.
- **Model breakers absent from the figure [F: counts]:** 330-12 has 40 circles against 46 switches. The figure labels
  `Spare 1–4` only, while the model and `hardware.xml` have `Spare_1`–`Spare_7`.
- **Figure content absent from the model [F]:** switchboards 316-2 (6+ circles, labels `Grid`, `P2XA`, `P2XB`, `Cable M1`) and
  119-10 (7 circles: `EVSE 12`, `Cable Q1`, `Battery 1–5`), and Cable Q1 (330-13 ↔ 119-10). The map entry for these has no
  model breaker and is flagged as a disagreement (the SVG is evidence, it never overrides `hardware.xml`).
- **Switchboard boxes for 319-2/3/4** are not rects, and a nearest-text fallback mis-assigns 319-3 cable circles to 716-2
  **[F: pair.py output]**. A curated box per figure version is the simple fix **[I]**.
- **Element ids are auto-generated** (`circle61904`, `path10659`) and change between versions (23 text ids are new in v7,
  2 gone) **[F]**. The label map must key on (switchboard, label, busbar) and may record the id only as a per-version
  pointer for the clickable SVG.

**Feasibility estimate [I]:** about 85–90 % of breaker circles map automatically with orientation-aware geometry. The rest,
around 30–40 circles per version (Grid bays, crossbar, 319-3 supply side, X-cables, 316-2/119-10), need a curated override
table of about 30–50 rows per figure version, which staff can review. Asking the figure owner to set stable `id`s or
`inkscape:label`s on breaker circles (for example `319-4/Cable_J1A-B`) would make future versions exact. The second pass
should check whether the Java code already holds such a table, which would make it the authoritative label map.

## (3) v6 versus v7, as far as sanitizing is concerned **[F: parsed and diffed]**

| Aspect | v6 | v7 |
|---|---|---|
| Canvas | 1307.73 × 735.6 | 1307.73 × 817.33 (taller: 316-2/119-10 area added; most y coordinates shifted) |
| Inkscape build | 1.3.2 (2023-11-25, custom) | 1.4.4 (2026-05-05) |
| namedview | window 1920×978, current-layer `layer5` | window 1920×1098, current-layer `g4883` (an Emstop group) |
| Emstop layer | **displayed** | `display:none` |
| Legend | `No data / Out of use` | `No connection`, `No data` |
| Switchboards | 14 labels | + `316-2`, `119-10`, `Building 316`, a second `Building 319`, `Fast charger site` |
| Breaker circles | 296 circles in total | 309 circles + 13 ellipses in total; 295 breakers in `Breakers` |
| Texts in `Breakers` layer | none | `Cable | M1`, `Grid`, `P2XA`, `P2XB` (316-2) |
| Renamed labels | `Rock store`, `P2X`, `PV 2/Bat`, `PV 3/Bat`, `Ext. 117-2`, `Ext. 117-5` | `Boiler`, `Cable | M1`, `PV 2/Batt`, `PV 3/Batt`, `Cable X1`, `Cable X2` |
| New v7 labels | — | `Battery 1–5`, `EVSE 12`, `Cable Q1` ×2, `PTX`, an extra empty `text18` |
| Same in both | `export-filename`, `docname` pattern, `risoe.syslab.config.base`, Login layer and its ids, `Xbar-CEE-Plugs` (24 paths), `OutOfService` (hidden), RDF block | |

For the sanitizer this means: the same layer allow-list works for both. **Visibility differs (Emstop), so rules must remove by
layer and never rely on `display:none`.** The label alias table is per figure version (`Rock store` versus `Boiler`), and
coordinates cannot be reused across versions.

## Second pass (pending the access ticket)

Questions for the Java code: which ids or labels it binds (`btnLogin`, `textUser`, …; breaker circles by id, by order or by
an external table); whether it holds a label → breaker table (which would then be the authoritative source of the label map);
how it fills `Username` and the countdown (to confirm that a captured figure can carry a real user name); what `OutOfService`
and `Xbar-CEE-Plugs` toggle.
