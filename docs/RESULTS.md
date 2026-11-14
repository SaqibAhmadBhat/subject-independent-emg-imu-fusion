# Primary Experimental Results & Benchmark Findings

This document presents the complete empirical results of the V2 multimodal robustness evaluation, comparing rate-matched downsampling (E3-D) against native-rate processing (E4) across 9 Leave-One-Subject-Out (LOSO) cross-validation folds and 5 initialization seeds (90 total neural network trainings).

---

## 1. Executive Summary of Benchmark Findings

| Evaluation Metric | Rate-Matched (E3-D) | Native-Rate (E4) | Delta ($\Delta$) | Statistical Test | p-Value | 95% Confidence Interval |
|---|---|---|---|---|---|---|
| **Mean Accuracy** | **72.90%** ($\pm 9.24\%$) | **69.07%** ($\pm 10.80\%$) | **+3.83 pp** | Paired Difference | — | $[1.07, 6.65]\text{ pp}$ |
| **Wilcoxon Signed-Rank** | — | — | $W = 5.0$ | Two-Sided Test | **$p = 0.039$** | — |
| **Permutation Test** | — | — | 16 / 512 | Exact Sign-Flip | **$p = 0.031$** | — |
| **Rank-Biserial ($r$)** | — | — | **+0.778** | Large Effect Size | — | — |
| **Participants Favoring** | **8 of 9 subjects** | 1 of 9 subjects | 88.9% favor E3-D | Binomial Sign | $p = 0.039$ | — |

---

## 2. Participant-Level Paired Comparisons

Performance varies widely across subjects due to biological differences in muscle volume, subcutaneous tissue impedance, and movement dynamics. Rate-matching improves performance for 8 of the 9 test subjects:

<figure class="scientific-figure">
  <img src="../assets/figures/fig1_participant_paired_comparison.svg" alt="Participant Paired Comparison" />
  <figcaption><strong>Figure 1:</strong> Subject-by-subject accuracy across Leave-One-Subject-Out cross-validation folds. Points denote 5-seed means; error bars indicate &plusmn;1 standard deviation across random seeds. Rate-matched processing (E3-D, teal) outperforms native-rate (E4, amber) in 8 of 9 participants.</figcaption>
</figure>

### Detailed Participant Breakdown Table

| Subject ID | Age (yr) | E3-D Mean (%) | E3-D Std (%) | E4 Mean (%) | E4 Std (%) | Delta ($\Delta$ pp) | Direction | Super-Nyquist sEMG Energy (%) |
|---|---|---|---|---|---|---|---|---|
| **P1** | 21 | 67.24% | 3.12% | **70.39%** | 3.28% | **-3.15 pp** | Favors E4 | **13.51%** (Lowest in cohort) |
| **P2** | 24 | **78.43%** | 1.84% | 77.76% | 2.10% | **+0.67 pp** | Favors E3-D | 17.84% |
| **P3** | 27 | **76.12%** | 2.45% | 70.55% | 2.89% | **+5.57 pp** | Favors E3-D | 20.12% |
| **P4** | 22 | **69.88%** | 2.61% | 68.76% | 3.01% | **+1.12 pp** | Favors E3-D | 16.95% |
| **P5** | 39 | **84.52%** | 1.95% | 82.05% | 2.15% | **+2.47 pp** | Favors E3-D | 18.42% |
| **P6** | 25 | **68.35%** | 2.80% | 61.98% | 3.14% | **+6.37 pp** | Favors E3-D | 21.05% |
| **P7** | 23 | **56.12%** | 3.40% | 46.18% | 3.82% | **+9.94 pp** | Favors E3-D | 22.38% (Highest gain) |
| **P8** | 28 | **74.19%** | 2.18% | 65.84% | 2.76% | **+8.35 pp** | Favors E3-D | 19.87% |
| **P9** | 12 | **81.25%** | 1.62% | 78.11% | 2.04% | **+3.14 pp** | Favors E3-D | 20.89% |
| **Mean** | 24.6 | **72.90%** | 2.44% | **69.07%** | 2.80% | **+3.83 pp** | **8 / 9 Favor E3-D** | **19.00% Average** |

---

## 3. Seed Stability & Multi-Seed Distribution

To evaluate whether results were sensitive to random weight initialization or data shuffling, all 9 LOSO folds were trained under 5 independently drawn random seeds: `[42, 123, 456, 789, 101112]`.

<figure class="scientific-figure">
  <img src="../assets/figures/fig2_accuracy_distribution_boxplot.svg" alt="Accuracy Distribution Boxplot" />
  <figcaption><strong>Figure 2:</strong> Boxplot distribution of test accuracy across all 90 runs, stratified by random initialization seed and experimental condition. E3-D maintains consistently higher median and quartile boundaries across every tested seed.</figcaption>
</figure>

### Multi-Seed Breakdown Table

| Random Seed | E3-D Mean Accuracy (%) | E4 Mean Accuracy (%) | Seed Delta ($\Delta$ pp) | Condition Advantage |
|---|---|---|---|---|
| **Seed 42** | 73.12% | 69.45% | +3.67 pp | E3-D |
| **Seed 123** | 72.84% | 68.92% | +3.92 pp | E3-D |
| **Seed 456** | 73.05% | 69.18% | +3.87 pp | E3-D |
| **Seed 789** | 72.68% | 68.80% | +3.88 pp | E3-D |
| **Seed 101112**| 72.81% | 69.00% | +3.81 pp | E3-D |
| **Overall** | **72.90%** | **69.07%** | **+3.83 pp** | **Stable across all seeds** |

---

## 4. Activity Recall & Confusion Dynamics

The dataset comprises 4 distinct locomotor tasks: **Level Walking**, **Ascending Stairs**, **Descending Stairs**, and **Stepping Over Obstacles**.

<figure class="scientific-figure">
  <img src="../assets/figures/fig6_confusion_matrix_comparison.svg" alt="Confusion Matrix Comparison" />
  <figcaption><strong>Figure 3:</strong> Normalized confusion matrices for Rate-Matched E3-D (left) versus Native-Rate E4 (right). Rate-matching achieves substantially higher recall in stair transitions and obstacle negotiation where dynamic kinematic coordination is pronounced.</figcaption>
</figure>
