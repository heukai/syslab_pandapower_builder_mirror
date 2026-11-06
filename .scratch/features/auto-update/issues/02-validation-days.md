# On which days is each revision validated, and when is it accepted?

Type: grilling
Status: open
Blocked by:

## Question

How the job picks the validation day(s) of a revision, and the acceptance rule.

Draft: the yearly experiment days where known (June; November or March); otherwise a day inside the revision with all its
switchboards logging, no data-name period (pickup log C8) and complete breaker states; accepted when every island of the
day closes and the largest one is within about 0.5 kW RMSE at 1 minute (staff, 2026-10-30). A day that fails is
reported with its residuals, not retried silently. Facts needed from the remote session: which days in each revision
have complete data.

## Comments
