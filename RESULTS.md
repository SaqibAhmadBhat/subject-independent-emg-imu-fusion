# Results

This document summarises the computational results of all four experiments. For the full evaluation protocol, see [`EXPERIMENTS.md`](EXPERIMENTS.md).

## Experiment-Level Summary

Results are reported as mean ± standard deviation across 9 LOSO folds.

| Experiment | Accuracy | Macro Precision | Macro Recall | Macro F1 |
|:---:|:---:|:---:|:---:|:---:|
| E1 — EMG only | 47.1 ± 12.6% | 47.4 ± 15.5% | 42.3 ± 11.0% | 37.9 ± 12.3% |
| E2 — IMU only | 67.9 ± 6.3% | 78.9 ± 4.8% | 66.5 ± 6.4% | 66.5 ± 6.3% |
| E3 — Rate-matched | 63.4 ± 13.9% | 75.4 ± 9.1% | 63.6 ± 10.6% | 62.2 ± 13.0% |
| E4 — Multirate | 71.7 ± 7.4% | 79.0 ± 4.9% | 70.3 ± 5.9% | 69.8 ± 7.3% |

### Additional Statistics

| Experiment | Acc Median | Acc Min | Acc Max | F1 Median | F1 Min | F1 Max |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| E1 | 45.2% | 25.0% | 68.8% | 35.3% | 19.2% | 62.2% |
| E2 | 66.2% | 59.8% | 79.9% | 64.8% | 58.1% | 77.7% |
| E3 | 69.0% | 40.5% | 79.9% | 67.8% | 40.3% | 78.7% |
| E4 | 70.9% | 54.0% | 81.5% | 71.2% | 52.5% | 79.3% |

---

## Fold-Level Results

### Accuracy

| Fold | E1 | E2 | E3 | E4 |
|:---:|:---:|:---:|:---:|:---:|
| 1 | 0.4003 | 0.7651 | 0.7975 | 0.7821 |
| 2 | 0.6074 | 0.7986 | 0.7986 | 0.8151 |
| 3 | 0.2497 | 0.5978 | 0.4241 | 0.5405 |
| 4 | 0.3951 | 0.6624 | 0.6968 | 0.6868 |
| 5 | 0.5630 | 0.6412 | 0.6359 | 0.7091 |
| 6 | 0.4515 | 0.6528 | 0.6902 | 0.7064 |
| 7 | 0.3807 | 0.6208 | 0.4052 | 0.7676 |
| 8 | 0.6884 | 0.6652 | 0.5406 | 0.7072 |
| 9 | 0.5020 | 0.7101 | 0.7207 | 0.7337 |

### Macro F1

| Fold | E1 | E2 | E3 | E4 |
|:---:|:---:|:---:|:---:|:---:|
| 1 | 0.3787 | 0.7503 | 0.7872 | 0.7605 |
| 2 | 0.4782 | 0.7771 | 0.7749 | 0.7934 |
| 3 | 0.1919 | 0.5836 | 0.4034 | 0.5249 |
| 4 | 0.2890 | 0.6398 | 0.6860 | 0.6611 |
| 5 | 0.4876 | 0.5808 | 0.5808 | 0.6742 |
| 6 | 0.3259 | 0.6396 | 0.6784 | 0.6984 |
| 7 | 0.2804 | 0.6483 | 0.4479 | 0.7485 |
| 8 | 0.6215 | 0.6700 | 0.5377 | 0.7119 |
| 9 | 0.3532 | 0.6917 | 0.7000 | 0.7115 |

---

## Statistical Comparisons

**Test:** Wilcoxon signed-rank (paired, two-sided, n = 9 folds per pair)
**Correction:** Holm–Bonferroni (6 pairwise comparisons)
**Effect size:** Cohen's d (paired differences)

### Accuracy Comparisons

| Pair | Mean Δ | p (raw) | p (Holm) | Significant | Cohen's d |
|---|:---:|:---:|:---:|:---:|:---:|
| E1 vs E2 | −0.208 | 0.0078 | 0.039 | ✓ | −1.71 |
| E1 vs E3 | −0.163 | 0.0195 | 0.078 | — | −1.01 |
| E1 vs E4 | −0.246 | 0.0039 | 0.023 | ✓ | −2.14 |
| E2 vs E3 | +0.045 | 0.6406 | 0.641 | — | +0.46 |
| E2 vs E4 | −0.037 | 0.0742 | 0.148 | — | −0.69 |
| E3 vs E4 | −0.082 | 0.0273 | 0.082 | — | −0.67 |

### Macro F1 Comparisons

| Pair | Mean Δ | p (raw) | p (Holm) | Significant | Cohen's d |
|---|:---:|:---:|:---:|:---:|:---:|
| E1 vs E2 | −0.286 | 0.0039 | 0.023 | ✓ | −2.27 |
| E1 vs E3 | −0.243 | 0.0078 | 0.031 | ✓ | −1.49 |
| E1 vs E4 | −0.320 | 0.0039 | 0.023 | ✓ | −2.81 |
| E2 vs E3 | +0.043 | 0.6523 | 0.652 | — | +0.43 |
| E2 vs E4 | −0.034 | 0.0547 | 0.164 | — | −0.70 |
| E3 vs E4 | −0.076 | 0.1289 | 0.258 | — | −0.71 |

---

## Interpretation

1. **E1 (EMG only) is significantly worse** than E2 and E4 for accuracy, and significantly worse than all other experiments for F1.

2. **E4 (multirate) achieved the highest observed mean** across all metrics, but its advantage over E2 (IMU only) and E3 (rate-matched) **is not statistically significant** after multiple-comparison correction.

3. **E2 and E3 are not significantly different** from each other, suggesting that adding rate-matched EMG to IMU does not reliably improve performance in this setting.

4. **High variance across folds** (especially for E1 and E3) indicates substantial subject-dependent performance variation, which is expected in subject-independent evaluation.

5. The relatively large Cohen's d values for E2 vs E4 (−0.69) and E3 vs E4 (−0.67/−0.71) suggest potentially meaningful effect sizes that may reach significance with more subjects.

---

## Limitations

- The sample size (n = 9 folds) limits statistical power; meaningful differences may exist that this study is underpowered to detect.
- The dataset contains only 4 lower-limb activities from 9 young adult participants.
- All experiments used the same CNN architecture family; alternative architectures may yield different relative rankings.
- No hyperparameter tuning was performed (all parameters were predetermined), which ensures a fair comparison but may not optimise absolute performance.

---

## Figures

Key evaluation figures are available in [`evaluation/figures/`](evaluation/figures/):

- `cm_all_experiments.png` — Aggregate normalised confusion matrices (2×2 grid)
- `accuracy_comparison.png` — Accuracy across LOSO folds (box + strip plot)
- `f1_comparison.png` — Macro F1 across LOSO folds (box + strip plot)
- `summary_bar.png` — Mean ± std bar chart for accuracy and F1

---

## Data Files

| File | Description |
|---|---|
| [`evaluation/final_metrics.csv`](evaluation/final_metrics.csv) | All per-fold metrics (36 rows) |
| [`evaluation/tables/per_experiment_summary.csv`](evaluation/tables/per_experiment_summary.csv) | Experiment-level statistics |
| [`evaluation/tables/statistical_comparisons.csv`](evaluation/tables/statistical_comparisons.csv) | Wilcoxon + Holm-Bonferroni results |
| [`evaluation/metrics/statistical_tests.json`](evaluation/metrics/statistical_tests.json) | Complete statistical output (JSON) |
