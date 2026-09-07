"""
evaluate.py
-----------
Loads trained models, computes metrics, saves confusion matrices and predictions.

Metrics computed (macro-averaged unless noted):
  - Accuracy
  - Macro F1
  - Macro Precision
  - Macro Recall
  - Per-class Precision / Recall / F1
  - Confusion matrix (per fold + aggregate)

Also saves a predictions CSV with columns:
  fold, subject_inferred, true_label, predicted_label, correct

Usage:
    python3 src/evaluate.py --exp E1 --fold 1       # single
    python3 src/evaluate.py --exp all --fold all     # full evaluation
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset

from models import build_model

# ── Paths ─────────────────────────────────────────────────────────────────────

PROCESSED_DIR = Path("data/processed")
RESULTS_DIR   = Path("results")

EXP_DIRS = {
    "E1": PROCESSED_DIR / "E1_emg_only",
    "E2": PROCESSED_DIR / "E2_imu_only",
    "E3": PROCESSED_DIR / "E3_rate_matched",
    "E4": PROCESSED_DIR / "E4_multirate",
}

LABEL_NAMES = {0: "jogging", 1: "stairs_down", 2: "stairs_up", 3: "walking"}
N_CLASSES   = 4

# ── Metric helpers ────────────────────────────────────────────────────────────

def _confusion_matrix(y_true, y_pred, n=N_CLASSES):
    cm = np.zeros((n, n), dtype=np.int64)
    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1
    return cm


def _per_class_metrics(cm):
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
    cm        = _confusion_matrix(y_true, y_pred)
    prec, rec, f1 = _per_class_metrics(cm)
    accuracy  = np.diag(cm).sum() / cm.sum()
    macro_p   = np.mean(prec)
    macro_r   = np.mean(rec)
    macro_f1  = np.mean(f1)

    return {
        "accuracy":        round(float(accuracy), 6),
        "macro_precision": round(float(macro_p),  6),
        "macro_recall":    round(float(macro_r),  6),
        "macro_f1":        round(float(macro_f1), 6),
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


def check_no_nan_inf(arr, name="array"):
    assert not np.any(np.isnan(arr)), f"NaN found in {name}"
    assert not np.any(np.isinf(arr)), f"Inf found in {name}"


# ── Inference ─────────────────────────────────────────────────────────────────

def predict_fold(exp: str, fold: int, device: torch.device) -> tuple:
    """
    Load saved model and test data, return (y_true, y_pred) numpy arrays.
    """
    # Load test data
    fold_dir = EXP_DIRS[exp] / f"fold_{fold}"
    npz = np.load(fold_dir / "dataset.npz", allow_pickle=False)

    if exp != "E4":
        X_te = torch.tensor(npz["X_test"],  dtype=torch.float32).permute(0, 2, 1)
        y_te = torch.tensor(npz["y_test"],  dtype=torch.long)
        ds   = TensorDataset(X_te, y_te)
    else:
        Xe_te = torch.tensor(npz["X_emg_test"], dtype=torch.float32).permute(0, 2, 1)
        Xi_te = torch.tensor(npz["X_imu_test"], dtype=torch.float32).permute(0, 2, 1)
        y_te  = torch.tensor(npz["y_test"],     dtype=torch.long)
        ds    = TensorDataset(Xe_te, Xi_te, y_te)

    loader = DataLoader(ds, batch_size=256, shuffle=False, num_workers=0)

    # Load model
    model_path = RESULTS_DIR / exp / f"fold_{fold}" / "model.pt"
    assert model_path.exists(), f"Model not found: {model_path}"

    model = build_model(exp).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
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
            all_true.extend(y.numpy())
            all_pred.extend(logits.argmax(1).cpu().numpy())

    return np.array(all_true), np.array(all_pred)


# ── Evaluation ────────────────────────────────────────────────────────────────

def evaluate_experiment(exp: str, folds: list, device: torch.device):
    print(f"\n{'='*55}")
    print(f"  Evaluating {exp}  ({len(folds)} fold(s))")
    print(f"{'='*55}")

    all_true_global = []
    all_pred_global = []
    fold_metrics    = []
    rows = []   # for CSV

    for fold in folds:
        y_true, y_pred = predict_fold(exp, fold, device)
        check_no_nan_inf(y_pred.astype(float), f"{exp}/fold{fold} predictions")

        assert set(np.unique(y_pred)).issubset({0,1,2,3}), \
            f"Unexpected classes in predictions: {np.unique(y_pred)}"

        metrics = compute_metrics(y_true, y_pred)
        metrics["fold"]           = fold
        metrics["test_subject_id"]= fold
        fold_metrics.append(metrics)

        all_true_global.extend(y_true.tolist())
        all_pred_global.extend(y_pred.tolist())

        # CSV rows
        for i, (t, p) in enumerate(zip(y_true.tolist(), y_pred.tolist())):
            rows.append({
                "experiment":    exp,
                "fold":          fold,
                "test_subject":  fold,
                "window_index":  i,
                "true_label":    t,
                "true_name":     LABEL_NAMES[t],
                "pred_label":    p,
                "pred_name":     LABEL_NAMES[p],
                "correct":       int(t == p),
            })

        acc = metrics["accuracy"]
        f1  = metrics["macro_f1"]
        print(f"  Fold {fold:02d} | acc={acc:.4f}  macro_F1={f1:.4f}")

    # Aggregate across folds
    agg_cm = _confusion_matrix(all_true_global, all_pred_global)
    agg_metrics = compute_metrics(np.array(all_true_global), np.array(all_pred_global))

    accs  = [m["accuracy"]        for m in fold_metrics]
    f1s   = [m["macro_f1"]        for m in fold_metrics]
    precs = [m["macro_precision"]  for m in fold_metrics]
    recs  = [m["macro_recall"]     for m in fold_metrics]

    summary = {
        "experiment":   exp,
        "folds":        folds,
        "mean_accuracy":        round(float(np.mean(accs)),  6),
        "std_accuracy":         round(float(np.std(accs)),   6),
        "mean_macro_f1":        round(float(np.mean(f1s)),   6),
        "std_macro_f1":         round(float(np.std(f1s)),    6),
        "mean_macro_precision": round(float(np.mean(precs)), 6),
        "std_macro_precision":  round(float(np.std(precs)),  6),
        "mean_macro_recall":    round(float(np.mean(recs)),  6),
        "std_macro_recall":     round(float(np.std(recs)),   6),
        "aggregate_metrics":    agg_metrics,
        "fold_metrics":         fold_metrics,
    }

    print(f"\n  SUMMARY  acc={np.mean(accs):.4f}±{np.std(accs):.4f}  "
          f"F1={np.mean(f1s):.4f}±{np.std(f1s):.4f}")

    # Save
    out_dir = RESULTS_DIR / exp
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(out_dir / "eval_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    np.save(out_dir / "aggregate_cm.npy", agg_cm)

    # Save CSV predictions
    import csv
    csv_path = out_dir / "predictions.csv"
    if rows:
        fieldnames = list(rows[0].keys())
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    print(f"  Saved: {out_dir}/eval_summary.json")
    print(f"  Saved: {out_dir}/predictions.csv")
    print(f"  Saved: {out_dir}/aggregate_cm.npy")
    return summary


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Evaluate trained SDALLE models")
    parser.add_argument("--exp",    default="E1", help="E1/E2/E3/E4/all")
    parser.add_argument("--fold",   default="1",  help="1-9 or 'all'")
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()

    device = torch.device(args.device)
    exps   = ["E1", "E2", "E3", "E4"] if args.exp.lower() == "all" else [args.exp.upper()]
    folds  = list(range(1, 10))        if args.fold.lower() == "all" else [int(args.fold)]

    for exp in exps:
        evaluate_experiment(exp, folds, device)


if __name__ == "__main__":
    main()
