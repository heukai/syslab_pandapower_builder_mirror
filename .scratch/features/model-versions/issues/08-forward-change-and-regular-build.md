# How is a forward change found and built?

Type: grilling
Status: resolved
Blocked by: 07

## Question

The regular build: diff each new release of a source (`hardware.xml`, curated YAML, SVG) against the record, decide
whether it opens a new era or corrects the current one, and build the model versions. Designed so that a CI/CD pipeline can
trigger it later (fog: its own epic).

## Answer

Settled with the maintainer, 2026-10-23 (three rounds).

1. **Change entry** is the name of one record in an era file (`E7-001`); "line" means a cable in the model.
2. **Two steps, `propose` and model development.** `propose` reads new source releases and writes *proposed* change entries
   (and, for a major indicator, a proposed new era with its first operational period). It never builds. A model comes out of
   a recorded **model development**: collect the confirmed in-force change entries; completeness check, listing missing
   parameters (Cable Q1's length and type, a bay's equipment) as **inquiries** to the staff, open or answered; consistency
   check per operational period; candidate model only when every inquiry is answered or covered by a declared, flagged
   placeholder; check against existing measured data (island residuals over periods with data); version and manifest only on
   the maintainer's acceptance. The development record (inquiries, checks, results) is the evidence behind the manifest.
   Building is explicit and investigative, never automatic.
3. **Sources and memory.** `propose` reads master commits of `syslab` touching `conf/*/hardware.xml`, `syslab-userspace`
   commits touching the overview figure or the displet, the builder's curated data and new header eras in the column archive,
   always by `git show` at a revision (never checkout, commit or fetch in the lab repos), and remembers per source the last
   commit it read, in a small file in the builder.
4. **What signals a new era (major):** the `hardware.xml` of a switchboard node showing a new switchboard, or a **layout
   change**, which refers to the overview figure: a new figure file, or a figure commit that changes the drawing beyond labels
   (checked by a person). Device nodes' `hardware.xml` (EVSE, boiler, booster heater on `syslab-32`, ...) never does; bay
   changes and renames (in `hardware.xml` or as figure labels) are minor.
5. **Three-level numbering `era.configuration.model`:** `7` = era (new switchboard or layout change); `7.2` = configuration
   revision (the era's second set of confirmed minor change entries, listing the entries it confirms); `7.2.3` = the third
   model of configuration 7.2, improved and validated over time; `7.2.3/summer-2027` = a scenario model derived from it.
   Versioning is explicit: each model release names the periods it was validated on.
6. **Where it lives:** the overhaul (era files, `propose`, model development, checks) is developed on the builder branch
   `model-versions` until it is sufficiently operational; quality improvements through more validation data come with
   time. `main` is informed meanwhile: whatever `propose` finds is posted as a note or ticket in the builder's tracker on
   `main` (e.g. "new switchboard 119-10 seen in master on 2026-10-05"). Fixes to today's model keep going to `main`.

The future CI/CD pipeline (fog, its own epic) maps onto this: a source change runs `propose` and opens a merge request for a
person to confirm; model development stays a human-led process.
