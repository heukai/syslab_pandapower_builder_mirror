# How does validation treat an island held up by a converter (grid emulator)?

Type: grilling
Status: resolved
Blocked by:

## Question

On 2026-09-21, 12:45-16:08, seven switchboards ran as one island on the 319-4 grid emulator (330-12's grid breaker
open). With the emulator as slack the island misses by a steady -3.03 kW (RMSE 5.22 kW). An island formed by a converter
is an experiment set-up in all likelihood (someone set the emulator to form a grid), and the model knows nothing of its
operation (losses, which side its meter measures, loads plugged in for the experiment). Does such an island count?

Draft: an island whose only grid-forming unit is a converter (grid emulator, B2B) is an **experiment island**: not
checkable unless the day has a declared set-up for it (like the J1A set-up), and listed separately in the merge request.
6.7.2 then stands validated on 2026-09-21 and 09-24 (every checkable, grid-connected island closes). The -3 kW offset is
noted for a later look at the emulator's metering (phase 2), not a reason to fail the model.

## Answer

Settled with the maintainer, 2026-11-08, with a caveat: it is a lab, there are always experiments, so "experiment" is not
the criterion. The criterion is **a converter driving the grid**: an island whose only grid-forming unit is a converter
(grid emulator, B2B) is not used for validation by default, because of the potential complexities (operation, losses,
metering side). This is a **guideline, not a hard rule**: the job marks such islands "converter-driven, not used" and
lists them separately in the merge request; a person may still include one (for example with a declared set-up). Islands
on the utility grid are validated as usual, whatever experiment runs. Consequence: 6.7.2 stands validated on 2026-09-21
and 09-24 (every checkable grid-connected island closes); the -3 kW offset of the emulator island on 09-21 is noted for a
later look at the emulator's metering.

## Comments
- 2026-11-08, implemented by the remote session: `syslab_data` main c528a26 (`validate_day`: slack a grid-forming
  converter -> "converter-driven, not used", worst figures still shown; an island with grid and converter periods counts
  only its grid periods; `--include-converter-islands`; periods.csv gains `slack_kind`). Builder `model-versions`
  9a40cbd: 6.7.2 validated on 2026-09-21 (every checkable grid-connected island closes, worst 716-2 0.32 kW; the
  grid-emulator island converter-driven, not used) and 09-24 (worst 330-13 0.17 kW).
