# Test Data

This folder contains released testing artifacts for PM2.5 ablation analysis.

Each ablation folder contains:

- `test_metrics.json`: saved metrics for horizons 1, 3, 6, 12, 24, and 48.
- `selected_test_results.npz`: prediction and target arrays for only those six horizons.

The selected arrays are sufficient to regenerate all released tables and
figures in `analysis_outputs/`.
