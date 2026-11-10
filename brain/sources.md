# Data sources

Every source we use, with licence. Feeds `declaration.json`.

| Source | Version | Date obtained | Role | Label origin | Licence |
|---|---|---|---|---|---|
| APCTT public sample cases (contracts/public-cases.json, USGS reports) | kit 0.5.0 | 2026-11-10 | development, tuning, hand-labelling | organizer's estimated TRL per report; not expert labels | U.S. public domain (USGS); some figures third-party, see the manifest's licence_note |
| Silver criterion labels for 8 public cases (`brain/labels/`) | v1 | 2026-11-10 | development benchmark for the evidence score (not training) | AI-generated (Claude) per `.scratch/trl-tracer/labelling-brief.md`, made blind to the organizer's estimate, cross-checked against it with `harness/check_labels.py`; not expert labels | derived from the U.S. public domain reports; the labels are the team's own work (MIT) |
