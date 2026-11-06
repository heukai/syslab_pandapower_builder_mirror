# What does the builder bot's merge request contain?

Type: grilling
Status: resolved
Blocked by:

## Question

The content and form of one merge request from the bot, so a person can confirm it quickly.

Draft: one merge request per revision: the era-file changes (proposed change entries, data-name periods, the model
version with status and validation record), the regenerated `VERSIONS.md`, and a short description (what was built from
which configuration date, the validation day and its residuals, what was skipped and why). Model files stay in
`outputs/` on the sandbox, not in git. Open: one merge request per revision or per run; who reviews.

## Answer

Settled with the maintainer, 2026-11-06: one merge request per revision, containing
- a **change list**: the change entries, data-name periods and model version it proposes, each with its evidence;
- the **figures of the residuals** of the validation day (per island: residual over the day, the topology), so the
  reviewer sees how well the model closes without opening the sandbox;
- the era-file changes and the regenerated `VERSIONS.md`;
- what was skipped and why.
Model files stay in `outputs/` on the sandbox, not in git. Figures are attached to the merge request (GitLab upload), not
committed, so the repository does not grow with images (proposal; to check in ticket 06 whether the bot can upload).

## Comments
