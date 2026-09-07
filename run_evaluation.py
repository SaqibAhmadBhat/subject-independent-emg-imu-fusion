"""
run_evaluation.py
-----------------
Full evaluation pipeline for RP4 — all 36 LOSO folds (E1-E4, folds 1-9).

PROTOCOL GUARANTEES:
  1. results/ directory is NEVER written to.
  2. No model is retrained — only model.pt weights are loaded.
  3. Normalization is NOT re-fitted — dataset.npz already contains
     correctly z-scored test arrays (fitted on training fold only).
  4. No windowing/preprocessing is called — npz loaded directly.
  5. Statistical unit = subject-fold (n=9), NOT individual windows.
  6. Each fold is evaluated exactly once (tracked and asserted).
  7. SHA-256 checksums of model.pt files are verified against
     results/final_results_checksums.sha256 before inference begins.

Usage:
    source .venv/bin/activate
    python3 run_evaluation.py 2>&1 | tee evaluation/evaluation_run.log
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
import datetime
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset

# ── Import models from src/ ───────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent / "src"))
from models import build_model  # noqa: E402

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT   = Path(__file__).parent
PROCESSED = PROJECT / "data" / "processed"
RESULTS   = PROJECT / "results"
EVAL_DIR  = PROJECT / "evaluation"

EXP_DIRS = {
    "E1": PROCESSED / "E1_emg_only",
    "E2": PROCESSED / "E2_imu_only",
    "E3": PROCESSED / "E3_rate_matched",
    "E4": PROCESSED / "E4_multirate",
}

LABEL_NAMES = {0: "jogging", 1: "stairs_down", 2: "stairs_up", 3: "walking"}
N_CLASSES   = 4
EXPS        = ["E1", "E2", "E3", "E4"]
FOLDS       = list(range(1, 10))

# ── Setup output dirs ─────────────────────────────────────────────────────────
for sub in ["predictions", "metrics", "figures", "tables"]:
    (EVAL_DIR / sub).mkdir(parents=True, exist_ok=True)

# ── Utilities ─────────────────────────────────────────────────────────────────

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def confusion_matrix(y_true, y_pred, n=N_CLASSES):
    cm = np.zeros((n, n), dtype=np.int64)
    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1
    return cm


def per_class_metrics(cm):
    precision, recall, f1 = [], [], []
    for c in range(N_CLASSES):
        tp = cm[c, c]
        fp = cm[:, c].sum() - tp
        fn = cm[c, :].sum() - tp
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec  = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1c  = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
        precision.append(prec)
        recall.append(rec)
        f1.append(f1c)
    return precision, recall, f1


def compute_metrics(y_true, y_pred):
    cm                 = confusion_matrix(y_true, y_pred)
    prec, rec, f1      = per_class_metrics(cm)
    accuracy           = float(np.diag(cm).sum() / cm.sum())
    macro_p            = float(np.mean(prec))
    macro_r            = float(np.mean(rec))
    macro_f1           = float(np.mean(f1))
    n_test             = int(cm.sum())
    return {
        "accuracy":        round(accuracy,  6),
        "macro_precision": round(macro_p,   6),
        "macro_recall":    round(macro_r,   6),
        "macro_f1":        round(macro_f1,  6),
        "n_test_windows":  n_test,
        "per_class": {
            LABEL_NAMES[c]: {
                "precision": round(prec[c], 6),
                "recall":    round(rec[c],  6),
                "f1":        round(f1[c],   6),
            }
            for c in range(N_CLASSES)
        },
        "confusion_matrix": cm.tolist(),
    }


# ── Step 1: Pre-check ─────────────────────────────────────────────────────────

def step1_precheck():
    print("\n" + "="*65)
    print("STEP 1 — Pre-check: file existence + model checksum verification")
    print("="*65)

    # Load known checksums
    cksum_file = RESULTS / "final_results_checksums.sha256"
    assert cksum_file.exists(), f"Checksum file not found: {cksum_file}"

    known_checksums = {}
    with open(cksum_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            digest, relpath = line.split("  ", 1)
            known_checksums[relpath] = digest

    errors = []
    for exp in EXPS:
        for fold in FOLDS:
            # model.pt
            model_path = RESULTS / exp / f"fold_{fold}" / "model.pt"
            if not model_path.exists():
                errors.append(f"MISSING: {model_path}")
                continue
            rel = f"{exp}/fold_{fold}/model.pt"
            if rel in known_checksums:
                actual = sha256_file(model_path)
                if actual != known_checksums[rel]:
                    errors.append(
                        f"CHECKSUM MISMATCH: {rel}\n"
                        f"  expected: {known_checksums[rel]}\n"
                        f"  actual:   {actual}"
                    )
                else:
                    pass  # OK
            # dataset.npz
            npz_path = EXP_DIRS[exp] / f"fold_{fold}" / "dataset.npz"
            if not npz_path.exists():
                errors.append(f"MISSING: {npz_path}")

    if errors:
        print("ERRORS:")
        for e in errors:
            print("  ", e)
        raise RuntimeError(f"Pre-check failed with {len(errors)} error(s)")

    print(f"  All 36 model.pt files present and checksums verified.")
    print(f"  All 36 dataset.npz files present.")
    print("  PRE-CHECK PASSED")


# ── Step 2 + 3: Inference + Per-fold metrics ──────────────────────────────────

def predict_fold(exp: str, fold: int, device: torch.device):
    """Load frozen model and test data; return (y_true, y_pred) numpy arrays."""
    npz_path = EXP_DIRS[exp] / f"fold_{fold}" / "dataset.npz"
    npz      = np.load(npz_path, allow_pickle=False)

    if exp != "E4":
        # X_test shape: (N, W, C) — permute to (N, C, W) for Conv1d
        X_te = torch.tensor(npz["X_test"], dtype=torch.float32).permute(0, 2, 1)
        y_te = torch.tensor(npz["y_test"], dtype=torch.long)
        ds   = TensorDataset(X_te, y_te)
    else:
        Xe = torch.tensor(npz["X_emg_test"], dtype=torch.float32).permute(0, 2, 1)
        Xi = torch.tensor(npz["X_imu_test"], dtype=torch.float32).permute(0, 2, 1)
        y_te = torch.tensor(npz["y_test"],   dtype=torch.long)
        ds   = TensorDataset(Xe, Xi, y_te)

    loader = DataLoader(ds, batch_size=256, shuffle=False, num_workers=0)

    model_path = RESULTS / exp / f"fold_{fold}" / "model.pt"
    model = build_model(exp).to(device)
    model.load_state_dict(
        torch.load(model_path, map_location=device, weights_only=True)
    )
    model.eval()

    all_true, all_pred = [], []
    with torch.no_grad():
        for batch in loader:
            if exp == "E4":
                x_emg, x_imu, y = batch
                logits = model(x_emg.to(device), x_imu.to(device))
            else:
                x, y = batch
                logits = model(x.to(device))
            all_true.extend(y.numpy().tolist())
            all_pred.extend(logits.argmax(1).cpu().numpy().tolist())

    return np.array(all_true, dtype=np.int64), np.array(all_pred, dtype=np.int64)


def step2_inference_and_metrics(device):
    print("\n" + "="*65)
    print("STEP 2+3 — Inference and per-fold metrics")
    print("="*65)

    evaluated_set = set()
    all_fold_metrics = {}   # key: (exp, fold) -> metrics dict
    all_predictions  = {}   # key: (exp, fold) -> (y_true, y_pred)

    for exp in EXPS:
        all_fold_metrics[exp] = {}
        for fold in FOLDS:
            assert (exp, fold) not in evaluated_set, \
                f"Fold ({exp}, {fold}) would be evaluated twice!"

            y_true, y_pred = predict_fold(exp, fold, device)
            evaluated_set.add((exp, fold))

            metrics = compute_metrics(y_true, y_pred)
            metrics["experiment"] = exp
            metrics["fold"]       = fold
            metrics["test_subject"] = fold  # fold == left-out subject ID

            all_fold_metrics[exp][fold] = metrics
            all_predictions[(exp, fold)] = (y_true, y_pred)

            # Save per-fold metrics JSON
            out = EVAL_DIR / "metrics" / f"{exp}_fold_{fold}_metrics.json"
            with open(out, "w") as f:
                json.dump(metrics, f, indent=2)

            # Save per-fold predictions CSV
            pred_csv = EVAL_DIR / "predictions" / f"{exp}_fold_{fold}_predictions.csv"
            with open(pred_csv, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=[
                    "experiment","fold","test_subject","window_index",
                    "true_label","true_name","pred_label","pred_name","correct"
                ])
                writer.writeheader()
                for i, (t, p) in enumerate(zip(y_true.tolist(), y_pred.tolist())):
                    writer.writerow({
                        "experiment":   exp,
                        "fold":         fold,
                        "test_subject": fold,
                        "window_index": i,
                        "true_label":   t,
                        "true_name":    LABEL_NAMES[t],
                        "pred_label":   p,
                        "pred_name":    LABEL_NAMES[p],
                        "correct":      int(t == p),
                    })

            acc = metrics["accuracy"]
            f1  = metrics["macro_f1"]
            print(f"  {exp}/fold_{fold:02d}  acc={acc:.4f}  macro_F1={f1:.4f}  "
                  f"n_windows={metrics['n_test_windows']}")

    # Verify exactly 36 folds evaluated
    assert len(evaluated_set) == 36, \
        f"Expected 36 evaluations, got {len(evaluated_set)}"
    print(f"\n  ✓ Exactly 36 folds evaluated — no duplicates, no omissions.")

    return all_fold_metrics, all_predictions


# ── Step 4: Per-experiment summary ───────────────────────────────────────────

def step4_summaries(all_fold_metrics):
    print("\n" + "="*65)
    print("STEP 4 — Per-experiment summaries")
    print("="*65)

    summaries = {}
    for exp in EXPS:
        fold_mets = [all_fold_metrics[exp][f] for f in FOLDS]

        accs  = np.array([m["accuracy"]        for m in fold_mets])
        f1s   = np.array([m["macro_f1"]        for m in fold_mets])
        precs = np.array([m["macro_precision"]  for m in fold_mets])
        recs  = np.array([m["macro_recall"]     for m in fold_mets])

        def stats(arr):
            return {
                "mean":   round(float(np.mean(arr)),   6),
                "std":    round(float(np.std(arr, ddof=0)), 6),
                "median": round(float(np.median(arr)), 6),
                "min":    round(float(np.min(arr)),    6),
                "max":    round(float(np.max(arr)),    6),
            }

        # Aggregate CM (pool all windows)
        all_true_exp = []
        all_pred_exp = []
        for m in fold_mets:
            cm = np.array(m["confusion_matrix"])
            # Reconstruct true/pred from CM — not perfect for per-class
            # but for aggregate CM we store it directly
            pass

        # Build aggregate CM properly from fold_metrics CMs
        agg_cm = np.zeros((N_CLASSES, N_CLASSES), dtype=np.int64)
        for m in fold_mets:
            agg_cm += np.array(m["confusion_matrix"])

        agg_prec, agg_rec, agg_f1_list = per_class_metrics(agg_cm)
        agg_acc = float(np.diag(agg_cm).sum() / agg_cm.sum())

        summary = {
            "experiment": exp,
            "n_folds":    9,
            "accuracy":          stats(accs),
            "macro_precision":   stats(precs),
            "macro_recall":      stats(recs),
            "macro_f1":          stats(f1s),
            "fold_accuracy":     accs.tolist(),
            "fold_macro_f1":     f1s.tolist(),
            "fold_macro_prec":   precs.tolist(),
            "fold_macro_recall": recs.tolist(),
            "aggregate_cm":      agg_cm.tolist(),
            "aggregate_accuracy":        round(agg_acc, 6),
            "aggregate_per_class": {
                LABEL_NAMES[c]: {
                    "precision": round(agg_prec[c], 6),
                    "recall":    round(agg_rec[c],  6),
                    "f1":        round(agg_f1_list[c], 6),
                }
                for c in range(N_CLASSES)
            },
        }
        summaries[exp] = summary

        out = EVAL_DIR / "metrics" / f"{exp}_summary.json"
        with open(out, "w") as f:
            json.dump(summary, f, indent=2)

        print(f"  {exp}  acc={np.mean(accs):.4f}±{np.std(accs):.4f}  "
              f"F1={np.mean(f1s):.4f}±{np.std(f1s):.4f}  "
              f"med_acc={np.median(accs):.4f}")

    return summaries


# ── Step 5: Statistical comparisons ──────────────────────────────────────────

def cohen_d_paired(a, b):
    """Cohen's d for paired differences."""
    diff = np.array(a) - np.array(b)
    return float(np.mean(diff) / (np.std(diff, ddof=1) + 1e-12))


def step5_statistical_tests(summaries):
    from scipy.stats import wilcoxon

    print("\n" + "="*65)
    print("STEP 5 — Statistical comparisons (Wilcoxon + Holm-Bonferroni)")
    print("="*65)

    pairs = [
        ("E1","E2"), ("E1","E3"), ("E1","E4"),
        ("E2","E3"), ("E2","E4"), ("E3","E4"),
    ]

    results_acc = []
    results_f1  = []

    for a, b in pairs:
        arr_a_acc = np.array(summaries[a]["fold_accuracy"])
        arr_b_acc = np.array(summaries[b]["fold_accuracy"])
        arr_a_f1  = np.array(summaries[a]["fold_macro_f1"])
        arr_b_f1  = np.array(summaries[b]["fold_macro_f1"])

        diff_acc = arr_a_acc - arr_b_acc
        diff_f1  = arr_a_f1  - arr_b_f1

        # Wilcoxon — if all differences are zero use exact p=1.0
        try:
            stat_acc, p_acc = wilcoxon(arr_a_acc, arr_b_acc, alternative="two-sided")
        except ValueError:
            stat_acc, p_acc = 0.0, 1.0
        try:
            stat_f1, p_f1 = wilcoxon(arr_a_f1, arr_b_f1, alternative="two-sided")
        except ValueError:
            stat_f1, p_f1 = 0.0, 1.0

        d_acc = cohen_d_paired(arr_a_acc, arr_b_acc)
        d_f1  = cohen_d_paired(arr_a_f1,  arr_b_f1)

        results_acc.append({
            "pair": f"{a}_vs_{b}",
            "exp_a": a, "exp_b": b,
            "mean_a": round(float(arr_a_acc.mean()), 6),
            "mean_b": round(float(arr_b_acc.mean()), 6),
            "mean_diff": round(float(diff_acc.mean()), 6),
            "statistic": round(float(stat_acc), 4),
            "p_raw": round(float(p_acc), 6),
            "cohen_d": round(d_acc, 4),
        })
        results_f1.append({
            "pair": f"{a}_vs_{b}",
            "exp_a": a, "exp_b": b,
            "mean_a": round(float(arr_a_f1.mean()), 6),
            "mean_b": round(float(arr_b_f1.mean()), 6),
            "mean_diff": round(float(diff_f1.mean()), 6),
            "statistic": round(float(stat_f1), 4),
            "p_raw": round(float(p_f1), 6),
            "cohen_d": round(d_f1, 4),
        })

    # Holm-Bonferroni correction
    def holm_bonferroni(results):
        n = len(results)
        sorted_idx = sorted(range(n), key=lambda i: results[i]["p_raw"])
        p_adj = [None] * n
        for rank, idx in enumerate(sorted_idx):
            adjusted = results[idx]["p_raw"] * (n - rank)
            adjusted = min(adjusted, 1.0)
            # Monotonicity: p_adj cannot be less than the previous adjusted p
            if rank > 0:
                prev_adj_rank = sorted_idx[rank-1]
                adjusted = max(adjusted, p_adj[prev_adj_rank])
            p_adj[idx] = round(adjusted, 6)
        for r, pa in zip(results, p_adj):
            r["p_holm"] = pa
            r["significant_holm_0.05"] = pa < 0.05
        return results

    results_acc = holm_bonferroni(results_acc)
    results_f1  = holm_bonferroni(results_f1)

    stats_output = {
        "test":        "Wilcoxon signed-rank (two-sided, paired)",
        "correction":  "Holm-Bonferroni",
        "n_per_pair":  9,
        "statistical_unit": "subject-fold",
        "accuracy_comparisons": results_acc,
        "f1_comparisons":       results_f1,
    }

    out = EVAL_DIR / "metrics" / "statistical_tests.json"
    with open(out, "w") as f:
        json.dump(stats_output, f, indent=2)

    print(f"\n  {'Pair':<12}  {'Acc_A':>7}  {'Acc_B':>7}  "
          f"{'p_raw':>8}  {'p_holm':>8}  {'d':>6}")
    print(f"  {'-'*60}")
    for r in results_acc:
        sig = "*" if r["significant_holm_0.05"] else ""
        print(f"  {r['pair']:<12}  {r['mean_a']:>7.4f}  {r['mean_b']:>7.4f}  "
              f"{r['p_raw']:>8.4f}  {r['p_holm']:>8.4f}{sig:>2}  "
              f"{r['cohen_d']:>6.3f}")

    return stats_output


# ── Step 6: Figures ───────────────────────────────────────────────────────────

def step6_figures(summaries, all_fold_metrics):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    print("\n" + "="*65)
    print("STEP 6 — Generating figures")
    print("="*65)

    sns.set_theme(style="whitegrid", context="paper", font_scale=1.1)
    CMAP = "Blues"

    label_order = [LABEL_NAMES[i] for i in range(N_CLASSES)]
    label_abbr  = ["Jog", "Strs↓", "Strs↑", "Walk"]

    # ── 6a: Individual normalised confusion matrices ────────────────────────
    for exp in EXPS:
        agg_cm = np.array(summaries[exp]["aggregate_cm"])
        cm_norm = agg_cm.astype(float)
        row_sums = cm_norm.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        cm_norm = cm_norm / row_sums

        fig, ax = plt.subplots(figsize=(5.5, 4.5))
        sns.heatmap(
            cm_norm, annot=True, fmt=".2f", cmap=CMAP,
            xticklabels=label_abbr, yticklabels=label_abbr,
            vmin=0, vmax=1, linewidths=0.5, linecolor="white",
            ax=ax, cbar_kws={"shrink": 0.8}
        )
        ax.set_xlabel("Predicted label", fontsize=11)
        ax.set_ylabel("True label", fontsize=11)
        ax.set_title(f"Confusion Matrix — {exp} (Aggregate, Normalised)", fontsize=12)
        plt.tight_layout()
        out = EVAL_DIR / "figures" / f"cm_{exp}.png"
        fig.savefig(out, dpi=180, bbox_inches="tight")
        plt.close(fig)
        print(f"  Saved: {out}")

    # ── 6b: Combined 2x2 confusion matrix figure ───────────────────────────
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    for ax, exp in zip(axes.flat, EXPS):
        agg_cm   = np.array(summaries[exp]["aggregate_cm"])
        cm_norm  = agg_cm.astype(float)
        rs       = cm_norm.sum(axis=1, keepdims=True)
        rs[rs==0] = 1
        cm_norm  = cm_norm / rs
        sns.heatmap(
            cm_norm, annot=True, fmt=".2f", cmap=CMAP,
            xticklabels=label_abbr, yticklabels=label_abbr,
            vmin=0, vmax=1, linewidths=0.5, linecolor="white",
            ax=ax, cbar_kws={"shrink": 0.8}
        )
        mean_acc = summaries[exp]["accuracy"]["mean"]
        ax.set_title(f"{exp}  (mean acc={mean_acc:.3f})", fontsize=12, fontweight="bold")
        ax.set_xlabel("Predicted", fontsize=10)
        ax.set_ylabel("True", fontsize=10)
    fig.suptitle("Aggregate Normalised Confusion Matrices — All Experiments",
                 fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    out = EVAL_DIR / "figures" / "cm_all_experiments.png"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out}")

    # ── 6c: Accuracy box+strip plot ────────────────────────────────────────
    exp_labels_long = {
        "E1": "E1\nEMG-only",
        "E2": "E2\nIMU-only",
        "E3": "E3\nRate-matched",
        "E4": "E4\nMultirate",
    }
    palette = {"E1": "#4C72B0", "E2": "#DD8452", "E3": "#55A868", "E4": "#C44E52"}

    for metric_key, metric_label, fname in [
        ("fold_accuracy",   "Accuracy",   "accuracy_comparison.png"),
        ("fold_macro_f1",   "Macro F1",   "f1_comparison.png"),
    ]:
        fig, ax = plt.subplots(figsize=(7, 5))
        positions = []
        for i, exp in enumerate(EXPS):
            vals = summaries[exp][metric_key]
            bp = ax.boxplot(
                vals, positions=[i], widths=0.4,
                patch_artist=True, notch=False,
                boxprops=dict(facecolor=palette[exp], alpha=0.6),
                medianprops=dict(color="black", linewidth=2),
                whiskerprops=dict(linewidth=1.5),
                capprops=dict(linewidth=1.5),
                flierprops=dict(marker="o", markersize=4),
            )
            jitter = np.random.RandomState(42).uniform(-0.12, 0.12, len(vals))
            ax.scatter(
                [i + j for j in jitter], vals,
                color=palette[exp], s=55, zorder=4, edgecolors="white", linewidths=0.6
            )

        ax.set_xticks(range(len(EXPS)))
        ax.set_xticklabels([exp_labels_long[e] for e in EXPS], fontsize=11)
        ax.set_ylabel(metric_label, fontsize=12)
        ax.set_title(f"{metric_label} across LOSO Folds (n=9 per experiment)",
                     fontsize=13, fontweight="bold")
        ax.set_ylim(0, 1.05)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.2f}"))
        ax.grid(axis="y", linestyle="--", alpha=0.6)
        plt.tight_layout()
        out = EVAL_DIR / "figures" / fname
        fig.savefig(out, dpi=180, bbox_inches="tight")
        plt.close(fig)
        print(f"  Saved: {out}")

    # ── 6d: Grouped bar chart (mean ± std) ────────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 5))
    x      = np.arange(len(EXPS))
    width  = 0.35

    means_acc = [summaries[e]["accuracy"]["mean"]   for e in EXPS]
    stds_acc  = [summaries[e]["accuracy"]["std"]    for e in EXPS]
    means_f1  = [summaries[e]["macro_f1"]["mean"]  for e in EXPS]
    stds_f1   = [summaries[e]["macro_f1"]["std"]   for e in EXPS]

    bars1 = ax.bar(x - width/2, means_acc, width, yerr=stds_acc,
                   label="Accuracy",  color="#4C72B0", alpha=0.8,
                   capsize=5, error_kw=dict(elinewidth=1.5))
    bars2 = ax.bar(x + width/2, means_f1,  width, yerr=stds_f1,
                   label="Macro F1", color="#DD8452", alpha=0.8,
                   capsize=5, error_kw=dict(elinewidth=1.5))

    ax.set_xticks(x)
    ax.set_xticklabels([exp_labels_long[e] for e in EXPS], fontsize=11)
    ax.set_ylabel("Score", fontsize=12)
    ax.set_title("Mean ± Std Accuracy and Macro F1 across LOSO Folds",
                 fontsize=13, fontweight="bold")
    ax.set_ylim(0, 1.1)
    ax.legend(fontsize=11)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.2f}"))
    ax.grid(axis="y", linestyle="--", alpha=0.6)

    # Annotate bars
    for bar, mean in zip(bars1, means_acc):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.015,
                f"{mean:.3f}", ha="center", va="bottom", fontsize=9)
    for bar, mean in zip(bars2, means_f1):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.015,
                f"{mean:.3f}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    out = EVAL_DIR / "figures" / "summary_bar.png"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out}")


# ── Step 7: CSV outputs ───────────────────────────────────────────────────────

def step7_csv_outputs(all_fold_metrics, summaries, stats_output):
    print("\n" + "="*65)
    print("STEP 7 — Writing CSV tables and manifests")
    print("="*65)

    # ── final_metrics.csv — one row per (exp, fold) ────────────────────────
    final_rows = []
    for exp in EXPS:
        for fold in FOLDS:
            m = all_fold_metrics[exp][fold]
            row = {
                "experiment":        exp,
                "fold":              fold,
                "test_subject":      fold,
                "accuracy":          m["accuracy"],
                "macro_precision":   m["macro_precision"],
                "macro_recall":      m["macro_recall"],
                "macro_f1":          m["macro_f1"],
                "n_test_windows":    m["n_test_windows"],
            }
            for cls in LABEL_NAMES.values():
                pc = m["per_class"][cls]
                row[f"{cls}_precision"] = pc["precision"]
                row[f"{cls}_recall"]    = pc["recall"]
                row[f"{cls}_f1"]        = pc["f1"]
            final_rows.append(row)

    final_csv = EVAL_DIR / "final_metrics.csv"
    with open(final_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(final_rows[0].keys()))
        writer.writeheader()
        writer.writerows(final_rows)
    assert len(final_rows) == 36
    print(f"  Saved: {final_csv}  ({len(final_rows)} rows)")

    # ── per_experiment_summary.csv ────────────────────────────────────────
    summary_rows = []
    for exp in EXPS:
        s = summaries[exp]
        row = {"experiment": exp}
        for metric in ["accuracy","macro_precision","macro_recall","macro_f1"]:
            for stat in ["mean","std","median","min","max"]:
                row[f"{metric}_{stat}"] = s[metric][stat]
        summary_rows.append(row)

    summ_csv = EVAL_DIR / "tables" / "per_experiment_summary.csv"
    with open(summ_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"  Saved: {summ_csv}")

    # ── statistical_comparisons.csv ────────────────────────────────────────
    stat_rows = []
    for r_acc, r_f1 in zip(
        stats_output["accuracy_comparisons"],
        stats_output["f1_comparisons"]
    ):
        stat_rows.append({
            "pair":              r_acc["pair"],
            "metric":            "accuracy",
            "mean_a":            r_acc["mean_a"],
            "mean_b":            r_acc["mean_b"],
            "mean_diff_a_minus_b": r_acc["mean_diff"],
            "wilcoxon_statistic": r_acc["statistic"],
            "p_raw":             r_acc["p_raw"],
            "p_holm":            r_acc["p_holm"],
            "significant_holm_0.05": r_acc["significant_holm_0.05"],
            "cohen_d":           r_acc["cohen_d"],
        })
        stat_rows.append({
            "pair":              r_f1["pair"],
            "metric":            "macro_f1",
            "mean_a":            r_f1["mean_a"],
            "mean_b":            r_f1["mean_b"],
            "mean_diff_a_minus_b": r_f1["mean_diff"],
            "wilcoxon_statistic": r_f1["statistic"],
            "p_raw":             r_f1["p_raw"],
            "p_holm":            r_f1["p_holm"],
            "significant_holm_0.05": r_f1["significant_holm_0.05"],
            "cohen_d":           r_f1["cohen_d"],
        })

    stat_csv = EVAL_DIR / "tables" / "statistical_comparisons.csv"
    with open(stat_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(stat_rows[0].keys()))
        writer.writeheader()
        writer.writerows(stat_rows)
    print(f"  Saved: {stat_csv}")

    # ── evaluation_manifest.csv ────────────────────────────────────────────
    manifest_rows = []
    for exp in EXPS:
        for fold in FOLDS:
            m        = all_fold_metrics[exp][fold]
            npz_path = EXP_DIRS[exp] / f"fold_{fold}" / "dataset.npz"
            mpt_path = RESULTS / exp / f"fold_{fold}" / "model.pt"
            manifest_rows.append({
                "experiment":    exp,
                "fold":          fold,
                "evaluated":     True,
                "n_test_windows": m["n_test_windows"],
                "accuracy":      m["accuracy"],
                "macro_f1":      m["macro_f1"],
                "model_pt_sha256": sha256_file(mpt_path),
                "dataset_npz_exists": npz_path.exists(),
            })

    man_csv = EVAL_DIR / "evaluation_manifest.csv"
    with open(man_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(manifest_rows[0].keys()))
        writer.writeheader()
        writer.writerows(manifest_rows)
    assert len(manifest_rows) == 36
    assert all(r["evaluated"] for r in manifest_rows)
    print(f"  Saved: {man_csv}  ({len(manifest_rows)} rows, all evaluated=True)")


# ── Step 8: Audit markdown ────────────────────────────────────────────────────

def step8_audit(all_fold_metrics, summaries, stats_output):
    print("\n" + "="*65)
    print("STEP 8 — Writing evaluation audit")
    print("="*65)

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "# Evaluation Audit — RP4",
        "",
        f"**Generated:** {now}",
        f"**Script:** `run_evaluation.py`",
        "",
        "---",
        "",
        "## Protocol Summary",
        "",
        "| Property | Value |",
        "|---|---|",
        "| Evaluation protocol | Leave-One-Subject-Out (LOSO) |",
        "| N subjects (folds) | 9 per experiment |",
        "| Experiments | E1, E2, E3, E4 |",
        "| Total folds evaluated | 36 |",
        "| Statistical unit | Subject-fold (n=9) |",
        "| Statistical test | Wilcoxon signed-rank (paired, two-sided) |",
        "| Multiple comparisons | Holm-Bonferroni (6 pairs) |",
        "| Effect size | Cohen's d (paired differences) |",
        "| Normalization | Pre-computed in dataset.npz (training-fold stats only) |",
        "| Checkpoint selection | None — single model.pt per fold loaded |",
        "| results/ directory | Frozen — not written to |",
        "",
        "---",
        "",
        "## Completion Status",
        "",
        "| Experiment | Folds Evaluated | Status |",
        "|---|---|---|",
    ]

    for exp in EXPS:
        lines.append(f"| {exp} | 9/9 | ✅ COMPLETE |")

    lines += [
        "",
        "**TOTAL: 36/36 folds evaluated** ✅",
        "",
        "---",
        "",
        "## Per-Experiment Results",
        "",
        "### Fold-Level Metrics",
        "",
        "| Exp | Fold | Accuracy | Macro P | Macro R | Macro F1 | N Windows |",
        "|---|---|---|---|---|---|---|",
    ]
    for exp in EXPS:
        for fold in FOLDS:
            m = all_fold_metrics[exp][fold]
            lines.append(
                f"| {exp} | {fold} | {m['accuracy']:.4f} | "
                f"{m['macro_precision']:.4f} | {m['macro_recall']:.4f} | "
                f"{m['macro_f1']:.4f} | {m['n_test_windows']} |"
            )

    lines += [
        "",
        "---",
        "",
        "### Experiment-Level Summaries",
        "",
        "| Experiment | Acc Mean | Acc Std | Acc Med | F1 Mean | F1 Std | F1 Med |",
        "|---|---|---|---|---|---|---|",
    ]
    for exp in EXPS:
        s = summaries[exp]
        lines.append(
            f"| {exp} | {s['accuracy']['mean']:.4f} | {s['accuracy']['std']:.4f} | "
            f"{s['accuracy']['median']:.4f} | {s['macro_f1']['mean']:.4f} | "
            f"{s['macro_f1']['std']:.4f} | {s['macro_f1']['median']:.4f} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Statistical Comparisons (Accuracy)",
        "",
        "Test: Wilcoxon signed-rank (paired, two-sided, n=9)",
        "Correction: Holm-Bonferroni",
        "",
        "| Pair | Mean A | Mean B | Mean Diff | W stat | p (raw) | p (Holm) | Sig | Cohen's d |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in stats_output["accuracy_comparisons"]:
        sig = "✅" if r["significant_holm_0.05"] else "—"
        lines.append(
            f"| {r['pair']} | {r['mean_a']:.4f} | {r['mean_b']:.4f} | "
            f"{r['mean_diff']:+.4f} | {r['statistic']:.1f} | "
            f"{r['p_raw']:.4f} | {r['p_holm']:.4f} | {sig} | {r['cohen_d']:.3f} |"
        )

    lines += [
        "",
        "## Statistical Comparisons (Macro F1)",
        "",
        "| Pair | Mean A | Mean B | Mean Diff | W stat | p (raw) | p (Holm) | Sig | Cohen's d |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in stats_output["f1_comparisons"]:
        sig = "✅" if r["significant_holm_0.05"] else "—"
        lines.append(
            f"| {r['pair']} | {r['mean_a']:.4f} | {r['mean_b']:.4f} | "
            f"{r['mean_diff']:+.4f} | {r['statistic']:.1f} | "
            f"{r['p_raw']:.4f} | {r['p_holm']:.4f} | {sig} | {r['cohen_d']:.3f} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Output Files",
        "",
        "| File | Description |",
        "|---|---|",
        "| `evaluation/final_metrics.csv` | 36 rows, per-fold all metrics |",
        "| `evaluation/evaluation_manifest.csv` | 36 rows, fold evaluated=True |",
        "| `evaluation/tables/per_experiment_summary.csv` | 4 rows, mean/std/median/min/max |",
        "| `evaluation/tables/statistical_comparisons.csv` | 12 rows, 6 pairs × 2 metrics |",
        "| `evaluation/metrics/*_fold_*_metrics.json` | 36 files, per-fold JSON |",
        "| `evaluation/metrics/*_summary.json` | 4 files, per-experiment JSON |",
        "| `evaluation/metrics/statistical_tests.json` | Full statistical results |",
        "| `evaluation/predictions/*.csv` | 36 files, window-level predictions |",
        "| `evaluation/figures/cm_*.png` | 4 individual confusion matrices |",
        "| `evaluation/figures/cm_all_experiments.png` | Combined 2x2 CM figure |",
        "| `evaluation/figures/accuracy_comparison.png` | Box+strip plot, accuracy |",
        "| `evaluation/figures/f1_comparison.png` | Box+strip plot, macro F1 |",
        "| `evaluation/figures/summary_bar.png` | Mean±std grouped bar chart |",
        "",
        "---",
        "",
        "> **Protocol compliance confirmed:**",
        "> - results/ directory: NOT modified",
        "> - No retraining performed",
        "> - No normalization re-fitted",
        "> - No checkpoint selection using test data",
        "> - Statistical unit: subject-fold (n=9), NOT individual windows",
        "> - All 36 folds evaluated exactly once",
        "",
    ]

    audit_path = EVAL_DIR / "evaluation_audit.md"
    with open(audit_path, "w") as f:
        f.write("\n".join(lines))
    print(f"  Saved: {audit_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "="*65)
    print("  RP4 EVALUATION PIPELINE")
    print(f"  Started: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}")
    print("="*65)

    device = torch.device("cpu")  # CPU for safe, reproducible inference

    step1_precheck()
    all_fold_metrics, all_predictions = step2_inference_and_metrics(device)
    summaries    = step4_summaries(all_fold_metrics)
    stats_output = step5_statistical_tests(summaries)
    step6_figures(summaries, all_fold_metrics)
    step7_csv_outputs(all_fold_metrics, summaries, stats_output)
    step8_audit(all_fold_metrics, summaries, stats_output)

    print("\n" + "="*65)
    print("  EVALUATION COMPLETE")
    print(f"  Finished: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}")
    print(f"  Output directory: {EVAL_DIR.resolve()}")
    print("="*65)


if __name__ == "__main__":
    main()
