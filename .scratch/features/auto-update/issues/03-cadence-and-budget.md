# How often does the cron job run, and within which budget?

Type: grilling
Status: open
Blocked by:

## Question

Cron cadence and limits on the sandbox: how much is done per run, how much data may be downloaded and kept, how long a
run may take, and what happens when a budget is reached.

Draft: nightly, one revision per run (build plus validation of one day); a data budget for the day files of validation
(the cache budget `SYSLAB_CACHE_MAX_GB` on the sandbox); a run stops cleanly at its budget and continues the next night.
Facts needed from the remote session: free disk, download speed, time of one `island_residuals` day with all boards.

## Comments
