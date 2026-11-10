Status: ready-for-agent
Owner: agent

# 03 — decision step

Test-first, build the pure decision step: case evidence record + checklist + settings → complete result. Includes quotation selection and verification (verbatim on page after whitespace/hyphen normalisation; bare TRL assertions rejected), up to 3 distinct pages strongest first, downgrade of unquotable `met`, `met` threshold and borderline band (incl. LLM answers), and the first TRL rule (prior 6, highest strongly met level of TRL 4-9, band limits, early-stage downgrade, abstain only for out-of-scope/conflict). Define the case evidence record as plain JSON.

## Done when

- [ ] Seam-2 tests cover every rule in the spec's Testing Decisions and run without models in under a second.
- [ ] Every result produced in tests passes the kit's contract validator.
- [ ] Same input gives byte-identical output.

Spec user stories: 11-17, 34, 37-46. Spec: `../spec.md`.
