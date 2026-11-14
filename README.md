# MDR-PM

This repository accompanies **Mechanism-aware distilled residual learning for fine particulate matter forecasting**. MDR-PM combines Atmospheric-Process-Informed Residual Evolution Modeling (APREM), Event-Gated Jump Residual Learning (EJRL), and Stable-Jump Regime-Complementary Distillation (SJ-RCD).

The repository includes the full repaired Beijing PM2.5 dataset, archived test forecasts, and scripts for checking the forecasts and regenerating offline analysis tables and figures.

## Beijing PM2.5 dataset

[The dataset directory](datasets/PM25) contains the repaired series used by the archived MDR-PM model. It covers 25,593 hourly time steps at 39 monitoring stations in Beijing during 2018-2020, with 15 stored fields in a single array. The Beijing dataset was also used in [DeepPM2.5](https://doi.org/10.1109/TGRS.2026.3656010) and [MVG-KAN](https://arxiv.org/abs/2606.24347).

| File | Contents |
|---|---|
| data.dat | Little-endian float32 array in C order with axes for time, station, and field |
| desc.json | Array shape, hourly sampling interval, and the 15 fields in storage order |
| input_features.txt | The 12 observation fields used as inputs |
| station_coordinates.csv | Longitude and latitude for each station, in array order |
| adj_mx.pkl | Archived station adjacency matrix |

The archived repair flagged 32,151 pollutant cells for temporal interpolation within each station and field. The final MDR-PM input uses the 12 observation fields plus hour of day and day of week. The stored month field is also available. The PM2.5 target is `PM2_5` at field index 11 (zero-based). Station indices 0-38 correspond to archive station IDs 1-39.

Read the full array from the repository root with NumPy.

~~~python
import json
from pathlib import Path

import numpy as np

dataset_dir = Path("datasets/PM25")
metadata = json.loads((dataset_dir / "desc.json").read_text(encoding="utf-8"))
data = np.memmap(
    dataset_dir / "data.dat",
    dtype="<f4",
    mode="r",
    shape=tuple(metadata["shape"]),
)
pm25 = data[:, :, metadata["feature_description"].index("PM2_5")]
~~~

## Archived single-run ablation results

The table reports the arithmetic means of the metrics at the six forecast horizons of 1, 3, 6, 12, 24, and 48 hours. MAE and RMSE are in micrograms per cubic meter. MAPE is shown as a ratio.

| Variant | APREM | EJRL | SJ-RCD | MAE | RMSE | MAPE |
|---|---|---|---|---:|---:|---:|
| MVG-KAN | no | no | no | 14.0928 | 21.4062 | 0.9744 |
| MVG-KAN + APREM | yes | no | no | 13.8790 | 21.2851 | 0.9032 |
| MVG-KAN + EJRL | no | yes | no | 13.9416 | 21.3962 | 0.8726 |
| MVG-KAN + APREM + EJRL | yes | yes | no | 13.8554 | 21.3202 | 0.8806 |
| MDR-PM | yes | yes | yes | 13.6339 | 21.0493 | 0.8465 |

See the [test data documentation](test_data/README.md) for the target versions used to evaluate each variant.

## Verify and regenerate

Use Python 3.9 or newer. Run these commands from the repository root.

~~~bash
python -m pip install -r requirements.txt
python test_code/verify_release.py
python test_code/prepare_offline_assets.py
~~~

`verify_release.py` checks the saved prediction and target arrays against their per-horizon metrics. `prepare_offline_assets.py` reads those arrays and writes tables and figures to [analysis_outputs](analysis_outputs/README_OFFLINE_ANALYSIS.md). Both scripts operate on saved test forecasts.
