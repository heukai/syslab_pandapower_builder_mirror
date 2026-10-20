# What in the switchboard overview figure is private or operator-only?

Type: research
Status: resolved
Blocked by: -

## Question

From the two samples (`sample_data_SYSLAB-NAS/switchboard_overview_6(1).svg`, `_7.svg`): list everything that must not reach
the public `syslab_pandapower` package or is meaningful only to the operator UI (layers such as `LayerLoginButton`,
`LayerAccessDenied`, user-name and logout texts, Inkscape metadata and export paths, hidden or out-of-service layers, anything
naming people, hosts or internal paths), and what the figure must keep for a label map (which texts name switchboards, bays,
breakers and cables, and how a label is tied to its switchboard: grouping, position). Second pass after the access ticket:
what the Java code reads from the figure.

## Comments

**First pass done (2026-10-20, agent):** findings on the throwaway branch `research/figure-privacy` (commit `dd6f9e9`,
`.scratch/features/model-versions/research/figure-privacy.md`, pushed to `kheu-home`, never merged). Gist:

- Nothing personal in either sample: no names, hosts, IPs, emails, absolute paths, images, fonts or scripts; login texts are
  placeholders (`Username: ----`).
- Strip: editor metadata (`inkscape:export-filename` = relative internal path `../../extensions/Unilab_2021/...`, export dpi,
  docname, version stamps, the whole `sodipodi:namedview`, the RDF block, all `inkscape:*`/`sodipodi:*` attributes); the
  `Login` layer (ids `btnLogin`, `btnLogout`, `textUser`, `textTime`), `Emstop`, `OutOfService`, `Xbar-CEE-Plugs`.
  Recommended: an allow-list sanitizer (keep `Buildings`, `Lines`, `Busbars`, `Breakers`, `Legend` minus emergency stop) with a
  deny-list check afterwards; remove layers by name, never rely on `display:none` (`Emstop` shown in v6, hidden in v7).
- Label map: 295 breaker circles in `Breakers`, labels loose at the root; position is the only link (switchboard box, bay
  label column/row, busbar row). Worked examples `J1.A` (310-2, 319-4) and `CEE x2` (319-2, 117-2) match `hardware.xml` and
  the model; 319-4's busbar rows match exactly. Estimate (inference): ~85-90 % automatic, plus a curated override table of
  ~30-50 rows per figure version. Ids change between versions: key on (switchboard, label, busbar).
- Ambiguities: unlabelled Grid and crossbar breakers; renamed bays (`Boiler`/`Rock store`, `M1`/`P2X`); X1/X2 cables drawn
  with fewer symbols than model switches; 330-12 `Spare 1-4` vs model `Spare_1..7`; 316-2, 119-10, Cable Q1 not in the model;
  319-2/3/4 without a box rectangle.

**Second pass pending** the access ticket: what the Java code binds (ids or labels), whether it holds a label -> breaker
table already, and whether a running UI fills in a real user name. The ticket stays open until then.

## Answer

Both passes done (2026-10-20/21, agents). Findings: branch `research/figure-privacy`, commits `dd6f9e9` (samples) and
`523af04` (Java mappings and figure history), `.scratch/features/model-versions/research/figure-privacy.md`; never merged.

**The label map already exists.** `SwitchboardsOverviewDisplet.java` binds the figure by element id only (never by text or
position). Each breaker is one entry (switchboard, busbar, bay, element id): 290 in the v7 era, no duplicates. Bay and busbar
names are those of `hardware.xml`, so the model's breaker name follows directly (`{swbd}_BRK_{bay}_{busbar}`): 277 of 290 match
`switch_name_map.json` exactly, 2 differ only by `Grid` vs `Busbar_Grid`, 11 are where the model lags `hardware.xml` (Boiler,
119-10, Cable Q1); 18 model breakers have no symbol in the figure (B conductors of the X cables, some spares, EVSE_12 on 330-13).
So the label map is generated from the Java table, not from geometry (revises the first pass's 85-90 % estimate); geometry is
needed only for 316-2's unbound symbols (also missing from `hardware.xml`). Breaker element ids are stable v6 -> v7.

**Versions tie together.** At every commit, every breaker id in the Java table exists in the figure it loads: v4 from
2018-07-02 to 2020-06-23 (116 breakers, old busbar names), v6 from 2023-06-23 to 2026-08-13 (275-283), v7 from 2026-10-05 (290);
v5 was never loaded. Figure, Java and `syslab/conf` changes land on the same days (2026-08-13 Boiler, 2026-10-05 119-10).

**Privacy.** Every committed figure holds placeholders only; the operator UI writes the logged-in user name into `textUser` at
runtime, in memory only, never to the file. No IPs, URLs, emails, hosts or credentials in any of the 40 Java versions. Strip list
(first pass) confirmed, with additions: every committed v4 carries an absolute export path naming a personal account, so the
final check rejects home-directory and drive-letter paths; the layers to keep are set per figure version (v4 differs); element
ids must be kept unchanged (they are the join key to the Java table); the `Lines` layer stays; `OutOfService`, `Emstop` and the
login layer are runtime state and go.

**Disagreements for the data owner:** the Java code labels 330-13's former EVSE_12 bay `Cable_Q1` while syslab-51's
`hardware.xml` still says `EVSE_12`; 119-10's emergency-stop id is a placeholder that is not in the figure; two line ids on the
319-3 supply side are missing from v7.
