Status: ready-for-agent
Owner: agent
Blocked by: 01, 03

# 04 — adapter and guard

Wire the adapter around the decision step: settings and checklist from `load`, stage time budgets from `context.remaining_ms()`, the never-fail guard (any exception or low time → valid result from work done so far with the TRL prior), cleanup that never raises, seeding from `compute.seed`. Evidence stage stubbed to empty evidence for now.

## Done when

- [ ] Seam-1 tests: valid result on the example and smoke cases; forced internal error → valid result; nearly exhausted time → valid result; changed checklist with unknown IDs → valid result keyed by the new IDs.
- [ ] Harness run on the tuning set passes the gates.

Spec user stories: 1-6, 47-50. Spec: `../spec.md`.
