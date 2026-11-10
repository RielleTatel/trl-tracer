# Decisions

Choices and why (thresholds, models, TRL rule). Newest first.

## 2026-11-10 — Thresholds from the first sweep (ticket 09; participant delegated the choice)

- Settings: `met_threshold` 0.5, `page_min_score` 0.2, `trl_strong` 0.8, `trl_extreme` 0.95
  (with the option-1 sizes bm25_k 20, fused_k 8, candidates_k 5, one hypothesis).
- Code change matching the spec: weakly met level criteria no longer move the TRL
  (`trl_weak_moves` false); only strongly met levels do. With weak moves on, every lower met
  threshold cost A (0.67-0.71) because weak matches pushed TRLs off 6 in the wrong direction.
- Why met 0.5 and not 0.85 (A's best): A only differs by one case (0.757 vs 0.764) once weak
  levels keep the prior, but met claims rise from 1.5% to 11.4% of criteria, and the evidence
  score B (40%, unmeasurable until hand labels) counts met hits double. Eyeballed precision of
  the best passage by entailment band: 0.3-0.5 about 1 in 4 plausible (titles, map grids,
  purpose statements); 0.5-0.85 about half; 0.85+ about two thirds. Claiming pays for B when
  twice the hit chance exceeds the not-met chance, which holds above about 0.5.
- `compare.py` says REVERT for this change because it sees only A; overridden on purpose.
- Known weaknesses for tickets 11/16: quotes are often purpose statements or figure captions;
  C07 (operational) is triggered by purpose statements; re-tune when labels make B measurable.

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
