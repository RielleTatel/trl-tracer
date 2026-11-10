Status: resolved
Owner: agent

# 06 — rules file v1

Draft the rules file v1 (per criterion: hypotheses with `{target}`/`{application}`/`{environment}` placeholders, search phrases, trap cues) from the checklist and public NASA TRL definitions, including the software/model/data-product reading by analogy. Write the same distilled section into each of the 12 cards in `brain/criteria/`. Build the rules loader with placeholder filling and the checklist-description fallback, and an export from cards to the rules file.

## Done when

- [x] All 12 cards have a filled distilled section; the rules file matches them.
- [x] Loader test: unknown criterion ID falls back to its description.

Spec user stories: 29, 30, 52, 71-73. Spec: `../spec.md`.

## Comments

- 2026-11-10: Done. Draft v1 of all 12 cards' distilled sections (2 hypotheses, 8-10 search
  phrases, trap cues each), plus first-draft "What it means" and "Reading it for software,
  models and data products" paragraphs; `brain/criteria/00-global.md` holds page traps
  (reference lists, front matter). `harness/export_rules.py` exports the cards to
  `assets/criteria_rules.json` (`--check` verifies they match). `participant_module/rules.py`
  loads it, fills placeholders from the case, and falls back to the checklist description for
  unknown IDs or a missing file. `tests/test_rules.py`: 5 tests; 37 tests pass in total.
  The wording is a first draft for the participant to revise while reading and labelling
  (tickets 11 and 16); the rules are not used by retrieval or judging until tickets 07 and 08.
