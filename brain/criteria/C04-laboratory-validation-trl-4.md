# APCTT-C04 — Laboratory validation (TRL 4)

Checklist text (APCTT-2026-CHECKLIST-v1): Laboratory validation (TRL 4): the report states that the assessed component or a low-fidelity breadboard was tested in a laboratory environment and reports the results.

## Distilled (exported to assets/criteria_rules.json)
- Hypotheses:
  - An early version of {target} was tested in a laboratory or controlled setting and the results are reported.
  - Components of {target} were tested on test data and the test results are reported.
- Search phrases:
  - laboratory
  - bench test
  - controlled conditions
  - test data
  - synthetic data
  - verification
  - unit test
  - calibration data set
  - prototype
- Trap cues:
  - will be
  - future work
  - planned
  - proposed
  - References Cited
  - Contents
  - Acknowledgments

## What it means
The component (or a low-fidelity breadboard) was tested in a laboratory and the report gives the results. (Draft v1: rewrite in your own words as you read reports.)

## Reading it for software, models and data products
The kit says hardware words are read by analogy: a representative version of the product, tested as the criterion says. A first version of the model or code tested in a controlled setting: verification against known solutions, tests on a subset of data, code checks, with reported results.

## Positive examples
- USGS-SDG-012 p.9: "This installation includes libraries, source code, startup scripts, and example datasets." — Released P2S v1.0 distribution (libraries, source code, startup scripts, example datasets): the coupling is implemented and runs on test data.
- USGS-SDG-096 p.98: "Once the sample dataset has been downloaded and added to ArcMap, the following user settings should be applied to run a controlled test of the sample data." — By analogy: the v5.1 software is run as a controlled test on sample (test) shoreline datasets, and the resulting rate outputs are shown in figs. 4.2 and 4.4.

(From the silver labels in brain/labels/, verified verbatim by harness/check_labels.py.)

## Traps (looks like evidence, is not)
- USGS-SDG-0xx p.N: "..." — why it does not count

## Open questions
- 
