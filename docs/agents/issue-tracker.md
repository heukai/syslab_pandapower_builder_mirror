# Issue tracker: Local Markdown (temporary — migrating to GitLab)

Issues and specs for this repo live as markdown files under `.scratch/features/`.

**Migration plan:** this repo's real remote is `git.elektro.dtu.dk/kheu/syslab_pandapower_builder`
(self-hosted GitLab). Local tracking is a stopgap until `glab auth login --hostname
git.elektro.dtu.dk` succeeds from this machine. Once that works, re-run
`/setup-matt-pocock-skills` and switch this file to the GitLab tracker template;
migrate any still-open `.scratch/features/` tickets to GitLab issues by hand.
Do this together with the same migration in `syslab_data`.

## Conventions

- One feature per directory: `.scratch/features/<feature-slug>/`
- The spec is `.scratch/features/<feature-slug>/spec.md`
- Implementation issues are one file per ticket at
  `.scratch/features/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`,
  never a single combined tickets file
- Triage state is recorded as a `Status:` line near the top of each issue file
  (see `triage-labels.md` for the role strings)
- Comments and conversation history append to the bottom of the file under a
  `## Comments` heading
- A change that ripples into `syslab_data` (model schema, BRK-name ↔ switch-index
  mapping, serialized model layout) gets a ticket here for the builder side and
  a cross-referencing ticket in `syslab_data/.scratch/features/` for the
  consumer side.

## When a skill says "publish to the issue tracker"

Create a new file under `.scratch/features/<feature-slug>/` (creating the
directory if needed).

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user will normally pass the path or
the issue number directly.

## Wayfinding operations

Used by `/wayfinder`.

- **Map**: `.scratch/features/<effort>/map.md` (the Notes / Decisions-so-far / Fog body).
- **Child ticket**: `.scratch/features/<effort>/issues/NN-<slug>.md`, numbered
  from `01`, with the question in the body. A `Type:` line records the ticket
  type (`research`/`prototype`/`grilling`/`task`); a `Status:` line records
  `claimed`/`resolved`.
- **Blocking**: a `Blocked by: NN, NN` line near the top. A ticket is unblocked
  when every file it lists is `resolved`.
- **Frontier**: scan `.scratch/features/<effort>/issues/` for files that are
  open, unblocked, and unclaimed; first by number wins.
- **Claim**: set `Status: claimed` and save before any work.
- **Resolve**: append the answer under an `## Answer` heading, set
  `Status: resolved`, then append a context pointer (gist + link) to the map's
  Decisions-so-far in `map.md`.
