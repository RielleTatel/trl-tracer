# APCTT-C10 — Quantified results against requirements

Checklist text (APCTT-2026-CHECKLIST-v1): Quantified results against requirements: the report compares measured performance with stated requirements or acceptance criteria and says whether they were met.

## Distilled (exported to assets/criteria_rules.json)
- Hypotheses:
  - The report compares the measured performance of {target} with stated requirements or acceptance criteria.
  - The report states whether the results of {target} met the stated accuracy criteria.
- Search phrases:
  - met the criteria
  - acceptance criteria
  - within
  - accuracy
  - requirement
  - performance criteria
  - satisfactory
  - threshold
  - objective
  - less than
- Trap cues:
  - References Cited
  - Contents
  - Acknowledgments

## What it means
Measured performance is compared with stated requirements or acceptance criteria, and the report says whether they were met. (Draft v1: rewrite in your own words as you read reports.)

## Reading it for software, models and data products
The kit says hardware words are read by analogy: a representative version of the product, tested as the criterion says. Fit or error statistics compared with a stated target (for example 'simulated peaks within 0.5 ft of observed, meeting the calibration criterion').

## Positive examples
- USGS-SDG-061 p.23: "Although mean bias (0.35) was high and considered not satisfactory according to the criteria by Moriasi and others (2015a), slope of the observed versus simulated regression line was nearly 1:1 (1.07), which supports the" — Compares R2, NSE, RSR and bias with the Moriasi (2007, 2015a) evaluation criteria and says which were met (satisfactory or good) and which were not (prefire bias).

(From the silver labels in brain/labels/, verified verbatim by harness/check_labels.py.)

## Traps (looks like evidence, is not)
- USGS-SDG-0xx p.N: "..." — why it does not count

## Open questions
- 
