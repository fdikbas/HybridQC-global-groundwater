# Workflow overview

## 1. Upstream preprocessing

The preprocessing pipeline ingests annual groundwater observations from:

- annual depth-to-water records
- annual groundwater elevation/head records

These are harmonized into a unified **wetness-like annual level**:

- depth-to-water is sign-inverted
- elevation/head is retained in its native directional meaning

Anomalies are then computed strictly as consecutive-year first differences.

## 2. HybridQC

HybridQC applies quality control at the **level–year** stage rather than the anomaly stage.

The QC logic combines:

- a hard global anomaly cap
- station-wise robust anomaly screening
- local level confirmation
- a conservative fallback rule
- a spike-pair rule for one-year reversals

Flagged observations are written to:

- `station_flagged_years.csv`

## 3. Fixed anomaly contract

After QC, the cleaned anomaly table becomes the fixed upstream contract:

- `station_anomalies_all.zip`

This contract is the authoritative base for later analyses.

## 4. Non-destructive inspection artifact

Retained statistical extremes are exported separately for review:

- `global_outlier_anomalies.csv`

These are surfaced for inspection, not automatically removed.

## 5. Range metadata

Annual anomaly-range metadata are externalized into:

- `annual_max_min_anomalies.csv`

These support transparent map-envelope reconstruction.

## 6. Decadal summaries

Station-level anomalies are summarized into decadal products:

- `station_decadal_stats.zip`
- `aquifer_decadal_stats.csv`

These provide deterministic downstream-ready summaries.

## 7. Post-analysis

The post-analysis layer operates primarily from:

- `station_anomalies_all.zip`
- `station_decadal_stats.zip`

and generates:

- network coverage summaries
- aquifer-scale trend diagnostics
- persistence/asymmetry metrics
- figure-ready outputs

## 8. Cache-stable reuse

The central design principle is that downstream scripts reuse cached upstream products rather than silently redefining the anomaly base on each rerun.
