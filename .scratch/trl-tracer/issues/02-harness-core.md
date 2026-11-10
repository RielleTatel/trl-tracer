Status: ready-for-agent
Owner: agent
Blocked by: 01

# 02 — harness core

Build the harness: run the module directly on a case set (tuning, held-out, smoke, IDs) with a real time-budget context; validate each result with the kit's validator; record timings and peak memory; write a run record (results, settings, rules hash, git commit); compute the dev score (official TRL table vs organizer estimates; evidence formula vs hand labels when present) and the gates; compare with the best run → keep/revert; append a summary line to `brain/experiments.md`. Create the stratified 70/29 split with a fixed seed in `brain/split.json`.

## Done when

- [ ] A baseline run of the always-abstain package on the tuning set produces a dev score, passes the gates and is logged.
- [ ] Compare prints keep/revert against the best run on the same set.
- [ ] Run records are git-ignored.

Spec user stories: 58-64, 67, 68. Spec: `../spec.md`.
