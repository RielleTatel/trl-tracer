Status: ready-for-agent
Owner: agent
Blocked by: 05, 06

# 07 — retrieval

Evidence stage part 1: BM25 (in-package) + `bge-base-en-v1.5` dense retrieval per criterion, rerank with `granite-embedding-reranker-english-r2`, keep the top distinct pages; write candidates into the case evidence record. Models loaded once in `load`, offline, from `APCTT_MODEL_STORE`; listed in `submission.json` `models[]`.

## Done when

- [ ] Harness slow run produces case evidence records with ranked candidates per criterion; gates pass.
- [ ] Load and retrieval time per case recorded.

Spec user stories: 31, 32, 49. Spec: `../spec.md`.
