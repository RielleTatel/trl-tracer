# trl-tracer assets

Rules written by the team (MIT). No model weights are shipped here: catalogue models come from
the organizer's model store.

- `criteria_rules.json`: per checklist criterion, short hypotheses (with `{target}`,
  `{application}` and `{environment}` filled from the case), search phrases and trap cues, plus
  global page traps. Exported from the team's criterion cards with `harness/export_rules.py`.
  A criterion missing from this file falls back to its checklist description.
