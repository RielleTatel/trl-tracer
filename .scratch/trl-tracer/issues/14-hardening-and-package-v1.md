Status: resolved
Owner: agent
Blocked by: 08, 12, 13

# 14 — hardening and package v1

Time the largest reports with cold loads, measure peak memory, run the changed-checklist check, run the 3 smoke cases through the real kit server, score the held-out set, fill `submission.json`/`declaration.json`/`README.md`/third-party notices, and pack with `make_submission.py`.

## Done when

- [x] `VALID` (or explained `VALID_WITH_REVIEW`); package hash matches the server's.
- [x] Held-out score recorded; all gates pass on tuning and held-out.

Spec user stories: 3, 7, 53-55, 62. Spec: `../spec.md`.

## Comments

- 2026-11-10: Done. Server config settings synced with submission.json; kit server smoke run
  (example + 3 smoke cases) passes; slow module tests 8/8 (crash, near-timeout, changed
  checklist, cleanup); largest reports within budget (tuning slowest 62.6 s, peak 4.73 GB);
  held-out A 0.759 = prior, gates pass. Packed 1.0.0: VALID_WITH_REVIEW (only the public-domain
  data source), package hash = server's verified hash. Zip in submissions/sub1-1.0.0/.
  README and declaration describe the full pipeline, both data sources and all four models.
