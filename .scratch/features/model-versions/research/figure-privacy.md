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

## Second pass (Java mappings and figure history)

Date: 2026-10-21. Sources, read only: `syslab-userspace/src/main/java/risoe/syslab/gui/wall/displets/switchboard/SwitchboardsOverviewDisplet.java`
(HEAD `d407f7f`, 2026-10-05, 1258 lines; and every earlier version via `git show`), `syslab-userspace/src/main/resources/media/svg/switchboard_overview_{4,5,6,7}.svg`
(every committed version), `syslab/conf/syslab-*/hardware.xml`, and `syslab_pandapower/model_data/switch_name_map.json`.
The helper classes next to the displet (`Breaker.java`, `Switchboard.java`, `Line.java`, `LoginDialog`, ...) are outside the
readable scope and were not read, so anything about how they build data-channel names is **[I]**. Throwaway scripts (regex
extraction of the constructor calls, `xml.etree` id/layer lookup, per-commit diff) ran from a temp folder with `python -I`; not
committed. Commits are cited by hash and date. No values from `hardware.xml` beyond bay, breaker and busbar names are copied.

### Summary

- **The Java code holds an explicit, complete breaker table keyed by SVG element id.** Each breaker is one constructor call
  `new Breaker(<switchboard>, "<busbar>", "<bay>", "<element id>")` (lines 340-707): 290 entries at HEAD, 13 switchboards.
  The names are `hardware.xml` names verbatim (bay name and the breaker's `busbar` attribute), so the model switch name is a
  string format away: `{swbd with _}_BRK_{bay}_{busbar}`. **[F]**
- It binds **only by element id** (`document.getElementById`), never by text label, layer name, position or document order.
  The figure's text labels are not read at all. **[F: lines 770, 814, 819, 825, 855, 906-911, 974, 1011, 1023, 1043]**
- Breaker ids are **stable from v6 to v7**: all 283 v6-era entries keep the same element id in v7 **[F]**. That corrects the
  first pass's caution "ids change between versions": text ids change, breaker ids do not (for v6 -> v7).
- **Revised feasibility:** for v6 and v7 the label map can be generated **from the Java table alone, without geometry**, for
  every breaker the UI shows (290/290 in v7, 283/283 in late v6). Geometry is needed only for figure symbols the Java code does
  not bind (316-2, about 6 circles in v7). Against the current model, 277/290 names match exactly; the other 13 are one
  busbar alias and model staleness, not naming differences (details below). This replaces the first pass's "85-90 %
  automatic plus 30-50 override rows" **[F for the counts; the estimate is now a measured result]**.
- **Runtime privacy:** the running UI writes the logged-in user's name into `textUser` and a countdown into `textTime`, in the
  in-memory DOM only; the code never writes the SVG back to disk **[F]**. Nothing private is in the Java table or in any of
  the 40 historical versions of the Java file (no hosts, IPs, URLs, emails, paths or credential words) **[F: regex scan]**.
- **New strip item from history:** every committed version of **v4** carries an *absolute* `inkscape:export-filename` under a
  personal home directory (it names an account) **[F]**. v5-v7 carry only the relative path already listed. v4 also has a
  different layer set, so the first pass's allow-list does not apply to v4 as is.

### (1) What the Java code binds

**[F]** All bindings are literal ids or constants in the displet (HEAD `d407f7f`):

| What | How bound | Ids (layer in v7) | Lines |
|---|---|---|---|
| Figure file | classpath resource constant `BREAKER_OVERVIEW_FILENAME` | `media/svg/switchboard_overview_7.svg` | 49, 871 |
| Load anchor | `getElementById("rect10736")`, `SVGLoad` listener | `rect10736` (`Buildings`) | 814 |
| Switchboard | `new Switchboard(<SyslabComponent enum>, "<name>", "<cover id>", "<emstop id>")` | 13 switchboards; cover ids are rect/path elements in `OutOfService`; emstop ids are groups in `Emstop` | 113-125 |
| Breaker | `new Breaker(swbd, busbar, bay, id)`; click listener + style recolouring | 290 ids: 289 circles in `Breakers`, 1 circle in `Lines` (`circle3-1` = 319-3 `ABB_Pri` on `Busbar_Supply`) | 340-707, 819, 1043 |
| Line (conductor) | `graph.addLine("<line key>", new Line([source,] "<id>", ...))`; stroke recoloured red when energised | ~150 path/group ids (`Lines`, `Busbars`) | 154-333, 770 |
| Breaker group | `new BreakerGroup(swbd, "T1", "g61998", [C1A_A, C1B_A])`; click toggles a combiner | `g61998` (`Lines`) | 361, 825 |
| Out-of-service | whole layer shown at start (`layer2` -> `display:inline`); per-switchboard cover fill toggled `url(#pattern251266)` / `none` by connection state | `layer2`, cover ids | 56-57, 855-858, 1011-1021 |
| Emergency stop | per-switchboard group shown/hidden by `isEmergencyStopped()` | emstop ids | 1023-1030 |
| Login UI | layers and ids shown/hidden by login state | `layer4-1` (LayerLoginButton), `layer7` (LayerLogoutButton), `layer3-2` (LayerControlWarning), `btnLogin`, `btnLogout`, `textUser`, `textTime` | 59-70, 831-852, 906-963 |

Not bound by any code in the displet **[F: no id from these appears]**: `Xbar-CEE-Plugs` (stays as authored, hidden),
`LayerAccessDenied`, `Legend`, the `Busbar X` texts, and every bay/equipment label text. The first pass's `[I]` that the
namedview id `risoe.syslab.config.base` might be looked up by Java is **false for this displet** **[F: no reference]**.

**Structure of the breaker table [F].** One call per breaker; `<busbar>` is the `hardware.xml` busbar (`Busbar_A`/`B`/`C`,
`Busbar_Supply`, `Busbar_Transformer`, `Grid`); `<bay>` is the `hardware.xml` bay (`Cable_J1A`, `CEEx2`, `Grid_2`,
`Booster_Heater`, ...). The surrounding `graph.addBreaker(..., "<line 1>", "<line 2>")` names the two `Line` keys the breaker
connects (e.g. `"J1A", "310-2_A"`), so the table also encodes **which cable or feeder line each breaker sits on** (cable lines
are keyed `A1A` ... `L1`, `Q1`, `X1AB`, `X2AB`). No data-channel string such as `319_2_BRK_CEEx2_Busbar_A` appears in the
displet; channel names are presumably derived from (switchboard, bay, busbar) inside `Breaker`/`Switchboard` **[I: those
classes are out of scope]**. Per switchboard at HEAD: 117-2 19, 117-4 4, 117-5 18, 117-6 16, 119-10 7, 310-2 26, 319-2 21,
319-3 40, 319-4 32, 330-12 40, 330-13 20, 715-2 19, 716-2 28. No duplicate ids, no duplicate (switchboard, busbar, bay) **[F]**.

The first pass's worked examples are confirmed exactly by the table **[F]**: `circle61904`/`circle61906` = 310-2 `Cable_J1A`
A/B (lines 431, 433); `circle40876`/`circle40874` = 319-4 `Cable_J1A` B/C (534, 536); `path10659`/`path10696` = 319-2
`CEEx2` A/B (465-466); `circle7041`/`circle7039` = 117-2 `CEEx2` A/B (343-344). The first pass's unlabelled breakers are all
bound: 117-2 `Grid_2` on `Grid`/`Busbar_A`/`Busbar_B` (340-342), the six 319-4 `Cross_A/B/C` circles (518-523), the 319-3
supply side (`Supply`, `Grid`, `ABB_Pri`, `Amp_1`, `Amp_2`, `Spare`; 506-511).

**Naming versus the model [F: script join against `switch_name_map.json`, 297 entries].** Rule
`{swbd with _}_BRK_{bay}_{busbar}`:

| Outcome | Count | Entries | Cause |
|---|---|---|---|
| Exact match | 277 / 290 | | |
| Busbar alias | 2 | 117-2 `Grid_2` on `Grid`; 715-2 `Grid` on `Grid` | `hardware.xml` says `busbar="Grid"` (syslab-11 line 12, syslab-09 line 21); the model writes `Busbar_Grid`. A one-line normalisation |
| Model behind `hardware.xml` | 2 | 310-2 `Boiler` A/B | Bay renamed `Spare_1` -> `Boiler` in `syslab` `627b0011c` (2026-08-13) and in the displet `5c6ee92` (same day); the model still has `310_2_BRK_Spare_1_*` |
| Not in the model | 9 | 119-10 (7: `Cable_Q1`, `Battery_1..5`, `EVSE_12`), 330-13 `Cable_Q1` A/B | 119-10 added in `syslab` `7c4a820a2` and the displet `c32720d`/`d407f7f` (all 2026-10-05) |

Model switches with **no figure symbol** in the Java table: 18, plus the 2 Grid aliases **[F]**: the B-conductor X-cable
breakers on 117-2/117-5 (`Cable_X1B_2`, `Cable_X2B_2`, `Cable_X1B_5`, `Cable_X2B_5`: the figure draws one symbol per X-cable
and the table binds the A conductor only), 330-12 `Spare_5..7`, 716-2 `Spare_3..4`, 330-13 `EVSE_12` A/B, and the stale
310-2 `Spare_1` A/B. So the map from figure symbol to model breaker is 1 -> 1, with these model breakers left unmapped (not
1 -> n as the first pass inferred). Whether the single X-cable symbol should also colour the B breaker is a design choice
for the spec **[I]**.

**Disagreements to flag, not to resolve [F].** (a) At HEAD the displet binds 330-13's former `EVSE_12` circles as
`Cable_Q1` (`d407f7f`, "fixed some mapping/naming errors"), while `syslab/conf/syslab-51/hardware.xml` still names that bay
`EVSE_12` (line 33). (b) 119-10's emstop id is the placeholder `gxxxx`, which does not exist in v7. (c) Two `Line` ids in
the v7 table (`path136559`, `path10`, both 319-3 supply side) do not exist in v7; a third (`g20199`) is only in a
commented-out line. (d) 316-2 is drawn in v7 but is in neither the Java table nor any `hardware.xml` (of the two new v7
switchboards only 119-10 is, in syslab-44). Its symbols are the only unbound shapes in `Breakers`: 6 circles
(`circle4687-0`, `circle4695-3`, `circle4697-6`, `circle4705-1`, `circle4707-0`, `circle124536-3`: Inkscape duplicates of
330-12 circles, `-N` suffix) and 4 paths **[F]**; that they are 316-2's breakers is **[I: suffix pattern and the first pass's
316-2 count]**.

**What can be generated from Java alone [F for v6/v7; I for the method].** Parsing the 290 constructor calls yields the full
(element id, switchboard, bay, busbar, model switch name, connected lines) table for v7, and the same for v6 at any commit
from `c2047c6` (2023-06-23) to `5c6ee92` (2026-08-13). Geometry is only needed (i) for symbols the owner has not bound yet
(316-2), and (ii) optionally to attach the human label text to each id for display. Recommended keying: (figure version,
element id) -> (switchboard, bay, busbar), with the model name derived; record the displet commit the table was taken from.
Because breaker ids survived v6 -> v7 unchanged, a per-version table is mostly a copy plus additions. The curated part
shrinks to: the `Grid` -> `Busbar_Grid` alias, model-staleness entries (until the model catches up), and the flagged
disagreements, i.e. under 15 rows for v7.

### (2) Runtime privacy

**[F]**
- `textUser.setTextContent(String.format("Username: %s", user.getUsername()))` (line 933) when a login succeeds; `textTime`
  gets `"Auto logout in: <n>s"` every second (942). Both are set on the Batik DOM held in memory by `JSVGCanvas`.
- The displet only **reads** the figure (`cl.getResource(...)`, `canvas.setURI`, lines 870-873); there is no serialisation,
  export, save or file write in the file. A real user name could leave the process only through a screenshot or a DOM dump
  by other code **[I: no such code in scope]**. The committed figures hold only placeholders in every version (v4-v7, all
  commits) **[F: scan]**.
- Other runtime writes are state, not identity: breaker fill/stroke colours (1035-1134), energised line strokes (757-784),
  out-of-service covers and emstop markers (1006-1033), combiner opacity (968-1004), login layer visibility (902-966).
- The user name comes from `LoginDialog.User` (out of scope). Access control is commented out ("Temporarily disabled",
  lines 1170-1171, 1181-1182), so login only changes the display.
- Logging: the displet logs button presses and `Breaker pressed: {breaker}` (1223) to slf4j; not part of the figure.

**Private content in the Java code itself: none found [F].** A regex scan of all 40 committed versions of the displet
(`02de357` 2018-07-02 .. `d407f7f` 2026-10-05) for IPv4 addresses, URLs, email addresses, Windows/Unix home paths, internal
host suffixes and the words password/secret/token/credential found no hits. The table contains only SVG ids, switchboard,
bay and busbar names, line keys and `SyslabComponent` enum names. (The IPs and serials sit in `hardware.xml`, which the table
does not copy.) Whether the owner allows the table, as a derived label map, to be published is the same permission question
as the figure **[I]**.

### (3) Which figure the Java code expects, and how figure and mapping move together

**[F: `BREAKER_OVERVIEW_FILENAME` and the breaker table at every commit of the displet; every id checked against the figure at
the same commit]**

| Period (displet commits) | Figure loaded | Breakers in table | Switchboards | Notes |
|---|---|---|---|---|
| `02de357` 2018-07-02 .. `8195dba` 2020-06-23 | `switchboard_overview_4.svg` (path `media/` until `90b0511` 2018-12-11, then `media/svg/`) | 116 | 8 (117-2/4/5/6, 319-2/3, 715-2, 716-2) | Old naming: busbars `Busbar 1`/`Busbar 2`, bays like `Machine`, `Solar`. Pre-Unilab era |
| `c2047c6`, `73b29d2` 2023-06-23 .. `5c6ee92` 2026-08-13 | `switchboard_overview_6.svg` | 275 -> 283 | 12 (+310-2, 319-4, 330-12, 330-13) | `73b29d2`: "Mapped all breakers and lines to the new (Unilab-extended) switchboard diagram". Current naming (`Busbar_A`, `Cable_J1A`) from `5563837` 2023-08-11 ("Synchronized bay and busbar names between syslab-52 and the switchboard displet") |
| `c32720d` .. `d407f7f`, both 2026-10-05 (HEAD) | `switchboard_overview_7.svg` | 290 | 13 (+119-10) | v7 added in `910fb87` the same day ("Extending switchboard overview with PTX and fast charging site") |

- **v5 was never loaded by the displet** in any commit; it was added together with v6 in `c2047c6` and never changed **[F]**.
  Its `sodipodi:docname` names a different working file (a "unilab sketch ... dblbreakers" draft name), so v5 is an
  intermediate draft **[I]**.
- At every commit except `02de357` (whose figure path did not exist yet), every breaker id in the table exists in the figure
  of the same commit (0 missing) **[F]**. Figure and mapping are versioned together, tied by same-day commits: v6 and displet
  edits on 2023-08-11, 2023-10-05, 2023-10-19, 2023-10-31, 2024-06-19, 2024-09-08, 2024-10-03, 2024-10-25, 2026-08-13; v7 on 2026-10-05
  **[F: `git log` of both paths]**. The `syslab/conf` side moved on the same days for the two latest changes (`627b0011c`
  2026-08-13 Boiler; `7c4a820a2` 2026-10-05 119-10) **[F]**.
- Within v6, between `0ecd4ea` (2024-10-25) and `5c6ee92` (2026-08-13): 5 keys changed, 278 keys and ids unchanged **[F]**; the commit
  messages attribute the changes to X-cable bay names (`eda6aac` 2025-01-17), a `Cable_D1` busbar fix (`0f881d5` 2025-02-18)
  and `Spare_1` -> `Boiler` (`5c6ee92`).
- v4 -> v6: only 2 (switchboard, busbar, bay) keys survive (the naming changed), although 101 element ids are reused **[F]**;
  v6 was drawn from v4's file **[I]**. A v4-era label map would need its own table and the old-era names, consistent with
  the rule that pre-2024 topology differs.
- **The NAS samples:** `switchboard_overview_7.svg` is identical (after newline normalisation) to the repo's v7 at
  `7979a0f`/HEAD; `switchboard_overview_6(1).svg` equals the repo's v6 at `0ecd4ea` (2024-10-25), i.e. before the `Boiler`
  rename `9c29ae3` (2026-08-13) **[F]**. So the first pass's v6 findings describe the v6 of 2024-10-25 .. 2026-08-12.
- Configuration-era mapping **[I]**: a model version can pick the figure version by date and take the label table from the
  displet commit current at that date (the commit hashes above are the boundaries).

### (4) Strip list, revised for the full figure set (v4..v7)

Changes against the first pass's table:

| # | Change | Applies to | Basis |
|---|---|---|---|
| R1 | `inkscape:export-filename` is an **absolute path inside a personal home directory** (names an account) in every committed v4. Must be removed; first-pass rule #1 covers it, but the deny-list check must also reject `/home/`, `/Users/` and drive-letter paths | v4 | **[F]** scan of all 5 v4 commits; value not reproduced |
| R2 | v5's `sodipodi:docname` differs from the file name (internal draft name). Covered by #3 (remove docname) | v5 | **[F]** |
| R3 | v4 layer set differs: `Buildings` (empty), `LayerGrid` (everything: 116 circles, 74 texts, 149 paths), `LayerQuestionMarks` (116 `?` texts, hidden; unknown-state markers), `LayerControlWarning`, `LayerLoginButton`, `LayerAccessDenied`, `LayoutLogoutButton` (sic), `LayerLoginStatus`; no `Login` parent. The v4 allow-list is `Buildings`, `LayerGrid`; drop the rest. Allow-lists are per figure version | v4 | **[F]** parsed |
| R4 | **Keep element ids** of breaker circles (and line paths) instead of treating them as noise: they are the join key to the Java table, stable v6 -> v7. The sanitizer must not renumber or drop ids in kept layers | v4-v7 | **[F]** binding by id |
| R5 | The `Lines` layer must stay (holds the 319-3 `ABB_Pri` breaker `circle3-1` and the `T1` combiner group `g61998`) | v5-v7 | **[F]** |
| R6 | `OutOfService` and `Emstop` are confirmed as runtime state (layer shown at start, covers and per-switchboard groups toggled). Keep removing both (#9, #10). `Xbar-CEE-Plugs` is not touched by the displet; keep removing it for the ADR-0004 reason (#11) | v5-v7 | **[F]** |
| R7 | Login layer ids confirmed as UI hooks (`layer4-1`, `layer7`, `layer3-2`, `btnLogin`, `btnLogout`, `textUser`, `textTime`); #7/#8 stand. The post-check should also assert that no text starting `Username:` holds anything but dashes | v4-v7 | **[F]** |
| R8 | The namedview id `risoe.syslab.config.base` is not used by the displet; still remove the namedview (#5) | v4-v7 | **[F]** |

Unchanged: the other first-pass rules (#2, #4, #6, #12-#16). No version contains `<image>`, `data:` URIs, `sodipodi:absref`,
`sodipodi:docbase`, emails, IPs or non-namespace URLs, and none has a filled `dc:creator`/`dc:rights` **[F: scan of every
committed version of v4-v7]**.
