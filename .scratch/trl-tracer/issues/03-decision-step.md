Status: resolved
Owner: agent

# 03 — decision step

Test-first, build the pure decision step: case evidence record + checklist + settings → complete result. Includes quotation selection and verification (verbatim on page after whitespace/hyphen normalisation; bare TRL assertions rejected), up to 3 distinct pages strongest first, downgrade of unquotable `met`, `met` threshold and borderline band (incl. LLM answers), and the first TRL rule (prior 6, highest strongly met level of TRL 4-9, band limits, early-stage downgrade, abstain only for out-of-scope/conflict). Define the case evidence record as plain JSON.

## Done when

- [x] Seam-2 tests cover every rule in the spec's Testing Decisions and run without models in under a second.
- [x] Every result produced in tests passes the kit's contract validator.
- [x] Same input gives byte-identical output.

Spec user stories: 11-17, 34, 37-46. Spec: `../spec.md`.

## Comments

- 2026-11-10: Done, test-first. `participant_module/decision.py` (`decide(meta, checklist,
  settings, evidence) -> result`, case evidence record documented in its docstring),
  `quotes.py` (verbatim quotations after whitespace/hyphen normalisation; sentences asserting a
  TRL number rejected; word-boundary shortening) and `trl.py` (levels parsed from "(TRL n)" in
  the checklist text; prior 6; highest strongly met level; band 5-7; very strong evidence to
  leave the band; early-stage rule). Defaults in `decision.DEFAULTS`, overridable from
  `settings`. `tests/test_decision.py`: 24 tests through the decision-step seam, every result
  checked with the kit's `validate_result`; 0.11 s, no models. Run with
  `apctt-participant-kit-0.5.0-cpu/.venv/bin/python -m pytest tests`.
  Conflict-based abstention is not implemented yet (only the `scope: "out"` flag); it is a
  tuning decision for the participant (ticket 16).
