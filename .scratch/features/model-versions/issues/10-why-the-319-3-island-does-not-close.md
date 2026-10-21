# Why does the 319_3 island not close on 2026-06-25?

Type: task
Status: claimed
Blocked by: -

## Question

The largest island on 2026-06-25 (slack 319_3 Grid) keeps a residual of RMSE ~5 kW, mean -0.24 kW at 30 min, unrelated
to the converter. Find whether the cause is on the model side (lines, bays of 319_3/319_4, curated cables) or the mapping side,
so that the reference era closes before older eras are derived from it. Data work runs on the remote (no local downloads).

## Comments

**Step 1: what exactly is meant (2026-10-21, main session; for the maintainer to confirm).**

*Where the claim comes from.* Our own notes only: the handover `syslab_data/docs/agents/remote-operations.md` (open task 3)
and the US-53 observations, from a remote-session run of `simulate_setup` on 2026-06-25 (breaker states at 10:00 UTC,
measurements 06:00-18:00 UTC resampled to 30 min). It was measured before the `syslab_pandapower` fix of 2026-10-19 (a missing
Grid measurement is NaN, not 0; never another board's Grid bay), and before US-53 part B (one bus per CEEx2 socket). Both can
change the number.

*What "closes" means.* The island is the connected component that contains the 319-3 Grid bay (the slack, fed by the
transformer). `IslandSimulation` drives every measured bay in the island as a P/Q injection from its own meter, runs the power
flow, and compares the slack's simulated P with the measured `P_Grid` of 319-3. The island *closes* when that residual is near
zero (other islands of the same day: ~0.01 kW). Here: mean -0.24 kW, RMSE ~5 kW. A small mean with a large RMSE points to
something that fluctuates (an unmeasured or mis-mapped load or generator, a meter with the wrong sign, or time misalignment
between nodes on fast-changing PV/wind), not to a constant model loss: line losses of the model would give a steady offset.

*Checked locally (fixture `syslab_data/tests/fixtures_1min_2026`, 06-18 UTC):* no breaker of 319-2, 319-3, 319-4, 310-2 or
330-12 changes state during the day, so the 10:00 island holds all day on those boards. The fixture lacks 117-x, 715-2, 716-2
and 330-13, so the island cannot be rebuilt here; the data work runs on the remote (no local downloads).

*Questions for the maintainer before any data work:*
1. Is the target "the residual of the island with the 319-3 Grid slack, 06-18 UTC on 2026-06-25, re-run with today's model
   and library" (so the two fixes above are included first)?
2. Which boards are in that island at 10:00? (The remote run knows; to be listed in the first data step.)
3. Which equipment in it is known to be unmetered or metered elsewhere on that day (mobile units, the P2X/PTX planned
   bays, PV inverters behind a bay meter)?
4. Is 1-min resolution and per-node time alignment worth checking first (cheap), before model-side checks of 319-3/319-4
   lines and bays?

*Proposed order:* re-run on the remote with the current model; list the island's bays with measured/NaN status; residual
per time step against each bay's P (correlation, as the flow-partner tool does) to find the fluctuating part; only then the
model side (lines and bays of 319-3/319-4). The result lands here; a model fix, if any, is pushed as a normal fix (not on the
versioning branch).
