# APCTT-C01 — Basic principles (TRL 1)

Checklist text (APCTT-2026-CHECKLIST-v1): Basic principles (TRL 1): the report states the scientific or engineering principles on which the assessed technology is based, citing observations, studies or literature.

## Distilled (exported to assets/criteria_rules.json)
- Hypotheses:
  - The report explains the scientific or engineering principles that {target} is based on.
  - The report cites earlier studies or literature that describe the processes behind {target}.
- Search phrases:
  - governing equations
  - physical processes
  - principles
  - theory
  - previous studies
  - literature
  - conceptual model
  - is based on
  - background
  - law
  - equation
  - physical
  - process
  - method
  - model that simulates
  - protocols
  - and others
- Trap cues:
  - References Cited
  - Contents
  - Acknowledgments

## What it means
The report says which science the technology rests on (processes, equations, theory) and points to observations or earlier studies that establish it. (Draft v1: rewrite in your own words as you read reports.)

## Reading it for software, models and data products
The kit says hardware words are read by analogy: a representative version of the product, tested as the criterion says. For a model or method: the hydrologic, physical or statistical principles it implements, with citations (for example 'streamflow is simulated with the Muskingum routing method (Cunge, 1969)').

## Positive examples
- USGS-SDG-012 p.6: "Each hydrologic component used to model the generation of streamflow is represented within PRMS by a process algorithm that is based on a physical law or empirical relation with measured or estimated characteristics (fig" — Introduction states the hydrologic (PRMS physical-process) and stream heat-transport (SNTemp) principles behind P2S, citing studies and model literature.
- USGS-SDG-040 p.13: "The HEC–RAS model is a one-dimensional step-backwater hydraulic model that simulates water-surface profiles with unsteady-state flow computation options." — The report states that the method rests on one-dimensional step-backwater hydraulics (HEC-RAS, Brunner 2016) and on Manning's roughness taken from cited studies (Barnes, Arcement and Schneider, Coon).
- USGS-SDG-043 p.12: "These energy losses are quantified by the Manning’s roughness coefficient (“n” value) (Barnes, 1967)." — States the hydraulic principles (1D step-backwater HEC-RAS modelling, Manning roughness energy losses) with cited literature.
- USGS-SDG-061 p.13: "Wildfires alter landscapes by burning groundcover, understory vegetation, and canopies and by altering physical, chemical, and biological properties of soil (Doerr and Cerda, 2005; Doerr and others, 2009; Terranova and o" — States the hydrologic principles of fire effects (reduced infiltration and ET, more runoff) with literature, and the process basis of PRMS (pages 13-14).
- USGS-SDG-081 p.10: "Fick’s Law (Fisher and others, 1979) is identical in form to Darcy’s Law and results in the classic onedimensional diffusion equation (eq. 1)." — Derives the model from Darcy's law, continuity and the groundwater tidal-diffusion solution, citing Turner, Todd, Ferris and Fischer.
- USGS-SDG-089 p.7: "Data were collected and processed following protocols established by McGee and others (2006) and expanded upon by McCallum and others (2012), which included correcting water pressure for changes in barometric pressure an" — States the measurement principle (pressure-sensor water level corrected for barometric pressure and salinity) citing prior USGS protocols; p5 defines storm tide citing NOAA.
- USGS-SDG-096 p.27: "DSAS uses a measurement baseline method (Leatherman and Clow, 1983) to calculate rate-of-change statistics for a time series of shorelines." — States the measurement-baseline and regression/end-point statistical principles behind the rate calculations, citing literature (Leatherman and Clow; Dolan; Crowell; Genz).
- USGS-SDG-099 p.7: "Sediment thickness was calculated as the difference between the seafloor and bLGM travel times." — Page 7 states the physical basis (two-way travel time converted with 1,500 m/s water and 1,600 m/s sediment velocities) and the gridding principle for discontinuous features, citing USGS surveys and E

(From the silver labels in brain/labels/, verified verbatim by harness/check_labels.py.)

## Traps (looks like evidence, is not)
- USGS-SDG-0xx p.N: "..." — why it does not count

## Open questions
- 
