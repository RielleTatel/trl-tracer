# APCTT-C12 — Evidence matches the assessment target

Checklist text (APCTT-2026-CHECKLIST-v1): Evidence matches the assessment target: the cited evidence concerns the assessed target itself (component, subsystem, system or technology), not a different element or only the parent project as a whole.

## Distilled (exported to assets/criteria_rules.json)
- Hypotheses:
  - The evidence in the report concerns {target} itself.
  - The report describes results produced by {target}, not only by the wider project.
- Search phrases:
  - {target}
  - this report
  - this study
  - the model
  - developed
  - presented in this report
  - described in this report
  - results of the
- Trap cues:
  - the program
  - the project as a whole
  - References Cited
  - Contents
  - Acknowledgments

## What it means
The cited evidence is about the assessed target itself, not a different element or only the parent project. (Draft v1: rewrite in your own words as you read reports.)

## Reading it for software, models and data products
The kit says hardware words are read by analogy: a representative version of the product, tested as the criterion says. The quoted passages name or clearly refer to the assessed model, tool or dataset, not the wider program or a related product.

## Positive examples
- USGS-SDG-012 p.9: "This report describes P2S version 1.0 and serves as the user’s manual." — The cited evidence (design, SNTemp modifications, execution steps) concerns the P2S coupling software itself, not only PRMS or SNTemp separately.
- USGS-SDG-040 p.15: "The stage data at the Meramec River at Valley Park streamgage, about midway along the reach, were used to calibrate the model performance." — All the evidence concerns the Meramec Eureka-to-Arnold model and map library itself, including its links to USGS real-time stages and NWS AHPS forecasts (p18), and not some other element.
- USGS-SDG-043 p.14: "The mapping application enables the production of customized flood-inundation maps from the map library for the North Platte River at Scottsbluff, Nebr." — The evidence concerns the North Platte River inundation-map library and application itself, not just the parent FIM program.
- USGS-SDG-061 p.23: "The PRMS postfire model was run for the entire period of Daymet gridded meteorological data record (October 1, 2007, to December 31, 2015), and results from the postfire period (October 31, 2013, to December 31, 2015) we" — The evidence concerns the Rio Hondo prefire and postfire PRMS models themselves, not PRMS in general or the parent NMDHSEM early-warning effort.
- USGS-SDG-081 p.15: "The method was validated by applying it to the four marshes by using different dates for which observed tide heights were available." — All calibration, validation and application evidence is about the diffusion-analogy model itself in the named Connecticut marshes.
- USGS-SDG-089 p.5: "Both efforts were undertaken as part of a coordinated federal emergency response as outlined by the Stafford Act under a directed mission assignment by the Federal Emergency Management Agency (FEMA)." — All evidence concerns the Sandy storm-tide sensor network, HWM campaign and Storm-Tide Mapper data delivery itself, in the stated Virginia-to-Maine environment.
- USGS-SDG-096 p.63: "Each method used to calculate shoreline rates of change is based on measured differences between shoreline positions through time." — The cited evidence concerns the DSAS rate-of-change calculations themselves (methods, worked examples and sample-data rate outputs), not a different element or the parent program.
- USGS-SDG-099 p.8: "The first sediment thickness grid interpolated from the SeisWorks® point data was processed with the ArcGIS TopoToRaster tool (Esri, 2011), an interpolator designed for topographic surfaces that often serves well for oth" — All of the evidence is about the Santa Barbara seafloor-sediment GIS interpolation workflow itself, not only the parent map series.

(From the silver labels in brain/labels/, verified verbatim by harness/check_labels.py.)

## Traps (looks like evidence, is not)
- USGS-SDG-0xx p.N: "..." — why it does not count

## Open questions
- 
