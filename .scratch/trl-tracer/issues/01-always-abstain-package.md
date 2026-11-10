Status: ready-for-agent
Owner: agent

# 01 — always abstain package

Create the submission folder with an always-abstain `AssessmentModule`, MIT `LICENSE`, `THIRD_PARTY_NOTICES.md`, `README.md`, `submission.json` (team `adzu`, package `trl-tracer`, CPU, no models yet) and `declaration.json` (`no_team_training`, public sample cases as a source). This is the permanent emergency fallback.

## Done when

- [ ] Runs through the local kit server on the example request and the 3 smoke cases with `result_origin: module` and no output issues.
- [ ] `make_submission.py` ends `VALID`; `GET /v1/package` shows `trl-tracer` and `verified`.
- [ ] The fallback zip is kept outside git and its hash recorded in `brain/decisions.md`.

Spec user stories: 1, 2, 6, 51, 53, 54. Spec: `../spec.md`.
