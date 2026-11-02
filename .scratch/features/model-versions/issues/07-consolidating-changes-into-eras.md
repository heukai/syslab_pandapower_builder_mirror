# How do changes from different sources consolidate into eras?

Type: grilling
Status: resolved
Blocked by: 06

## Question

Authority per kind of element (ADR-0002: `hardware.xml` for breakers and bays, curated data for cables, the SVG as
evidence), what happens when sources disagree (the SVG ahead of `hardware.xml`), changes known only to a date window, and how a
set of changes becomes era boundaries and one consistent configuration per era.

## Answer

Settled with the maintainer, 2026-10-23. Already decided on the way (hypotheses and configuration-change tickets):
authority per source (`hardware.xml` for switchboards, bays and breakers; curated data for cables; figure and Java as
evidence), not-in-force claims kept as lines, eras marked by a major change and starting at the first operational evidence,
the 2023 rebuild as one era with a commissioning period. This ticket adds how a configuration is assembled per era:

1. **`hardware.xml` of an operational period** = the last master commit inside that period (later commits in a period are
   corrections); confirmed change entries override that revision where they say otherwise.
2. **Curated data gets dates**: every entry of `cables.yaml`, `socket_meters.yaml`, breaker groups and inline ports carries
   `valid_from` / `valid_to`; the builder selects the entries in force for each operational period (Cable Q1 from 2026-10-05).
3. **Headers ahead of master** (feature-branch configs): master's `hardware.xml` names win once master catches up; each
   differing name becomes a proposed rename line; the header names stay as aliases for the early period so its data stays
   readable, uncorrected.
4. **Date windows**: a change known only to a window is an uncertain period; the change takes effect at the window's end;
   no model counts as validated inside the window; data inside it stays as logged, flagged.
5. **Consistency check per operational period**, refusing the build on failure: every cable end lands on a bay or busbar of
   that period; socket meters and breaker groups refer to existing breakers; no confirmed line contradicts `hardware.xml`
   without a declaration. Messages name the line to fix.
6. **A model that falls behind**: a confirmed line newer than a model's build and not accommodated by it marks the model
   *behind* for dates after the change; selection still offers it, with the warning.

As for the configuration-change ticket, human-facing parts are proposals to validate with the staff.

## Comments

**2026-10-25, amendment (maintainer):** "the last master commit inside the period" is dated by the commit's **author date**
(when the configuration was written), not by the date it reached master's first-parent line by a merge, which is often weeks
later (310-2 Boiler: written 2026-08-13, merged 2026-09-12). The data files follow the author date. The merge date is kept
as evidence. Found by the column-archive cross-check (`research/column-archive-sample.md`), which also proposed
**data-name periods** (era file section `header_periods`) and an era-6 start of 2023-06-16; both are questions for the staff
in the change-log draft (questions 7 and 8).
