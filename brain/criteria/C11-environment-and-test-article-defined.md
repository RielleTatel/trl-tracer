# APCTT-C11 — Environment and test article defined

Checklist text (APCTT-2026-CHECKLIST-v1): Environment and test article defined: the report describes the test conditions and the configuration or fidelity of the tested article (for example breadboard, prototype, production unit) relative to the intended application.

## Distilled (exported to assets/criteria_rules.json)
- Hypotheses:
  - The report describes the test conditions and the version of {target} that was tested.
  - The report describes the data, time period and site used to test {target}.
- Search phrases:
  - test conditions
  - data set
  - period of record
  - study site
  - model version
  - configuration
  - setup
  - input data
  - boundary conditions
  - time period
- Trap cues:
  - References Cited
  - Contents
  - Acknowledgments

## What it means
The report describes the test conditions and the configuration or fidelity of the tested article relative to the intended application. (Draft v1: rewrite in your own words as you read reports.)

## Reading it for software, models and data products
The kit says hardware words are read by analogy: a representative version of the product, tested as the criterion says. Which version of the model or dataset was tested, on which data, period and site, and how that compares with the intended use.

## Positive examples
- USGS-SDG-040 p.15: "The upstream boundary condition for the hydraulic-model calibration was a discharge hydrograph corresponding to the flows observed for the calibration event, the flood of December 28, 2015–January 3, 2016, herein referre" — Test conditions are defined: the calibration event, the upstream and downstream boundary conditions, the Mississippi backwater scenarios and the flow regime. The tested article is also defined: HEC-RA
- USGS-SDG-043 p.13: "Subcritical (tranquil) flow regime was assumed for the simulations." — Defines the simulation conditions (steady flow, subcritical regime, normal-depth boundary, 9-18 ft stages) and the configuration (HEC-RAS 5.0.3, lidar DEM, 6-ft grid, 8.8-mi reach).
- USGS-SDG-061 p.22: "Calibration of PRMS was conducted only for the May through October period in this study for two reasons." — Defines the test conditions (two HRUs, May-October only, calibration periods, Daymet versus Cloudcroft forcing, observed hydrograph built by subtraction) and the model configuration, with limits relat
- USGS-SDG-081 p.19: "The simulations included conditions with the gates closed (existing condition with some leakage of water past the gates which do not close completely in some cases), one gate open, and both gates open." — Defines the test conditions (tide data source, gate states, dates) and the tested configuration (GIS flow paths, spreadsheet, fixed channel/marsh diffusivities).
- USGS-SDG-089 p.7: "An additional eight locations were rapid-deployment gages (RDG) instrumented with real-time telemetered sensors that recorded water-level elevations and meteorological data every 15 minutes during the hurricane and trans" — Describes the deployed configuration (sensor types, sampling intervals, telemetry, counts by state, installation) and the storm conditions; p9 covers the survey/datum setup.
- USGS-SDG-096 p.96: "The basic sample data include four shoreline positions for a section of the North Carolina coast near Rodanthe along the Outer Banks and a reference baseline from which the DSAS transects are cast." — Test conditions are defined: sample shoreline sources, dates and proxies, the ArcGIS geodatabase environment, and run settings (spacing, smoothing, CI, uncertainty) for the released DSAS add-in.
- USGS-SDG-099 p.7: "The data points are spaced 1 m apart along track (the shot interval of the seismic-reflection data systems) and are spaced 1–2 km apart cross track (fig. 3)." — The input data and conditions are described (2007/2008 surveys, ~925,000 points, spacing, velocities, clip mask). Page 8 gives the exact gridding parameters and the final configuration used for the pu

(From the silver labels in brain/labels/, verified verbatim by harness/check_labels.py.)

## Traps (looks like evidence, is not)
- USGS-SDG-0xx p.N: "..." — why it does not count

## Open questions
- 
