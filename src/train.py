"""
train.py
--------
Training loop for E1–E4 LOSO experiments.

Predetermined hyperparameters (fixed before seeing any results):
  optimizer      : Adam, lr=1e-3, weight_decay=1e-4
  batch size     : 64
  epochs         : 50  (or --epochs N for smoke test)
  lr scheduler   : ReduceLROnPlateau(patience=5, factor=0.5),
                   monitors TRAINING loss only (no test-fold
                   signal is read anywhere during training)
  loss           : CrossEntropyLoss (handles class imbalance-awareness is
                   achieved via class-weighted loss if --weighted flag is set)
  random seed    : 42

Usage:
    python3 src/train.py --exp E1 --fold 1           # single fold
    python3 src/train.py --exp E1 --fold 1 --epochs 3  # smoke test
    python3 src/train.py --exp all --fold all          # full run (not yet!)
"""

from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from models import build_model, count_parameters

# ── Paths ─────────────────────────────────────────────────────────────────────

PROCESSED_DIR = Path("data/processed")
RESULTS_DIR   = Path("results")

EXP_DIRS = {
    "E1": PROCESSED_DIR / "E1_emg_only",
    "E2": PROCESSED_DIR / "E2_imu_only",
    "E3": PROCESSED_DIR / "E3_rate_matched",
    "E4": PROCESSED_DIR / "E4_multirate",
}

# ── Fixed hyperparameters ─────────────────────────────────────────────────────

HP = {
    "lr":           1e-3,
    "weight_decay": 1e-4,
    "batch_size":   64,
    "epochs":       50,
    "lr_patience":  5,
    "lr_factor":    0.5,
    "seed":         42,
    "dropout":      0.3,
}


# ── Reproducibility ───────────────────────────────────────────────────────────

def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark     = False


# ── Data loading ──────────────────────────────────────────────────────────────

def load_fold(exp: str, fold: int, device: torch.device):
    """Load one LOSO fold for the given experiment."""
    fold_dir = EXP_DIRS[exp] / f"fold_{fold}"
    npz = np.load(fold_dir / "dataset.npz", allow_pickle=False)

    if exp != "E4":
        X_tr = torch.tensor(npz["X_train"], dtype=torch.float32)  # (N, W, C)
        X_te = torch.tensor(npz["X_test"],  dtype=torch.float32)
        y_tr = torch.tensor(npz["y_train"], dtype=torch.long)
        y_te = torch.tensor(npz["y_test"],  dtype=torch.long)

        # PyTorch Conv1d expects (N, C, W)
        X_tr = X_tr.permute(0, 2, 1).to(device)
        X_te = X_te.permute(0, 2, 1).to(device)
        y_tr = y_tr.to(device)
        y_te = y_te.to(device)

        train_ds = TensorDataset(X_tr, y_tr)
        test_ds  = TensorDataset(X_te, y_te)
    else:
        Xe_tr = torch.tensor(npz["X_emg_train"], dtype=torch.float32).permute(0, 2, 1)
        Xi_tr = torch.tensor(npz["X_imu_train"], dtype=torch.float32).permute(0, 2, 1)
        Xe_te = torch.tensor(npz["X_emg_test"],  dtype=torch.float32).permute(0, 2, 1)
        Xi_te = torch.tensor(npz["X_imu_test"],  dtype=torch.float32).permute(0, 2, 1)
        y_tr  = torch.tensor(npz["y_train"], dtype=torch.long)
        y_te  = torch.tensor(npz["y_test"],  dtype=torch.long)

        train_ds = TensorDataset(Xe_tr, Xi_tr, y_tr)
        test_ds  = TensorDataset(Xe_te, Xi_te, y_te)

    return train_ds, test_ds


# ── Training loop ─────────────────────────────────────────────────────────────

def train_one_fold(exp: str, fold: int, epochs: int, device: torch.device,
                   out_dir: Path, verbose: bool = True) -> dict:
    """
    Train and save one (experiment, fold) combination.
    Returns a dict with history and timing info.
    """
    set_seed(HP["seed"])

    out_dir.mkdir(parents=True, exist_ok=True)

    # Data
    train_ds, test_ds = load_fold(exp, fold, device)
    train_loader = DataLoader(train_ds, batch_size=HP["batch_size"], shuffle=True,
                              num_workers=0, pin_memory=False)
    # Test loader: no shuffle, for evaluation
    test_loader  = DataLoader(test_ds,  batch_size=HP["batch_size"], shuffle=False,
                              num_workers=0, pin_memory=False)

    # Model
    model = build_model(exp).to(device)
    n_params = count_parameters(model)
    if verbose:
        print(f"  Parameters: {n_params:,}")

    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(),
                                 lr=HP["lr"], weight_decay=HP["weight_decay"])
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", patience=HP["lr_patience"], factor=HP["lr_factor"])

    # NOTE (leakage fix): history only ever stores training-set metrics.
    # No test-fold loss or accuracy is computed anywhere inside this
    # epoch loop, and the held-out test subject is never read here.
    history = {"train_loss": [], "train_acc": []}

    t_train_start = time.time()

    for epoch in range(1, epochs + 1):
        # ── Train ──
        model.train()
        running_loss = correct = total = 0
        for batch in train_loader:
            if exp == "E4":
                x_emg, x_imu, y = batch
                logits = model(x_emg, x_imu)
            else:
                x, y = batch
                logits = model(x)

            loss = criterion(logits, y)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * y.size(0)
            correct      += (logits.argmax(1) == y).sum().item()
            total        += y.size(0)

        train_loss = running_loss / total
        train_acc  = correct / total

        # NOTE (leakage fix): the scheduler is driven by TRAINING loss,
        # not test loss. No separate validation-subject partition exists
        # in this protocol (Sec. VI-A/VI-C), and the held-out test
        # subject must not influence optimization, LR scheduling,
        # checkpoint selection, or any other training-time decision.
        # Test-set performance is computed only in evaluate.py, after
        # training has finished.
        scheduler.step(train_loss)

        history["train_loss"].append(round(train_loss, 6))
        history["train_acc"].append(round(train_acc,   6))

        if verbose and (epoch == 1 or epoch % 10 == 0 or epoch == epochs):
            lr_now = optimizer.param_groups[0]["lr"]
            print(f"  Epoch {epoch:3d}/{epochs} | "
                  f"loss {train_loss:.4f} acc {train_acc:.4f} | lr {lr_now:.2e}")

    t_train_end = time.time()
    train_time  = t_train_end - t_train_start

    # ── Inference time (on test set) ──────────────────────────────────────
    model.eval()
    t_inf_start = time.time()
    all_preds = []
    with torch.no_grad():
        for batch in test_loader:
            if exp == "E4":
                x_emg, x_imu, _ = batch
                logits = model(x_emg, x_imu)
            else:
                x, _ = batch
                logits = model(x)
            all_preds.append(logits.argmax(1).cpu().numpy())
    t_inf_end  = time.time()
    inf_time   = t_inf_end - t_inf_start

    # ── Save model ────────────────────────────────────────────────────────
    torch.save(model.state_dict(), out_dir / "model.pt")

    meta = {
        "experiment":   exp,
        "fold":         fold,
        "n_params":     n_params,
        "epochs":       epochs,
        "train_time_s": round(train_time, 2),
        "inf_time_s":   round(inf_time,   4),
        "hp":           HP,
    }
    with open(out_dir / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    with open(out_dir / "history.json", "w") as f:
        json.dump(history, f, indent=2)

    if verbose:
        print(f"  Training time: {train_time:.1f}s  |  "
              f"Inference time: {inf_time:.3f}s  |  "
              f"Params: {n_params:,}")

    return {"meta": meta, "history": history}


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Train SDALLE experiment models")
    parser.add_argument("--exp",    default="E1",
                        help="Experiment code: E1/E2/E3/E4/all")
    parser.add_argument("--fold",   default="1",
                        help="Fold number 1-9 or 'all'")
    parser.add_argument("--epochs", type=int, default=HP["epochs"],
                        help="Override epoch count (e.g. 3 for smoke test)")
    parser.add_argument("--device", default="cpu",
                        help="PyTorch device string (cpu / mps / cuda)")
    args = parser.parse_args()

    device = torch.device(args.device)

    exps  = ["E1", "E2", "E3", "E4"] if args.exp.lower() == "all" else [args.exp.upper()]
    folds = list(range(1, 10))       if args.fold.lower() == "all" else [int(args.fold)]

    for exp in exps:
        for fold in folds:
            print(f"\n{'='*55}")
            print(f"  {exp}  Fold {fold:02d}  ({args.epochs} epochs)")
            print(f"{'='*55}")
            out_dir = RESULTS_DIR / exp / f"fold_{fold}"
            train_one_fold(exp, fold, args.epochs, device, out_dir, verbose=True)

    print("\nDone.")


if __name__ == "__main__":
    main()
