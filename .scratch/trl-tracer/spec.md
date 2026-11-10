Status: ready-for-agent

# Spec: trl-tracer — evidence-backed TRL assessment package

Trace every readiness claim to the page that proves it.

## Problem Statement

Before a technology is transferred, funded or deployed, someone has to judge how mature it is,
using the Technology Readiness Level (TRL) scale from 1 to 9. Today an assessor reads the
technical reports and assigns a TRL by hand: it is slow, and different assessors read the same
report differently. When an assessor does get a TRL from someone else, they cannot see *why*
without rereading the whole report.

As a solo participant in the 2nd APCTT Hackathon 2026 (Philippines track, team `adzu`), I need
an Assessment Package that the organizer's server can run, offline and unattended, on hidden
USGS technical reports: for each case it must judge the 12 criteria of the official checklist
`APCTT-2026-CHECKLIST-v1`, cite the pages that support each criterion, and propose a TRL. It is
scored on the TRL (45%), on whether its cited pages match the experts' gold pages (40%), and on
whether its quoted evidence really supports the criterion (15%), where a fabricated quote costs
points and an invalid, crashed or timed-out case scores zero.

I also need a way to improve it continuously: a loop that tells me, after every change, whether
the package got better, without fooling me into overfitting the 99 public sample cases, whose
labels are only the organizer's rough estimated TRLs.

## Solution

`trl-tracer` is a Python Assessment Package that reads each case's PDF, finds the pages most
likely to answer each checklist criterion, judges whether each criterion is met, quotes the
supporting sentence straight from the page (never generated), and derives a TRL from which
criteria are met, starting from a prior of TRL 6. It always returns a contract-valid result,
inside the 3-minute limit, whatever happens.

Around it sits a development loop:

- a **harness** that runs the package on chosen public cases and scores every run (a TRL score
  against the organizer's estimates, an evidence score against my own hand labels, and hard
  gates for validity, time and memory), with a **slow cycle** that re-runs the models and a
  **fast cycle** that replays cached model outputs through the decision logic in seconds;
- a **second brain**: criterion cards I write from reading reports, distilled into a rules file
  (hypotheses, search phrases and trap cues per criterion) that the package reads;
- a **labelling tool** that helps me hand-label a small set of cases with criterion statuses and
  gold pages.

The full product is submitted once it passes the hard gates; improvements found afterwards go
into a second submission. Work proceeds in ordered increments, each ending runnable, scored and
committed; there is no fixed schedule, only the competition's hard deadline.

## User Stories

### The organizer's evaluation server

1. As the organizer's evaluation server, I want to construct the module with no arguments and call `load`, `assess`, `reset_case` and `close` in order, so that every team's package runs the same way.
2. As the evaluation server, I want every result to follow the result contract exactly, so that it is stored instead of being replaced by an `INVALID_OUTPUT` failure.
3. As the evaluation server, I want each case to finish within 3 minutes including interpreter start and model loading, so that it is not stopped as a `TIMEOUT`.
4. As the evaluation server, I want the module to read the criteria only from the checklist it is given, so that it works with the official checklist and any other.
5. As the evaluation server, I want the module to load public models only from the read-only model store with network access disabled, so that the run is offline and reproducible.
6. As the evaluation server, I want `reset_case` and `close` never to raise, so that a written result is not turned into a `CLEANUP_ERROR`.
7. As the evaluation server, I want the module to stay within the memory available to a worker (12 GB), so that it is not killed mid-case.
8. As the evaluation server, I want the module to write nothing outside its scratch directory, so that the read-only base environment and model store stay intact.
9. As the evaluation server, I want the module to use only the CPU, so that it matches its declared `compute.device` and needs no GPU.
10. As the evaluation server, I want the module to start no detached processes, so that the worker can be terminated cleanly.

### Scoring and expert review

11. As the scorer, I want one status per checklist criterion (`met`, `not met` or `insufficient evidence`), so that I can compare it with the expert labels.
12. As the scorer, I want each `met` criterion to list up to three distinct cited pages with the strongest first, so that a gold page among the first three counts as a hit.
13. As the scorer, I want a TRL between 1 and 9 for every case where the evidence allows one, so that the TRL part can be scored.
14. As the scorer, I want an abstention only with one of the four allowed reasons, so that an abstention where no TRL is determinable can earn full points.
15. As a blinded expert reviewer, I want each `met` claim's first evidence item to carry a quotation that appears on the cited page, so that I can judge whether it supports the criterion.
16. As an expert reviewer, I want quotations to describe what was built, tested or demonstrated, where and with what result, so that they are not dismissed as a bare TRL assertion.
17. As an expert reviewer, I want quotations to concern the assessed target itself, so that evidence about the parent project alone is not presented as support.

### The assessor (the person the product is ultimately for)

18. As an assessor, I want to see the proposed TRL for a technology, so that I have a starting point for my judgement.
19. As an assessor, I want to see, for each criterion, whether it is met and on which page of which report, so that I can check the judgement page by page instead of rereading everything.
20. As an assessor, I want each cited page to come with the exact sentence that supports it, so that I can verify the claim in seconds.
21. As an assessor, I want a short explanation for each criterion judged to have insufficient evidence, so that I know what is missing from the reports.
22. As an assessor, I want a short rationale for the TRL, so that I understand how the criteria led to it.
23. As an assessor, I want the same report always to produce the same assessment, so that I can trust and reproduce it.

### Reading the reports

24. As the package, I want to extract the text of every page with its page number, so that every citation points at a real page.
25. As the package, I want to read text quickly enough that a 200-page report leaves time for judging, so that long reports do not time out.
26. As the package, I want to OCR pages that have little or no extractable text, so that scanned reports are still readable.
27. As the package, I want to cap how many pages are OCR'd and skip OCR when time is short, so that one scanned report cannot use the whole time limit.
28. As the package, I want to split pages into passages of a few sentences while keeping their page numbers, so that retrieval and judging work on focused text.

### Finding and judging evidence

29. As the package, I want search phrases and short hypotheses for each criterion from the rules file, filled in with the case's target, application and environment, so that retrieval and judging are specific to the case.
30. As the package, I want to fall back to a criterion's checklist description when the rules file has no entry for its ID, so that a changed checklist still works.
31. As the package, I want to retrieve candidate passages with both keyword (BM25) and dense-embedding search, so that both exact terms and paraphrases are found.
32. As the package, I want to rerank candidates and keep the best three distinct pages, so that the strongest evidence comes first.
33. As the package, I want an entailment model to score whether a passage supports a criterion hypothesis, so that judging needs no training data.
34. As the package, I want a threshold that leans towards `met` when the best page is plausibly right, so that I do not lose the double-weighted met part of the evidence score.
35. As the package, I want a small language model to give a `met` / `not met` second opinion only on borderline criteria, only while enough time remains, and at most a few times per case, so that it can improve a case but never make it time out.
36. As the package, I want the language model never to write quotations, so that no quotation can be fabricated.

### Quotations

37. As the package, I want to take each quotation verbatim from the extracted text of the cited page, so that it is on the page by construction.
38. As the package, I want to verify every quotation against its page text, tolerant only of whitespace and hyphenation differences, so that a mismatch is caught before the result is returned.
39. As the package, I want to reject sentences that only assert a TRL number, so that no claim is judged NOT_SUPPORTS for that reason.
40. As the package, I want to downgrade a `met` criterion with no verifiable quotation to `insufficient evidence` with an explanation, so that the result stays valid and honest.

### Deriving the TRL

41. As the package, I want to start from a prior TRL of 6, so that an ambiguous case still earns most of the TRL score.
42. As the package, I want to move the TRL to the highest of the level criteria (TRL 4 to 9) that is met with a strong score, so that strong evidence of maturity is rewarded.
43. As the package, I want to move the TRL down only when the strongest evidence is clearly early-stage, so that missing early-stage descriptions do not drag a mature technology down.
44. As the package, I want to leave the 5–7 band only on strong evidence, so that near misses still earn half the TRL score.
45. As the package, I want to use the evidence-quality criteria (quantified results, test conditions, evidence about the target) to adjust confidence in the TRL, so that weakly evidenced levels are not over-trusted.
46. As the package, I want to abstain only when the report is out of scope or the evidence clearly conflicts, so that I do not trade a likely 0.5–1.0 for 0.25.

### Never failing

47. As the package, I want to watch the remaining time and stop starting new work before the limit, so that the case always returns.
48. As the package, I want any unexpected error to produce a valid result built from the work done so far (with the TRL prior), so that a crash costs as little as possible.
49. As the package, I want to load every model once per case in `load`, never per criterion, so that load time is paid once.
50. As the package, I want to seed every random source from the run's seed, so that results are reproducible.

### The participant: building and submitting

51. As the participant, I want an always-abstain version of the package that passes the kit's submission checks, so that I always have a valid fallback submission.
52. As the participant, I want the package's numeric tuning values in the submission's `settings` and its criterion language in a rules file, so that I can tune without editing code.
53. As the participant, I want `submission.json` and `declaration.json` filled in for team `adzu` and package `trl-tracer`, listing every catalogue model used and every data source with its licence, so that intake accepts the submission.
54. As the participant, I want my own work licensed MIT with third-party notices listed, so that the licence checker passes.
55. As the participant, I want to run the smoke cases through the real kit server before every submission, so that anything a direct call misses (process isolation, environment, time limit) is caught.
56. As the participant, I want each submitted version tagged in git, so that I can always rebuild the exact zip.
57. As the participant, I want to submit the full product once it passes the hard gates, and a second, improved version only if I find one, so that my latest valid submission is my best.

### The participant: the development loop

58. As the participant, I want a harness that runs the package directly on a chosen set of public cases, so that I can measure it without the server's overhead.
59. As the participant, I want each harness run to validate every result with the kit's own contract validator, so that invalid output is counted as a failure exactly as the organizer would.
60. As the participant, I want each run to record per-case timings and peak memory, so that I can enforce the time and memory gates.
61. As the participant, I want a single dev score per run (the TRL score against the organizer's estimates and the evidence score against my labels), so that I can tell whether a change helped.
62. As the participant, I want hard gates (zero invalid results, zero timeouts, slowest case under 90 seconds on my machine, peak memory within budget), so that no change that risks a zero is ever kept.
63. As the participant, I want each run's results, settings, rules-file hash and git commit stored in a run record, with a one-line summary in my experiments log, so that every score traces back to exact code and settings.
64. As the participant, I want to compare a run with the best run so far and get a keep or revert verdict, so that every cycle ends with a decision.
65. As the participant, I want the slow cycle to cache each case's intermediate model outputs, so that the fast cycle can replay them.
66. As the participant, I want a fast cycle that re-applies only the decision logic to cached outputs in seconds, so that I can tune thresholds, the met lean, the number of cited pages and the TRL rule dozens of times.
67. As the participant, I want a fixed, stratified split of the 99 public cases into 70 tuning and 29 held-out cases, so that I can detect overfitting.
68. As the participant, I want the held-out set scored only before each submission, so that it does not leak into my decisions.
69. As the participant, I want autonomous sweeps over fast-cycle values that propose the best settings with their scores but never commit, so that the search is automated while the decisions stay mine.
70. As the participant, I want to run a model or retrieval experiment (for example the larger language model) as a slow-cycle run with its own record, so that I can decide on evidence whether to adopt it.

### The participant: the second brain and labelling

71. As the participant, I want one card per checklist criterion, holding its distilled hypotheses, search phrases and trap cues, plus definitions, examples and traps, so that my understanding of evidence is written down and reusable.
72. As the participant, I want the distilled sections of the cards exported into the rules file the package reads, so that what I learn changes the package's behaviour.
73. As the participant, I want a first draft of every card's distilled section and of the rules file, so that the first slow cycle runs on real hypotheses rather than raw checklist text.
74. As the participant, I want a labelling tool that shows, per criterion, the pipeline's candidate pages with snippets while letting me browse any page, so that labelling a case is fast.
75. As the participant, I want my labels saved as one file per case (criterion status, best pages, notes, my own TRL estimate), so that the harness can compute the evidence score.
76. As the participant, I want each labelling decision to add a capture to the matching criterion card, so that labelling also grows the second brain.
77. As the participant, I want to label eight cases (the three smoke cases plus five covering TRLs 4, 5, 7, 8 and 9), so that the evidence score and the met threshold rest on a varied sample.
78. As the participant, I want the module's errors on the public cases to become new captures, so that each loop cycle improves the rules.

## Implementation Decisions

### Architecture

- One Python package, `participant_module`, entry point `participant_module.adapter:AssessmentModule`, running in the frozen common base environment (`apctt-base-9e7fe1324bb6`) on the CPU (`compute.device = "cpu"`).
- The package is split by responsibility into small modules, all shipped inside the one package:
  - **adapter**: the four protocol methods, model loading, time budgeting and the never-fail guard;
  - **pdf text**: per-page text extraction with `pypdfium2`, passage splitting, OCR fallback with `rapidocr-onnxruntime`;
  - **rules**: loading the rules file, filling placeholders, the checklist-description fallback;
  - **retrieve**: BM25 (implemented in the package; no extra dependency) plus `bge-base-en-v1.5` dense retrieval, reranked with `granite-embedding-reranker-english-r2` (`ms-marco-minilm-l6-v2` kept as an experiment);
  - **judge**: entailment scoring with `deberta-v3-base-zeroshot-v2.0-c`, and the gated second opinion with `qwen3-0.6b` (thinking off, `met` / `not met` answers only);
  - **decision**: the pure decision step (quotations, statuses, evidence lists, TRL, the result) — see the interface below;
  - **trl**: the TRL derivation rule, used by the decision step.
- The pipeline is split into an **evidence stage** (everything that runs a model: extraction, retrieval, reranking, entailment, language-model answers) and a **decision stage** (pure logic over the evidence). The harness caches the evidence stage's output; the fast cycle replays the decision stage.

### The decision step interface (the seam the fast cycle and the tests share)

- Input: the case's identity fields (schema version, case ID, assessment target), the checklist, the `settings`, and a **case evidence** record:
  - per document: page count and the extracted text of each page;
  - per criterion: a ranked list of candidate passages, each with document ID, page, passage text, retrieval score, rerank score and entailment score;
  - per criterion, optionally: the language model's `met` / `not met` answer;
  - flags for work skipped because of time (OCR skipped, language model skipped).
- Output: a complete, contract-valid result object.
- Deterministic: the same input always gives the same output; no models, no file or network access.
- The case evidence record is plain JSON, so it can be cached by the harness and replayed.

### Decision rules (first versions; thresholds come from `settings`)

- A criterion is `met` when its best entailment score clears the `met` threshold (set to lean towards `met`), or when it is in the borderline band and the language model answered `met`.
- For a `met` criterion, cite up to three distinct pages, strongest first; each item carries a quotation taken verbatim from that page's text. The first item gets the strongest quotation.
- A quotation is valid only if it is found in the page text after normalising whitespace and hyphenated line breaks, and it is not a sentence that only asserts a TRL number. A `met` criterion with no valid quotation becomes `insufficient evidence`.
- Criteria that are not `met` are `insufficient evidence` with a non-blank explanation (`not met` is used only where the evidence explicitly contradicts the criterion).
- TRL: start from the prior (6); move to the highest of the TRL 4–9 criteria met with a strong score; move down only when the strongest evidence is clearly early-stage; leave the 5–7 band only on strong evidence; the evidence-quality criteria adjust confidence. Abstain only for out-of-scope or clearly conflicting evidence, with the matching reason.
- `trl_rationale`, `criterion_rationale` and `confidence` are filled where available; `uncertainty`, if given, contains the predicted TRL.

### Contract the result must satisfy (from the kit's data contract)

- Exactly the contract's fields; one key per checklist criterion in `criterion_status` and `evidence_reference`; a `met` criterion has at least one evidence item with a page within that document's page count; every `insufficient evidence` criterion has a non-blank `missing_evidence` entry; `abstention_reason` only when abstained and `error_code` only when failed; JSON types only, no NaN or Infinity; under 2 MiB.

### Time and memory budget

- Models are loaded once in `load`. The language model is loaded only if enough time remains after text extraction, and is skipped otherwise.
- The adapter keeps a time budget per stage and checks `context.remaining_ms()` before each expensive step; when time runs low it stops starting new work and returns a result from what is done.
- Development target: every case under 90 seconds and within the memory budget on the development Mac (M1, 8 GB), leaving margin for the event laptop (4-core Intel i7-11370H, 12 GB for the worker).

### Configuration

- Numeric tuning values live in `submission.json` `settings` (passed to `load` as `config["module"]["settings"]`): `met` threshold, borderline band, language-model call cap and minimum remaining time, OCR character threshold and page cap, retrieval and rerank sizes, pages cited per criterion, TRL-rule values, stage time budgets.
- Criterion language lives in a rules file in the package's assets: per criterion ID, hypotheses (with `{target}`, `{application}` and `{environment}` placeholders), search phrases and trap cues. Unknown IDs fall back to the checklist description. The rules are our own writing under MIT; report quotations stay in the second brain, not in the rules file.

### Submission

- Team `adzu`, package `trl-tracer`, licence MIT, `models[]` listing every catalogue model loaded (`bge-base-en-v1.5`, `granite-embedding-reranker-english-r2`, `deberta-v3-base-zeroshot-v2.0-c`, `qwen3-0.6b`), `declaration.json` with `no_team_training` and the public sample cases as a data source.
- An always-abstain package is built and checked to `VALID` first, and kept as an emergency fallback.
- Submission 1 is the full product once it passes the hard gates. Submission 2 is an improved version, if one is found. Each submitted version is tagged.

### Harness

- Lives outside the submission and runs in the base environment's Python.
- Calls the module directly (the four methods), with a context object that implements the real time budget, on a chosen case set: tuning, held-out, smoke, or a list of case IDs.
- Validates each result with the kit's contract validator against the server's view of the case.
- Writes a run record per run: per-case results, case evidence (the cache), timings, peak memory, the dev score, settings, rules-file hash and git commit. Run records are not committed; a one-line summary per run goes into the experiments log.
- Dev score: the TRL score computed with the official TRL scoring table against the organizer's estimated TRLs, and the evidence score computed with the official evidence formula against the hand labels. Gates: invalid results, timeouts, slowest case, peak memory.
- Compare: a run against the best run on the same case set gives keep or revert.
- Fast cycle: replays the decision step over the cached case evidence of a slow-cycle run with new settings or rules.
- Sweeps: search fast-cycle settings on the tuning set, report the best with scores, never commit.
- Split: 70 tuning / 29 held-out, stratified by estimated TRL and SDG, fixed seed, stored in the second brain; the eight hand-labelled cases come from the tuning set plus the three smoke cases.

### Second brain and labelling

- One card per checklist criterion; each card's distilled section (hypotheses, search phrases, trap cues) is the source that is exported into the rules file.
- A labelling tool shows, per criterion, the pipeline's candidate pages with snippets and lets the participant browse any page; it saves one label file per case (criterion status, best pages, note, own TRL estimate) and appends a capture to the captures log for each decision.

### Ownership

- The agent builds the package plumbing, the harness, the labelling tool, the packaging, and first working versions of judging, the decision step and the TRL rule.
- The participant owns tuning of judging, the decision step, the TRL rule and the rules file through the loop, the criterion cards, the hand labels, and every keep or revert decision.

## Testing Decisions

- **What makes a good test here:** it exercises external behaviour through one of the two seams below and asserts on the result, never on internal functions, passage splitting, intermediate scores or file layout. Internals change constantly during tuning; tests must keep passing as long as the result is still right.
- **Seam 1 — the module contract.** Construct the module, call `load`, `assess`, `reset_case`, `close` on real cases (the kit's two-page example report and the three smoke cases), and check the result with the kit's own contract validator. Covers: valid output on every path; the never-fail guard (a forced internal error, or a context whose remaining time is nearly exhausted, still yields a valid result); criteria taken from the configuration (a changed checklist whose IDs are not in the rules file still yields a valid result keyed by the new IDs); cleanup never raising. These tests load real models, so they are few and slow and are marked so they can be skipped in quick runs.
- **Seam 2 — the decision step.** Feed hand-built case evidence records and settings; assert on the returned result. Covers: quotations always appear on the cited page and bare TRL assertions are rejected; at most three distinct pages per `met` criterion, strongest first; a `met` with no valid quotation is downgraded with an explanation; the `met` threshold and borderline band behave as configured, including language-model answers; the TRL rule (prior, highest strongly met level, band limits, early-stage downgrade, abstention only for out-of-scope or conflict); every result passes the contract validator; the same input always gives the same output. These tests need no models and run in milliseconds.
- **Not unit-tested:** text extraction quality, retrieval, reranking, entailment and language-model behaviour. Their quality is measured by the harness on the public cases, not by tests.
- **Test-first** for the decision step and the never-fail guard: the parts whose failure scores zero.
- **Prior art:** the kit's own test suite (contract, runtime and tool tests run with pytest) and the direct-call check in the kit's module guide (call the class, then the kit's contract validator) are the patterns to follow. Tests live outside the submission and are not shipped.

## Out of Scope

- The Stage 2 web system: it is built on site at the event, only if the team qualifies, and wraps the frozen package.
- GPU execution and the 4-bit language models.
- Training or fine-tuning any model; there are no expert labels to train on.
- Any public model outside the catalogue, any extra Python package, any network access at run time, and any cloud OCR or API.
- Scoring the expert-review part (quotation support) automatically; it is estimated only by hand during labelling.
- `qwen3-1.7b` in the shipped package; it is evaluated only as a slow-cycle experiment.
- Multi-document cases beyond what the contract allows; the public and hidden cases have one PDF each, but the package must still handle up to three.

## Further Notes

- The kit (0.5.0) is the source of truth where it differs from the competition website; open questions to the organizers (Philippines-track finalist selection, when Submission 1 feedback returns, the hidden set's TRL-band composition) may change the TRL prior or the submission strategy.
- Hard deadline: 2026-11-15, 23:59 IST (2026-11-16, 02:29 PHT). The latest valid submission received by then is the final model; there is no third submission.
- The development Mac has 8 GB of RAM and little free disk; slow-cycle runs are sequential, and run records should be pruned when disk runs low.
- Every harness score is a proxy: the TRL score is against rough estimates, and the evidence score rests on eight hand-labelled cases. They rank versions; they do not predict the hidden-case score.
