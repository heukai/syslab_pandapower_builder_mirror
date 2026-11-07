# How are old names in the data translated to a model's names?

Type: grilling
Status: resolved
Blocked by:

## Question

In a data-name period the data files use the names of another configuration (pickup log C8, era-file `header_periods`
with what they `carries`): revision 6.1 (lag: the data keep the June 2023 names), 6.2 (unmatched: the 319-3 ABB_Pri
breaker on a busbar "Grid_Distribution" no configuration names, staff C9), and 6.0's 319-2 and 319-3 until 2023-11-30.
How is such a day validated? A column map per data-name period (data name -> model breaker or meter), derived from the
configuration the data carry and confirmed by a person; or skip such days for good. The same column maps are what model
selection needs (map "dated model versions", ticket on publishing and selection), so the form should serve both.

## Answer

Settled with the maintainer, 2026-11-07:
1. **One column map per data-name period** (data name -> the model's breaker or meter), derived automatically from the
   configuration the data carry (`carries`): same switchboard, same bay, same busbar, then names equal after normalising
   spelling. Names that do not match are listed, never guessed; a person confirms the map in the bot's merge request.
   This covers the meter-lag and alias periods (`Grid` -> `Grid_4`) and lag periods such as 6.1 (old configuration
   names); an unmatched period such as 6.2 (busbar "Grid_Distribution") waits for the staff (C9).
2. **Where:** in the era file next to its data-name period (private builder); each published model version gets a public
   `column_map.json` with the name pairs only, no lab references, since model selection needs the same maps. The
   publishing format stays with the ticket on publishing and selection (map "dated model versions").
3. Consequence for ticket 02: lag periods are validated once their column map is confirmed, so 6.1 joins the backfill
   then; 6.2 stays skipped until C9 is answered.

## Comments
- 2026-11-07: meter names count as well (ticket 09): with the model naming a bay's meter `Grid_4`, the days of
  meter-lag period D27 (data `P_Grid`) need the same translation; ticket 02 accepted meter-lag days assuming the meter
  names do not matter, which holds only once they are translated.
