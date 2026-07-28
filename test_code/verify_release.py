"""Verify released PM2.5 selected-horizon test data and metrics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


HORIZONS = [1, 3, 6, 12, 24, 48]
FOLDERS = [
    "01_baseline",
    "02_baseline_removal",
    "03_baseline_jump",
    "04_baseline_removal_jump",
    "05_baseline_removal_jump_kd",
]


def mae(pred: np.ndarray, target: np.ndarray) -> float:
    return float(np.mean(np.abs(pred - target)))


def rmse(pred: np.ndarray, target: np.ndarray) -> float:
    return float(np.sqrt(np.mean((pred - target) ** 2)))


def mape(pred: np.ndarray, target: np.ndarray) -> float:
    mask = np.abs(target) > 1e-5
    return float(np.mean(np.abs((pred[mask] - target[mask]) / target[mask])))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="test_data/ablation_results")
    parser.add_argument("--atol", type=float, default=1e-4)
    args = parser.parse_args()

    root = Path(args.root)
    ok = True
    for folder in FOLDERS:
        data_path = root / folder / "selected_test_results.npz"
        metrics_path = root / folder / "test_metrics.json"
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        with np.load(data_path) as data:
            pred = data["prediction"]
            target = data["target"]
            horizons = data["horizons"].tolist()

        if horizons != HORIZONS:
            raise SystemExit(f"{folder}: unexpected horizons {horizons}")
        if pred.shape != target.shape:
            raise SystemExit(f"{folder}: shape mismatch {pred.shape} vs {target.shape}")
        if pred.ndim != 4 or pred.shape[1] != len(HORIZONS):
            raise SystemExit(f"{folder}: unexpected selected result shape {pred.shape}")
        if not (np.isfinite(pred).all() and np.isfinite(target).all()):
            raise SystemExit(f"{folder}: non-finite values found")

        calc_mae = []
        calc_rmse = []
        calc_mape = []
        for idx, horizon in enumerate(HORIZONS):
            p = pred[:, idx, :, :]
            t = target[:, idx, :, :]
            calc_mae.append(mae(p, t))
            calc_rmse.append(rmse(p, t))
            calc_mape.append(mape(p, t))
            hmetrics = metrics[f"horizon_{horizon}"]
            for key, value, saved in [
                ("MAE", calc_mae[-1], hmetrics["MAE"]),
                ("RMSE", calc_rmse[-1], hmetrics["RMSE"]),
                ("MAPE", calc_mape[-1], hmetrics["MAPE"]),
            ]:
                if abs(value - saved) > args.atol:
                    ok = False
                    print(f"[WARN] {folder} horizon {horizon} {key}: computed={value:.6f}, saved={saved:.6f}")

        overall = metrics["overall"]
        print(
            f"{folder}: shape={pred.shape}, saved overall "
            f"MAE={overall['MAE']:.4f}, RMSE={overall['RMSE']:.4f}, MAPE={overall['MAPE']:.4f}"
        )

    if not ok:
        raise SystemExit("Verification finished with metric differences above tolerance.")
    print("Verification passed.")


if __name__ == "__main__":
    main()
