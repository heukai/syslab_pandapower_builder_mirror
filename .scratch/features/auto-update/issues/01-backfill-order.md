# In which order does the backfill build past revisions?

Type: grilling
Status: open
Blocked by:

## Question

Which revisions does the job build first, and what does it do with a revision whose curated data are not dated yet?

Draft: newest first, 6.6 down to 6.0, then era 4 (4.1, 4.0); eras 0 to 3 (data headers only) only on request (staff
C15). The newest revisions need the least missing data: from 6.3 down, the curated cable data need dates (the X cables
between 117-2 and 117-5 were split on 2024-10-09), and era 4 needs the cables before the 2023 rebuild (staff C14). A
revision whose curated data do not cover its date is skipped and reported, not built with guessed data.

## Comments
