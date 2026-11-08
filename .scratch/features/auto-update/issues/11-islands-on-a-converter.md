# How does validation treat an island held up by a converter (grid emulator)?

Type: grilling
Status: open
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

## Comments
