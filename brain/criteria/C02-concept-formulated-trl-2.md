# APCTT-C02 — Concept formulated (TRL 2)

Checklist text (APCTT-2026-CHECKLIST-v1): Concept formulated (TRL 2): the report describes a practical application of those principles and how the assessed technology is intended to work in it.

## Distilled (exported to assets/criteria_rules.json)
- Hypotheses:
  - The report describes how {target} is intended to be used for {application}.
  - The report describes the purpose of {target} and how it is designed to work.
- Search phrases:
  - purpose and scope
  - objectives
  - approach
  - designed to
  - intended to
  - framework
  - application
  - decision support
  - is used to
- Trap cues:
  - References Cited
  - Contents
  - Acknowledgments

## What it means
The report turns the principles into a concrete application: what the technology is for and how it is meant to work in that application. (Draft v1: rewrite in your own words as you read reports.)

## Reading it for software, models and data products
The kit says hardware words are read by analogy: a representative version of the product, tested as the criterion says. The purpose-and-scope or approach section: what the model, tool or dataset is built to do and how it fits the intended use (for example flood mapping for county planning).

## Positive examples
- USGS-SDG-012 p.9: "P2S is implemented as loosely coupled software (fig. 3)." — Design of P2S describes how it works: PRMS outputs are read by P2S to build SNTemp input files, then SNTemp simulates daily stream temperature per segment.
- USGS-SDG-040 p.11: "One way to address these informational gaps is to produce a library of flood-inundation maps that are referenced to the stages recorded at the USGS streamgage." — The report describes the application: a map library tied to streamgage stages and NWS forecasts that responders use to judge flood depth and extent, closed roads and evacuations.
- USGS-SDG-043 p.9: "One way to address these informational gaps is to produce a library of flood-inundation maps that are referenced to the stages recorded at the USGS streamgage." — Describes the application: a stage-referenced map library used with gage data by emergency responders to judge flood depth and extent.
- USGS-SDG-061 p.10: "This report describes the development, sensitivity analysis, calibration, and implementation of PRMS to simulate the prefire and postfire streamflow and surface hydrologic conditions of the fire-affected North Fork Eagle" — Describes the application (simulating fire effects on streamflow for flood and emergency planning) and how the HRU-based prefire/postfire models are meant to work.
- USGS-SDG-081 p.9: "The method was designed to be easily adaptable to other regions of the coast, and it requires only planimetric marsh geometry and the size of the gate opening (leakage) to define the relation between downstream and upstr" — Describes applying the model to estimate high-tide heights inland of tide gates in marshes, and how it works from planimetric geometry and calibrated diffusivity.
- USGS-SDG-089 p.5: "FEMA mission assigned the USGS to deploy storm-tide monitoring instruments to characterize the height, extent, and timing of storm tides better than could be accomplished by existing USGS or NOAA observational fixed-plac" — Describes the application (FEMA storm-tide monitoring) and how the network of sensors, HWM surveys and Storm-Tide Mapper delivery work in it.
- USGS-SDG-096 p.25: "The distances from the baseline to each intersection point along a transect (fig. 3) are used to compute the selected statistics." — Describes how the tool works in its application: transects cast from a baseline intersect dated shorelines, and the intersect distances and dates give the change rates.
- USGS-SDG-099 p.6: "A satisfactory interpolation of the two datasets that accounted for regional geologic structure was developed using geographic information systems modeling and graphics software tools." — The application is producing the depth-to-bLGM and sediment-thickness map layers for the California State Waters Map Series (p. 6). Page 7 explains how the GIS workflow turns seismic picks into gridde

(From the silver labels in brain/labels/, verified verbatim by harness/check_labels.py.)

## Traps (looks like evidence, is not)
- USGS-SDG-0xx p.N: "..." — why it does not count

## Open questions
- 
