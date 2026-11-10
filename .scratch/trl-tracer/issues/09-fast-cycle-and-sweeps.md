Status: ready-for-agent
Owner: agent
Blocked by: 08

# 09 — fast cycle and sweeps

Fast cycle: replay the decision step over a slow run's cached evidence with new settings or rules, scored and compared like a normal run. Sweeps: search fast-cycle settings on the tuning set, report the best with scores, never commit.

## Done when

- [ ] Replay of the tuning set takes seconds and reproduces the slow run's score exactly with unchanged settings.
- [ ] A sweep proposes settings with scores and changes no file under git.

Spec user stories: 65, 66, 69. Spec: `../spec.md`.
