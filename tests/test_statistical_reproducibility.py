"""Tests verifying exact reproduction of manuscript statistical findings from prediction files."""
import csv
import itertools
from pathlib import Path
import numpy as np
from scipy import stats
import pytest

STUDY_ROOT = Path(__file__).resolve().parent.parent / "v2_rate_matching_study" / "V2_ROBUSTNESS_STUDY"
SEEDS = [42, 123, 2024, 3407, 7777]


@pytest.fixture(scope="module")
def participant_accuracies():
    """Extract participant-level 5-seed mean accuracies for E3-D and E4."""
    acc_data = {"E3-D": np.zeros((5, 9)), "E4": np.zeros((5, 9))}
    for s_idx, s in enumerate(SEEDS):
        for cond in ["E3-D", "E4"]:
            for k in range(1, 10):
                pred_path = STUDY_ROOT / f"seed_{s}" / cond / f"fold_{k}" / "predictions.csv"
                with open(pred_path, newline="") as fp:
                    rows = list(csv.DictReader(fp))
                    correct = sum(1 for r in rows if r["correct"] == "1")
                    acc_data[cond][s_idx, k - 1] = (correct / len(rows)) * 100
    
    e3d_means = acc_data["E3-D"].mean(axis=0)
    e4_means = acc_data["E4"].mean(axis=0)
    diffs = e3d_means - e4_means
    return {
        "E3-D": e3d_means,
        "E4": e4_means,
        "diffs": diffs,
        "raw_matrix_diff": acc_data["E3-D"] - acc_data["E4"]
    }


def test_primary_endpoint_accuracies(participant_accuracies):
    """Verify mean accuracy: E3-D 72.90%, E4 69.07%, difference +3.83 pp."""
    e3d = participant_accuracies["E3-D"]
    e4 = participant_accuracies["E4"]
    diffs = participant_accuracies["diffs"]
    
    assert np.isclose(e3d.mean(), 72.9009, atol=1e-3)
    assert np.isclose(e4.mean(), 69.0706, atol=1e-3)
    assert np.isclose(diffs.mean(), 3.8303, atol=1e-3)
    
    # 8 of 9 participants positive
    assert (diffs > 0).sum() == 8
    # Only P1 negative
    assert diffs[0] < 0 and np.isclose(diffs[0], -3.1530, atol=1e-3)


def test_exact_wilcoxon_signed_rank(participant_accuracies):
    """Verify exact two-sided Wilcoxon signed-rank test: W = 5, p = 0.0390625, r = +0.778."""
    diffs = participant_accuracies["diffs"]
    ranks = stats.rankdata(np.abs(diffs))
    
    w_pos = ranks[diffs > 0].sum()
    w_neg = ranks[diffs < 0].sum()
    w = min(w_pos, w_neg)
    
    assert w == 5.0, f"Expected W = 5.0, got {w}"
    assert w_pos == 40.0
    assert w_neg == 5.0
    
    # Exact p-value: 10 out of 512 permutations
    exact_p = 2 * 10 / 512
    assert np.isclose(exact_p, 0.0390625)
    
    # Matched-pairs rank-biserial correlation
    r = (w_pos - w_neg) / (w_pos + w_neg)
    assert np.isclose(r, 0.777777, atol=1e-3)


def test_exact_sign_flip_permutation(participant_accuracies):
    """Verify exact sign-flip permutation test: p = 0.03125."""
    diffs = participant_accuracies["diffs"]
    obs_mean = diffs.mean()
    
    permutations = [
        np.mean(diffs * np.array(signs))
        for signs in itertools.product([1, -1], repeat=len(diffs))
    ]
    p_perm = np.mean(np.abs(permutations) >= abs(obs_mean) - 1e-12)
    
    # Exactly 16 permutations >= observed mean
    assert np.isclose(p_perm, 0.03125), f"Expected permutation p = 0.03125, got {p_perm}"


def test_variance_components(participant_accuracies):
    """Verify seed-level SD (4.23 pp) vs between-participant SD (3.66 pp), ICC = 0.43."""
    D = participant_accuracies["raw_matrix_diff"] # (5 seeds x 9 participants)
    d = D.mean(axis=0)
    
    ms_between = 5 * d.var(ddof=1)
    ms_within = float(np.mean(D.var(axis=0, ddof=1)))
    
    var_between = max((ms_between - ms_within) / 5.0, 0.0)
    sd_between = np.sqrt(var_between)
    sd_within = np.sqrt(ms_within)
    icc = var_between / (var_between + ms_within)
    
    assert np.isclose(sd_within, 4.2321, atol=1e-2), f"Expected within SD 4.23, got {sd_within}"
    assert np.isclose(sd_between, 3.6569, atol=1e-2), f"Expected between SD 3.66, got {sd_between}"
    assert np.isclose(icc, 0.4275, atol=1e-2), f"Expected ICC 0.43, got {icc}"
