# Evaluation Audit — RP4

**Generated:** 2026-09-07 15:08:31
**Script:** `run_evaluation.py`

---

## Protocol Summary

| Property | Value |
|---|---|
| Evaluation protocol | Leave-One-Subject-Out (LOSO) |
| N subjects (folds) | 9 per experiment |
| Experiments | E1, E2, E3, E4 |
| Total folds evaluated | 36 |
| Statistical unit | Subject-fold (n=9) |
| Statistical test | Wilcoxon signed-rank (paired, two-sided) |
| Multiple comparisons | Holm-Bonferroni (6 pairs) |
| Effect size | Cohen's d (paired differences) |
| Normalization | Pre-computed in dataset.npz (training-fold stats only) |
| Checkpoint selection | None — single model.pt per fold loaded |
| results/ directory | Frozen — not written to |

---

## Completion Status

| Experiment | Folds Evaluated | Status |
|---|---|---|
| E1 | 9/9 | ✅ COMPLETE |
| E2 | 9/9 | ✅ COMPLETE |
| E3 | 9/9 | ✅ COMPLETE |
| E4 | 9/9 | ✅ COMPLETE |

**TOTAL: 36/36 folds evaluated** ✅

---

## Per-Experiment Results

### Fold-Level Metrics

| Exp | Fold | Accuracy | Macro P | Macro R | Macro F1 | N Windows |
|---|---|---|---|---|---|---|
| E1 | 1 | 0.4003 | 0.6518 | 0.4516 | 0.3787 | 647 |
| E1 | 2 | 0.6074 | 0.5780 | 0.4807 | 0.4782 | 568 |
| E1 | 3 | 0.2497 | 0.2257 | 0.2567 | 0.1919 | 729 |
| E1 | 4 | 0.3951 | 0.4609 | 0.3394 | 0.2890 | 696 |
| E1 | 5 | 0.5630 | 0.6129 | 0.5166 | 0.4876 | 746 |
| E1 | 6 | 0.4515 | 0.3846 | 0.4042 | 0.3259 | 722 |
| E1 | 7 | 0.3807 | 0.2992 | 0.3153 | 0.2804 | 654 |
| E1 | 8 | 0.6884 | 0.6829 | 0.6424 | 0.6215 | 690 |
| E1 | 9 | 0.5020 | 0.3742 | 0.3979 | 0.3532 | 751 |
| E2 | 1 | 0.7651 | 0.8121 | 0.7460 | 0.7503 | 647 |
| E2 | 2 | 0.7986 | 0.8348 | 0.7561 | 0.7771 | 571 |
| E2 | 3 | 0.5978 | 0.7869 | 0.5759 | 0.5836 | 731 |
| E2 | 4 | 0.6624 | 0.8695 | 0.6019 | 0.6398 | 696 |
| E2 | 5 | 0.6412 | 0.7458 | 0.5965 | 0.5808 | 747 |
| E2 | 6 | 0.6528 | 0.7750 | 0.6272 | 0.6396 | 723 |
| E2 | 7 | 0.6208 | 0.8235 | 0.6666 | 0.6483 | 654 |
| E2 | 8 | 0.6652 | 0.7405 | 0.7003 | 0.6700 | 690 |
| E2 | 9 | 0.7101 | 0.7138 | 0.7151 | 0.6917 | 752 |
| E3 | 1 | 0.7975 | 0.8267 | 0.7814 | 0.7872 | 647 |
| E3 | 2 | 0.7986 | 0.8344 | 0.7690 | 0.7749 | 571 |
| E3 | 3 | 0.4241 | 0.5469 | 0.4695 | 0.4034 | 731 |
| E3 | 4 | 0.6968 | 0.8481 | 0.6476 | 0.6860 | 696 |
| E3 | 5 | 0.6359 | 0.7530 | 0.5791 | 0.5808 | 747 |
| E3 | 6 | 0.6902 | 0.7659 | 0.6661 | 0.6784 | 723 |
| E3 | 7 | 0.4052 | 0.8051 | 0.4906 | 0.4479 | 654 |
| E3 | 8 | 0.5406 | 0.6653 | 0.5912 | 0.5377 | 690 |
| E3 | 9 | 0.7207 | 0.7394 | 0.7259 | 0.7000 | 752 |
| E4 | 1 | 0.7821 | 0.8237 | 0.7724 | 0.7605 | 647 |
| E4 | 2 | 0.8151 | 0.8544 | 0.7689 | 0.7934 | 568 |
| E4 | 3 | 0.5405 | 0.6904 | 0.6119 | 0.5249 | 729 |
| E4 | 4 | 0.6868 | 0.8395 | 0.6309 | 0.6611 | 696 |
| E4 | 5 | 0.7091 | 0.7650 | 0.6649 | 0.6742 | 746 |
| E4 | 6 | 0.7064 | 0.7991 | 0.6821 | 0.6984 | 722 |
| E4 | 7 | 0.7676 | 0.7753 | 0.7713 | 0.7485 | 654 |
| E4 | 8 | 0.7072 | 0.7438 | 0.7466 | 0.7119 | 690 |
| E4 | 9 | 0.7337 | 0.8188 | 0.6804 | 0.7115 | 751 |

---

### Experiment-Level Summaries

| Experiment | Acc Mean | Acc Std | Acc Med | F1 Mean | F1 Std | F1 Med |
|---|---|---|---|---|---|---|
| E1 | 0.4709 | 0.1263 | 0.4515 | 0.3785 | 0.1233 | 0.3532 |
| E2 | 0.6793 | 0.0626 | 0.6624 | 0.6646 | 0.0631 | 0.6483 |
| E3 | 0.6344 | 0.1389 | 0.6902 | 0.6218 | 0.1295 | 0.6784 |
| E4 | 0.7165 | 0.0738 | 0.7091 | 0.6983 | 0.0729 | 0.7115 |

---

## Statistical Comparisons (Accuracy)

Test: Wilcoxon signed-rank (paired, two-sided, n=9)
Correction: Holm-Bonferroni

| Pair | Mean A | Mean B | Mean Diff | W stat | p (raw) | p (Holm) | Sig | Cohen's d |
|---|---|---|---|---|---|---|---|---|
| E1_vs_E2 | 0.4709 | 0.6793 | -0.2084 | 1.0 | 0.0078 | 0.0391 | ✅ | -1.706 |
| E1_vs_E3 | 0.4709 | 0.6344 | -0.1635 | 3.0 | 0.0195 | 0.0781 | — | -1.014 |
| E1_vs_E4 | 0.4709 | 0.7165 | -0.2456 | 0.0 | 0.0039 | 0.0234 | ✅ | -2.137 |
| E2_vs_E3 | 0.6793 | 0.6344 | +0.0449 | 14.0 | 0.6406 | 0.6406 | — | 0.456 |
| E2_vs_E4 | 0.6793 | 0.7165 | -0.0372 | 7.0 | 0.0742 | 0.1484 | — | -0.688 |
| E3_vs_E4 | 0.6344 | 0.7165 | -0.0821 | 4.0 | 0.0273 | 0.0820 | — | -0.675 |

## Statistical Comparisons (Macro F1)

| Pair | Mean A | Mean B | Mean Diff | W stat | p (raw) | p (Holm) | Sig | Cohen's d |
|---|---|---|---|---|---|---|---|---|
| E1_vs_E2 | 0.3785 | 0.6646 | -0.2861 | 0.0 | 0.0039 | 0.0234 | ✅ | -2.273 |
| E1_vs_E3 | 0.3785 | 0.6218 | -0.2433 | 1.0 | 0.0078 | 0.0312 | ✅ | -1.492 |
| E1_vs_E4 | 0.3785 | 0.6983 | -0.3198 | 0.0 | 0.0039 | 0.0234 | ✅ | -2.813 |
| E2_vs_E3 | 0.6646 | 0.6218 | +0.0428 | 18.0 | 0.6523 | 0.6523 | — | 0.431 |
| E2_vs_E4 | 0.6646 | 0.6983 | -0.0337 | 6.0 | 0.0547 | 0.1641 | — | -0.702 |
| E3_vs_E4 | 0.6218 | 0.6983 | -0.0765 | 9.0 | 0.1289 | 0.2578 | — | -0.706 |

---

## Output Files

| File | Description |
|---|---|
| `evaluation/final_metrics.csv` | 36 rows, per-fold all metrics |
| `evaluation/evaluation_manifest.csv` | 36 rows, fold evaluated=True |
| `evaluation/tables/per_experiment_summary.csv` | 4 rows, mean/std/median/min/max |
| `evaluation/tables/statistical_comparisons.csv` | 12 rows, 6 pairs × 2 metrics |
| `evaluation/metrics/*_fold_*_metrics.json` | 36 files, per-fold JSON |
| `evaluation/metrics/*_summary.json` | 4 files, per-experiment JSON |
| `evaluation/metrics/statistical_tests.json` | Full statistical results |
| `evaluation/predictions/*.csv` | 36 files, window-level predictions |
| `evaluation/figures/cm_*.png` | 4 individual confusion matrices |
| `evaluation/figures/cm_all_experiments.png` | Combined 2x2 CM figure |
| `evaluation/figures/accuracy_comparison.png` | Box+strip plot, accuracy |
| `evaluation/figures/f1_comparison.png` | Box+strip plot, macro F1 |
| `evaluation/figures/summary_bar.png` | Mean±std grouped bar chart |

---

> **Protocol compliance confirmed:**
> - results/ directory: NOT modified
> - No retraining performed
> - No normalization re-fitted
> - No checkpoint selection using test data
> - Statistical unit: subject-fold (n=9), NOT individual windows
> - All 36 folds evaluated exactly once
