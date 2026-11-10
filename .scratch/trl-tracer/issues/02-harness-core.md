Status: resolved
Owner: agent
Blocked by: 01

# 02 — harness core

Build the harness: run the module directly on a case set (tuning, held-out, smoke, IDs) with a real time-budget context; validate each result with the kit's validator; record timings and peak memory; write a run record (results, settings, rules hash, git commit); compute the dev score (official TRL table vs organizer estimates; evidence formula vs hand labels when present) and the gates; compare with the best run → keep/revert; append a summary line to `brain/experiments.md`. Create the stratified 70/29 split with a fixed seed in `brain/split.json`.

## Done when

- [x] A baseline run of the always-abstain package on the tuning set produces a dev score, passes the gates and is logged.
- [x] Compare prints keep/revert against the best run on the same set.
- [x] Run records are git-ignored.

Spec user stories: 58-64, 67, 68. Spec: `../spec.md`.

## Comments

- 2026-11-10: Done. `harness/` has run.py (slow cycle), score.py, compare.py, split.py,
  worker_case.py, common.py and a README. Each case runs in a fresh base-Python worker with a
  restricted environment and the real 3-minute budget; results are checked with the kit's
  `validate_result`. Verified failure handling: crash -> MODULE_ERROR, unknown field ->
  INVALID_OUTPUT, NaN -> INVALID_OUTPUT, sleep past the budget -> TIMEOUT (all score 0, gates
  fail). Split: tuning 70 (TRL 4:1, 5:8, 6:38, 7:21, 8:1, 9:1), held-out 29 (5:4, 6:16, 7:8,
  9:1); smoke cases kept in tuning. Baselines (always-abstain): smoke and tuning A 0.250, gates
  pass, accepted as best. The evidence score B appears once `brain/labels/` has files.
  Worker reads `module.last_evidence` (if the module sets it) as the fast-cycle cache.
