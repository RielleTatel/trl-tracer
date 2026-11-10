# APCTT-C05 — Relevant-environment validation (TRL 5)

Checklist text (APCTT-2026-CHECKLIST-v1): Relevant-environment validation (TRL 5): the report states that the assessed component or breadboard was tested in a simulated or relevant environment representative of the intended environment, and reports the results.

## Distilled (exported to assets/criteria_rules.json)
- Hypotheses:
  - The model was calibrated or validated against observed field data and the results are reported.
  - {target} was tested under conditions representative of {environment} and the results are reported.
- Search phrases:
  - calibration
  - validation
  - observed data
  - field data
  - compared with measured
  - goodness of fit
  - Nash-Sutcliffe
  - error statistics
  - representative conditions
  - test site
  - was calibrated
  - calibrated to
  - agreed with the observed
  - observed water-surface
  - satisfactory
  - R2
  - NSE
  - root mean square error
  - standard deviation
  - difference between
  - not used in the calibration
  - high-water marks
- Trap cues:
  - will be
  - future work
  - planned
  - proposed
  - References Cited
  - Contents
  - Acknowledgments

## What it means
The component or breadboard was tested in a simulated or relevant environment that represents the intended one, with reported results. (Draft v1: rewrite in your own words as you read reports.)

## Reading it for software, models and data products
The kit says hardware words are read by analogy: a representative version of the product, tested as the criterion says. Calibration or validation against real observations from conditions like the intended use (gages, field measurements), with fit statistics or error values.

## Positive examples
- USGS-SDG-040 p.15: "The model was calibrated by adjusting Manning’s n values and changing the ineffective flow areas until the results of the hydraulic computations closely agreed with the observed water-surface elevations for given flows." — The model was calibrated and checked against real observations of the reach's flood of record (December 2015): 26 high-water marks, the Eureka rating and Valley Park stages, with an RMSE of 0.47 ft. T
- USGS-SDG-043 p.13: "The HEC–RAS model was calibrated to the current stage-discharge relation at the North Platte River at Scottsbluff streamgage." — Calibrated against real observations at the study-reach streamgage, with differences reported in table 4.
- USGS-SDG-061 p.23: "The calibrated model performance in simulating monthly prefire streamflow for the May through October period was assessed as satisfactory based on statistical measures of R2 (0.74) and NSE (0.62), on the basis of watersh" — Prefire (2007-12) and postfire (2014-15) models calibrated against observed streamflow from the burned subwatershed, with statistics reported.
- USGS-SDG-081 p.15: "The method was validated by using the calibrated values for diffusivity to estimate tide heights in Leetes Island marsh, Wilson Cove marsh, and Pine Creek marsh for days not used in the calibration and comparing the esti" — Validation against real observed tide heights on independent dates in the target marshes; accuracy about 0.1-0.2 ft, max error 0.3 ft (table 2).
- USGS-SDG-089 p.7: "Of the 162 sensors, 7 waterlevel sensors were lost or the structure they were attached to was damaged during the storm, and 5 sensors (4 storm-tide and 1 wave-height) did not record storm tide either due to a lack of wat" — Sensors were tested in the real storm environment with reported outcomes and QC checks against redundant sensors, permanent gages and HWMs; p9 gives survey accuracy.
- USGS-SDG-099 p.9: "along-track seafloor depths digitized in SeisWorks® and the multibeam bathymetry was 0.6 m, with a standard deviation of 5 m, an acceptable uncertainty for the depth of the bLGM (table 1)." — Validated against independent real observations from the target area: SeisWorks seafloor depths compared with multibeam bathymetry (Table 1: mean difference 0.6 m, SD 4.7 m).

(From the silver labels in brain/labels/, verified verbatim by harness/check_labels.py.)

## Traps (looks like evidence, is not)
- USGS-SDG-0xx p.N: "..." — why it does not count

## Open questions
- 
