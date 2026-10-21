# What should a human-readable change log look like for the lab staff?

Type: prototype
Status: claimed
Blocked by: -

## Question

A rough change log, built by hand from the changes already known (AirCon 715_2 -> 319_2, the Gaia move, the CEEx2 bays
with two sockets, the SVG 6 -> 7 differences), in a form the technical staff can read, correct and add to without the code.
It is the frame for the first conversation with them (US-25) and is tried in the equipment-catalog task. Question: which
shape (per date, per switchboard, per element; table or prose; where it lives) makes staff contribute?

## Comments

**Draft for the maintainer's reaction (2026-10-21).** Throwaway branch `prototype/configuration-change` (commit `b9b48d8`):
`.scratch/features/model-versions/prototype/CHANGELOG-proposal.md`, a hand-built change log of the dated changes found so far
(eras v4, v6, v7, planned 316-2), newest first, one table per era (date, switchboard, change, sources, certainty), with the
open questions for the staff at the end. The HTML prototype of the configuration-change ticket also generates a change log from
its records, to compare.
