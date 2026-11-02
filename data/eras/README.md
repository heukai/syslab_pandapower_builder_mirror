# Configuration eras

One YAML file per configuration era (`E6.yaml`, `E7.yaml`, ...). Branch `model-versions` only, until the
versioning overhaul is sufficiently operational. Decisions behind the form: map "dated model versions" in
`.scratch/features/model-versions/` (tickets on configuration changes, consolidation and forward builds).
The form is a proposal to validate with the technical staff.

- **Era** (`E7`): a time period marked by a major configuration change (a new switchboard, or a new layout of
  the switchboard overview figure), named after the figure. It starts at the first operational evidence.
- **Eras so far:** E0 (2009, unnumbered EDISON figure), E2 (2012), E3 (2013), E4 (2015), E6 (2023), E7 (2026). There
  is no E1 (figure v1 was replaced by its wide variant v2 within three weeks) and no E5 (figure v5 was a draft of v6,
  never displayed). E0, E2 and E3 have `basis: header-only`: no `hardware.xml` exists for them, so their models can only
  be rebuilt from the data headers and the figures, and stay unverified until checked against measurements.
- **Operational periods** (`6-a`, `6-b`, ...): the switchboards in operation, in stages while the era's major
  change is being commissioned.
- **Change entries** (`E6-011`): one configuration change each, by `hardware.xml` names, with its evidence
  (role: announced, evidenced, materialized, displayed, declared), origin, certainty (an uncertain entry says why),
  whether it is in force (`yes`, or `no: evidence only` / `no: planned`) and its status (`proposed` by the builder
  or research, `confirmed` by a person). Ids are never reused.
- **Configuration revisions** (`6.3`): sets of confirmed, in-force entries; a model version `6.3.N` describes one.
- **Inquiries**: parameters a model needs that no source gives yet (Cable Q1's length and type).
- **Header periods** (`E6-H04`): stretches where the data files carry other names than the master
  `hardware.xml` in force (kind `lag`, `lead`, `unmatched`, `transition`, `meter-lag`), with the config whose
  names they carry. They do not change the model; they tell a column map which names to translate, and model
  selection warns inside them. Found by the column-archive cross-check (`.scratch/features/model-versions/research/`
  on `main`).

Lab refs are commits of the lab repositories (`syslab`, `syslab-userspace`), which are read-only: never commit
or push there. They stay in this private builder and are not published with a model.

Check the files: `python -c "from syslab_pandapower_builder.eras import load_eras, check_eras; print(check_eras(load_eras()))"`
(run from the workspace root); `tests/test_eras.py` does the same.

**Versions log:** `VERSIONS.md`, generated from the era files (revisions, entries not yet in a revision, model versions,
data-name periods; newest era first): `python -m syslab_pandapower_builder.eras > syslab_pandapower_builder/data/eras/VERSIONS.md`
from the workspace root. A test fails when it is out of date.

**Building a model version:** `python -m syslab_pandapower_builder.build_model --conf-repo syslab --conf-date <first day of
the revision> --model-version <era.revision.model> --valid-from ... --valid-to ... --output-dir ...` (workspace root). It takes,
per node, the master hardware.xml written on or before that day, and the curated entries valid on that day
(`valid_from`/`valid_to` in `breaker_groups.yaml`); it refuses breaker groups naming switches the configuration lacks.
