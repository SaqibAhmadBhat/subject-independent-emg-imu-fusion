#!/usr/bin/env python3
"""
validate_predictions_from_source.py
-----------------------------------
Phase 3.24 Strengthened Independent Prediction-Level Validator:
Directly reconstructs confusion matrices and classification metrics from the 90
run-level predictions.csv files across 5 seeds (42, 123, 2024, 3407, 7777) and 9 folds.

Enforces:
  1. Discovery of all 90 model run outputs. If any run is missing, stops with a clear
     error and non-zero exit code: no claim of 90/90 validation is permitted.
  2. Required columns: ['window_index', 'true_label', 'true_name', 'pred_label', 'pred_name'].
  3. No NaN / null values.
  4. Sequential window indexing: np.array_equal(indices, np.arange(n_samples)).
  5. Valid label bounds [0, 3] and consistent string-to-int class name mappings.
  6. Reconstructed confusion matrix and metrics exact match to meta.json.
  7. Exact sample-by-sample ground truth and ordering alignment across all 45 paired runs.

Exit Codes:
  0 : All 90 runs verified, sample alignment 100% concordant, zero discrepancies.
  1 : Fatal failure (missing run files, sample misalignment, index error, or metric discrepancy).

Usage:
  python3 analysis/scripts/validate_predictions_from_source.py [--dry-run] [--study-root PATH] [--output-dir PATH]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

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


SEEDS = [42, 123, 2024, 3407, 7777]
CONDITIONS = ["E3-D", "E4"]
FOLDS = list(range(1, 10))
N_CLASSES = 4
CLASS_NAMES = ["jogging", "stairs_down", "stairs_up", "walking"]
LABEL_MAP = {0: "jogging", 1: "stairs_down", 2: "stairs_up", 3: "walking"}
REQUIRED_COLUMNS = ["window_index", "true_label", "true_name", "pred_label", "pred_name"]


def compute_cm_and_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
    cm = np.zeros((N_CLASSES, N_CLASSES), dtype=np.int64)
    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1
        
    precisions = []
    recalls = []
    f1s = []
    supports = []
    
    for c in range(N_CLASSES):
        tp = cm[c, c]
        fp = cm[:, c].sum() - tp
        fn = cm[c, :].sum() - tp
        
        prec = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
        rec = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        f1 = float(2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
        sup = int(cm[c, :].sum())
        
        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)
        supports.append(sup)
        
    accuracy = float(np.diag(cm).sum() / cm.sum())
    macro_f1 = float(np.mean(f1s))
    macro_prec = float(np.mean(precisions))
    macro_rec = float(np.mean(recalls))
    
    return {
        "confusion_matrix": cm,
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "macro_precision": macro_prec,
        "macro_recall": macro_rec,
        "per_class": {
            CLASS_NAMES[c]: {
                "precision": precisions[c],
                "recall": recalls[c],
                "f1": f1s[c],
                "support": supports[c]
            }
            for c in range(N_CLASSES)
        }
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate all 90 run predictions against metadata.")
    parser.add_argument("--study-root", type=str, default=None, help="Path to V2_ROBUSTNESS_STUDY root.")
    parser.add_argument("--output-dir", type=str, default=None, help="Directory to save validation CSV and JSON.")
    parser.add_argument("--dry-run", action="store_true", help="Perform full validation without writing files to disk.")
    args = parser.parse_args()

    study_root = find_study_root(args.study_root)
    output_dir = Path(args.output_dir).resolve() if args.output_dir else (study_root / "analysis" / "tables")

    print("=" * 80)
    print("V2 RELEASE SCRIPT: INDEPENDENT PREDICTION-LEVEL SOURCE VALIDATOR (PHASE 3.24)")
    print(f"Study Root: {study_root}")
    print(f"Output Dir: {output_dir}")
    print(f"Mode: {'DRY-RUN (No files written)' if args.dry_run else 'ACTIVE VALIDATION'}")
    print("=" * 80)
    
    validation_records = []
    fatal_errors = []
    missing_files = []
    total_evaluated_runs = 0
    sequential_index_checks_passed = 0
    paired_alignment_checks_passed = 0
    reconstructed_cm_matches = 0
    
    # Track paired alignment
    for seed in SEEDS:
        for fold in FOLDS:
            p_e3d = study_root / f"seed_{seed}" / "E3-D" / f"fold_{fold}" / "predictions.csv"
            p_e4 = study_root / f"seed_{seed}" / "E4" / f"fold_{fold}" / "predictions.csv"
            m_e3d = study_root / f"seed_{seed}" / "E3-D" / f"fold_{fold}" / "meta.json"
            m_e4 = study_root / f"seed_{seed}" / "E4" / f"fold_{fold}" / "meta.json"
            
            # Check file existence
            for p, name in [(p_e3d, f"seed_{seed}/E3-D/fold_{fold}/predictions.csv"),
                            (p_e4, f"seed_{seed}/E4/fold_{fold}/predictions.csv"),
                            (m_e3d, f"seed_{seed}/E3-D/fold_{fold}/meta.json"),
                            (m_e4, f"seed_{seed}/E4/fold_{fold}/meta.json")]:
                if not p.exists():
                    missing_files.append(name)
                    fatal_errors.append(f"Missing file: {name} (expected at {p})")
                    
            if not p_e3d.exists() or not p_e4.exists() or not m_e3d.exists() or not m_e4.exists():
                continue
                
            df_e3d = pd.read_csv(p_e3d)
            df_e4 = pd.read_csv(p_e4)
            
            with open(m_e3d) as fp:
                meta_e3d = json.load(fp)
            with open(m_e4) as fp:
                meta_e4 = json.load(fp)
                
            # Alignment checks between paired runs
            paired_len_match = (len(df_e3d) == len(df_e4))
            paired_idx_match = np.array_equal(df_e3d["window_index"].values, df_e4["window_index"].values)
            paired_true_match = np.array_equal(df_e3d["true_label"].values, df_e4["true_label"].values)
            paired_name_match = (list(df_e3d["true_name"]) == list(df_e4["true_name"]))
            
            if not paired_len_match:
                fatal_errors.append(f"Length mismatch between E3-D and E4 for seed {seed} fold {fold}: {len(df_e3d)} vs {len(df_e4)}")
            if not paired_idx_match:
                fatal_errors.append(f"Window index sequence mismatch between E3-D and E4 for seed {seed} fold {fold}")
            if not paired_true_match:
                fatal_errors.append(f"True label sequence mismatch between E3-D and E4 for seed {seed} fold {fold}")
            if not paired_name_match:
                fatal_errors.append(f"True name sequence mismatch between E3-D and E4 for seed {seed} fold {fold}")
                
            if paired_len_match and paired_idx_match and paired_true_match and paired_name_match:
                paired_alignment_checks_passed += 1

            for cond, df, meta in [("E3-D", df_e3d, meta_e3d), ("E4", df_e4, meta_e4)]:
                total_evaluated_runs += 1
                n_samples = len(df)
                run_id = f"{cond}_seed{seed}_fold{fold}"
                
                # Required columns check
                missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
                if missing_cols:
                    fatal_errors.append(f"{run_id}: Missing required columns: {missing_cols}")
                    
                # Missing/NaN values check
                if df[REQUIRED_COLUMNS].isna().any().any():
                    fatal_errors.append(f"{run_id}: Missing (NaN/null) values detected in required columns")
                    
                # Numeric label check
                if not pd.api.types.is_numeric_dtype(df["true_label"]) or not pd.api.types.is_numeric_dtype(df["pred_label"]):
                    fatal_errors.append(f"{run_id}: Non-numeric types in label columns")
                    
                # Label bounds check {0, 1, 2, 3}
                valid_true = set(df["true_label"].unique()).issubset({0, 1, 2, 3})
                valid_pred = set(df["pred_label"].unique()).issubset({0, 1, 2, 3})
                if not valid_true or not valid_pred:
                    fatal_errors.append(f"{run_id}: Invalid label values found outside {{0, 1, 2, 3}}")
                    
                # Explicitly check unique and sequential indices: np.array_equal(indices, np.arange(n_samples))
                indices = df["window_index"].values
                if not np.array_equal(indices, np.arange(n_samples)):
                    fatal_errors.append(f"{run_id}: Window indices are not strictly sequential integers 0..{n_samples-1}")
                else:
                    sequential_index_checks_passed += 1
                    
                # Check string to int mapping consistency
                map_consistent = True
                for idx, row in df.iterrows():
                    if LABEL_MAP.get(int(row["true_label"])) != row["true_name"]:
                        map_consistent = False
                        break
                    if LABEL_MAP.get(int(row["pred_label"])) != row["pred_name"]:
                        map_consistent = False
                        break
                if not map_consistent:
                    fatal_errors.append(f"{run_id}: String-to-int class name mapping is inconsistent")
                    
                # Reconstruct confusion matrix and metrics from predictions.csv
                y_true = df["true_label"].values
                y_pred = df["pred_label"].values
                metrics = compute_cm_and_metrics(y_true, y_pred)
                
                cm_rec = metrics["confusion_matrix"]
                acc_rec = metrics["accuracy"]
                macro_f1_rec = metrics["macro_f1"]
                
                # Compare against meta.json
                cm_meta = np.array(meta["metrics"]["confusion_matrix"])
                acc_meta = meta["metrics"]["accuracy"]
                macro_f1_meta = meta["metrics"]["macro_f1"]
                
                cm_match = np.array_equal(cm_rec, cm_meta)
                acc_match = (abs(acc_rec - acc_meta) < 1e-5)
                f1_match = (abs(macro_f1_rec - macro_f1_meta) < 1e-5)
                
                if cm_match and acc_match and f1_match:
                    reconstructed_cm_matches += 1
                else:
                    fatal_errors.append(f"{run_id}: CM or metric discrepancy between predictions.csv and meta.json")
                    
                validation_records.append({
                    "run_id": run_id,
                    "condition": cond,
                    "seed": seed,
                    "fold": fold,
                    "participant": fold,
                    "n_test_samples": n_samples,
                    "reconstructed_accuracy": acc_rec,
                    "meta_accuracy": acc_meta,
                    "accuracy_delta": abs(acc_rec - acc_meta),
                    "reconstructed_macro_f1": macro_f1_rec,
                    "meta_macro_f1": macro_f1_meta,
                    "macro_f1_delta": abs(macro_f1_rec - macro_f1_meta),
                    "cm_exact_match": cm_match,
                    "sequential_indices": np.array_equal(indices, np.arange(n_samples)),
                    "columns_valid": (len(missing_cols) == 0),
                    "labels_bounded": (valid_true and valid_pred),
                    "mapping_consistent": map_consistent
                })

    # If any run was missing, stop with clear failure
    if missing_files or total_evaluated_runs < 90:
        print("\n" + "!" * 80)
        print("VALIDATION STATUS: INCOMPLETE / FAILED")
        print(f"Evaluated Runs: {total_evaluated_runs} / 90 expected.")
        print(f"Missing Files Count: {len(missing_files)}")
        print("Missing Run Artifacts (first 10):")
        for mf in missing_files[:10]:
            print(f"  - {mf}")
        if len(missing_files) > 10:
            print(f"  ... and {len(missing_files) - 10} more missing files.")
        print("\nNO CLAIM OF 90/90 VALIDATION IS PERMITTED.")
        print("!" * 80)
        return 1

    df_val = pd.DataFrame(validation_records)
    summary_data = {
        "validator": "validate_predictions_from_source.py (Phase 3.24 Release Version)",
        "total_runs_expected": 90,
        "total_runs_evaluated": total_evaluated_runs,
        "sequential_index_assertion": {
            "assertion": "np.array_equal(indices, np.arange(n_samples))",
            "passed_count": sequential_index_checks_passed,
            "all_passed": (sequential_index_checks_passed == 90)
        },
        "paired_alignment_integrity": {
            "total_pairs_tested": 45,
            "pairs_fully_aligned": paired_alignment_checks_passed,
            "all_pairs_concordant": (paired_alignment_checks_passed == 45)
        },
        "confusion_matrix_reconstruction": {
            "classes_verified": CLASS_NAMES,
            "total_matrices_verified": 90,
            "matrices_exactly_matching_meta": reconstructed_cm_matches,
            "max_accuracy_discrepancy": float(df_val["accuracy_delta"].max()) if len(df_val) > 0 else 0.0,
            "max_macro_f1_discrepancy": float(df_val["macro_f1_delta"].max()) if len(df_val) > 0 else 0.0
        },
        "fatal_errors": fatal_errors
    }
    
    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
        csv_path = output_dir / "prediction_validation_by_run.csv"
        df_val.to_csv(csv_path, index=False)
        print(f"Saved: {csv_path} ({len(df_val)} records)")
        
        json_path = output_dir / "prediction_validation_summary.json"
        with open(json_path, "w") as fp:
            json.dump(summary_data, fp, indent=2)
        print(f"Saved: {json_path}")
    else:
        print("[DRY-RUN] Validation completed without writing CSV/JSON files.")
    
    print("-" * 80)
    print(f"Coverage: {total_evaluated_runs}/90 runs verified.")
    print(f"Sequential Indices: {sequential_index_checks_passed}/90 runs strictly sequential 0..N-1.")
    print(f"Paired Alignment: {paired_alignment_checks_passed}/45 pairs have 100% identical sample order and ground truth.")
    print(f"Reconstructed CM Concordance: {reconstructed_cm_matches}/90 match meta.json exactly.")
    print(f"Fatal Discrepancies: {len(fatal_errors)}")
    print("=" * 80)
    
    if fatal_errors:
        print("FAIL: Validation encountered fatal discrepancies:")
        for err in fatal_errors:
            print(f"  - {err}")
        return 1
        
    print("SUCCESS: Prediction-level independent validation PASSED (Exit Code 0).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
