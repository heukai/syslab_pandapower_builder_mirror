# Phase 1 only, or an early residual-based detector?

Type: grilling
Status: resolved
Blocked by:

## Question

Does the first version of the job stop at phase 1 (sources -> proposals -> models -> validation with residuals in the
report), or does it already include one phase-2 detector (for example swapped or mislabelled meters, as the 117-2 CEEx2
swap found on 2026-06-25)?

Draft: phase 1 only; the validation report shows the residuals per island so a person can spot phase-2 problems;
detectors follow once phase 1 runs reliably.

## Answer

Settled with the maintainer, 2026-11-06: the job's first version is phase 1 (sources -> proposals -> models -> validation
with residual figures in the merge request). Phase 2 stays in this map as a **prototype**: ticket "What should a
phase-2 detector find, and how does it propose?" (07).

## Comments
