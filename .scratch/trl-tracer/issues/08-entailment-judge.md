Status: resolved
Owner: agent
Blocked by: 02, 07

# 08 — entailment judge

Evidence stage part 2: score each candidate passage against the criterion hypotheses with `deberta-v3-base-zeroshot-v2.0-c`; complete the case evidence record. First end-to-end real assessment through the decision step.

## Done when

- [x] Harness slow run on the tuning set: gates pass; dev score beats the always-abstain baseline; result logged.
- [x] Evidence records cached in the run record for replay.

Spec user stories: 33, 34. Spec: `../spec.md`.

## Comments

- 2026-11-10: Done. `judge.py`: `deberta-v3-base-zeroshot-v2.0-c` P(entailment) of the
  criterion hypothesis given each candidate passage (length-sorted batches of 16, max 256
  tokens, time check per batch); each candidate's sentences ranked by word overlap so the most
  relevant sentence is quoted. Model listed in `models[]` and the notices.
  Time budget, participant's choice (option 1, keep all models, shrink the workload):
  `settings` bm25_k 20, fused_k 8, candidates_k 5, hypotheses_per_criterion 1. A re-test with
  other apps closed showed no speed change (memory pressure was not the cause).
  Tuning run `20261110-183015-tuning`: 70/70 valid, gates pass, slowest 42.8 s, mean 29.3 s,
  judge 5.7 s mean, peak 2.83 GB; A 0.764 (exact 41, ±1 25) vs 0.750 prior baseline and 0.250
  always-abstain. Accepted as best. Best entailment per criterion: median 0.03, p90 0.34, max
  0.96 — the default thresholds (met 0.85, borderline 0.60) are far above most scores; set in
  ticket 09 by sweep (participant delegated the choice). Evidence cached for replay.
