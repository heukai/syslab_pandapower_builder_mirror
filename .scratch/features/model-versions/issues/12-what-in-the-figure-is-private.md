# What in the switchboard overview figure is private or operator-only?

Type: research
Status: open
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
