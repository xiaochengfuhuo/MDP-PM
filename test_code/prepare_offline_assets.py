"""Generate PM2.5 ablation tables and figures from released test data."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


HORIZONS = [1, 3, 6, 12, 24, 48]
ROW_ORDER = [
    ("01_baseline", "Geo-Wind + KAN baseline"),
    ("02_baseline_removal", "Geo-Wind + KAN + Removal"),
    ("03_baseline_jump", "Geo-Wind + KAN + Jump"),
    ("04_baseline_removal_jump", "Geo-Wind + KAN + Removal + Jump"),
    ("05_baseline_removal_jump_kd", "Geo-Wind + KAN + Removal + Jump + KD"),
]
FEATURE_FLAGS = {
    "01_baseline": ("no", "no", "no"),
    "02_baseline_removal": ("yes", "no", "no"),
    "03_baseline_jump": ("no", "yes", "no"),
    "04_baseline_removal_jump": ("yes", "yes", "no"),
    "05_baseline_removal_jump_kd": ("yes", "yes", "yes"),
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def load_results(path: Path) -> dict[str, np.ndarray]:
    with np.load(path) as data:
        return {key: data[key] for key in data.files}


def metric_rows(root: Path) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    overall_rows, horizon_rows, jump_rows = [], [], []
    baseline_overall = None

    for idx, (folder, model_name) in enumerate(ROW_ORDER, start=1):
        metrics = read_json(root / folder / "test_metrics.json")
        removal, jump, kd = FEATURE_FLAGS[folder]
        overall = metrics["overall"]
        if baseline_overall is None:
            baseline_overall = overall

        overall_rows.append(
            {
                "ID": idx,
                "folder": folder,
                "model": model_name,
                "removal": removal,
                "jump": jump,
                "kd": kd,
                "MAE": overall["MAE"],
                "RMSE": overall["RMSE"],
                "MAPE": overall["MAPE"],
            }
        )

        for horizon in HORIZONS:
            h = metrics[f"horizon_{horizon}"]
            horizon_rows.append(
                {
                    "ID": idx,
                    "folder": folder,
                    "model": model_name,
                    "horizon": horizon,
                    "MAE": h["MAE"],
                    "RMSE": h["RMSE"],
                    "MAPE": h["MAPE"],
                }
            )

        jump_subset = metrics.get("jump_subset", {})
        for subset in ["overall", "jump", "non_jump"]:
            values = jump_subset.get(subset)
            if values:
                jump_rows.append(
                    {
                        "ID": idx,
                        "folder": folder,
                        "model": model_name,
                        "subset": subset,
                        "MAE": values.get("MAE"),
                        "RMSE": values.get("RMSE"),
                        "MAPE": values.get("MAPE"),
                    }
                )

    improvement_rows = []
    for row in overall_rows:
        improvement_rows.append(
            {
                "ID": row["ID"],
                "folder": row["folder"],
                "model": row["model"],
                "MAE_delta_vs_baseline": row["MAE"] - baseline_overall["MAE"],
                "MAE_improvement_pct": (baseline_overall["MAE"] - row["MAE"])
                / baseline_overall["MAE"]
                * 100.0,
                "RMSE_delta_vs_baseline": row["RMSE"] - baseline_overall["RMSE"],
                "RMSE_improvement_pct": (baseline_overall["RMSE"] - row["RMSE"])
                / baseline_overall["RMSE"]
                * 100.0,
                "MAPE_delta_vs_baseline": row["MAPE"] - baseline_overall["MAPE"],
                "MAPE_improvement_pct": (baseline_overall["MAPE"] - row["MAPE"])
                / baseline_overall["MAPE"]
                * 100.0,
            }
        )
    return overall_rows, horizon_rows, improvement_rows, jump_rows


def inventory_rows(root: Path) -> list[dict]:
    rows = []
    folders = [folder for folder, _ in ROW_ORDER]
    if (root / "teacher").exists():
        folders.append("teacher")
    for folder in folders:
        d = root / folder
        npz_path = d / "selected_test_results.npz"
        shape = ""
        finite = ""
        if npz_path.exists():
            arrays = load_results(npz_path)
            pred = arrays.get("prediction")
            target = arrays.get("target")
            if pred is not None and target is not None:
                shape = f"prediction={tuple(pred.shape)}; target={tuple(target.shape)}"
                finite = bool(np.isfinite(pred).all() and np.isfinite(target).all())
        rows.append(
            {
                "folder": folder,
                "has_metrics": (d / "test_metrics.json").exists(),
                "has_selected_results_npz": npz_path.exists(),
                "array_shape": shape,
                "finite_prediction_target": finite,
            }
        )
    return rows


def distribution_rows(root: Path) -> list[dict]:
    rows = []
    for folder, model_name in ROW_ORDER:
        arrays = load_results(root / folder / "selected_test_results.npz")
        pred = arrays["prediction"][:, :, :, 0]
        target = arrays["target"][:, :, :, 0]
        error = pred - target
        for name, arr in [("prediction", pred), ("target", target), ("error", error)]:
            flat = arr.reshape(-1)
            qs = np.percentile(flat, [1, 5, 25, 50, 75, 95, 99])
            rows.append(
                {
                    "folder": folder,
                    "model": model_name,
                    "array": name,
                    "mean": float(np.mean(flat)),
                    "std": float(np.std(flat)),
                    "min": float(np.min(flat)),
                    "p01": float(qs[0]),
                    "p05": float(qs[1]),
                    "p25": float(qs[2]),
                    "p50": float(qs[3]),
                    "p75": float(qs[4]),
                    "p95": float(qs[5]),
                    "p99": float(qs[6]),
                    "max": float(np.max(flat)),
                }
            )
    return rows


def plot_overall(out_dir: Path, overall_rows: list[dict]) -> None:
    labels = [str(row["ID"]) for row in overall_rows]
    x = np.arange(len(labels))
    width = 0.25
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x - width, [row["MAE"] for row in overall_rows], width, label="MAE")
    ax.bar(x, [row["RMSE"] for row in overall_rows], width, label="RMSE")
    ax.bar(x + width, [row["MAPE"] for row in overall_rows], width, label="MAPE")
    ax.set_xticks(x, labels)
    ax.set_xlabel("Ablation ID")
    ax.set_title("Overall Metrics")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_dir / "figures" / "overall_metrics_bar.png", dpi=180)
    plt.close(fig)


def plot_horizon_metric(out_dir: Path, horizon_rows: list[dict], metric: str) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    for folder, model_name in ROW_ORDER:
        rows = [row for row in horizon_rows if row["folder"] == folder]
        ax.plot([row["horizon"] for row in rows], [row[metric] for row in rows], marker="o", label=model_name)
    ax.set_xlabel("Forecast horizon")
    ax.set_ylabel(metric)
    ax.set_title(f"{metric} by Horizon")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / "figures" / f"horizon_{metric.lower()}.png", dpi=180)
    plt.close(fig)


def plot_improvement(out_dir: Path, improvement_rows: list[dict]) -> None:
    rows = improvement_rows[1:]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    bars = ax.bar([row["ID"] for row in rows], [row["MAE_improvement_pct"] for row in rows])
    ax.set_xlabel("Ablation ID")
    ax.set_ylabel("MAE improvement vs baseline (%)")
    ax.set_title("MAE Improvement over Baseline")
    ax.grid(axis="y", alpha=0.25)
    for bar, row in zip(bars, rows):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{row['MAE_improvement_pct']:.2f}%", ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / "figures" / "mae_improvement_vs_baseline.png", dpi=180)
    plt.close(fig)


def plot_distributions(root: Path, out_dir: Path) -> None:
    base = load_results(root / "01_baseline" / "selected_test_results.npz")
    best = load_results(root / "05_baseline_removal_jump_kd" / "selected_test_results.npz")
    target = best["target"][:, :, :, 0].reshape(-1)
    best_pred = best["prediction"][:, :, :, 0].reshape(-1)
    base_err = (base["prediction"][:, :, :, 0] - base["target"][:, :, :, 0]).reshape(-1)
    best_err = (best["prediction"][:, :, :, 0] - best["target"][:, :, :, 0]).reshape(-1)

    fig, ax = plt.subplots(figsize=(9, 5))
    bins = np.linspace(0, np.percentile(target, 99.5), 60)
    ax.hist(target, bins=bins, density=True, alpha=0.55, label="Ground truth")
    ax.hist(best_pred, bins=bins, density=True, alpha=0.55, label="Best prediction")
    ax.set_xlabel("PM2.5")
    ax.set_ylabel("Density")
    ax.set_title("Best Model Prediction vs Ground Truth Distribution")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "figures" / "best_prediction_vs_truth_distribution.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5))
    lo, hi = np.percentile(np.concatenate([base_err, best_err]), [0.5, 99.5])
    bins = np.linspace(lo, hi, 80)
    ax.hist(base_err, bins=bins, density=True, alpha=0.55, label="Baseline error")
    ax.hist(best_err, bins=bins, density=True, alpha=0.55, label="Best error")
    ax.axvline(0, color="black", linewidth=1)
    ax.set_xlabel("Prediction error")
    ax.set_ylabel("Density")
    ax.set_title("Error Distribution: Baseline vs Best")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "figures" / "baseline_vs_best_error_hist.png", dpi=180)
    plt.close(fig)


def write_markdown(out_dir: Path, overall_rows: list[dict], improvement_rows: list[dict]) -> None:
    lines = [
        "# Offline PM2.5 Ablation Analysis",
        "",
        "Generated from released selected-horizon prediction and target arrays.",
        "",
        "## Main Ablation Table",
        "",
        "| ID | Model | Removal | Jump | KD | MAE | RMSE | MAPE |",
        "|---:|---|---|---|---|---:|---:|---:|",
    ]
    for row in overall_rows:
        lines.append(
            f"| {row['ID']} | {row['model']} | {row['removal']} | {row['jump']} | {row['kd']} | "
            f"{row['MAE']:.4f} | {row['RMSE']:.4f} | {row['MAPE']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Improvement vs Baseline",
            "",
            "| ID | Model | MAE delta | MAE improvement | RMSE delta | MAPE delta |",
            "|---:|---|---:|---:|---:|---:|",
        ]
    )
    for row in improvement_rows:
        lines.append(
            f"| {row['ID']} | {row['model']} | {row['MAE_delta_vs_baseline']:.4f} | "
            f"{row['MAE_improvement_pct']:.2f}% | {row['RMSE_delta_vs_baseline']:.4f} | "
            f"{row['MAPE_delta_vs_baseline']:.4f} |"
        )
    (out_dir / "README_OFFLINE_ANALYSIS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="test_data/ablation_results")
    parser.add_argument("--output-dir", default="analysis_outputs")
    args = parser.parse_args()

    root = Path(args.root)
    out_dir = Path(args.output_dir)
    (out_dir / "figures").mkdir(parents=True, exist_ok=True)

    overall_rows, horizon_rows, improvement_rows, jump_rows = metric_rows(root)
    inventory = inventory_rows(root)
    dist_rows = distribution_rows(root)

    write_csv(out_dir / "ablation_overall_metrics.csv", overall_rows, ["ID", "folder", "model", "removal", "jump", "kd", "MAE", "RMSE", "MAPE"])
    write_csv(out_dir / "ablation_horizon_metrics.csv", horizon_rows, ["ID", "folder", "model", "horizon", "MAE", "RMSE", "MAPE"])
    write_csv(out_dir / "ablation_improvement_vs_baseline.csv", improvement_rows, ["ID", "folder", "model", "MAE_delta_vs_baseline", "MAE_improvement_pct", "RMSE_delta_vs_baseline", "RMSE_improvement_pct", "MAPE_delta_vs_baseline", "MAPE_improvement_pct"])
    write_csv(out_dir / "artifact_inventory.csv", inventory, ["folder", "has_metrics", "has_selected_results_npz", "array_shape", "finite_prediction_target"])
    write_csv(out_dir / "prediction_distribution_stats.csv", dist_rows, ["folder", "model", "array", "mean", "std", "min", "p01", "p05", "p25", "p50", "p75", "p95", "p99", "max"])
    write_csv(out_dir / "jump_subset_metrics.csv", jump_rows, ["ID", "folder", "model", "subset", "MAE", "RMSE", "MAPE"])

    plot_overall(out_dir, overall_rows)
    for metric in ["MAE", "RMSE", "MAPE"]:
        plot_horizon_metric(out_dir, horizon_rows, metric)
    plot_improvement(out_dir, improvement_rows)
    plot_distributions(root, out_dir)
    write_markdown(out_dir, overall_rows, improvement_rows)
    print(f"Wrote offline analysis assets to {out_dir.resolve()}")


if __name__ == "__main__":
    main()
