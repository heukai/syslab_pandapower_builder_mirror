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
- **NEVER PUSH, NEVER COMMIT to the lab repositories `syslab/` and `syslab-userspace/`** (read-only sources in the
  workspace; see the workspace `AGENTS.md`). Tell every subagent.
- **Maintainer clarifications (2026-10-21):**
  - **Trust the sources, not our notes.** Where they disagree, `hardware.xml` is authoritative; its labels name bays and
    breakers (they also drive the logging). Every contradiction is reported with its origin (FTP data, lab source, or our own
    notes and model). Two traced so far, both from our side, not from the data: the AirCon move (from the registry text of
    commit `3f6c51a` and US-50, a guess; probably the Gaia move was meant; a turbine's physical location can change without its
    grid connection changing) and the `319_2.json` alias (the FTP headers of 2021-2023 say `Grid`/`Local`; our hand-written
    alias of commit `a9d3a5c` sends `Grid` to `Busbar_A`, `hardware.xml` puts the Grid busbar on B).
  - **Figure versions are configuration eras.** v7 is simply the next era after v6, not a contradiction: era changes are
    found by comparing the v6 figure and the matching older Java and `hardware.xml` versions with the v7 ones.
  - **Planned elements:** 316-2 (PTX, P2XA/B, Cable M1) is only planned and drawn greyed out; not part of a configuration
    era until it appears in `hardware.xml`.
  - **Cable Q1** (330-13 to 119-10, the Kempower fast charger) belongs to the new era; the 330-13 end keeps the
    `hardware.xml` label `EVSE_12` until the lab renames it.
  - **Lag and branches are flagged, not corrected:** a node reads `hardware.xml` only at restart, so logging can lag the
    config; a node may run a feature-branch config for a while. Such periods are flagged as uncertain, not reconstructed.
  - **Label mix-ups are uncertainty:** cables E1/E2 (and maybe others) went through transition periods with not fully correct
    graphics or labels; no consistent ground truth exists for those periods, so they are flagged, not corrected.
  - The rock store is cancelled; spares can disappear when they are allocated to a named unit.
- **Branches:** fixes to the current model may be pushed as usual; the major overhaul (versioning mechanism, dated model
  versions) is developed on a branch until complete. The first era file on that branch is **E6** (maintainer, 2026-10-23):
  the 319-3 breaker issue of 2026-06-25 sits in it, and its commissioning period exercises the operational periods.
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
- The current era's model is behind its sources: 119-10 (`syslab-44`) and Cable Q1 are in `hardware.xml` since 2026-10-05 and
  the Boiler bay since 2026-08-13, but not in the model; 316-2, PTX, P2XA/B and Cable M1 exist only in figure v7 (no
  `hardware.xml`, no Java mapping). The builder reads `syslab/conf`, not the stale `syslab-master-conf/` copy.

## Decisions so far

- [Access to the figure repository and the hardware.xml history](issues/01-access-to-figure-repo-and-hardware-history.md): both lab repos are in the workspace, read-only (never push): `syslab/conf` has `hardware.xml` history from 2015, `syslab-userspace` has figures v4 to v7 and the Java label mappings; the `syslab-master-conf` copy is stale.
- [What in the switchboard overview figure is private or operator-only?](issues/12-what-in-the-figure-is-private.md): nothing private in the committed figures except a personal export path in v4; strip editor metadata and the runtime layers (login, out of service, emergency stop) by name, keep element ids; the Java displet already holds an element-id -> (switchboard, busbar, bay) table that maps 277 of 290 breakers straight to model names, so the label map comes from the Java code, not geometry.
- [What does each source say, and since when?](issues/02-what-each-source-says-and-since-when.md): `syslab/conf` dates configuration changes best (figure and Java change the same day, headers follow months later); dated changes since 2015; AirCon was never on 715-2 since 2015 (registry claim contradicted); the 319_2 Grid-busbar alias is swapped; 316-2 exists only in figure v7.
- [Hypotheses for what one configuration change is](issues/05-hypotheses-for-a-configuration-change.md): an era is a time period marked by a major configuration change (typically a new switchboard), announced by a figure, evidenced by headers, materialized by hardware.xml, starting at the first operational evidence; eras named after the figure (E6, E7, E7b); one base model per era improved as versions 7.1, 7.2, scenario models 7.1/x; the 2023 rebuild is one era with a commissioning period in operational periods.
- [What is one configuration change?](issues/06-what-is-one-configuration-change.md): one YAML file per era in the builder (major change with evidence per step, operational periods, minor changes); one change entry per change (id `E7-001`, date or window, bay-level element by hardware.xml names incl. asset links, change, evidence with role, origin, certainty, in force, proposed/confirmed); the builder proposes, a person confirms; each model version has a public manifest; human-facing parts are proposals to validate with the staff.
- [How do changes from different sources consolidate into eras?](issues/07-consolidating-changes-into-eras.md): per operational period, the last master `hardware.xml` inside it plus confirmed change entries; curated data dated (`valid_from`/`valid_to`); master names win over feature-branch header names (kept as aliases); a commit is dated by its author date, not its merge into master (amended 2026-10-25); date windows are uncertain periods; a consistency check per period refuses bad builds; models not accommodating newer lines are marked behind.
- [How is a forward change found and built?](issues/08-forward-change-and-regular-build.md): `propose` writes proposed change entries (never builds); a model comes from a recorded model development (completeness check with inquiries to staff, consistency check, check against measured data, acceptance); new eras only from a new switchboard or a layout change of the figure; numbering `era.configuration.model` (7.2.3, scenario 7.2.3/x); developed on branch `model-versions`, findings posted to `main`.
- [Why does the 319_3 island not close on 2026-06-25?](issues/10-why-the-319-3-island-does-not-close.md): it closes now (RMSE 0.22 kW at 1 min, all islands of the day closed with the J1A set-up); the old residual predated two fixes, and the remaining spikes revealed the swapped 117-2 CEEx2 meters (fixed); first validation of an era-6 model (6.4.2); tool `island_residuals`.

## Not yet specified

- **Configurations before 2015:** whether eras before the first `hardware.xml` (2015-08-03) are addressed at all.
- **Verification per era:** how each era's model is checked against a baseline period of measured data (US-28), and how an
  unverified era is marked.
- **Era boundaries from the data:** how the topology state index (US-49) and the header eras (US-23) feed or confirm era
  boundaries. First pass done (2026-10-25, `research/column-archive-sample.md`): the header cross-check finds missing
  change entries, an earlier era-6 start and data-name periods (proposed, questions to the staff in the change-log draft);
  eras before 2023 drafted as E0, E2, E3 (header-only) and E4 (2015-2023) from the data and the older figures (step 2, same note).
- **CI/CD pipeline (the goal, its own epic):** a change to `hardware.xml` triggers a builder update, which triggers an update of
  the `syslab_pandapower` model. This map only has to leave the forward build ready to be triggered that way; the pipeline
  itself is charted as a separate effort.

## Out of scope

- Loads on ports as sub-network elements (US-42): consumer code in `syslab_data`, no effect on configuration eras.
- The Streamlit app (US-51): its own map in `syslab_data/.scratch/features/streamlit-app/`.
- Migrating this tracker to GitLab: tracked in `docs/agents/issue-tracker.md`.
- The `syslab_data` user mode that shows an era's figure and changes breakers in a data set by clicking: its own effort; this map
  only provides the figure and label map per model version (see Notes).
