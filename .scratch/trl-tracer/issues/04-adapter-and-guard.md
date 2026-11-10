Status: resolved
Owner: agent
Blocked by: 01, 03

# 04 — adapter and guard

Wire the adapter around the decision step: settings and checklist from `load`, stage time budgets from `context.remaining_ms()`, the never-fail guard (any exception or low time → valid result from work done so far with the TRL prior), cleanup that never raises, seeding from `compute.seed`. Evidence stage stubbed to empty evidence for now.

## Done when

- [x] Seam-1 tests: valid result on the example and smoke cases; forced internal error → valid result; nearly exhausted time → valid result; changed checklist with unknown IDs → valid result keyed by the new IDs.
- [x] Harness run on the tuning set passes the gates.

Spec user stories: 1-6, 47-50. Spec: `../spec.md`.

## Comments

- 2026-11-10: Done. `adapter.py` runs the evidence stage (`evidence.py`, a stub until tickets
  05/07/08) and then the decision step. Guard: an evidence-stage exception keeps the partial
  record; a decision-step exception retries with no evidence; a last-resort prior-only result
  does not depend on the decision step. `has_time` stops new work when `remaining_ms()` is under
  `reserve_ms` (default 15 s). Seeding from `compute.seed`; `reset_case`/`close` swallow errors.
  Test hooks in settings: `debug_fault: "evidence" | "cleanup"` (off by default).
  `tests/test_module_contract.py` (marker `module`): example report, 3 smoke cases, forced
  internal error, exhausted time, changed checklist, cleanup — all run in real worker processes
  via the harness and pass the kit validator. 32 tests pass.
  Harness tuning run: A 0.750 (exact 38, ±1 29), gates pass, slowest 0.25 s — this is the TRL-6
  prior baseline every real version now has to beat. Accepted as best for tuning.
