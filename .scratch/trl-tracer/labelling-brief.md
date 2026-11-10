# Labelling brief: silver labels for the trl-tracer dev benchmark

You label one public USGS report the way the competition's experts label hidden cases. Your
labels become the development benchmark for the evidence score. Be careful and conservative:
a label is only useful if another careful reader would agree with it.

## What you judge

The official checklist `APCTT-2026-CHECKLIST-v1` has 12 criteria. For **each** criterion decide:

- `met`: the report itself states it, with evidence; give the **gold pages** where the proof is.
- `not met`: the report clearly shows the criterion is not the case.
- `insufficient evidence`: the report does not establish it (the usual answer when it is simply not covered).

| ID | Criterion (full text) |
|---|---|
| APCTT-C01 | Basic principles (TRL 1): the report states the scientific or engineering principles on which the assessed technology is based, citing observations, studies or literature. |
| APCTT-C02 | Concept formulated (TRL 2): the report describes a practical application of those principles and how the assessed technology is intended to work in it. |
| APCTT-C03 | Proof of concept (TRL 3): the report presents analytical or laboratory results that demonstrate the critical function or characteristic of the assessed technology. |
| APCTT-C04 | Laboratory validation (TRL 4): the report states that the assessed component or a low-fidelity breadboard was tested in a laboratory environment and reports the results. |
| APCTT-C05 | Relevant-environment validation (TRL 5): the report states that the assessed component or breadboard was tested in a simulated or relevant environment representative of the intended environment, and reports the results. |
| APCTT-C06 | Prototype in relevant environment (TRL 6): the report states that a representative model or prototype of the assessed system or subsystem was demonstrated in a relevant environment. |
| APCTT-C07 | Prototype in operational environment (TRL 7): the report states that a prototype close to the final configuration was demonstrated in the actual operational environment. |
| APCTT-C08 | System qualified (TRL 8): the report states that the final system was completed and qualified through test and demonstration against its requirements. |
| APCTT-C09 | Proven in operation (TRL 9): the report states that the final system was used successfully in actual operations or deployment over a stated period. |
| APCTT-C10 | Quantified results against requirements: the report compares measured performance with stated requirements or acceptance criteria and says whether they were met. |
| APCTT-C11 | Environment and test article defined: the report describes the test conditions and the configuration or fidelity of the tested article (for example breadboard, prototype, production unit) relative to the intended application. |
| APCTT-C12 | Evidence matches the assessment target: the cited evidence concerns the assessed target itself (component, subsystem, system or technology), not a different element or only the parent project as a whole. |

## Rules (from the competition's scoring rules)

1. **Evidence describes what was built, tested or demonstrated, where, and with which result.**
   A sentence that only asserts a TRL number ("the system has reached TRL 6") is never evidence.
   A purpose statement ("the purpose of this report is to describe calibration…") is weak: prefer
   the page that reports the actual calibration or results.
2. **Models, software, workflows and data products are read by analogy** (the organizer's rule):
   hardware words mean an early or representative version of the product, tested as the
   criterion says. Examples: lab/breadboard → a first version tested on controlled or test data;
   relevant environment → calibration or validation against real observations from conditions
   like the intended ones; prototype in relevant environment → the working model applied to a
   real study area like the intended one; operational environment → actually used by its
   intended users for real decisions; qualified → formally reviewed/approved release tested
   against stated requirements; proven in operation → in routine operational use over a stated period.
3. **Judge against the case's assessment target, application and environment** (given at the top
   of the report file). Evidence about a different element, or only about the parent project, does
   not count (that is also what C12 checks).
4. **Gold pages**: list the 1-3 pages that most directly contain the proof, best first. Not the
   table of contents, not the abstract if the body has the real evidence (the abstract may be
   listed second), not reference lists.
5. **Quote**: for every `met` criterion, copy one short sentence (under 300 characters) **verbatim**
   from the first gold page's text as given in the file (same words; whitespace may differ).
   Never paraphrase.
6. **C04 (strict rule, participant decision 2026-11-10):** met only when the report has a
   separate controlled or test-data stage (synthetic data, sample/test datasets, benchmark
   problems). Calibration or validation against site observations counts for C05, not C04.
7. **Released software (organizer's reading, participant decision 2026-11-10):** a released,
   working program distributed with source code or example datasets counts as implemented and
   tested on test data (C03, C04); a formal release tested against stated requirements (for
   example platform compatibility) counts as qualification (C08).
8. **Do not guess the TRL from anything outside the report.** Give your own TRL estimate (1-9)
   from the evidence at the end.

## Input

A text file with a header (case ID, title, assessment target, intended application and
environment, document ID, page count) followed by every page as `=== PAGE n ===` and its text.
Read the whole report (use offsets to read it in parts if it is long).

## Output

Write exactly this JSON (UTF-8, 2-space indent) to `brain/labels/<case_id>.json`:

```json
{
  "case_id": "USGS-SDG-012",
  "trl": 4,
  "trl_reason": "one or two sentences on why",
  "label_origin": "ai-silver: AI-generated development label following .scratch/trl-tracer/labelling-brief.md; not an expert label",
  "criteria": {
    "APCTT-C01": {
      "status": "met",
      "pages": [{"document_id": "D001", "page": 9}],
      "quote": "verbatim sentence from page 9",
      "note": "one line: why it is met"
    },
    "APCTT-C02": {"status": "insufficient evidence", "pages": [], "note": "one line: what is missing"}
  }
}
```

All 12 criteria must be present. `pages` is empty unless the status is `met`.
