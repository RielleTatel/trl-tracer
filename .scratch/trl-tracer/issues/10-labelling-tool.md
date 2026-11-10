Status: resolved
Owner: agent
Blocked by: 07

# 10 — labelling tool

Labelling tool: for a case, show per criterion the pipeline's candidate pages with snippets, allow browsing any page's text, record status, best pages, note and own TRL estimate into `brain/labels/<case_id>.json`, and append a capture per decision to `brain/captures.jsonl`. Remind the labeller to skim the report's contents/methods before viewing candidates.

## Done when

- [x] Labelling one smoke case end to end writes a label file and captures.
- [x] The harness reads label files and computes the evidence score.

Spec user stories: 74-76. Spec: `../spec.md`.

## Comments

- 2026-11-10: Done. `harness/label.py <case_id>`: terminal tool over a run's cached evidence;
  per criterion `toc`, `page N`, `find WORDS` to read first, then `cands` for the pipeline's
  candidates; `met P,P` / `not` / `ins`, `note`, `trap N`, `back`, `skip`, `quit`. Saves
  `brain/labels/<case_id>.json` after every decision (resumable), appends one capture per
  decision to `brain/captures.jsonl`, asks for the labeller's own TRL at the end and only then
  shows the organizer's estimate. Tested end to end on USGS-SDG-012 in a temp folder
  (`TRL_LABELS_DIR`, `TRL_CAPTURES_FILE`): quit and resume, invalid input, trap capture, full
  pass with TRL; the harness then scored B 0.333 from that label file. No real labels written.
