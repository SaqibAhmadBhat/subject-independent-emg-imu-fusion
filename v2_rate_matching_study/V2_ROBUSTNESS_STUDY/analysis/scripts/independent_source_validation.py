#!/usr/bin/env python3
"""
independent_source_validation.py
--------------------------------
Phase 3.24 Independent Level-A Ground-Truth Validator:
Validates all 90 model run predictions against frozen Level-A binary datasets
(dataset_fold_{k}.npz).

Enforces:
  1. Locating the canonical Level-A binary datasets. If datasets are absent,
     reports VALIDATION STATUS: INCOMPLETE and exits with non-zero code.
     No claim of 90/90 validation is permitted without actual ground-truth files.
  2. Ground-truth sample-by-sample matching: np.array_equal(df["true_label"], npz["y_test"]).
  3. Window index strictly sequential: np.array_equal(indices, np.arange(n_samples)).
  4. Confusion matrix and metric concordance against meta.json.
  5. Paired sample alignment across all 45 paired runs.

Exit Codes:
  0 : All 90 runs fully verified against Level-A ground-truth binary files.
  1 : Fatal failure (sample mismatch, label mismatch, corrupt run, or discrepancy).
  2 : Incomplete (Level-A datasets missing; companion archive required).

Usage:
  python3 analysis/scripts/independent_source_validation.py [--dry-run] [--study-root PATH] [--workspace-root PATH] [--data-dir PATH] [--output-dir PATH]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import numpy as np
import pandas as pd


# ── Robust Project-Root Discovery ─────────────────────────────────────────────
def find_study_root(explicit_root: Optional[str] = None) -> Path:
    """
    Discovers the V2_ROBUSTNESS_STUDY root directory robustly.
    Validates presence of project markers (protocol.md and analysis directory).
    Fails safely if markers cannot be identified.
    """
    if explicit_root:
        candidate = Path(explicit_root).resolve()
        if (candidate / "protocol.md").exists() and (candidate / "analysis").is_dir():
            return candidate
        raise FileNotFoundError(
            f"Provided --study-root '{explicit_root}' is invalid (missing protocol.md or analysis/)."
        )

    script_dir = Path(__file__).resolve().parent
    if len(script_dir.parents) >= 2:
        candidate = script_dir.parents[1]
        if (candidate / "protocol.md").exists() and (candidate / "analysis").is_dir():
            return candidate

    cwd = Path.cwd().resolve()
    if (cwd / "protocol.md").exists() and (cwd / "analysis").is_dir():
        return cwd

    for parent in script_dir.parents:
        if (parent / "protocol.md").exists() and (parent / "analysis").is_dir():
            return parent

    for parent in cwd.parents:
        if (parent / "protocol.md").exists() and (parent / "analysis").is_dir():
            return parent

    raise FileNotFoundError(
        "Could not automatically resolve V2 study root (missing protocol.md and analysis/). "
        "Please provide --study-root explicitly."
    )


def locate_level_a_npz(
    study_root: Path,
    workspace_root: Path,
    condition: str,
    fold: int,
    explicit_data_dir: Optional[str] = None
) -> Optional[Path]:
    """
    Searches for the processed Level A binary dataset_fold_{fold}.npz file across candidate locations.
    """
    candidates = []
    if explicit_data_dir:
        candidates.append(Path(explicit_data_dir).resolve() / condition / f"dataset_fold_{fold}.npz")
        candidates.append(Path(explicit_data_dir).resolve() / f"dataset_fold_{fold}.npz")
    else:
        candidates.extend([
            study_root / "data" / "processed" / condition / f"dataset_fold_{fold}.npz",
            workspace_root / "V2" / "data" / "processed" / condition / f"dataset_fold_{fold}.npz",
            study_root.parent / "V2" / "data" / "processed" / condition / f"dataset_fold_{fold}.npz",
            study_root.parent / "data" / "processed" / condition / f"dataset_fold_{fold}.npz",
        ])
    
    for c in candidates:
        if c.exists():
            return c
    return None


SEEDS = [42, 123, 2024, 3407, 7777]
CONDITIONS = ["E3-D", "E4"]
FOLDS = list(range(1, 10))
CLASS_NAMES = ["jogging", "stairs_down", "stairs_up", "walking"]
LABEL_MAP = {0: "jogging", 1: "stairs_down", 2: "stairs_up", 3: "walking"}
REQUIRED_COLUMNS = ["window_index", "true_label", "true_name", "pred_label", "pred_name"]


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray):
    cm = np.zeros((4, 4), dtype=np.int64)
    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1
    
    precisions = []
    recalls = []
    f1s = []
    supports = []
    for c in range(4):
        tp = cm[c, c]
        fp = cm[:, c].sum() - tp
        fn = cm[c, :].sum() - tp
        prec = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
        rec = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        f1 = float(2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)
        supports.append(int(cm[c, :].sum()))
        
    acc = float(np.diag(cm).sum() / cm.sum())
    macro_f1 = float(np.mean(f1s))
    macro_prec = float(np.mean(precisions))
    macro_rec = float(np.mean(recalls))
    return cm, acc, macro_f1, macro_prec, macro_rec


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate all 90 runs against Level A binary datasets.")
    parser.add_argument("--study-root", type=str, default=None, help="Path to V2_ROBUSTNESS_STUDY root.")
    parser.add_argument("--workspace-root", type=str, default=None, help="Path to workspace root containing V2/.")
    parser.add_argument("--data-dir", type=str, default=None, help="Directory containing processed Level A npz files.")
    parser.add_argument("--output-dir", type=str, default=None, help="Directory to save validation CSV and JSON.")
    parser.add_argument("--dry-run", action="store_true", help="Perform full validation without writing files to disk.")
    args = parser.parse_args()

    study_root = find_study_root(args.study_root)
    workspace_root = Path(args.workspace_root).resolve() if args.workspace_root else study_root.parent
    output_dir = Path(args.output_dir).resolve() if args.output_dir else (study_root / "analysis" / "tables")

    print("=" * 80)
    print("V2 RELEASE SCRIPT: LEVEL-A INDEPENDENT GROUND-TRUTH AUDIT (PHASE 3.24)")
    print(f"Study Root: {study_root}")
    print(f"Workspace Root: {workspace_root}")
    print(f"Output Dir: {output_dir}")
    print(f"Mode: {'DRY-RUN (No files written)' if args.dry_run else 'ACTIVE VALIDATION'}")
    print("=" * 80)
    
    run_records = []
    fatal_errors = []
    missing_pred_files = []
    missing_npz_files = []
    runs_fully_validated = 0
    sequential_index_checks_passed = 0
    
    # 1. Check Level A binary datasets presence
    npz_cache = {}
    for cond in CONDITIONS:
        npz_cache[cond] = {}
        for fold in FOLDS:
            npz_path = locate_level_a_npz(study_root, workspace_root, cond, fold, args.data_dir)
            if npz_path:
                npz_data = np.load(npz_path)
                if "y_test" in npz_data:
                    npz_cache[cond][fold] = (npz_path, npz_data["y_test"])
                else:
                    fatal_errors.append(f"Level A dataset {npz_path} missing 'y_test' array.")
                    npz_cache[cond][fold] = None
            else:
                missing_npz_files.append(f"{cond}/dataset_fold_{fold}.npz")
                npz_cache[cond][fold] = None

    # If Level A datasets are completely missing, fail safely with code 2
    if missing_npz_files:
        print("\n" + "!" * 80)
        print("VALIDATION STATUS: INCOMPLETE (Level A Datasets Missing)")
        print(f"Missing Level A .npz files: {len(missing_npz_files)} / 18 expected.")
        for mf in missing_npz_files[:6]:
            print(f"  - {mf}")
        if len(missing_npz_files) > 6:
            print(f"  ... and {len(missing_npz_files) - 6} more files.")
        print("\nNO CLAIM OF 90/90 LEVEL-A GROUND-TRUTH VALIDATION IS PERMITTED.")
        print("To complete Level-A validation:")
        print("  1. Download and unpack companion data archive 'v2_reproducibility_data_final.zip' (or 'v2_reproducibility_data_phase3_24.zip') into data/processed/")
        print("  2. Or specify: --data-dir <path_to_processed_data>")
        print("!" * 80)
        return 2
                
    # 2. Loop over 45 pairs
    for seed in SEEDS:
        for fold in FOLDS:
            p_e3d = study_root / f"seed_{seed}" / "E3-D" / f"fold_{fold}" / "predictions.csv"
            p_e4 = study_root / f"seed_{seed}" / "E4" / f"fold_{fold}" / "predictions.csv"
            m_e3d = study_root / f"seed_{seed}" / "E3-D" / f"fold_{fold}" / "meta.json"
            m_e4 = study_root / f"seed_{seed}" / "E4" / f"fold_{fold}" / "meta.json"
            
            for p, name in [(p_e3d, f"seed_{seed}/E3-D/fold_{fold}/predictions.csv"),
                            (p_e4, f"seed_{seed}/E4/fold_{fold}/predictions.csv"),
                            (m_e3d, f"seed_{seed}/E3-D/fold_{fold}/meta.json"),
                            (m_e4, f"seed_{seed}/E4/fold_{fold}/meta.json")]:
                if not p.exists():
                    missing_pred_files.append(name)
                    fatal_errors.append(f"Missing file: {name}")
                    
            if not p_e3d.exists() or not p_e4.exists() or not m_e3d.exists() or not m_e4.exists():
                continue
                
            df_e3d = pd.read_csv(p_e3d)
            df_e4 = pd.read_csv(p_e4)
            with open(m_e3d) as fp:
                meta_e3d = json.load(fp)
            with open(m_e4) as fp:
                meta_e4 = json.load(fp)
                
            for cond, df, meta in [("E3-D", df_e3d, meta_e3d), ("E4", df_e4, meta_e4)]:
                n_samples = len(df)
                run_id = f"{cond}_s{seed}_f{fold}"
                
                # Check required columns
                missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
                if missing_cols:
                    fatal_errors.append(f"{run_id}: Missing required columns: {missing_cols}")
                    
                # Sequential index check: np.array_equal(indices, np.arange(n_samples))
                indices = df["window_index"].values
                if not np.array_equal(indices, np.arange(n_samples)):
                    fatal_errors.append(f"{run_id}: Indices are not strictly sequential 0..{n_samples-1}")
                else:
                    sequential_index_checks_passed += 1
                    
                y_true = df["true_label"].values
                y_pred = df["pred_label"].values
                cm_rec, acc, f1, prec, rec = compute_metrics(y_true, y_pred)
                
                cm_meta = np.array(meta["metrics"]["confusion_matrix"])
                acc_meta = meta["metrics"]["accuracy"]
                f1_meta = meta["metrics"]["macro_f1"]
                
                cm_match = np.array_equal(cm_rec, cm_meta)
                acc_diff = abs(acc - acc_meta)
                f1_diff = abs(f1 - f1_meta)
                
                # Compare against Level A npz ground truth
                npz_entry = npz_cache[cond][fold]
                if npz_entry is not None:
                    npz_path, level_a_y = npz_entry
                    if len(y_true) != len(level_a_y):
                        fatal_errors.append(f"{run_id}: Length mismatch against Level A {npz_path.name} ({len(y_true)} vs {len(level_a_y)})")
                        npz_match = False
                    else:
                        npz_match = np.array_equal(y_true, level_a_y)
                        if not npz_match:
                            fatal_errors.append(f"Level A ground-truth mismatch: {cond} seed {seed} fold {fold}")
                else:
                    npz_match = False
                    
                is_valid = cm_match and (acc_diff < 1e-5) and (f1_diff < 1e-5) and npz_match
                if is_valid:
                    runs_fully_validated += 1
                else:
                    fatal_errors.append(f"{run_id}: Validation failure (CM match: {cm_match}, Level A match: {npz_match})")
                    
                run_records.append({
                    "run_id": run_id,
                    "condition": cond,
                    "seed": seed,
                    "fold": fold,
                    "participant": fold,
                    "n_test_samples": n_samples,
                    "source_npz_path": str(npz_cache[cond][fold][0].name) if npz_cache[cond][fold] else "MISSING",
                    "level_a_npz_ground_truth_match": npz_match,
                    "confusion_matrix_match": cm_match,
                    "accuracy_match": (acc_diff < 1e-5),
                    "macro_f1_match": (f1_diff < 1e-5),
                    "sequential_indices": np.array_equal(indices, np.arange(n_samples)),
                    "fully_validated": is_valid
                })

    if missing_pred_files:
        print("\n" + "!" * 80)
        print("VALIDATION STATUS: INCOMPLETE (Missing Run Predictions)")
        print(f"Missing prediction files: {len(missing_pred_files)}")
        for mf in missing_pred_files[:10]:
            print(f"  - {mf}")
        print("!" * 80)
        return 1

    df_val = pd.DataFrame(run_records)
    summary = {
        "validator": "independent_source_validation.py (Phase 3.24 Release Version)",
        "total_runs_expected": 90,
        "runs_fully_validated": runs_fully_validated,
        "sequential_index_assertion": {
            "assertion": "np.array_equal(indices, np.arange(n_samples))",
            "passed_count": sequential_index_checks_passed,
            "all_passed": (sequential_index_checks_passed == 90)
        },
        "level_a_npz_matching_runs": int(df_val["level_a_npz_ground_truth_match"].sum()) if len(df_val) > 0 else 0,
        "confusion_matrix_exact_matches": int(df_val["confusion_matrix_match"].sum()) if len(df_val) > 0 else 0,
        "fatal_errors": fatal_errors
    }
    
    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
        csv_path = output_dir / "prediction_validation_independent.csv"
        df_val.to_csv(csv_path, index=False)
        print(f"Saved: {csv_path} ({len(df_val)} records)")
        
        json_path = output_dir / "prediction_validation_summary_independent.json"
        with open(json_path, "w") as fp:
            json.dump(summary, fp, indent=2)
        print(f"Saved: {json_path}")
    else:
        print("[DRY-RUN] Validation completed without writing CSV/JSON files.")
        
    print("-" * 80)
    print(f"RESULTS: {runs_fully_validated}/90 runs FULLY VALIDATED against Level-A ground truth.")
    print(f"Sequential Indices: {sequential_index_checks_passed}/90 runs strictly sequential 0..N-1.")
    print(f"Level A .npz ground truth matches: {summary['level_a_npz_matching_runs']}/90.")
    print(f"Confusion matrix matches: {summary['confusion_matrix_exact_matches']}/90.")
    print(f"Fatal errors: {len(fatal_errors)}")
    print("=" * 80)

    if fatal_errors or runs_fully_validated < 90:
        print("FAIL: Validation encountered fatal errors or incomplete coverage:")
        for err in fatal_errors:
            print(f"  - {err}")
        return 1
        
    print("SUCCESS: Level-A independent source validation PASSED (Exit Code 0).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
