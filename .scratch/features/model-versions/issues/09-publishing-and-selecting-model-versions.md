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
