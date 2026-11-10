Status: resolved
Owner: agent

# 01 — always abstain package

Create the submission folder with an always-abstain `AssessmentModule`, MIT `LICENSE`, `THIRD_PARTY_NOTICES.md`, `README.md`, `submission.json` (team `adzu`, package `trl-tracer`, CPU, no models yet) and `declaration.json` (`no_team_training`, public sample cases as a source). This is the permanent emergency fallback.

## Done when

- [x] Runs through the local kit server on the example request and the 3 smoke cases with `result_origin: module` and no output issues.
- [x] `make_submission.py` ends `VALID`; `GET /v1/package` shows `trl-tracer` and `verified`.
- [x] The fallback zip is kept outside git and its hash recorded in `brain/decisions.md`.

Spec user stories: 1, 2, 6, 51, 53, 54. Spec: `../spec.md`.

## Comments

- 2026-11-10: Done. Kit server: example + 3 smoke cases `result_origin: module`, no issues.
  `make_submission.py`: `VALID_WITH_REVIEW` (only the public-domain data source, expected; see
  `brain/decisions.md`). Fallback zip in `submissions/fallback-0.1.0/` (not in git). Added
  `harness/server_submit.py` to send request files to the local server.
