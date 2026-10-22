# Hypotheses for what one configuration change is

Type: prototype
Status: resolved
Blocked by: 02

## Question

Agent exploration: from the source inventory, write two or three candidate shapes of a configuration-change record
(granularity, fields, identity and aliases per ADR-0005, where it lives, how staff would edit it), each applied to real cases:
the AirCon move, the CEEx2 sockets (a bay that became two sockets), version 7's 316-2 / 119-10 / Cable Q1, a rename (`Solar`
-> `PV`). The maintainer reacts; the grilling ticket decides.

## Comments

**Prototype ready for the maintainer's reaction (2026-10-21).** Throwaway branch `prototype/configuration-change` (commit
`b9b48d8`, pushed to `kheu-home`): `.scratch/features/model-versions/prototype/configuration-change.html`, a single file to
open by double-click. Input: the v6 -> v7 comparison (third pass of the source-inventory ticket).

The same source observations (hardware.xml, Java displet, figure, FTP header, curated cable; real commits of 2026-08-13 and
2026-10-05 plus two hypothetical future ones) are recorded three ways, with eras and a change log generated:

- **H1, one record per element edit** (bay X added or renamed), dated by its authoritative source, every other source as
  evidence; status *in force*, *evidence only* (e.g. the Java relabel of 330-13 `EVSE_12` -> `Cable_Q1`) or *planned* (316-2).
- **H2, one record per change event** ("119-10 connected"), holding its element edits and sources; it opens an era unless it
  is only a rename (a setting to try).
- **H3, one record per era**: a snapshot of the whole configuration; changes are computed diffs.

Scenarios: Boiler rename (is a rename an era?), the real v6 -> v7 change, logging lag (header after config), display first
and config later, planned becomes built.

Agent's reading, for discussion (not a decision): H1 as the stored unit (small, one source line each, easy for staff to correct
line by line), H2 as the human grouping that names an era and drives the change log, H3 derived by the builder for each model
version, never edited by hand.

**Maintainer's reactions (2026-10-22), reflected in prototype rounds 2-3 (`91edc49`, `cc4526f`):**

- H2 (change events) was unclear and is dropped. The era is best described as in H3 (a snapshot) plus the change log;
  H1 element edits stay as the log lines.
- **Era = a time period marked by a major configuration change**, typically a new switchboard or another major
  reorganization. "Major" resolves the conflict with "every change opens an era". The major change is announced by a new
  figure, evidenced by new headers (the node often runs a feature-branch config well before master), and materialized by
  `hardware.xml` in master; all of that belongs to the same era. Planned becoming built (316-2) is the important case.
- Eras are named after the figure (E6, E7; E7b for a further era under the same figure).
- **One base model per era**, improved over the era's life (calibrated at lab events such as yearly experiments), published
  as model versions 7.1, 7.2, ...; scenario models derive from a base version. Each records accommodated changes,
  validation instances and optional validity periods. The base model applies anywhere in its era, with fewer guarantees
  outside its validations. A model belongs to the era it models, not the one it was published in.
- Glossary updated in `syslab_data` (`45883a0`): Major Configuration Change, Configuration Era, Base Model, Model Version.

Still open for the decision: the era start rule (first operational evidence, `hardware.xml` only, or any evidence), the
naming scheme for scenario models (`7.1/summer-2027`), and whether 330-12 / 330-13 (2023) opened eras inside E6.

## Answer

Settled with the maintainer, 2026-10-22, over three prototype rounds (branch `prototype/configuration-change`: `b9b48d8`,
`91edc49`, `cc4526f`; `.scratch/features/model-versions/prototype/configuration-change.html` and `CHANGELOG-proposal.md`).

- **Two levels, not one record.** H1 (element edits) are the log lines; H3 (snapshots) describes an era; H2 (change events) was
  unclear and is dropped.
- **Configuration era = a time period marked by a major configuration change** (typically a new switchboard, or another major
  reorganization; also planned equipment becoming built). Minor changes are logged inside the era. The major change is
  announced by a new figure, evidenced by new data headers (often from a feature-branch config, well before master) and
  materialized by `hardware.xml` in master; all of that belongs to the same era.
- **Era start = first operational evidence** (headers or `hardware.xml`, whichever comes first); a figure alone only announces.
- **Naming:** eras after the figure (E6, E7; E7b for a further era under the same figure); model versions per era (7.1, 7.2);
  scenario models derived from a base version (`7.1/summer-2027`). Accepted.
- **One base model per era**, improved over the era's life (calibrated at lab events such as yearly experiments), applying
  anywhere in the era with fewer guarantees outside its validations; each model version records accommodated changes,
  validation instances and optional validity periods; a model belongs to the era it models, not the one it was published in.
  A date selects its era, then a model validated on it, else one whose validity covers it, else the latest base version.
- **The 2023 rebuild is one era (E6) with a commissioning period** divided into **operational periods**, since experiments
  ran during commissioning. From `syslab/conf` (master): 319-3 on `syslab-52` 2023-06-23 (rebuild; figure v6 and Java the
  same day), 319-4 2023-07-02, 330-12 and 330-13 2023-10-06, 310-2 2023-10-19; figure v6 updated step by step (2023-10-05
  as-built 330-12/330-13, 2023-10-19 final 310-2). Headers came later (319_4 2023-12-01, 330_13 2023-12-19, 330_12
  2024-06-10, 310_2 2025-02-24). 776-1 left the config on 2024-05-23 (not a grid node of the model). Only other major change
  since: 119-10 on 2026-10-05 (E7).
- Glossary (`syslab_data/CONTEXT.md`): Major Configuration Change, Configuration Era, Commissioning Period, Operational
  Period, Base Model, Model Version.

For the decision ticket "What is one configuration change?": the record's fields, storage and format, how operational periods
are recorded inside a commissioning period, and whether a model version can be validated per operational period.
