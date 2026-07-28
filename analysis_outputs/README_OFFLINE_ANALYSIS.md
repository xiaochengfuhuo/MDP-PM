# Offline PM2.5 Ablation Analysis

Generated from released selected-horizon prediction and target arrays.

## Main Ablation Table

| ID | Model | Removal | Jump | KD | MAE | RMSE | MAPE |
|---:|---|---|---|---|---:|---:|---:|
| 1 | Geo-Wind + KAN baseline | no | no | no | 14.0928 | 21.4062 | 0.9744 |
| 2 | Geo-Wind + KAN + Removal | yes | no | no | 13.8790 | 21.2851 | 0.9032 |
| 3 | Geo-Wind + KAN + Jump | no | yes | no | 13.9416 | 21.3962 | 0.8726 |
| 4 | Geo-Wind + KAN + Removal + Jump | yes | yes | no | 13.8554 | 21.3202 | 0.8806 |
| 5 | Geo-Wind + KAN + Removal + Jump + KD | yes | yes | yes | 13.6339 | 21.0493 | 0.8465 |

## Improvement vs Baseline

| ID | Model | MAE delta | MAE improvement | RMSE delta | MAPE delta |
|---:|---|---:|---:|---:|---:|
| 1 | Geo-Wind + KAN baseline | 0.0000 | 0.00% | 0.0000 | 0.0000 |
| 2 | Geo-Wind + KAN + Removal | -0.2138 | 1.52% | -0.1211 | -0.0712 |
| 3 | Geo-Wind + KAN + Jump | -0.1512 | 1.07% | -0.0100 | -0.1017 |
| 4 | Geo-Wind + KAN + Removal + Jump | -0.2374 | 1.68% | -0.0860 | -0.0938 |
| 5 | Geo-Wind + KAN + Removal + Jump + KD | -0.4589 | 3.26% | -0.3569 | -0.1279 |
