# Which time window does a validation day use?

Type: grilling
Status: open
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

## Comments
