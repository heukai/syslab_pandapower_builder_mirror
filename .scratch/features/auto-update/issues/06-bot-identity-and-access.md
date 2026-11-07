# How does the bot push branches and open merge requests from the sandbox?

Type: task
Status: open
Blocked by:

## Question

Set up and record (remote session, with the maintainer for credentials): the bot's identity on git.elektro.dtu.dk,
push rights limited to bot branches of the builder, a way to open merge requests from the sandbox (API token or `glab`;
`glab` login does not work from the maintainer's machine yet), read access to the lab repositories and the data sources.
Answer: what was set up, where the credentials live (not in a repository), and any limits found.

## Comments
- 2026-11-06, remote session: the sandbox has no access to the lab repository `syslab` (git.elektro.dtu.dk/syslab/syslab)
  yet, so there is no `syslab/` clone there; the sync and build stages (`build_model --conf-repo`) need read access to
  it (and to `syslab-userspace` for the figures). Model 6.7.1 is validated from files copied over from the maintainer's
  machine meanwhile.
- 2026-11-07: also needed on the sandbox, an admin step: `loginctl enable-linger kheu`, so the job's systemd user
  timer runs without a login (ticket 03).
- 2026-11-07, maintainer: the sandbox now has a copy of `syslab/conf`. Dated builds (`build_model --conf-repo
  --conf-date`) and column maps (ticket 08) need its git history, not only today's files: to check on the sandbox.
  Read-only as everywhere: never commit or push to the lab repositories.
