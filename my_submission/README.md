# trl-tracer

Trace every readiness claim to the page that proves it.

Assessment Package for the 2nd APCTT Hackathon 2026 (team `adzu`). For each case it reads the PDF
reports and returns, for every criterion of the official checklist `APCTT-2026-CHECKLIST-v1`, a
status with the pages that support it (each with a quotation taken verbatim from that page), and
a proposed TRL. CPU only, offline, catalogue models only.

## How it works

1. **Text**: per-page text with `pypdfium2`; a document whose text layer is mostly missing is
   OCR'd with `rapidocr-onnxruntime` (at most 3 pages per case).
2. **Rules**: per criterion, short hypotheses and search phrases written by the team
   (`assets/criteria_rules.json`), filled in with the case's target, application and
   environment; an unknown criterion ID falls back to its checklist description.
3. **Retrieval**: BM25 (in-package) and `bge-base-en-v1.5` dense retrieval, fused by reciprocal
   rank, reranked with `granite-embedding-reranker-english-r2`; reference lists and front matter
   are never cited.
4. **Judging**: `deberta-v3-base-zeroshot-v2.0-c` entailment of the criterion hypothesis given
   each candidate passage; for criteria in a borderline band, `qwen3-0.6b` gives a yes/no second
   opinion read as a probability (one forward pass, no generated text).
5. **Decision** (pure, deterministic): met criteria cite up to 3 distinct pages, strongest
   first, each with a sentence copied verbatim from that page (sentences that only assert a TRL
   number are never used, and headers, headings and cut-off fragments are tidied away); the TRL
   starts from a prior set by the kind of product the target is (6, or 7 for maps, services and
   systems) and moves only on strongly met level criteria; criteria without enough support are `insufficient evidence` with an explanation.
6. **Never fail**: a time budget is checked before every expensive step; any error or shortage
   of time still returns a contract-valid result built from the evidence gathered so far.

## Configuration

Tuning values are in `submission.json` `settings` (thresholds, retrieval sizes, language-model
band); the criterion language is in `assets/criteria_rules.json`.

## How it was built

- Python in the common base environment `apctt-base-9e7fe1324bb6`; no packages are shipped.
- No team training (`declaration.json`). Settings were tuned on the APCTT public sample cases
  (70 tuning / 29 held-out) against the organizer's estimated TRLs and against AI-made
  development labels for 8 cases (criterion status and gold pages), cross-checked against the
  organizer's reference labels.
- Licensed under MIT (`participant_module/LICENSE`); third-party notices in
  `participant_module/THIRD_PARTY_NOTICES.md`.
