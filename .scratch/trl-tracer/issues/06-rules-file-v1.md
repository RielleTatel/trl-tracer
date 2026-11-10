Status: ready-for-agent
Owner: agent

# 06 — rules file v1

Draft the rules file v1 (per criterion: hypotheses with `{target}`/`{application}`/`{environment}` placeholders, search phrases, trap cues) from the checklist and public NASA TRL definitions, including the software/model/data-product reading by analogy. Write the same distilled section into each of the 12 cards in `brain/criteria/`. Build the rules loader with placeholder filling and the checklist-description fallback, and an export from cards to the rules file.

## Done when

- [ ] All 12 cards have a filled distilled section; the rules file matches them.
- [ ] Loader test: unknown criterion ID falls back to its description.

Spec user stories: 29, 30, 52, 71-73. Spec: `../spec.md`.
