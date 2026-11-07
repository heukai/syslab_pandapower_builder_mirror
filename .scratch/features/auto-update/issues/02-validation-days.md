# On which days is each revision validated, and when is it accepted?

Type: grilling
Status: resolved
Blocked by:

## Question

How the job picks the validation day(s) of a revision, and the acceptance rule.

Draft: the yearly experiment days where known (June; November or March); otherwise a day inside the revision with all its
switchboards logging, no data-name period (pickup log C8) and complete breaker states; accepted when every island of the
day closes and the largest one is within about 0.5 kW RMSE at 1 minute (staff, 2026-10-30). A day that fails is
reported with its residuals, not retried silently. Facts needed from the remote session: which days in each revision
have complete data.

## Answer

Settled with the maintainer, 2026-11-07, after the sandbox facts (comment below):
1. **Data-name periods:** the first version accepts days whose data differ from the model only in meter names or
   spelling (kinds `meter-lag`, `alias`) and skips days in breaker-name periods (`lag`, `lead`, `branch`, `unmatched`,
   `transition`); 6.1 and 6.2 are skipped and reported for now. Translating old names is its own ticket (08).
2. **Switchboards without data:** an island whose switchboards all have data is checked; an island with a switchboard
   lacking data is "not checkable" (not a failure). A revision is validated when every checkable island closes on at
   least one day (largest within about 0.5 kW RMSE at 1 min, staff 2026-10-30). The merge request lists the unchecked
   switchboards and islands; a revision with no checkable island is skipped.
3. **Days per revision:** three, spread over the revision, from the candidates; a yearly experiment day goes first once
   the maintainer names one (the sandbox does not know them).

## Comments
- 2026-11-07, facts from the remote session (FTP listings of 2026-11-06, nothing downloaded; "complete" = every board
  of the revision has a day file of at least 80 % of its median size, a proxy for complete breaker states):
  - Strictly free of data-name periods are only 6.6 (from 2026-06-25) and 6.7. Tolerating meter-lag and alias periods
    (meter names only: D27 117-4 Grid_4 and D31 117-2 CEEx2 until 2026-06-24) opens 6.0 partly, 6.3, 6.4, 6.5.
    6.1 and 6.2 have no day free of breaker-name periods (D23 to D26 lag; D28 319-3 unmatched covers all of 6.2).
  - Boards without data: 6.0 has no files for 319-2, 319-3, 319-4, 330-12, 330-13, 310-2 (117-4 and 117-5 half);
    6.1 has gaps on 117-2, 117-5 (2023-10-10 to 2024-02-27), 716-2 (to 2024-03-21), 330-12 (9 of 240 days), 319 boards
    from about 2023-12-01: no day with all boards. 310-2 logs from 2025-02-24; 117-6 is mostly absent 2024-2026 (no
    days in 6.2, 6.3, 6.5, 6.6; 52 in 6.4; 25 in 6.7). The era file has both in operation from 6-d (2023-10-19).
  - Candidate weekdays: 6.0 (5 boards, meter-lag tolerated) 2023-06-23, 06-30, 07-07, 07-17, 07-24; 6.1 none;
    6.2 none (file-complete would be 2024-06-19, 07-03, 07-18, 08-23, 09-06); 6.3 (D30 tolerated) 2024-09-09, 09-16,
    09-23, 09-30, 10-07; 6.4 (D27/D31 tolerated, 310-2 from 2025-02-25) 2025-02-25, 05-15, 08-01, 10-20, 2026-01-06;
    6.5 (D27/D31 tolerated) 2026-01-07, 02-17, 03-26, 05-04, 06-12; 6.6 2026-06-25, 07-07, 07-20, 07-31, 08-12;
    6.7 2026-08-13, 08-26, 09-08, 09-21, 10-02. Yearly experiment days not known on the sandbox.
