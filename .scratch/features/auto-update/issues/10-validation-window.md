# Which time window does a validation day use?

Type: grilling
Status: resolved
Blocked by:

## Question

A fixed window (06:00-18:00 UTC) with islands taken at one instant fails when breakers change inside the window: on
2026-09-21 and 09-24 the 330-12+330-13 island failed on every model (1.93 / 3.75 kW RMSE) because 330-12 Grid and PV_1
switched during the day; in windows free of the changes every island closed (ticket 02 comment). How does the job choose
its windows?

Draft: per day, the job takes its windows from the island periods (`syslab_data` topology/island_periods, US-51):
stretches in which the breaker states, and so the islands, do not change; each island is checked over the periods it
exists in that are at least 2 hours long within 06:00-18:00 UTC; the day's result per island is the worst of its
periods; switching minutes themselves are left out. A day without such a period for an island marks that island not
checkable on that day.

## Answer

Settled with the maintainer, 2026-11-08: as drafted. Per validation day the job takes its windows from the island periods
(`syslab_data` topology/island_periods, US-51), stretches with unchanged breaker states; each island is checked over its
periods of at least 2 hours within 06:00-18:00 UTC, the minutes around a switch left out; the island's result for the day
is the worst of its periods; an island without such a period is not checkable that day (not failed).

## Comments
- 2026-11-08, implemented by the remote session: `syslab_data` main 48f00a5, `utilities/validate_day.py` (island periods
  from the model's own graph, 2 minutes left out next to each breaker change, periods >= 120 min, 1-min means, an
  island = its switchboards, worst period counts, closes at <= 0.5 kW; output periods.csv, islands.csv,
  model_version.json). 6.7.2: 2026-09-24 PASS (9 close, worst 330-13 0.170 kW; 2 not checkable); 2026-09-21: 9 close,
  5 not checkable, one fails: 12:45-16:08 seven switchboards (117-2, 117-5, 117-6, 319-3, 319-4, 330-12, 330-13) run on
  the 319-4 grid emulator after 330-12's grid breaker opened; with GridEmu as slack P mean -3.03 kW, RMSE 5.22 kW over
  204 min (ticket 11).
