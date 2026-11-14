"""Tests for prediction file completeness, window count validity, and label alignment across runs."""
import csv
import json
from pathlib import Path
import pytest

STUDY_ROOT = Path(__file__).resolve().parent.parent / "v2_rate_matching_study" / "V2_ROBUSTNESS_STUDY"
SEEDS = [42, 123, 2024, 3407, 7777]
CONDITIONS = ["E3-D", "E4"]
EXPECTED_WINDOWS_PER_FOLD = {
    1: 647,
    2: 568,
    3: 729,
    4: 696,
    5: 746,
    6: 722,
    7: 654,
    8: 690,
    9: 751,
}
TOTAL_WINDOWS_PER_SEED = 6203


def test_all_90_run_directories_exist():
    """Verify that all 90 run output directories exist and contain expected files."""
    for s in SEEDS:
        for c in CONDITIONS:
            for k in range(1, 10):
                run_dir = STUDY_ROOT / f"seed_{s}" / c / f"fold_{k}"
                assert run_dir.exists(), f"Missing directory: {run_dir}"
                
                pred_file = run_dir / "predictions.csv"
                meta_file = run_dir / "meta.json"
                hist_file = run_dir / "history.json"
                
                assert pred_file.exists(), f"Missing {pred_file}"
                assert meta_file.exists(), f"Missing {meta_file}"
                assert hist_file.exists(), f"Missing {hist_file}"


def test_prediction_row_counts_per_fold():
    """Verify exact test window counts per participant fold across conditions and seeds."""
    for s in SEEDS:
        seed_total = 0
        for k in range(1, 10):
            expected_n = EXPECTED_WINDOWS_PER_FOLD[k]
            for c in CONDITIONS:
                pred_path = STUDY_ROOT / f"seed_{s}" / c / f"fold_{k}" / "predictions.csv"
                with open(pred_path, newline="") as fp:
                    reader = list(csv.DictReader(fp))
                    assert len(reader) == expected_n, (
                        f"Seed {s}, {c}, Fold {k}: expected {expected_n} rows, got {len(reader)}"
                    )
            seed_total += expected_n
        assert seed_total == TOTAL_WINDOWS_PER_SEED


def test_label_consistency_across_conditions_and_seeds():
    """Verify that true class labels match identically across conditions and seeds in each fold."""
    for k in range(1, 10):
        # Reference labels from Seed 42, Condition E3-D
        ref_path = STUDY_ROOT / "seed_42" / "E3-D" / f"fold_{k}" / "predictions.csv"
        with open(ref_path, newline="") as fp:
            ref_labels = [r["true_label"] for r in csv.DictReader(fp)]
            
        for s in SEEDS:
            for c in CONDITIONS:
                test_path = STUDY_ROOT / f"seed_{s}" / c / f"fold_{k}" / "predictions.csv"
                with open(test_path, newline="") as fp:
                    test_labels = [r["true_label"] for r in csv.DictReader(fp)]
                assert test_labels == ref_labels, (
                    f"Label mismatch in Fold {k} between Seed 42 E3-D and Seed {s} {c}"
                )
