# Data dictionary

## Core derived products

### `station_anomalies_all.zip`
QC-clean station-year anomaly contract.

Typical fields:
- `StnID`: station identifier
- `Year`: anomaly year (later year in the consecutive pair)
- `Lat`, `Lon`: station coordinates
- `Anomaly`: strict consecutive-year groundwater anomaly

### `station_decadal_stats.zip`
Station-level decadal summaries derived from the anomaly contract.

Typical fields:
- `StnID`
- `Decade`
- `Lat`, `Lon`
- `n_anom`
- `sum_anom`

Possible optional fields:
- `sum_neg`, `sum_pos`
- `n_neg`, `n_pos`
- `ratio_neg`, `ratio_pos`
- `frac_neg`, `frac_pos`

### `station_flagged_years.csv`
Excluded level–year records identified by HybridQC.

Typical fields:
- `StnID`
- `Year`
- `Reason`
- optional trigger/support fields depending on workflow version

### `global_outlier_anomalies.csv`
Retained extreme anomalies exported for inspection.

Typical fields:
- `StnID`
- `Year`
- `Anomaly`
- `Lat`, `Lon`
- optional `SourceType`

### `annual_max_min_anomalies.csv`
Annual anomaly-range metadata used for mapped products.

Typical fields:
- `Region`
- `Year`
- `data_min`
- `data_max`
- `n_total`

Possible optional fields:
- `q_min`, `q_max`
- `median`
- `n_plotted`

### `aquifer_decadal_stats.csv`
Aquifer-level decadal aggregates derived from station-decadal products.

Typical fields:
- `AQUIFER_ID`
- `Decade`
- aquifer-scale anomaly summaries
- optional persistence/asymmetry/trend-related fields

## External source data

The workflow relies on public annual groundwater observations and aquifer polygons released by Jasechko (2023). Those raw source data are not duplicated here unless specifically needed for reproducibility packaging.
