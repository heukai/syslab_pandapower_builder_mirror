# Busbar-Grid breakers of 715-2 and 117-2 are logged

Status: resolved
Filed: 2026-10-27, handover from the syslab_data session (consumer side: syslab_data commit 1f0f7ca)

## Problem

`data/breaker_groups.yaml` marks `715_2_BRK_Grid_Busbar_Grid` (around line 659) and `117_2_BRK_Grid_2_Busbar_Grid`
(around line 289) `logged: false`, and `tests/test_builder.py` (around lines 219-224) asserts that. Both are logged:

- The data log them as `BRK_Grid_Grid` (715_2) and `BRK_Grid_2_Grid` (117_2): FTP cache 715_2 on 2019-06-04 (v02 file)
  and 2026-10-19, 117_2 on 2026-06-25 and 2026-10-20; column archive 715_2 since 2009-12-16, 117_2 since 2023-09-27.
- `syslab_data/topology/breakers.py` `RENAME_BREAKERS` maps those CSV names to the model names
  (`BRK_Grid_Grid` -> `BRK_Grid_Busbar_Grid`, `BRK_Grid_2_Grid` -> `BRK_Grid_2_Busbar_Grid`).
- hardware.xml (syslab-09 for 715-2, syslab-11 for 117-2) has busbar "Grid" and breaker "Grid" / "Grid_2" on it. These
  are the only two boards with a grid busbar: the transformer feeds it, one breaker above the Grid bay with its meter.

Why it matters: syslab_data treats an island as grid-connected on these two boards only when it holds both the Grid
bay and its Busbar-Grid, so the state of this breaker decides whether an island has the grid. With `logged: false`,
`apply_breaker_states` does not warn when the state is missing.

Found while checking: the other 17 switches marked `logged: false` are logged too (column archive, current header eras):
`117_4_BRK_Cable_D1_Manual_Busbar_A` since 2026-01-07 (E6-025) and the 16 `117_6_BRK_EVSE_0n_Busbar_A/B` since
2025-02-14 (data names before that: NEVIC, header period E6-H09). The flag was added on 2026-04-19 (`dc056cf`).

## Acceptance

- Both Busbar-Grid switches are logged (the `logged` default, so the key is left out); likewise the other 17.
- The test asserts that no switch is marked unlogged, and names the two Busbar-Grid switches.
- The rebuilt model (`syslab_pandapower/model_data/breaker_groups.json`) asks for their state, so
  `apply_breaker_states` warns when it is missing.

## Comments

## Answer

Resolved 2026-10-27. All 19 `logged: false` flags removed from `data/breaker_groups.yaml` (the default is logged),
including the two Busbar-Grid switches. `tests/test_builder.py` asserts that no switch is unlogged and names the
Busbar-Grid switches and 117-4 Cable_D1_Manual; the 117-6 EVSE test now expects them logged. Model rebuilt
(`--conf-dir syslab-master-conf/conf --valid-from 2024-08-15`, as before): only `breaker_groups.json` (19 flags) and
`model_version.json` (build date) change; committed to `syslab_pandapower` dev. Tests: builder 59 passed,
syslab_pandapower 26 passed, syslab_data breaker/island/graph subset 196 passed.
