# What should a phase-2 detector find, and how does it propose?

Type: prototype
Status: resolved
Blocked by: 02

## Question

A throwaway prototype of one phase-2 detector on validation results: from the residuals of a day (`island_residuals`
output: residual per island, partner channels and their correlation, breaker states), find a model error the sources do
not show and turn it into a proposal a person can confirm. First candidate: a swapped or mislabelled meter, as the 117-2
CEEx2 swap found on 2026-06-25 (spikes in the 319-3 island residual followed one socket meter; the swap closed the
island). Run against that day before and after the fix: the prototype should find the swap on the "before" model and
nothing on the "after" model. Also look at: steady meter offsets (the -0.16 kW of the 319-3 island). What does the
proposal look like (a third-level model improvement, e.g. 6.6.3, with the evidence figures)?

Runs in the remote session (data access); the question and the verdict are settled here.

## Answer

Prototype run in the remote session, 2026-11-07; verdict accepted here. **PASS:** on 2026-06-25 the detector finds the
117-2 CEEx2 swap on the model before the fix (syslab_pandapower 8376311^) and nothing on the fixed model (8376311, and
dev efebbdc).

**Rule (first phase-2 detector, "swapped socket meter"):** in an island that does not close, a socket meter whose
1-min changes follow the residual (|corr| >= 0.5, slope 0.6 to 1.6) while the model puts it on a port outside the
island and the other port of the same bay inside -> propose swapping the two ports' meters and build the candidate.
(Opposite-sign pairs did not work: the unused socket reads exactly 0.) On the "before" model: P_CEEx2_2 corr 0.655,
lag 0, slope 1.07; the candidate equals the fixed model.

**Form of the proposal** (a third-level model improvement, e.g. 6.6.3): the change (port -> meter, now -> proposed);
the evidence (channel, corr, lag, slope, which port it is assigned to and which is in the island, the island figure
before and after); the closure check (rerun on the candidate: island RMSE before -> after, other islands unchanged).

**Caveat:** this run used no experiment set-up; 2026-06-25 is the J1A experiment day (converter between `J1A Port` and
`319-2 CEEx2.B`, variant 6.6.2.J1A; task 5c ran with `--setup`). Without it the 310-2 island shows the converter
(residual = -P_Grid, `Cable_J1A` flow with the far end open) and the 319-3 island stays at 0.61 kW instead of 0.22 kW.
Rerun with the set-up requested; findings 1 and 3 of the remote session are expected to vanish. Findings 2 (330-13
island +0.14 kW steady at 0.20 kW RMSE: a meter offset?) and 4 (117-4/117-5 island has no residual: slack 117-4 Grid
without P on 2026-06-25, the day after data-name period D27) stand until the rerun.

## Comments
- 2026-11-07, rerun with the J1A set-up (remote session): **a regression in syslab_data** made every island's RMSE too
  high since b6aee8a (US-51 v2 ticket 02, 2026-10-25): `find_test_periods.read_board_minutes`/`load_day` give P/Q/U as
  the first valid sample of each minute instead of the minute mean (right for breakers, wrong for power balances across
  boards that sample at different instants); 6c3442d reproduces task 5c exactly. Fix tested in a scratch copy
  (`load_day(..., meas_how="mean")` for island_residuals, breakers still first samples), not committed, waiting for the
  maintainer; `find_flow_partner` probably affected too. With set-up and fix (06-18 UTC, 1 min; P mean / P RMSE kW):
  319-3 island -0.161 / 0.218; 319-2 0.016 / 0.099; 330-13 0.135 / 0.200; 310-2 0.007 / 0.059; 716-2 0.016 / 0.017;
  117-4/117-5 NaN (see ticket 09). Same for the published model and the `--model-dir` build. Before model: 319-3
  -0.229 / 0.743. Detector with set-up: finds the swap more clearly (P_CEEx2_2 corr 0.980, slope 0.94), nothing on the
  fixed model. Findings 1 and 3 withdrawn (set-up plus regression). Finding 2 (330-13 offset +0.135 kW) stays; an offset
  rule needs a slope condition on the partner, not only a correlation threshold.
