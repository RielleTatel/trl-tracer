Status: ready-for-agent
Owner: agent
Blocked by: 07

# 10 — labelling tool

Labelling tool: for a case, show per criterion the pipeline's candidate pages with snippets, allow browsing any page's text, record status, best pages, note and own TRL estimate into `brain/labels/<case_id>.json`, and append a capture per decision to `brain/captures.jsonl`. Remind the labeller to skim the report's contents/methods before viewing candidates.

## Done when

- [ ] Labelling one smoke case end to end writes a label file and captures.
- [ ] The harness reads label files and computes the evidence score.

Spec user stories: 74-76. Spec: `../spec.md`.
