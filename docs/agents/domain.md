# Domain Docs

How the engineering skills should consume this repo's domain documentation
when exploring the codebase. Repo root for all paths below is
`syslab_pandapower_builder/` (the outer workspace folder is not
version-controlled).

## Before exploring, read these

- **`CONTEXT.md`** at this repo's root, if it exists.
- **`docs/adr/`** at this repo's root, if it exists: read ADRs that touch the
  area you're about to work in.

Neither exists yet. Until they do, the shared domain vocabulary and the
decisions that shape this builder live in the sibling `syslab_data` repo:

- `../syslab_data/CONTEXT.md` — glossary (switchboard, bay, busbar, breaker,
  cable, port, equipment catalog, bus/switch, topology era, ...).
- `../syslab_data/docs/adr/` — notably ADR-0002 (two-source grid model:
  `hardware.xml` + curated YAML) and ADR-0004 (temporary equipment recorded
  per experiment, not in the model).

Read those instead. Don't flag the missing local files; the `/domain-modeling`
skill creates them lazily when builder-specific terms or decisions actually
get resolved.

This is a single-context repo: no `CONTEXT-MAP.md`, one `CONTEXT.md`, one
`docs/adr/`.

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor
proposal, a hypothesis, a test name), use the term as defined in `CONTEXT.md`
(this repo's, or `syslab_data`'s until this one exists). Don't drift to
synonyms the glossary explicitly avoids.

If the concept you need isn't in the glossary yet, that's a signal: either
you're inventing language the project doesn't use (reconsider) or there's a
real gap (note it for `/domain-modeling`).

## Flag ADR conflicts

If your output contradicts an existing ADR (here or in `syslab_data`), surface
it explicitly rather than silently overriding, e.g.:

> _Contradicts ADR-0002 (two-source grid model), but worth reopening because…_
