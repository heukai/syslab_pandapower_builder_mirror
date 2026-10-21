# Hypotheses for what one configuration change is

Type: prototype
Status: claimed
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
