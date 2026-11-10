Status: resolved
Owner: agent
Blocked by: 08

# 09 — fast cycle and sweeps

Fast cycle: replay the decision step over a slow run's cached evidence with new settings or rules, scored and compared like a normal run. Sweeps: search fast-cycle settings on the tuning set, report the best with scores, never commit.

## Done when

- [x] Replay of the tuning set takes seconds and reproduces the slow run's score exactly with unchanged settings.
- [x] A sweep proposes settings with scores and changes no file under git.

Spec user stories: 65, 66, 69. Spec: `../spec.md`.

## Comments

- 2026-11-10: Done. `harness/replay.py` (fast cycle) reproduced a slow run exactly (identical
  results and score) in 0.36 s; a 70-case replay takes about a quarter of a second.
  `harness/sweep.py` replays a grid in memory, ranks by dev score with met share and TRL moves,
  saves to runs/sweeps/ and never changes files under git (203 combinations in 49 s).
  First sweep (participant delegated the choice) found that weakly met levels pushed TRLs off
  the prior; fixed to match the spec (`trl_weak_moves` false). Chosen settings: met 0.5,
  page_min 0.2, trl_strong 0.85, trl_extreme 0.95 — tuning A 0.764, held-out A 0.759 (= the
  prior on held-out), met share 11.4%. Reasoning and the held-out check in brain/decisions.md.
