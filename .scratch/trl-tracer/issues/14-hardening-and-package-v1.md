Status: ready-for-agent
Owner: agent
Blocked by: 08, 12, 13

# 14 — hardening and package v1

Time the largest reports with cold loads, measure peak memory, run the changed-checklist check, run the 3 smoke cases through the real kit server, score the held-out set, fill `submission.json`/`declaration.json`/`README.md`/third-party notices, and pack with `make_submission.py`.

## Done when

- [ ] `VALID` (or explained `VALID_WITH_REVIEW`); package hash matches the server's.
- [ ] Held-out score recorded; all gates pass on tuning and held-out.

Spec user stories: 3, 7, 53-55, 62. Spec: `../spec.md`.
