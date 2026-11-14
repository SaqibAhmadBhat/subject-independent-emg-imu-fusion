"""
robustness_train.py
-------------------
Robustness study trainer for E3-D vs E4.

Runs all (seed x fold x condition) combinations and saves results to
V2_ROBUSTNESS_STUDY/seed_{S}/{exp}/fold_{k}/.

Does NOT overwrite V2/results/raw/.
Does NOT modify any existing files.

Usage:
    python robustness_train.py --exp E3-D --seeds 42 123 2024 3407 7777 --folds all
    python robustness_train.py --exp all  --seeds all --folds all
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

# ── Path setup ────────────────────────────────────────────────────────────────
STUDY_DIR   = Path(__file__).resolve().parent
LOCAL_SRC   = STUDY_DIR / "src"
WORKSPACE   = STUDY_DIR.parent
V2_SRC      = WORKSPACE / "V2" / "src"
SRC         = WORKSPACE / "src"

sys.path.insert(0, str(LOCAL_SRC))
sys.path.insert(0, str(V2_SRC))
sys.path.insert(0, str(SRC))

from models_v2 import build_model_v2
from models import count_parameters

# ── Paths ─────────────────────────────────────────────────────────────────────
PROCESSED_DIR = WORKSPACE / "V2" / "data" / "processed"
STUDY_DIR     = WORKSPACE / "V2_ROBUSTNESS_STUDY"

# ── Fixed hyperparameters (identical to original V2) ──────────────────────────
HP = {
    "lr":           1e-3,
    "weight_decay": 1e-4,
    "batch_size":   64,
    "epochs":       50,
    "dropout":      0.3,
}

EXPECTED_PARAMS = {"E3-D": 330052, "E4": 330052}
LABEL_NAMES     = {0: "jogging", 1: "stairs_down", 2: "stairs_up", 3: "walking"}
N_CLASSES       = 4
SEEDS           = [42, 123, 2024, 3407, 7777]
FOLDS           = list(range(1, 10))

# ── Reproducibility ───────────────────────────────────────────────────────────

def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark     = False

# ── Data loading ──────────────────────────────────────────────────────────────

def load_fold(exp: str, fold: int, device: torch.device):
    npz_path = PROCESSED_DIR / exp / f"dataset_fold_{fold}.npz"
    if not npz_path.exists():
        raise FileNotFoundError(f"Dataset not found: {npz_path}")
    npz = np.load(npz_path, allow_pickle=False)

    Xe_tr = torch.tensor(npz["X_emg_train"], dtype=torch.float32).permute(0, 2, 1).to(device)
    Xi_tr = torch.tensor(npz["X_imu_train"], dtype=torch.float32).permute(0, 2, 1).to(device)
    Xe_te = torch.tensor(npz["X_emg_test"],  dtype=torch.float32).permute(0, 2, 1).to(device)
    Xi_te = torch.tensor(npz["X_imu_test"],  dtype=torch.float32).permute(0, 2, 1).to(device)
    y_tr  = torch.tensor(npz["y_train"],     dtype=torch.long).to(device)
    y_te  = torch.tensor(npz["y_test"],      dtype=torch.long).to(device)

    train_ds = TensorDataset(Xe_tr, Xi_tr, y_tr)
    test_ds  = TensorDataset(Xe_te, Xi_te, y_te)
    return train_ds, test_ds, y_te.cpu().numpy()

# ── Metric helpers ────────────────────────────────────────────────────────────

def _confusion_matrix(y_true, y_pred, n=N_CLASSES):
    cm = np.zeros((n, n), dtype=np.int64)
    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1
    return cm

def _per_class_metrics(cm):
    precision, recall, f1, support = [], [], [], []
    for c in range(N_CLASSES):
        tp = cm[c, c]
        fp = cm[:, c].sum() - tp
        fn = cm[c, :].sum() - tp
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec  = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1c  = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
        precision.append(round(float(prec), 6))
        recall.append(round(float(rec), 6))
        f1.append(round(float(f1c), 6))
        support.append(int(cm[c, :].sum()))
    return precision, recall, f1, support

def compute_metrics(y_true, y_pred):
    cm = _confusion_matrix(y_true, y_pred)
    prec, rec, f1, sup = _per_class_metrics(cm)
    accuracy  = float(np.diag(cm).sum() / cm.sum())
    macro_f1  = float(np.mean(f1))
    macro_p   = float(np.mean(prec))
    macro_r   = float(np.mean(rec))
    return {
        "accuracy":        round(accuracy, 6),
        "macro_f1":        round(macro_f1, 6),
        "macro_precision": round(macro_p,  6),
        "macro_recall":    round(macro_r,  6),
        "per_class": {
            LABEL_NAMES[c]: {
                "precision": prec[c],
                "recall":    rec[c],
                "f1":        f1[c],
                "support":   sup[c],
            } for c in range(N_CLASSES)
        },
        "confusion_matrix": cm.tolist(),
    }

REQUIRED_FOLD_FILES = ["model.pt", "meta.json", "predictions.csv", "history.json"]


def check_fold_status(fold_dir: Path, exp: str, fold: int, seed: int) -> tuple[str, dict | None, str | None]:
    """
    Check the status of a fold directory.
    Returns:
        (status, result_dict, diagnostic_msg)
        status is one of: "COMPLETED", "MISSING", "INCONSISTENT"
    """
    if not fold_dir.exists():
        return "MISSING", None, None

    present = [f for f in REQUIRED_FOLD_FILES if (fold_dir / f).exists()]
    missing = [f for f in REQUIRED_FOLD_FILES if not (fold_dir / f).exists()]

    if len(present) == 0:
        non_hidden = [p.name for p in fold_dir.iterdir() if not p.name.startswith(".")]
        if len(non_hidden) == 0:
            return "MISSING", None, None
        return "INCONSISTENT", None, (
            f"Fold directory {fold_dir} contains unexpected non-fold files: {non_hidden}"
        )

    if len(missing) > 0:
        return "INCONSISTENT", None, (
            f"Partial fold in {fold_dir}: found {present}, missing {missing}"
        )

    # All 4 files exist; now validate contents
    model_path = fold_dir / "model.pt"
    if model_path.stat().st_size == 0:
        return "INCONSISTENT", None, f"model.pt in {fold_dir} is 0 bytes (empty file)"

    # meta.json
    try:
        with open(fold_dir / "meta.json") as f:
            meta = json.load(f)
    except Exception as e:
        return "INCONSISTENT", None, f"Failed to parse meta.json in {fold_dir}: {e}"

    if meta.get("experiment") != exp:
        return "INCONSISTENT", None, (
            f"Metadata mismatch in {fold_dir}/meta.json: "
            f"expected experiment '{exp}', got '{meta.get('experiment')}'"
        )
    if meta.get("seed") != seed:
        return "INCONSISTENT", None, (
            f"Metadata mismatch in {fold_dir}/meta.json: "
            f"expected seed {seed}, got {meta.get('seed')}"
        )
    if meta.get("fold") != fold:
        return "INCONSISTENT", None, (
            f"Metadata mismatch in {fold_dir}/meta.json: "
            f"expected fold {fold}, got {meta.get('fold')}"
        )

    metrics = meta.get("metrics")
    if not metrics or "accuracy" not in metrics or "macro_f1" not in metrics:
        return "INCONSISTENT", None, f"meta.json in {fold_dir} missing valid metrics"

    # history.json
    try:
        with open(fold_dir / "history.json") as f:
            history = json.load(f)
    except Exception as e:
        return "INCONSISTENT", None, f"Failed to parse history.json in {fold_dir}: {e}"

    if not isinstance(history, dict) or "train_loss" not in history or "train_acc" not in history:
        return "INCONSISTENT", None, f"history.json in {fold_dir} missing train_loss/train_acc"

    # predictions.csv
    try:
        y_true, y_pred = [], []
        with open(fold_dir / "predictions.csv", newline="") as f:
            reader = csv.DictReader(f)
            rows = sorted(reader, key=lambda r: int(r["window_index"]))
            for r in rows:
                y_true.append(int(r["true_label"]))
                y_pred.append(int(r["pred_label"]))
        if len(y_true) == 0:
            return "INCONSISTENT", None, f"predictions.csv in {fold_dir} contains no rows"
        y_true_np = np.array(y_true, dtype=np.int64)
        y_pred_np = np.array(y_pred, dtype=np.int64)
    except Exception as e:
        return "INCONSISTENT", None, f"Failed to parse predictions.csv in {fold_dir}: {e}"

    result = {
        "meta": meta,
        "history": history,
        "metrics": metrics,
        "y_true": y_true_np,
        "y_pred": y_pred_np,
    }
    return "COMPLETED", result, None


# ── Training loop ─────────────────────────────────────────────────────────────

def train_one_fold(exp: str, fold: int, seed: int, device: torch.device,
                   out_dir: Path, verbose: bool = True) -> dict:
    """Train one (exp, fold, seed) combination. Never modifies V2/results/."""
    # Safety guard: never overwrite existing completed fold checkpoint
    model_pt = out_dir / "model.pt"
    if model_pt.exists() and model_pt.stat().st_size > 0:
        raise RuntimeError(f"SAFETY VIOLATION: Refusing to overwrite existing checkpoint in {out_dir}")

    # CRITICAL: Set seed BEFORE model instantiation and data loading
    set_seed(seed)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Check output dir is NOT inside V2/results (safety guard)
    v2_results = (WORKSPACE / "V2" / "results").resolve()
    if str(out_dir.resolve()).startswith(str(v2_results)):
        raise RuntimeError(f"SAFETY VIOLATION: out_dir={out_dir} is inside V2/results/")

    train_ds, test_ds, y_te_np = load_fold(exp, fold, device)

    train_loader = DataLoader(train_ds, batch_size=HP["batch_size"], shuffle=True,
                              generator=torch.Generator().manual_seed(seed))
    test_loader  = DataLoader(test_ds,  batch_size=HP["batch_size"], shuffle=False)

    model    = build_model_v2(exp).to(device)
    n_params = count_parameters(model)

    # PARAMETER MATCHING ASSERTION
    expected = EXPECTED_PARAMS.get(exp)
    if expected and n_params != expected:
        raise AssertionError(f"Parameter mismatch: {exp} has {n_params}, expected {expected}")

    if verbose:
        print(f"    Params: {n_params:,}  |  Seed: {seed}  |  Device: {device}")

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=HP["lr"],
                                  weight_decay=HP["weight_decay"])
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=HP["epochs"])

    history = {"train_loss": [], "train_acc": []}
    t_train_start = time.time()

    for epoch in range(1, HP["epochs"] + 1):
        model.train()
        running_loss = correct = total = 0
        for x_emg, x_imu, y in train_loader:
            logits = model(x_emg, x_imu)
            loss   = criterion(logits, y)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * y.size(0)
            correct      += (logits.argmax(1) == y).sum().item()
            total        += y.size(0)

        train_loss = running_loss / total
        train_acc  = correct / total
        scheduler.step()
        history["train_loss"].append(round(train_loss, 6))
        history["train_acc"].append(round(train_acc,   6))

        if verbose and (epoch == 1 or epoch % 10 == 0 or epoch == HP["epochs"]):
            print(f"    Epoch {epoch:3d}/{HP['epochs']} | "
                  f"loss={train_loss:.4f}  acc={train_acc:.4f}")

    t_train_end = time.time()
    train_time  = t_train_end - t_train_start

    # Inference + prediction collection
    model.eval()
    all_true, all_pred = [], []
    t_inf_start = time.time()
    with torch.no_grad():
        for x_emg, x_imu, y in test_loader:
            logits = model(x_emg.to(device), x_imu.to(device))
            all_true.extend(y.cpu().numpy())
            all_pred.extend(logits.argmax(1).cpu().numpy())
    t_inf_end = time.time()
    inf_time  = t_inf_end - t_inf_start

    all_true = np.array(all_true, dtype=np.int64)
    all_pred = np.array(all_pred, dtype=np.int64)
    metrics  = compute_metrics(all_true, all_pred)

    # Save model checkpoint into study dir (NOT V2/results)
    torch.save(model.state_dict(), out_dir / "model.pt")

    # meta.json
    meta = {
        "experiment":   exp,
        "fold":         fold,
        "seed":         seed,
        "n_params":     n_params,
        "epochs":       HP["epochs"],
        "train_time_s": round(train_time, 2),
        "inf_time_s":   round(inf_time,   4),
        "hp":           HP,
        "metrics":      metrics,
    }
    with open(out_dir / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    # history.json
    with open(out_dir / "history.json", "w") as f:
        json.dump(history, f, indent=2)

    # predictions.csv
    rows = [
        {
            "experiment":   exp,
            "fold":         fold,
            "seed":         seed,
            "window_index": i,
            "true_label":   int(t),
            "true_name":    LABEL_NAMES[int(t)],
            "pred_label":   int(p),
            "pred_name":    LABEL_NAMES[int(p)],
            "correct":      int(t == p),
        }
        for i, (t, p) in enumerate(zip(all_true, all_pred))
    ]
    with open(out_dir / "predictions.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    return {"meta": meta, "history": history, "metrics": metrics,
            "y_true": all_true, "y_pred": all_pred}

# ── Evaluate one seed ─────────────────────────────────────────────────────────

def evaluate_seed(exp: str, seed: int, fold_results: list, out_dir: Path):
    """Aggregate fold results for one (exp, seed) pair."""
    fold_metrics = [r["metrics"] for r in fold_results]
    accs  = [m["accuracy"]  for m in fold_metrics]
    f1s   = [m["macro_f1"]  for m in fold_metrics]

    all_true = np.concatenate([r["y_true"] for r in fold_results])
    all_pred = np.concatenate([r["y_pred"] for r in fold_results])
    agg_metrics = compute_metrics(all_true, all_pred)

    fold_ids = [r["meta"].get("fold", FOLDS[i]) for i, r in enumerate(fold_results)]

    summary = {
        "experiment":       exp,
        "seed":             seed,
        "folds":            fold_ids,
        "mean_accuracy":    round(float(np.mean(accs)), 6),
        "std_accuracy":     round(float(np.std(accs)),  6),
        "mean_macro_f1":    round(float(np.mean(f1s)),  6),
        "std_macro_f1":     round(float(np.std(f1s)),   6),
        "fold_accuracy":    [round(a, 6) for a in accs],
        "fold_macro_f1":    [round(f, 6) for f in f1s],
        "aggregate_metrics": agg_metrics,
        "fold_metrics":     [
            {**m, "fold": fold_ids[i], "test_subject_id": fold_ids[i]}
            for i, m in enumerate(fold_metrics)
        ],
    }
    with open(out_dir / "eval_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"  [{exp} seed={seed}] "
          f"acc={np.mean(accs):.4f}+/-{np.std(accs):.4f}  "
          f"F1={np.mean(f1s):.4f}+/-{np.std(f1s):.4f}")
    return summary

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Robustness study trainer")
    parser.add_argument("--exp",   default="all",
                        help="E3-D, E4, or all (default: all)")
    parser.add_argument("--seeds", nargs="+", type=int, default=SEEDS,
                        help="Seeds to run (default: all 5)")
    parser.add_argument("--folds", default="all",
                        help="Fold numbers or 'all' (default: all)")
    parser.add_argument("--device", default="cpu",
                        help="PyTorch device (default: cpu)")
    parser.add_argument("--verbose", action="store_true", default=True)
    parser.add_argument("--resume", action="store_true", default=False,
                        help="Resume study: skip valid completed folds, train only missing")
    parser.add_argument("--dry-run", action="store_true", default=False,
                        help="Scan completed and missing folds without training")
    args = parser.parse_args()

    device = torch.device(args.device)
    exps   = ["E3-D", "E4"] if args.exp.lower() == "all" else [args.exp.upper()]
    folds  = FOLDS if args.folds.lower() == "all" else [int(f) for f in args.folds.split(",")]
    seeds  = args.seeds

    print(f"\nRobustness Study Configuration:")
    print(f"  Experiments : {exps}")
    print(f"  Seeds       : {seeds}")
    print(f"  Folds       : {folds}")
    print(f"  Device      : {device}")
    print(f"  Resume      : {args.resume}")
    if args.dry_run:
        print(f"  Dry Run     : True")
    print(f"  Total runs  : {len(exps) * len(seeds) * len(folds)}")
    print()

    # ── Pre-flight scan across all requested combinations ─────────────────────
    completed_runs = []
    missing_runs   = []
    inconsistent_runs = []

    for seed in seeds:
        for exp in exps:
            for fold in folds:
                fdir = STUDY_DIR / f"seed_{seed}" / exp / f"fold_{fold}"
                status, res, diag = check_fold_status(fdir, exp, fold, seed)
                if status == "COMPLETED":
                    completed_runs.append((seed, exp, fold, res))
                elif status == "MISSING":
                    missing_runs.append((seed, exp, fold))
                else:
                    inconsistent_runs.append((seed, exp, fold, diag))

    print("=" * 60)
    print("Pre-flight scan summary:")
    print(f"  Total planned runs : {len(seeds) * len(exps) * len(folds)}")
    print(f"  Valid completed    : {len(completed_runs)}")
    print(f"  Missing to train   : {len(missing_runs)}")
    print(f"  Inconsistent/error : {len(inconsistent_runs)}")
    print("=" * 60)

    if inconsistent_runs:
        print("\nERROR: Inconsistent or partial fold outputs detected:")
        for s, e, f, diag in inconsistent_runs:
            print(f"  - Seed {s}, {e}, fold {f}: {diag}")
        raise RuntimeError(
            f"Aborting due to {len(inconsistent_runs)} inconsistent/partial fold output(s). "
            f"Fix or clean these directories before proceeding."
        )

    if not args.resume and len(completed_runs) > 0:
        raise RuntimeError(
            f"Safety guard: Found {len(completed_runs)} completed fold(s) but --resume was not specified. "
            f"Pass --resume to skip completed folds and train only missing folds."
        )

    if args.dry_run:
        print(f"\n[DRY RUN] Scan complete.")
        print(f"  Completed folds recognized : {len(completed_runs)}")
        print(f"  Missing folds to train     : {len(missing_runs)}")
        for s, e, f in missing_runs:
            print(f"    -> Missing: Seed {s}, {e}, fold {f}")
        print("\nExiting dry run without training.")
        return

    run_log = {"successful": [], "failed": []}

    def save_run_log():
        STUDY_DIR.mkdir(parents=True, exist_ok=True)
        with open(STUDY_DIR / "run_log.json", "w") as f:
            json.dump(run_log, f, indent=2)

    try:
        for seed in seeds:
            seed_dir = STUDY_DIR / f"seed_{seed}"
            for exp in exps:
                print(f"\n{'='*60}")
                print(f"  {exp}  |  seed={seed}  |  {len(folds)} folds")
                print(f"{'='*60}")
                exp_dir = seed_dir / exp
                exp_dir.mkdir(parents=True, exist_ok=True)

                fold_results = []
                for fold in folds:
                    fold_dir = exp_dir / f"fold_{fold}"
                    status, result, diag = check_fold_status(fold_dir, exp, fold, seed)

                    if status == "INCONSISTENT":
                        raise RuntimeError(f"INCONSISTENT FOLD DETECTED in {fold_dir}: {diag}")

                    if status == "COMPLETED" and args.resume:
                        print(f"  [RESUME] Fold {fold}/9 already completed "
                              f"(acc={result['metrics']['accuracy']:.4f}, "
                              f"F1={result['metrics']['macro_f1']:.4f}) — loaded.")
                        fold_results.append(result)
                        run_log["successful"].append({
                            "exp": exp,
                            "seed": seed,
                            "fold": fold,
                            "acc": result["metrics"]["accuracy"],
                            "macro_f1": result["metrics"]["macro_f1"],
                        })
                        save_run_log()
                        continue

                    # Train missing fold
                    print(f"\n  Fold {fold}/9 (test_subject={fold}) [TRAINING]")
                    try:
                        result = train_one_fold(exp, fold, seed, device, fold_dir,
                                                verbose=args.verbose)
                        fold_results.append(result)
                        run_log["successful"].append({
                            "exp": exp,
                            "seed": seed,
                            "fold": fold,
                            "acc": result["metrics"]["accuracy"],
                            "macro_f1": result["metrics"]["macro_f1"],
                        })
                        save_run_log()
                    except Exception as e:
                        print(f"  ERROR: {e}")
                        run_log["failed"].append({
                            "exp": exp, "seed": seed, "fold": fold, "error": str(e)
                        })
                        save_run_log()

                if fold_results:
                    evaluate_seed(exp, seed, fold_results, exp_dir)

    finally:
        save_run_log()

    print(f"\n\nRun complete.")
    print(f"  Successful: {len(run_log['successful'])}")
    print(f"  Failed    : {len(run_log['failed'])}")
    if run_log["failed"]:
        print(f"  Failed runs:")
        for r in run_log["failed"]:
            print(f"    {r}")

if __name__ == "__main__":
    main()
