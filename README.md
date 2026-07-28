# PM2.5 Process-Informed Forecasting Ablation Artifacts

This anonymous repository contains lightweight test artifacts for reproducing
the PM2.5 ablation tables and figures. It is intended for offline analysis of
the reported results rather than full training.

## What Is Included

```text
test_code/
  prepare_offline_assets.py   # regenerate tables and figures
  verify_release.py           # verify selected-horizon arrays and saved metrics

test_data/
  ablation_results/
    01_baseline/
    02_baseline_removal/
    03_baseline_jump/
    04_baseline_removal_jump/
    05_baseline_removal_jump_kd/
    teacher/

analysis_outputs/
  CSV tables and PNG figures generated from the released test data
```

The released prediction arrays are selected to the six evaluated horizons:

```text
1, 3, 6, 12, 24, 48
```

For each ablation row, `selected_test_results.npz` contains:

```text
prediction: [num_samples, 6, 39, 1]
target:     [num_samples, 6, 39, 1]
horizons:   [1, 3, 6, 12, 24, 48]
```

The full 48-horizon result arrays, checkpoints, training logs, raw project
paths, and server environment files are intentionally excluded to keep the
release small and anonymous.

## Main Results

| ID | Model | Removal | Jump | KD | MAE | RMSE | MAPE |
|---:|---|---|---|---|---:|---:|---:|
| 1 | Geo-Wind + KAN baseline | no | no | no | 14.0928 | 21.4062 | 0.9744 |
| 2 | Geo-Wind + KAN + Removal | yes | no | no | 13.8790 | 21.2851 | 0.9032 |
| 3 | Geo-Wind + KAN + Jump | no | yes | no | 13.9416 | 21.3962 | 0.8726 |
| 4 | Geo-Wind + KAN + Removal + Jump | yes | yes | no | 13.8554 | 21.3202 | 0.8806 |
| 5 | Geo-Wind + KAN + Removal + Jump + KD | yes | yes | yes | 13.6339 | 21.0493 | 0.8465 |

## Setup

Use Python 3.9 or newer.

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Verify Released Test Data

```bash
python test_code/verify_release.py
```

This checks that the selected-horizon arrays are finite and match the saved
horizon metrics.

## Regenerate Tables and Figures

```bash
python test_code/prepare_offline_assets.py
```

Outputs are written to:

```text
analysis_outputs/
```

The most useful files are:

```text
analysis_outputs/ablation_overall_metrics.csv
analysis_outputs/ablation_horizon_metrics.csv
analysis_outputs/ablation_improvement_vs_baseline.csv
analysis_outputs/prediction_distribution_stats.csv
analysis_outputs/figures/
```

## Notes on Anonymity

This repository is a cleaned artifact release. It does not include server
addresses, local filesystem paths, user names, training logs, or original
project history.
