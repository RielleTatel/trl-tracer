# APCTT-C06 — Prototype in relevant environment (TRL 6)

Checklist text (APCTT-2026-CHECKLIST-v1): Prototype in relevant environment (TRL 6): the report states that a representative model or prototype of the assessed system or subsystem was demonstrated in a relevant environment.

## Distilled (exported to assets/criteria_rules.json)
- Hypotheses:
  - The model was applied to the study area and produced results for {application}.
  - A representative version of {target} was demonstrated in {environment}.
- Search phrases:
  - demonstrated
  - applied to
  - pilot
  - case study
  - study area
  - simulated
  - application of the model
  - field demonstration
  - results show
  - was used to generate
  - were created
  - was applied
  - was tested for
  - were deployed
  - study reach
  - maps were
  - simulated for
- Trap cues:
  - hypothetical
  - will be
  - future work
  - planned
  - proposed
  - References Cited
  - Contents
  - Acknowledgments

## What it means
A representative model or prototype of the system was demonstrated in a relevant environment (not yet the operational one). (Draft v1: rewrite in your own words as you read reports.)

## Reading it for software, models and data products
The kit says hardware words are read by analogy: a representative version of the product, tested as the criterion says. The full model, tool or dataset was applied to a real study area like the intended environment and produced the intended outputs (maps, estimates, simulations).

## Positive examples
- USGS-SDG-040 p.15: "The calibrated hydraulic model was used to generate a total of 411 water-surface profiles (table 4)." — The calibrated working model was applied to the actual study area. It produced profiles for 8 Mississippi backwater conditions, and these were combined with the lidar DEM to make the inundation map li
- USGS-SDG-043 p.14: "Flood-inundation maps for the 8.8-mi reach of the North Platte River at Scottsbluff, Nebr., were created in a GIS by combining the water-surface profiles and DEM data." — The working model was applied to the actual target reach, producing 10 maps that are delivered through the USGS mapping application (fig. 2 shows the 18-ft map).
- USGS-SDG-061 p.27: "Comparison of the distribution and magnitudes of prefire (2010) observed streamflow generally demonstrated a better match to prefire model results, and the postfire (2014) observed streamflow demonstrated a better match " — The working calibrated models were applied in the real burned study area with Cloudcroft gage precipitation and compared with observed 2010 and 2014 hydrographs.
- USGS-SDG-081 p.15: "The method was tested for Sybil Creek in Branford, Conn., by using a GIS application to estimate tide heights at the upland edge of the eastern portion of the Sybil Creek marsh, which is shown on figure 4." — Working model applied via GIS/spreadsheet to the real Sybil Creek marsh for gate scenarios, checked against one-gate-open observations (within 0.1 ft) and LiDAR.
- USGS-SDG-089 p.7: "A total of 224 temporarily deployed sensors were used for Hurricane Sandy, 162 water-level and wave-height sensors were deployed at 147 locations (fig. 1)." — The full working network was demonstrated along the Virginia-to-Maine coast during Hurricane Sandy (exceeds the relevant-environment bar).
- USGS-SDG-099 p.9: "The thickness of the uppermost Pleistocene to Holocene sediments in the State waters of the eastern Santa Barbara Channel has a mean value of 15 m and a maximum thickness of 57 m (table 2)." — The working workflow was applied to the full real study area (the intended environment) and produced region-wide thickness, depth and volume results (Tables 2-3).

(From the silver labels in brain/labels/, verified verbatim by harness/check_labels.py.)

## Traps (looks like evidence, is not)
- USGS-SDG-0xx p.N: "..." — why it does not count

## Open questions
- 
