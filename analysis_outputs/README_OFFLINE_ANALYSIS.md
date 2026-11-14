# MDR-PM Archived Ablation Analysis

The metrics below come from the archived single runs at 1, 3, 6, 12, 24, and 48 hours.
The runs used different settings. MVG-KAN used pre-repair test targets, and the four variants used repaired targets.
See [the test data documentation](../test_data/README.md) for the test target versions.

MAE and RMSE are in micrograms per cubic meter. MAPE is shown as a ratio.
`jump_subset_metrics.csv` contains the saved historical subset metrics for two variants.

## Archived single-run results

| ID | Model | APREM | EJRL | SJ-RCD | MAE | RMSE | MAPE |
|---:|---|---|---|---|---:|---:|---:|
| 1 | MVG-KAN | no | no | no | 14.0928 | 21.4062 | 0.9744 |
| 2 | MVG-KAN + APREM | yes | no | no | 13.8790 | 21.2851 | 0.9032 |
| 3 | MVG-KAN + EJRL | no | yes | no | 13.9416 | 21.3962 | 0.8726 |
| 4 | MVG-KAN + APREM + EJRL | yes | yes | no | 13.8554 | 21.3202 | 0.8806 |
| 5 | MDR-PM | yes | yes | yes | 13.6339 | 21.0493 | 0.8465 |

## Differences from the archived MVG-KAN run

| ID | Model | MAE delta | MAE reduction | RMSE delta | MAPE delta |
|---:|---|---:|---:|---:|---:|
| 1 | MVG-KAN | 0.0000 | 0.00% | 0.0000 | 0.0000 |
| 2 | MVG-KAN + APREM | -0.2138 | 1.52% | -0.1211 | -0.0712 |
| 3 | MVG-KAN + EJRL | -0.1512 | 1.07% | -0.0100 | -0.1017 |
| 4 | MVG-KAN + APREM + EJRL | -0.2374 | 1.68% | -0.0860 | -0.0938 |
| 5 | MDR-PM | -0.4589 | 3.26% | -0.3569 | -0.1279 |
