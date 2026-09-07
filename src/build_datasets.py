"""
build_datasets.py
-----------------
Orchestrates the full SDALLE preprocessing pipeline:
  1. Loads all trials (with subject-level isolation preserved)
  2. Runs 9-fold LOSO splits
  3. For each fold:
       - Windows each split for E1, E2, E3, E4
       - Normalizes using TRAINING-FOLD statistics only
       - Saves to data/processed/<EXPERIMENT>/fold_<N>/dataset.npz
  4. Prints a summary verification table

INVARIANTS ENFORCED (with assertions):
  a. EMG must have 8 channels
  b. IMU must have 48 channels
  c. EMG rate is ~1259.2593 Hz
  d. IMU rate is ~148.1481 Hz
  e. No window crosses a trial boundary   (guaranteed by per-trial slicing)
  f. No test subject appears in training  (checked explicitly)
  g. Normalization stats derived from training data only (structural guarantee)
"""

from __future__ import annotations

import shutil
import time
from pathlib import Path
from typing import List, Set

import numpy as np

import dataset_loader
import normalizer
import windower
from dataset_loader import Trial, EXPECTED_EMG_RATE, EXPECTED_IMU_RATE

# ── Output directory ──────────────────────────────────────────────────────────

OUTPUT_DIR = Path("data/processed")

# ── Helpers ───────────────────────────────────────────────────────────────────

def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def assert_no_subject_leakage(train: List[Trial], test: List[Trial], test_sid: int):
    """Assertion f: no test subject appears in training."""
    train_sids: Set[int] = {t.subject_id for t in train}
    assert test_sid not in train_sids, (
        f"LEAKAGE: test subject S{test_sid} appears in training fold!"
    )
    test_sids: Set[int] = {t.subject_id for t in test}
    assert test_sids == {test_sid}, (
        f"Test fold contains unexpected subjects: {test_sids}"
    )


def assert_shapes(name: str, X: np.ndarray, expected_win: int, expected_channels: int):
    assert X.ndim == 3, f"{name}: expected 3-D array, got {X.ndim}-D"
    assert X.shape[1] == expected_win, (
        f"{name}: expected window length {expected_win}, got {X.shape[1]}"
    )
    assert X.shape[2] == expected_channels, (
        f"{name}: expected {expected_channels} channels, got {X.shape[2]}"
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    t_start = time.time()

    print("=" * 65)
    print("SDALLE Preprocessing Pipeline")
    print("=" * 65)
    print(f"Window : {windower.WINDOW_SEC:.1f}s  |  "
          f"Stride : {windower.STRIDE_SEC:.1f}s (50% overlap)")
    print(f"EMG    : {windower.EMG_WIN} samples/window @ ~{EXPECTED_EMG_RATE} Hz")
    print(f"IMU    : {windower.IMU_WIN} samples/window @ ~{EXPECTED_IMU_RATE} Hz")
    print()

    # 1. Load all trials
    all_trials = dataset_loader.load_all_trials()
    assert len(all_trials) > 0, "No trials loaded — check dataset path."

    # Global assertions (c, d) — spot-check first trial
    t0 = all_trials[0]
    assert t0.emg.shape[1] == 8,  f"Assertion a failed: EMG has {t0.emg.shape[1]} channels"
    assert t0.imu.shape[1] == 48, f"Assertion b failed: IMU has {t0.imu.shape[1]} channels"
    # Rates are validated inside dataset_loader._parse_raw_array on file load

    print(f"Loaded {len(all_trials)} trials  "
          f"from {len(set(t.subject_id for t in all_trials))} subjects.")
    print()

    # Clear previous output
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    subjects = sorted(set(t.subject_id for t in all_trials))

    fold_stats = []

    for test_sid in subjects:
        print(f"--- Fold {test_sid:02d}  (Test = Subject_{test_sid}) ---")

        # Split
        train_trials = [t for t in all_trials if t.subject_id != test_sid]
        test_trials  = [t for t in all_trials if t.subject_id == test_sid]

        # Assertion f
        assert_no_subject_leakage(train_trials, test_trials, test_sid)

        # ── E1: EMG only ──────────────────────────────────────────────────────
        print("  E1 EMG-only ...", end=" ", flush=True)
        X_tr, y_tr, _ = windower.window_e1(train_trials)
        X_te, y_te, _ = windower.window_e1(test_trials)
        assert_shapes("E1-train", X_tr, windower.EMG_WIN, 8)
        assert_shapes("E1-test",  X_te, windower.EMG_WIN, 8)
        X_tr_n, X_te_n, _ = normalizer.normalize_single_branch(X_tr, X_te)
        fold_dir = ensure_dir(OUTPUT_DIR / "E1_emg_only" / f"fold_{test_sid}")
        np.savez_compressed(fold_dir / "dataset.npz",
                            X_train=X_tr_n, y_train=y_tr,
                            X_test=X_te_n,  y_test=y_te)
        print(f"train={len(y_tr)} test={len(y_te)}")

        # ── E2: IMU only ──────────────────────────────────────────────────────
        print("  E2 IMU-only ...", end=" ", flush=True)
        X_tr, y_tr, _ = windower.window_e2(train_trials)
        X_te, y_te, _ = windower.window_e2(test_trials)
        assert_shapes("E2-train", X_tr, windower.IMU_WIN, 48)
        assert_shapes("E2-test",  X_te, windower.IMU_WIN, 48)
        X_tr_n, X_te_n, _ = normalizer.normalize_single_branch(X_tr, X_te)
        fold_dir = ensure_dir(OUTPUT_DIR / "E2_imu_only" / f"fold_{test_sid}")
        np.savez_compressed(fold_dir / "dataset.npz",
                            X_train=X_tr_n, y_train=y_tr,
                            X_test=X_te_n,  y_test=y_te)
        print(f"train={len(y_tr)} test={len(y_te)}")

        # ── E3: Rate-matched ──────────────────────────────────────────────────
        print("  E3 Rate-matched ...", end=" ", flush=True)
        X_tr, y_tr, _ = windower.window_e3(train_trials)
        X_te, y_te, _ = windower.window_e3(test_trials)
        assert_shapes("E3-train", X_tr, windower.IMU_WIN, 56)
        assert_shapes("E3-test",  X_te, windower.IMU_WIN, 56)
        X_tr_n, X_te_n, _ = normalizer.normalize_single_branch(X_tr, X_te)
        fold_dir = ensure_dir(OUTPUT_DIR / "E3_rate_matched" / f"fold_{test_sid}")
        np.savez_compressed(fold_dir / "dataset.npz",
                            X_train=X_tr_n, y_train=y_tr,
                            X_test=X_te_n,  y_test=y_te)
        print(f"train={len(y_tr)} test={len(y_te)}")

        # ── E4: Multirate dual-branch ──────────────────────────────────────────
        print("  E4 Multirate ...", end=" ", flush=True)
        Xe_tr, Xi_tr, y_tr, _ = windower.window_e4(train_trials)
        Xe_te, Xi_te, y_te, _ = windower.window_e4(test_trials)
        assert_shapes("E4-emg-train", Xe_tr, windower.EMG_WIN, 8)
        assert_shapes("E4-imu-train", Xi_tr, windower.IMU_WIN, 48)
        assert_shapes("E4-emg-test",  Xe_te, windower.EMG_WIN, 8)
        assert_shapes("E4-imu-test",  Xi_te, windower.IMU_WIN, 48)
        Xe_tr_n, Xe_te_n, Xi_tr_n, Xi_te_n, _, _ = normalizer.normalize_dual_branch(
            Xe_tr, Xe_te, Xi_tr, Xi_te)
        fold_dir = ensure_dir(OUTPUT_DIR / "E4_multirate" / f"fold_{test_sid}")
        np.savez_compressed(fold_dir / "dataset.npz",
                            X_emg_train=Xe_tr_n, X_imu_train=Xi_tr_n, y_train=y_tr,
                            X_emg_test=Xe_te_n,  X_imu_test=Xi_te_n,  y_test=y_te)
        print(f"train={len(y_tr)} test={len(y_te)}")

        fold_stats.append((test_sid, len(y_tr), len(y_te)))
        print()

    elapsed = time.time() - t_start

    # Final summary
    print("=" * 65)
    print("PIPELINE COMPLETE")
    print("=" * 65)
    print(f"Total time : {elapsed:.1f}s")
    print(f"Output dir : {OUTPUT_DIR.resolve()}")
    print()
    print(f"{'Fold':>6}  {'Train windows':>14}  {'Test windows':>12}")
    print("-" * 40)
    for sid, n_tr, n_te in fold_stats:
        print(f"  S{sid:02d}   {n_tr:>14,}  {n_te:>12,}")
    print("-" * 40)
    print()
    print("Tensor shapes (per window):")
    print(f"  E1 EMG           : ({windower.EMG_WIN}, 8)")
    print(f"  E2 IMU           : ({windower.IMU_WIN}, 48)")
    print(f"  E3 Rate-matched  : ({windower.IMU_WIN}, 56)")
    print(f"  E4 EMG branch    : ({windower.EMG_WIN}, 8)")
    print(f"  E4 IMU branch    : ({windower.IMU_WIN}, 48)")
    print()
    print("All assertions passed. No leakage detected.")


if __name__ == "__main__":
    main()
