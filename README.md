# HybridQC-global-groundwater

Code and derived workflow products for **HybridQC**, a transparency-first preprocessing workflow for heterogeneous annual groundwater records.

## Repository scope

This repository documents the **method layer** behind the article rather than the journal submission package. It contains:

- preprocessing code for annual groundwater anomaly construction with HybridQC
- post-analysis code for reproducible diagnostics and downstream summaries
- figure-generation code or archived figure-code bundles
- derived workflow products referenced in the manuscript

It intentionally does **not** include:

- the manuscript text
- final journal figure files
- cover letters or submission-system files

## Scientific purpose

HybridQC converts heterogeneous annual groundwater observations into a unified wetness-like annual level representation, computes strict consecutive-year anomalies without gap infilling, applies level–year quality control, exports destructive and non-destructive audit artifacts separately, and stabilizes downstream reuse through a fixed anomaly contract.

## Core workflow products

### Canonical upstream / handoff products
- `station_anomalies_all.zip`
- `station_decadal_stats.zip`

### Audit and metadata products
- `station_flagged_years.csv`
- `global_outlier_anomalies.csv`
- `annual_max_min_anomalies.csv`

### Derived regional/aquifer products
- `aquifer_decadal_stats.csv`

## External source data

The annual groundwater observations and aquifer delineation data analyzed by the workflow come from the public release associated with Jasechko (2023):

- https://doi.org/10.5281/zenodo.10003697

This repository documents the HybridQC workflow and the derived products generated from those public source data.

## Reproducibility notes

The workflow is organized around a **cache-stable handoff**:

1. annual observations are harmonized into a wetness-like level representation
2. strict consecutive-year anomalies are computed
3. HybridQC excludes implausible level–year records
4. QC-clean anomalies are written as the fixed anomaly contract
5. downstream analyses reuse the fixed contract instead of silently recomputing it

This design is intended to minimize anomaly drift across reruns.

## How to cite this repository

Please cite both:

1. the journal article
2. the repository release / archived DOI for the exact code-data snapshot used

See `CITATION.cff`.

