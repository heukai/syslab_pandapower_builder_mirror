# How often does the cron job run, and within which budget?

Type: grilling
Status: resolved
Blocked by:

## Question

Cron cadence and limits on the sandbox: how much is done per run, how much data may be downloaded and kept, how long a
run may take, and what happens when a budget is reached.

Draft: nightly, one revision per run (build plus validation of one day); a data budget for the day files of validation
(the cache budget `SYSLAB_CACHE_MAX_GB` on the sandbox); a run stops cleanly at its budget and continues the next night.
Facts needed from the remote session: free disk, download speed, time of one `island_residuals` day with all boards.

## Answer

Settled with the maintainer, 2026-11-07:
1. **Scheduler:** a systemd user timer for the user `kheu` on the sandbox, with lingering enabled
   (`loginctl enable-linger kheu`, an admin step, ticket 06), so it runs without a login; logs in the journal. Same role
   as the cron job of the map's notes; installing cronie is the alternative.
2. **Pace:** one revision per night (three days, about 20 minutes); the era-6 backfill (6.0, 6.3 to 6.7) takes about a
   week.
3. **Disk:** the job deletes the day files it downloaded itself once validated, keeps files that were in the cache
   before, and stops cleanly, to continue the next night, when free disk would fall below 10 GB.

## Comments
- 2026-11-07, facts from the remote session: disk 31 GB free of 196 GB (84 % used), the FTP cache holds 92 GB; one
  all-boards day is 1.37-1.39 GB (6.4 to 6.7), about 1.2 GB (6.2, 6.3). Downloads are limited to 10 MB/s by the data
  server (configured, not measured): about 2.5 min per day. `island_residuals`, one day, 11 boards, from the cache:
  4.0 min, one core. So about 6.5 min per day with download. **No cron** on the sandbox (Arch Linux: no crontab, no
  cronie); the user has systemd user timers, but without lingering they run only while the user is logged in.
  Installing cronie or enabling lingering needs the user or an admin.
