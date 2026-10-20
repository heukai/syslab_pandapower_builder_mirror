# Map: dated model versions from consolidated configuration changes (US-24, US-25, US-50)

## Destination

A spec for **one core mechanism** that records every **configuration change** of the SYSLAB grid, dated and with its source,
whether it is found going forward (a new release of a source, at a regular build) or looking back (discovered in past data or
past versions of a source, or declared), and from which the builder derives one **model version** per **configuration era**,
published side by side by `syslab_pandapower`, each with its **switchboard overview figure** (sanitized SVG, PNG render,
and a label map from each label to the model's breaker), piped safely from its private source to the public package. Ready for
`/to-spec` and `/to-tickets`. Stories: `syslab_data/user_stories.md`
US-24, US-25, US-50 (and US-49 for era boundaries).

## Notes

Settled while charting (maintainer, 2026-10-20):

- **Terms:** `syslab_data/CONTEXT.md`: Configuration Change (origin *built*, *discovered* or *declared*), Configuration Era
  (grid-wide; replaces "topology era"), Model Version (the model of one era). The builder gets its own `CONTEXT.md` and
  `docs/adr/` lazily, when the first builder-only term or decision settles.
- **Sources, each dated:** `hardware.xml` (`syslab-master-conf`; authoritative for breakers and bays, ADR-0002), the builder's
  curated YAML (cables, socket meters, ...), the **switchboard overview SVG** with the Java code that maps its text labels to
  breakers (major versions as files, `switchboard_overview_6.svg`, `_7.svg`; minor versions as git commits in its own
  repository), data headers (column archive, header eras), the device registry, flow partners, and declarations. The SVG is
  **evidence with a date**: it never overrides `hardware.xml`, and disagreements are flagged.
- **Discovery is in scope** on two axes: integrating diverse sources, and both directions in time. The forward build is
  orthogonal to discovering the past, but one mechanism consolidates both kinds of change.
- **The technical staff will contribute directly to future versioning.** Every format decision (the change record, the change
  log) is judged by whether staff can read and edit it without the code. The human-readable change log is the frame for the
  first conversation with them.
- **Rules that hold:** a declared configuration is applied as given; Q is not evidence; zero voltage means an open breaker.
- **Repos:** builder (`kheu-home`, private), `syslab_pandapower` (public, `dev` only: no private data or paths), `syslab_data`
  (`kheu-personal`). Skills: grilling and domain-modeling for grilling tickets; prototype; research.
- **The figure is for the human in the loop (maintainer, 2026-10-20):** several integrations will use it. Each figure version
  corresponds to exactly one configuration era. Only the builder has access to its source, so the builder sanitizes it and
  publishes, per model version, the sanitized SVG (clickable labels kept), a PNG render for other UIs, and a label map
  (label + switchboard -> breaker, bay, switchboard of the model). Nothing private reaches the public package: operator-UI
  layers (login, access denied, user name), internal paths and metadata are stripped, and publishing needs the figure owner's
  permission.
- **Future need this map must leave room for:** a user mode in `syslab_data` that shows the era's figure and lets the user change
  breakers in an existing data set by clicking. It needs the figure and label map per model version.
- Version 7 of the SVG shows switchboards 316-2 and 119-10 and Cable Q1, which exist but are in neither `hardware.xml` nor the
  model: the current era's model is already behind its sources.

## Decisions so far

## Not yet specified

- **Verification per era:** how each era's model is checked against a baseline period of measured data (US-28), and how an
  unverified era is marked.
- **Era boundaries from the data:** how the topology state index (US-49) and the header eras (US-23) feed or confirm era
  boundaries.
- **Asset links:** whether the device registry's dated asset links (US-48) become configuration changes in the same record.
- **CI/CD pipeline (the goal, its own epic):** a change to `hardware.xml` triggers a builder update, which triggers an update of
  the `syslab_pandapower` model. This map only has to leave the forward build ready to be triggered that way; the pipeline
  itself is charted as a separate effort.

## Out of scope

- Loads on ports as sub-network elements (US-42): consumer code in `syslab_data`, no effect on configuration eras.
- The Streamlit app (US-51): its own map in `syslab_data/.scratch/features/streamlit-app/`.
- Migrating this tracker to GitLab: tracked in `docs/agents/issue-tracker.md`.
- The `syslab_data` user mode that shows an era's figure and changes breakers in a data set by clicking: its own effort; this map
  only provides the figure and label map per model version (see Notes).
