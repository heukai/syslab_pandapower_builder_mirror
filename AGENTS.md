# AGENTS.md (syslab_pandapower_builder)

This is a separate git repository (`git.elektro.dtu.dk/kheu/syslab_pandapower_builder`).
For workspace-wide dev environment, testing, and PR conventions shared with
sibling packages (`syslab_data`, `syslab_pandapower`, ...), see the outer
workspace `AGENTS.md` one directory up.

## Agent skills

### Issue tracker

Local markdown under `.scratch/features/`, migrating to GitLab once `glab` auth
against `git.elektro.dtu.dk` is working. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary, unchanged (`needs-triage`, `needs-info`, `ready-for-agent`,
`ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` + `docs/adr/` at this repo's root (neither exists
yet; until then the shared glossary and ADRs live in `syslab_data`). See
`docs/agents/domain.md`.
