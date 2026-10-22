# What is one configuration change?

Type: grilling
Status: resolved
Blocked by: 05

## Question

Decide the record: granularity (switchboard, bay, breaker, cable, asset link), fields (date or date window, source,
origin built/discovered/declared, evidence, note), persistent identity and aliases (ADR-0005; e.g. SVG `CEE x2` vs hardware
`CEEx2`), and where the record lives and in what format, readable and editable by the technical staff.

## Answer

Settled with the maintainer, 2026-10-22 (grilling, two rounds).

**Caveat (maintainer):** everything human-facing here (operational periods written by hand, the propose/confirm workflow, the
change log's form) is a **proposal to validate with the technical staff**. We build the prototype on it; if the staff want
something else, that is a new Wayfinder effort, not a reopening of this map.

1. **One YAML file per configuration era** in the builder: `data/eras/E6.yaml`, `E7.yaml`, ... holding the era's major
   change (its evidence per step: announced, evidenced, materialized, with dates), its operational periods and its minor
   changes. Same plain style as the other curated data; the human-readable change log is generated from these files.
2. **One change line** per configuration change, major or minor: `id`, `date` (or a `from`/`to` window), `element`
   (switchboard, bay, cable or asset link by its `hardware.xml` names), `change` (added, removed, renamed, moved, retyped),
   `evidence` (list of source, ref, role: announced, evidenced, materialized, displayed, declared), `origin` (built,
   discovered, declared), `certainty` (confirmed or uncertain, with the flag reason), `in_force` (yes, or no with the reason:
   evidence only, planned), `status` (proposed or confirmed), `note`.
3. **Identity** by the `hardware.xml` names at the time (switchboard, bay; busbar for a breaker); a rename is a change line
   old -> new and lookups follow the chain. ADR-0005 persistent ids wait until the topology index (US-49) needs them.
4. **Operational periods are written in the era file** ({from, to, switchboards in operation}); the builder proposes them
   from the operational dates of the major change; a person corrects them.
5. **The builder proposes, a person confirms**: forward builds diff new source releases into proposed lines, research adds
   proposed lines backward, the maintainer or staff confirm or declare; only confirmed, in-force lines change a model version.
6. **Each model version has its own manifest** in `syslab_pandapower` (extending `model_version.json`): era and version
   (`7.1`, `7.1/summer-2027`), the base version a scenario derives from, the ids of the change lines it accommodates,
   validation instances (name, period, operational period, result) and validity periods. Public: dates, element names,
   validations and results only; lab commit refs and private paths stay in the builder's era files.
7. **Line ids** `<era>-<number>` (`E7-001`), in order of addition, never reused.
8. **Bay level**: lines name bays (and switchboards, cables, asset links); breakers come from `hardware.xml`; a breaker gets
   its own line only when it changes alone.
9. **Not-in-force claims stay** in the era file (`in_force: no` with the reason): they announce coming eras; builds ignore
   them, the change log lists them apart.

Asset links (US-48) are elements of change lines (point 2), which settles the map's fog patch on asset links.
