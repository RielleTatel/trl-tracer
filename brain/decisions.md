# Decisions

Choices and why (thresholds, models, TRL rule). Newest first.

## 2026-11-11 — Final submission: trl-tracer 1.1.0 (the team's single planned upload)

- Zip: `submissions/final-1.1.0/adzu_submission.zip` (not in git), 31.1 KB,
  zip sha256 `4683dffb9bd765008d2aa387f173e5bd1559109a733debb664fcb8c54aa789ca`,
  package sha256 `d9688049b5bc6a432a54db362b7fa5cfd4aa3e9dd3ff8174ceac950ef131cdf7` (equals the kit
  server's `verified_package_sha256`).
- Intake check: `VALID_WITH_REVIEW` (only the public-domain USGS data source). Kit server: example
  and smoke cases completed, no output issues (USGS-SDG-040 now TRL 7). Slow module tests 8/8; fast
  tests 45/45.
- Scores: tuning A 0.843, B 0.663, dev 0.758; held-out A 0.793; gates pass (slowest 60.2 s, peak
  4.2 GB) on the development Mac.
- The participant plans a single upload; the second slot stays in reserve in case the intake refuses it.

## 2026-11-11 — TRL prior from the target description; tidy quotations (Submission 2 candidate)

- Audit finding: the TRL rule predicted 6 for all 99 public cases. The words of the assessment
  target description separate the organizer's levels: "model" is in 33 of 54 TRL-6 targets and
  0 of 29 TRL-7 targets. New setting `trl_prior_by_target`: model/simulation words -> 6, then
  map/service/system/application words -> 7, otherwise `trl_prior` (6). Slow runs
  `20261111-004815-tuning` and the held-out run after it: A 0.750 -> 0.843 (tuning), 0.759 -> 0.793
  (held-out). The variant "everything without a model word is 7" gave 0.829 / 0.810; not chosen,
  because a target with no cue then risks an off-by-2 (TRL 5 predicted 7).
- Caveats: the pattern was found looking at all 99 cases, so the held-out number is not clean; the
  hidden cases are scored against expert TRLs, not the organizer's estimates.
- Quotations (only the first one of a claim is judged in C): running headers and section headings
  glued to a sentence are dropped; a fragment cut at an abbreviation ("U.S.", "fig.") is widened
  to the whole sentence (the splitter no longer cuts there); complete sentences are tried before
  ones that need shortening; purpose statements (allowed for C02: `purpose_quote_ok`), fragments,
  table rows and reference-list entries are tried last; contents lines are never quoted and
  contents pages are page traps. Of 354 first quotes on the tuning set: cut at an abbreviation
  22 -> 0, starting mid-sentence or with a header 43 -> 7, without closing punctuation 75 -> 25.
- B: unchanged in the replay (0.681, same pages cited); 0.663 in the slow run, because passages are
  split slightly differently and four labelled criteria near a threshold flipped (040 C06 lost,
  043 C10 and 099 C04 newly claimed, 099 C11 gained). Read as noise on 8 labelled cases; total met
  claims 354 -> 355. Dev 0.718 -> 0.758. Gates pass: slowest 60.2 s, peak 4.22 GB.

## 2026-11-10 — Recall fixes for Submission 2: derived C12, per-criterion thresholds for C02/C03

- C12 ("the cited evidence concerns the assessed target itself") is met by the strongest other
  met criterion's evidence when not met on its own (`derived_any_met: ["APCTT-C12"]`; never feeds
  the TRL rule). B 0.474 -> 0.543, dev 0.620 -> 0.653. 6 of 8 labelled C12 now hit; 012 has no
  other met criterion, 096 cites a non-gold page.
- C02 and C03 were met in all 8 labelled reports but never claimed: their gold pages are usually
  in the top 3 candidates, but deberta scores them 0.01-0.28 on every report. Per-criterion
  thresholds `met_threshold_by_criterion` {C02: 0.03, C03: 0.03} (extra pages use the same bar).
  B 0.543 -> 0.681, dev 0.653 -> 0.718, A unchanged (0.750). Claims 21% -> 42% of criteria (labels:
  60% met). Precision on the labelled cases: 15/15 new claims correct.
- Trade-off accepted: C03 first quotes on unlabelled cases are mixed (some are results, some are
  methods or assumptions) and may be judged PARTIAL in the expert review (C, 15%): estimated cost
  up to ~0.015 against +0.056 from B. Risk: chosen on 8 cases where both criteria are always met;
  relies on most USGS reports describing an application and presenting results.

## 2026-11-10 — Submission 1 candidate: trl-tracer 1.0.0 (ticket 14)

- Zip: `submissions/sub1-1.0.0/adzu_submission.zip` (not in git), 28 KB,
  zip sha256 `30968f126e9a7955d182bb37bc47767884e950ddf917693f0cb3831bc0f4c18a`,
  package sha256 `57043ca7712fa838280b58d5230c48103ae6cf7b483ff30f540b1c6dc857a143` (equals the kit
  server's `verified_package_sha256`).
- Intake check: `VALID_WITH_REVIEW`; the only review item is the public-domain licence of the
  declared USGS public cases (same as the fallback, unavoidable). The labels' licence is `MIT`.
- Kit server (dev profile): example + smoke cases USGS-SDG-012, -040, -061: `result_origin:
  module`, completed, no output issues, 20-41 s. Slow module tests 8/8 pass.
- Scores: tuning A 0.750, B 0.474 (8 silver-labelled cases), dev 0.620; held-out A 0.759 (equal to
  the TRL-6 prior there), met share 22.1%. Gates: slowest 62.6 s (tuning), peak 4.73 GB, on the
  development Mac; not measured on the event laptop.

## 2026-11-10 — Second opinion (ticket 12) and OCR fallback (ticket 13)

- `qwen3-0.6b` yes/no read as P(yes) in one forward pass (float32: 2.7 s load, ~1-2 s per
  question). With a plain prompt it said yes to everything (P about 0.99); a stricter instruction
  and two worked examples (one yes, one no) fixed that. Probe on the 96 labelled criteria (AUC for
  "the best passage supports the criterion"): granite rerank 0.60, deberta 0.62, qwen 0.66,
  deberta and qwen combined 0.67.
- Asked only for criteria in the borderline band [borderline_low, met_threshold). Real tuning
  run `20261110-213853-tuning`: gates pass, slowest 62.6 s, peak 4.73 GB, ~8 questions and
  17.5 s per case. Fast-cycle sweep on its cached answers: `borderline_low` 0.2, `llm_yes` 0.8 ->
  B 0.474, dev 0.620 (best so far; A 0.750 unchanged), 20.6% of criteria met.
- OCR (rapidocr, PP-OCRv4 models bundled in the base) only when at least half of a document's
  pages have under 200 characters, at most 3 pages (~4.5 s each). Recovers text on a scanned test
  document; words often run together. Never triggered on the public cases (all have text).
- Process rule after a slip: never edit `my_submission/` while a slow run is in progress (each
  case loads the package from disk); a mixed run was stopped and discarded before it finished a case.

## 2026-11-10 — Retrieval and TRL-rule improvements measured on the silver labels

- 3(a) `candidates_k` 5 -> 8: gold page among candidates 58% -> 81%, in the top 3 44% -> 64%;
  B 0.368 -> 0.391, A 0.764 -> 0.757, dev 0.578 -> 0.585. Kept.
- 3(b) cards C01/C05/C06: plain model-style hypothesis first for C05 and C06 (only the first
  hypothesis is used), search phrases from the gold evidence patterns. Top-3 gold pages 64% ->
  72%, B 0.391 -> 0.428, but A fell to 0.550: 34 cases became TRL 5 because a strongly met C05
  stopped the TRL below the prior.
- TRL rule: new setting `trl_below_prior`; chosen "never" — a strongly met level inside the
  band never pulls the TRL below the prior (the spec's "move down only when clearly
  early-stage"; the separate early-stage rule still applies). A back to 0.750, dev 0.599 (best
  so far). "no_higher_met" gave only 0.571 because most cases have no level at or above 6 met.
- Caveat: B rests on 8 silver-labelled cases; the held-out set is scored before submission.

## 2026-11-10 — Label rules: strict C04, organizer's reading of released software

- C04 is met only with a separate controlled or test-data stage; site calibration counts for
  C05. Applied to USGS-SDG-040, 043, 081, 099 (C04 -> insufficient evidence); 096 keeps C04
  (explicit sample-data test runs).
- Released software is read the organizer's way: a released working program with source code
  or example datasets counts for C03/C04; a formal release tested against stated requirements
  counts for C08. Applied to USGS-SDG-012 (C03, C04 met p9; TRL 4) and 096 (C08 met p15; TRL 8).
- Rules added to the labelling brief; every edit is listed in each label's `revisions`.
  `check_labels.py`: 0 flags. Pipeline baseline on the revised labels: B 0.368, dev 0.578.

## 2026-11-10 — Thresholds from the first sweep (ticket 09; participant delegated the choice)

- Settings: `met_threshold` 0.5, `page_min_score` 0.2, `trl_strong` 0.85 (first 0.8, see held-out
  check below), `trl_extreme` 0.95
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
- Held-out check (29 cases, run `20261110-190741-heldout`): with `trl_strong` 0.8, A 0.741 vs
  0.759 for the TRL-6 prior alone (one case worse). `trl_strong` 0.85, the best on the tuning
  set (A 0.764), gives 0.759 on held-out: equal to the prior, no loss on unseen cases. 0.9 looked
  better on held-out (0.776) but was not chosen, so the held-out set does not drive tuning.
  All differences are one or two cases: within noise. TRL moves from the TRL rule are not yet
  better than the prior; the gain to expect from this version is in the evidence score B.

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
