"""
sanity_test.py
--------------
Runs targeted tests on 3 trials from different subjects and activities
to verify dataset_loader, windower, and normalizer correctness
BEFORE running the full pipeline.
"""

import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import dataset_loader
import windower
import normalizer
from dataset_loader import EXPECTED_EMG_RATE, EXPECTED_IMU_RATE

PASS = "PASS"
FAIL = "FAIL"

def check(cond, msg):
    status = PASS if cond else FAIL
    mark = "✓" if cond else "✗"
    print(f"  [{status}] {mark} {msg}")
    return cond

def section(title):
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")

def run_all():
    all_ok = True

    # ── 1. Load 3 specific trials ──────────────────────────────────────────
    section("1. Dataset Loader — 3 Trials")

    target_files = [
        ("Subject_1", "Walking",     "Trial_140.csv"),
        ("Subject_3", "Jogging",     None),           # first trial found
        ("Subject_7", "Stairs_down", None),
    ]

    sampled_trials = []
    for subj, act, fname in target_files:
        base = Path("data/raw/SDALLE") / subj / act
        if not base.exists():
            print(f"  [SKIP] {subj}/{act} not found")
            continue
        csvs = sorted(base.glob("*.csv"))
        if not csvs:
            print(f"  [SKIP] No CSVs in {base}")
            continue
        target = base / fname if fname else csvs[0]
        if not target.exists():
            target = csvs[0]

        # Load just this file
        trials = dataset_loader.load_all_trials(limit=None)
        match = [t for t in trials
                 if t.file_path.name == target.name
                 and t.activity_name == act.lower()]
        if not match:
            print(f"  [SKIP] Could not find {target} in loaded trials")
            continue
        t = match[0]
        sampled_trials.append(t)

    if not sampled_trials:
        print("  No trials found — aborting.")
        return False

    for t in sampled_trials:
        print(f"\n  Trial: S{t.subject_id} / {t.activity_name} / {t.file_path.name}")

        ok = True
        ok &= check(t.emg.shape[1] == 8,
                    f"EMG has 8 channels  (got {t.emg.shape[1]})")
        ok &= check(t.imu.shape[1] == 48,
                    f"IMU has 48 channels (got {t.imu.shape[1]})")

        # Verify approximate sampling rates from sample counts and known durations
        emg_dur = t.emg.shape[0] / EXPECTED_EMG_RATE
        imu_dur = t.imu.shape[0] / EXPECTED_IMU_RATE
        ok &= check(abs(emg_dur - imu_dur) < 0.5,
                    f"EMG and IMU durations align  "
                    f"(EMG: {emg_dur:.2f}s, IMU: {imu_dur:.2f}s)")
        ok &= check(not np.any(np.isnan(t.emg)),
                    "No NaN in EMG array")
        ok &= check(not np.any(np.isnan(t.imu)),
                    "No NaN in IMU array (after filtering empty rows)")

        print(f"    EMG: {t.emg.shape}  IMU: {t.imu.shape}  "
              f"EMG_dur={emg_dur:.2f}s  IMU_dur={imu_dur:.2f}s")
        all_ok &= ok

    # ── 2. Windowing tests ──────────────────────────────────────────────────
    section("2. Windower — Shapes & Boundary Safety")

    t = sampled_trials[0]
    print(f"\n  Trial: S{t.subject_id} / {t.activity_name} / {t.file_path.name}")

    # E1
    X_e1, y_e1, meta_e1 = windower.window_e1([t])
    ok = check(X_e1.ndim == 3,         f"E1 is 3-D: {X_e1.shape}")
    ok &= check(X_e1.shape[1] == windower.EMG_WIN, f"E1 window = {windower.EMG_WIN}: {X_e1.shape[1]}")
    ok &= check(X_e1.shape[2] == 8,   f"E1 channels = 8: {X_e1.shape[2]}")
    all_ok &= ok
    print(f"    E1 shape: {X_e1.shape}, windows={len(y_e1)}")

    # E2
    X_e2, y_e2, meta_e2 = windower.window_e2([t])
    ok = check(X_e2.ndim == 3,         f"E2 is 3-D: {X_e2.shape}")
    ok &= check(X_e2.shape[1] == windower.IMU_WIN, f"E2 window = {windower.IMU_WIN}: {X_e2.shape[1]}")
    ok &= check(X_e2.shape[2] == 48,  f"E2 channels = 48: {X_e2.shape[2]}")
    all_ok &= ok
    print(f"    E2 shape: {X_e2.shape}, windows={len(y_e2)}")

    # E3
    X_e3, y_e3, meta_e3 = windower.window_e3([t])
    ok = check(X_e3.ndim == 3,         f"E3 is 3-D: {X_e3.shape}")
    ok &= check(X_e3.shape[1] == windower.IMU_WIN, f"E3 window = {windower.IMU_WIN}: {X_e3.shape[1]}")
    ok &= check(X_e3.shape[2] == 56,  f"E3 channels = 56: {X_e3.shape[2]}")
    ok &= check(not np.any(np.isnan(X_e3)), "E3 no NaN after resampling")
    all_ok &= ok
    print(f"    E3 shape: {X_e3.shape}, windows={len(y_e3)}")

    # E4
    Xe_e4, Xi_e4, y_e4, meta_e4 = windower.window_e4([t])
    ok = check(Xe_e4.shape[1] == windower.EMG_WIN, f"E4 EMG window = {windower.EMG_WIN}: {Xe_e4.shape[1]}")
    ok &= check(Xe_e4.shape[2] == 8,  f"E4 EMG channels = 8")
    ok &= check(Xi_e4.shape[1] == windower.IMU_WIN, f"E4 IMU window = {windower.IMU_WIN}: {Xi_e4.shape[1]}")
    ok &= check(Xi_e4.shape[2] == 48, f"E4 IMU channels = 48")
    ok &= check(len(y_e4) == len(y_e1), f"E4 window count equals E1 ({len(y_e4)} vs {len(y_e1)})")
    all_ok &= ok
    print(f"    E4 EMG shape: {Xe_e4.shape}  IMU shape: {Xi_e4.shape}, windows={len(y_e4)}")

    # No-boundary-crossing test: check metadata
    if meta_e1:
        last = meta_e1[-1]
        ok = check(
            last["end_time"] <= (t.emg.shape[0] / EXPECTED_EMG_RATE) + 0.01,
            f"Last E1 window end time ({last['end_time']:.3f}s) ≤ trial duration ({t.emg.shape[0]/EXPECTED_EMG_RATE:.3f}s)"
        )
        all_ok &= ok

    # ── 3. Normalizer tests ─────────────────────────────────────────────────
    section("3. Normalizer — Leakage & Statistics")

    # Use E1 windows from first two trials as fake train/test split
    if len(sampled_trials) >= 2:
        X_tr, _, _ = windower.window_e1([sampled_trials[0]])
        X_te, _, _ = windower.window_e1([sampled_trials[1]])

        X_tr_n, X_te_n, params = normalizer.normalize_single_branch(X_tr, X_te)

        # Training set should be approximately zero-mean, unit-std
        flat_tr = X_tr_n.reshape(-1, X_tr_n.shape[2])
        tr_mean = flat_tr.mean(axis=0)
        tr_std  = flat_tr.std(axis=0)
        ok = check(np.allclose(tr_mean, 0.0, atol=1e-4),
                   f"Training set mean ≈ 0  (max_abs={np.abs(tr_mean).max():.2e})")
        ok &= check(np.allclose(tr_std,  1.0, atol=1e-4),
                    f"Training set std  ≈ 1  (max_dev={np.abs(tr_std - 1).max():.2e})")
        # Test set should NOT necessarily be zero-mean (different distribution)
        flat_te = X_te_n.reshape(-1, X_te_n.shape[2])
        te_mean = flat_te.mean(axis=0)
        ok &= check(not np.allclose(te_mean, 0.0, atol=1e-3),
                    f"Test set mean ≠ 0 (leakage would produce ≈0; got max={np.abs(te_mean).max():.4f})")
        ok &= check(not np.any(np.isnan(X_tr_n)), "No NaN in normalized train")
        ok &= check(not np.any(np.isnan(X_te_n)), "No NaN in normalized test")
        all_ok &= ok
        print(f"    Train shape after norm: {X_tr_n.shape}")
        print(f"    Test  shape after norm: {X_te_n.shape}")

    # ── 4. LOSO leakage assertion ───────────────────────────────────────────
    section("4. LOSO Subject Isolation")
    all_loaded = dataset_loader.load_all_trials()
    for test_sid in sorted(set(t.subject_id for t in all_loaded)):
        train_sids = {t.subject_id for t in all_loaded if t.subject_id != test_sid}
        ok = check(test_sid not in train_sids,
                   f"S{test_sid:02d} not in training fold when it is the test subject")
        all_ok &= ok

    # ── Summary ────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    if all_ok:
        print("  ALL TESTS PASSED — safe to run build_datasets.py")
    else:
        print("  SOME TESTS FAILED — review output above before proceeding")
    print(f"{'='*60}")
    return all_ok


if __name__ == "__main__":
    run_all()
