# Decisions

Choices and why (thresholds, models, TRL rule). Newest first.

## 2026-11-10 — Fallback package 0.1.0 (ticket 01)

- Always-abstain package built and kept as the emergency fallback, uploaded only if the full
  product cannot pass the gates before the deadline.
- Zip: `submissions/fallback-0.1.0/adzu_submission.zip` (not in git),
  zip sha256 `f5af11a534d8464ffa9918fba54734e70ffddbd150d17c9cbca9cd3928f79277`,
  package sha256 `ce113e7507a8048138ea0888928769b42ff01592d57eeeb9076e50396c155f95`.
- Intake check: `VALID_WITH_REVIEW`. The single review item is the declared data source
  "APCTT public sample cases" under a public-domain licence: the policy routes every
  `LicenseRef-Public-Domain` to review. Kept on purpose: SUBMISSION.md §3 asks us to declare the
  public cases if we used them to develop or check the module, and the kit counts
  `VALID_WITH_REVIEW` as valid.
- Kit server: example request and smoke cases USGS-SDG-012, -040, -061 all `result_origin:
  module`, `abstained`, no output issues, about 0.1 s each.
