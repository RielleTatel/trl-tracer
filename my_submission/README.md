# trl-tracer

Trace every readiness claim to the page that proves it.

Assessment Package for the 2nd APCTT Hackathon 2026 (team `adzu`). It reads the PDF reports of a
case and returns, for each criterion of the official checklist `APCTT-2026-CHECKLIST-v1`, a status
and the pages that support it, plus a proposed TRL.

## This version

Version 0.1.0 is the always-abstain fallback: it returns a contract-valid abstention
(`insufficient evidence`) for every case and claims no criterion. It uses no models and reads no
assets.

## How it is built

- Pure Python, running in the common base environment `apctt-base-9e7fe1324bb6` on the CPU.
- No team training (see `declaration.json`).
- Licensed under MIT (`participant_module/LICENSE`).
