Status: ready-for-human
Owner: participant
Blocked by: 10

# 11 — hand label 8 cases

Label 8 cases: the 3 smoke cases plus 5 from the tuning set covering estimated TRLs 4, 5, 7, 8 and 9. Turn insights into card updates.

## Cases (picked 2026-11-10; shortest report per TRL band from the tuning set)

| Case | Estimated TRL | Pages | Why |
|---|---|---|---|
| USGS-SDG-012 | 4 | 24 | smoke case; the only TRL 4 |
| USGS-SDG-040 | 7 | — | smoke case |
| USGS-SDG-061 | 6 | — | smoke case |
| USGS-SDG-081 | 5 | 26 | TRL 5 |
| USGS-SDG-099 | 6 | 21 | TRL 6 |
| USGS-SDG-043 | 7 | 20 | TRL 7 |
| USGS-SDG-096 | 8 | 120 | the only TRL 8 in tuning |
| USGS-SDG-089 | 9 | 48 | the only TRL 9 in tuning |

Run `python3 harness/label.py <case_id>` for each (see `harness/README.md`).

## Done when

- [ ] 8 label files exist; the harness reports an evidence score on them.
- [ ] Cards updated with positive examples and traps found while labelling.

Spec user stories: 77, 78. Spec: `../spec.md`.
