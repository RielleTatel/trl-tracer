# Experiments

One entry per run: date, settings, result, what changed.
- 2026-11-10 15:53 | `20261110-155331-smoke` | smoke(3) | 228c6a3+dirty | A 0.250 (exact 0, ±1 0, abstain 3) | B – | dev 0.250 | gates PASS (invalid 0, timeouts 0, slowest 0.04 s, peak 0.02 GB) | KEEP: baseline (no best run yet for this case set) | baseline: always-abstain 0.1.0
- 2026-11-10 15:54 | `20261110-155414-tuning` | tuning(70) | 228c6a3+dirty | A 0.250 (exact 0, ±1 0, abstain 70) | B – | dev 0.250 | gates PASS (invalid 0, timeouts 0, slowest 0.09 s, peak 0.02 GB) | KEEP: baseline (no best run yet for this case set) | baseline: always-abstain 0.1.0
- 2026-11-10 16:05 | `20261110-160513-tuning` | tuning(70) | 63f20b5+dirty | A 0.750 (exact 38, ±1 29, abstain 0) | B – | dev 0.750 | gates PASS (invalid 0, timeouts 0, slowest 0.25 s, peak 0.03 GB) | KEEP: vs 20261110-155414-tuning: dev +0.5000 (A +0.5000, B +0.0000) | ticket 04: adapter + never-fail guard, evidence stub
