# Map: auto-update job (backfill and discovery of model versions)

## Destination

A spec for a **scheduled job on the sandbox** (the remote machine with data access) that first **backfills** model
versions for past configuration revisions (era 6 down to era 4 and earlier), builds and validates them, and proposes
everything through **merge requests from a builder bot**; later it also watches for new changes. Ready for `/to-spec`
and `/to-tickets` in the remote session.

## Notes

Settled while charting (maintainer, 2026-11-06):

- **Scheduler: a scheduled job on the sandbox for now** (a systemd user timer, ticket 03; the sandbox has no cron). A GitLab scheduled pipeline (CI/CD) is the right future approach,
  but only once the builder is fully rolled out, with the old model versions built. Until then cron.
- **First job: backfill.** The job works through past eras and revisions and builds their models first; watching for new
  changes (forward detection) comes after.
- **Proposals reach `main` only through merge requests from a builder bot** (bot branches). A person confirms every
  change entry, revision and validation; nothing is published automatically.
- **Division of work:** design questions are settled in the local session (this map, its tickets: only
  `.scratch/features/auto-update/`); code, era files, model builds and validation runs belong to the remote session
  "Syslab pandapower builder assessments" (syslab-model-data-05), which owns the builder otherwise.
- **Phases** (ticket 05): phase 1 answers "what was the grid on that day?" from the sources (hardware.xml
  history, data headers, figures, curated data): proposals, one model per revision, validation with its residuals.
  Phase 2 answers "how do we make the model more accurate from the data?" (swapped or mislabelled meters, meter offsets,
  cable parameters): third-level model improvements.
- **Stages of one run** (draft): sync (lab repos read-only, data headers) -> detect (against the era files) -> propose
  (bot branch, merge request) -> build (`build_model --conf-date`) -> validate (`island_residuals`) -> report.
- **What exists** (map "dated model versions", branch `model-versions`): era files E0-E7 and `eras.py`;
  `conf_snapshot.py` and `build_model --conf-repo --conf-date --model-version`; dated curated data
  (`valid_from`/`valid_to` in `breaker_groups.yaml`); research scripts `header_xcheck.py`, `data_name_periods.py`;
  in `syslab_data`: the column archive and its scanner, `utilities/island_residuals.py`, `cache_cleanup`.
  The validate stage: `island_residuals --model-dir <build>/model_data` takes network and topology from a given build and
  writes its `model_version.json` with the results (remote session, 2026-11-06; in `syslab_data`, not committed yet).
- **Rules that hold:** never commit or push to the lab repositories `syslab/` and `syslab-userspace/`;
  `syslab_pandapower` is public (no lab refs, private data or paths); no whole data files downloaded on the maintainer's
  machine (weak connection); the staff decisions on model versions (map "dated model versions", ticket 09 comments).

## Decisions so far

<!-- one line per resolved ticket -->

- [In which order does the backfill build past revisions?](issues/01-backfill-order.md): newest first (6.6 to 6.0, then era 4); a revision whose curated data do not cover its date is skipped and reported, never guessed.
- [What does the builder bot's merge request contain?](issues/04-merge-request-contents.md): one per revision, with a change list, the residual figures of the validation day, the era-file changes and what was skipped; model files stay on the sandbox.
- [Phase 1 only, or an early residual-based detector?](issues/05-phase-1-scope.md): the job starts with phase 1; phase 2 is prototyped in this map (ticket 07).
- [On which days is each revision validated, and when is it accepted?](issues/02-validation-days.md): three days per revision; days with only meter-name or spelling differences count, breaker-name periods are skipped (6.1, 6.2 for now); islands with a switchboard lacking data are not checkable, not failed.
- [How often does the job run, and within which budget?](issues/03-cadence-and-budget.md): a systemd user timer with lingering on the sandbox (no cron there), one revision per night, own downloads deleted after validation, stop below 10 GB free.

## Not yet specified

- **Forward detection:** how a new hardware.xml commit, figure change or header change on a later day becomes a proposal
  (the detect stage after the backfill).
- **Moving to a GitLab scheduled pipeline** (runner on the sandbox) once the builder is rolled out; the CI/CD epic of the
  map "dated model versions".
- **Alerts:** how a failed or stuck run reaches the maintainer.

## Out of scope

- Publishing model versions in `syslab_pandapower` (map "dated model versions", ticket on publishing and selection).
- The Streamlit app.
