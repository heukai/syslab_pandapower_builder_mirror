# What should a phase-2 detector find, and how does it propose?

Type: prototype
Status: open
Blocked by: 02

## Question

A throwaway prototype of one phase-2 detector on validation results: from the residuals of a day (`island_residuals`
output: residual per island, partner channels and their correlation, breaker states), find a model error the sources do
not show and turn it into a proposal a person can confirm. First candidate: a swapped or mislabelled meter, as the 117-2
CEEx2 swap found on 2026-06-25 (spikes in the 319-3 island residual followed one socket meter; the swap closed the
island). Run against that day before and after the fix: the prototype should find the swap on the "before" model and
nothing on the "after" model. Also look at: steady meter offsets (the -0.16 kW of the 319-3 island). What does the
proposal look like (a third-level model improvement, e.g. 6.6.3, with the evidence figures)?

Runs in the remote session (data access); the question and the verdict are settled here.

## Comments
