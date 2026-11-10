Status: resolved
Owner: agent
Blocked by: 05, 06

# 07 — retrieval

Evidence stage part 1: BM25 (in-package) + `bge-base-en-v1.5` dense retrieval per criterion, rerank with `granite-embedding-reranker-english-r2`, keep the top distinct pages; write candidates into the case evidence record. Models loaded once in `load`, offline, from `APCTT_MODEL_STORE`; listed in `submission.json` `models[]`.

## Done when

- [x] Harness slow run produces case evidence records with ranked candidates per criterion; gates pass.
- [x] Load and retrieval time per case recorded.

Spec user stories: 31, 32, 49. Spec: `../spec.md`.

## Comments

- 2026-11-10: Done. `retrieve.py`: in-package BM25 over passages (also the embedding
  pre-filter, top 40 per criterion), `bge-base-en-v1.5` dense scores on the union, reciprocal-
  rank fusion, `granite-embedding-reranker-english-r2` on the fused top 12, top 8 kept per
  criterion; page-trap pages (reference lists, front matter) excluded; trap cues flagged on
  candidates. `models.py` holds the catalogue paths and offline loading; models load once in
  `load()` and a load failure degrades retrieval instead of failing the case. Both models in
  `submission.json` `models[]` and the notices.
  Tuning run `20261110-162243-tuning`: 70/70 valid, 0 timeouts, A 0.750 (unchanged: no judge
  yet, so every case still takes the prior), slowest case 50.8 s (USGS-SDG-006), peak 1.94 GB;
  wall mean 33.7 s; retrieval mean 27.2 s, max 43.4 s; model load mean 4.3 s; every criterion
  has candidates.
  Findings for ticket 08: on this Mac, embedding and reranking run at only ~7-10 passages/s and
  the worker uses ~1 core (OpenMP with 4 threads configured) under heavy memory pressure (8 GB
  RAM, ~2 GB swap in use). Adding the entailment judge at the same speed puts the slowest cases
  near or over the 90 s gate. The participant decides the time-budget option before 08.
  The granite reranker's scores are narrow (about 0.67-0.91) and may not discriminate well.
