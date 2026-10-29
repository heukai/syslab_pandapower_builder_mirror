# How are model versions published and selected?

Type: grilling
Status: open
Blocked by: 06, 13

## Question

The side-by-side layout of model versions in `syslab_pandapower` (public: no private data), `model_version.json` per
era, how `syslab_data` selects the model by the date of the data and says so, and what a request spanning an era change does
(split or warn).

## Comments

- 2026-10-22 (syslab_data, US-51 app map, ticket 17): the app's topology-finding batch (version 2) takes era boundaries and
  model selection from this ticket's answer and keeps no era table of its own. Until then it uses E6 from 2023-06-23
  (commissioning until 2023-10-19) and E7 from 2026-10-05 as declared constants, gives residuals from 2023-10-19 on (per
  island in E7, none where the model lacks a node), refuses windows before 2023-06-23 and splits periods at era boundaries.
  See `syslab_data/.scratch/features/streamlit-app/issues/17-current-configuration-era.md`.
- 2026-10-30, **staff answers to the handout's six questions** (relayed by the maintainer):
  1. *Choosing a model:* by date. Levels 1 and 2 of the number (era, configuration revision) follow the lab's changes, so
     the date of the data selects them; within that revision, the highest third level (the most validated, most accurate
     model) is taken. Our draft held.
  2. *Validated:* not discussed; 0.5 kW RMSE (largest island, 1 min) seems fine.
  3. *Data spanning an era change:* **warn and use one model** (an era change inside a request is unlikely). Our draft
     (split) did not hold. Note: the syslab_data app (ticket 17 above) currently splits at era boundaries.
  4. *How many versions:* models are small, keep them all; but third-level versions only add knowledge, not lab changes,
     so the superseded ones **fade into the git history** instead of being published side by side.
  5. *Who records a validation:* the toolbox that generates the models (this builder) should also hold the validation
     (today `syslab_data/utilities/island_residuals.py`).
  6. *Which days:* no days named yet; typical experiments repeat every year with slightly modified configurations, some
     in June, some in November or March.
  New: a **fourth level** for variants of a model version that add cables or equipment for one experiment, with an
  alphanumeric identifier such as a project code (replaces the scenario notation `6.4.2/j1a-2026`; form to settle, e.g.
  `6.4.2.J1A`).
