# Archived MDR-PM predictions

`ablation_results/` contains the five archived single-run results reported in the manuscript. Each variant has a `test_metrics.json` file and a `selected_test_results.npz` file. The NPZ entries `prediction` and `target` have shape `[5023, 6, 39, 1]`. The `horizons` entry lists 1, 3, 6, 12, 24, and 48 hours. See [the manifest](ablation_results/MANIFEST.json) for repository-relative paths, shapes, and SHA-256 checksums.

All five test sets use the final 20% of the series. Each test window contains 48 hours of input followed by 48 hours of targets. The archived forecasts and targets retain the six evaluation horizons.

| Folder | Variant | Test target version |
|---|---|---|
| 01_baseline | MVG-KAN | Before repair |
| 02_baseline_removal | MVG-KAN + APREM | Repaired |
| 03_baseline_jump | MVG-KAN + EJRL | Repaired |
| 04_baseline_removal_jump | MVG-KAN + APREM + EJRL | Repaired |
| 05_baseline_removal_jump_kd | MDR-PM | Repaired |

The four repaired test target arrays match the corresponding windows in [the complete dataset](../datasets/PM25). The archived APREM + EJRL variant uses the month field. MDR-PM uses hour of day and day of week as calendar inputs.

`jump_subset` fields in the saved metric files record historical test summaries. The manuscript's normal and abrupt results use common aligned test entries and a fixed threshold for each forecast horizon.
