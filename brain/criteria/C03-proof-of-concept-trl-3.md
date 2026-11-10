# APCTT-C03 — Proof of concept (TRL 3)

Checklist text (APCTT-2026-CHECKLIST-v1): Proof of concept (TRL 3): the report presents analytical or laboratory results that demonstrate the critical function or characteristic of the assessed technology.

## Distilled (exported to assets/criteria_rules.json)
- Hypotheses:
  - Analytical or laboratory results show that the main function of {target} works.
  - Initial tests or calculations show that the method used by {target} is feasible.
- Search phrases:
  - proof of concept
  - preliminary results
  - feasibility
  - initial test
  - sensitivity analysis
  - analytical solution
  - benchmark
  - test case
  - demonstrated that
- Trap cues:
  - will be
  - future work
  - planned
  - proposed
  - References Cited
  - Contents
  - Acknowledgments

## What it means
Analytical or laboratory results that show the critical function or characteristic actually works, before it is tested as a system. (Draft v1: rewrite in your own words as you read reports.)

## Reading it for software, models and data products
The kit says hardware words are read by analogy: a representative version of the product, tested as the criterion says. Early results of the method itself: a sensitivity analysis, a benchmark problem, a test on a small or synthetic case that shows the approach works.

## Positive examples
- USGS-SDG-012 p.9: "This installation includes libraries, source code, startup scripts, and example datasets." — Released P2S v1.0 distribution (libraries, source code, startup scripts, example datasets): the coupling is implemented and runs on test data.
- USGS-SDG-040 p.15: "The root mean square error computed from the differences between surveyed high-water marks in the simulation reach for the December 2015 flood and simulated peak elevations was 0.47 ft." — Analytical results (the RMSE and the Fig. 2 comparison) show the critical function: the model simulates water levels along the reach accurately.
- USGS-SDG-043 p.13: "The absolute value of differences between observed and simulated water-surface elevations for the nine simulated flows at the USGS streamgage were equal to or less than 0.33 ft (table 4)." — Analytical calibration results (table 4) show the model reproduces observed water-surface elevations, the map library's critical function.
- USGS-SDG-061 p.23: "Overall, the postfire model was considered to be satisfactory to good." — Calibrated simulation results (table 5) show the model reproduces prefire and postfire streamflow, which is its critical function.
- USGS-SDG-081 p.11: "The tide heights were fit by adjusting the diffusivity and thus are in good agreement with the observed heights." — Calibration results (table 1) show the model reproduces observed high-tide heights and plausible lag times at the four marshes.
- USGS-SDG-089 p.9: "The reference points and HWMs were surveyed to a vertical accuracy of 0.26 foot at the 95-percent confidence level and within 10 feet horizontally, except for Union, Middlesex, and Monmouth Counties in New Jersey." — Analytical results show the critical characteristic (datum-referenced elevations) with quantified vertical accuracy checked against NGS benchmarks (table 2); recorded peak storm tides are in table 3.
- USGS-SDG-096 p.66: "The slope of the equation describing the line is the rate (1.34 meters per year)." — Worked analytical examples show the critical function on a shoreline dataset: an LRR of 1.34 m/yr with LCI95 of 0.50, plus a full numeric summary report.
- USGS-SDG-099 p.8: "The most satisfactory approach to accommodate the fault was to generate two separate grids–one to the north of the fault and one to the south (fig. 9)–and then mosaic the two into one (fig. 7D)." — The report gives analytical results comparing TopoToRaster, TIN with and without breaklines, and edited-isopach gridding. These show the critical function, a continuous surface that respects the fault

(From the silver labels in brain/labels/, verified verbatim by harness/check_labels.py.)

## Traps (looks like evidence, is not)
- USGS-SDG-0xx p.N: "..." — why it does not count

## Open questions
- 
