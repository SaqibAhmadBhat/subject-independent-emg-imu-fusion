# Experimental Design & Protocol Specification

## 1. Participant Cohort & Dataset Demographics

The study utilizes recordings from the public **SDALLE** benchmark (Abdellatif Hamed Ibrahim et al., 2025; DOI: `10.5281/zenodo.14841611`).

- **Cohort Size:** $N = 9$ healthy male human participants.
- **Demographics:** Age range 12–39 years (Participant P9 is 12 years old; participants P1–P8 are adults aged 21–39 years).
- **Physical Characteristics:** Height range 152–182 cm, body mass 47–88 kg.
- **Sensors:** 8 Delsys Trigno Discover wireless surface sensors positioned bilaterally on the lower extremities.
  - Channels per sensor: 1 sEMG channel (1259.2593 Hz) + 6 IMU channels (triaxial accelerometer $\pm 16g$ + triaxial gyroscope $\pm 2000^\circ/\text{s}$, 148.1481 Hz).
  - Target Muscle Groups (from raw CSV headers): Rectus femoris, Vastus medialis, Vastus lateralis, Semitendinosus (bilateral: left and right).
  - Total channels: 8 sEMG + 48 IMU = 56 channels.

---

## 2. Activity Tasks & Segmentation

### Four Locomotor Activities
1. **Walking:** Level-ground walking at self-selected speed (largest class: 2,234 test windows per seed, $36.01\%$).
2. **Jogging:** Level-ground jogging (1,528 test windows per seed, $24.63\%$).
3. **Stairs Up:** Ascending stairs (1,237 test windows per seed, $19.94\%$).
4. **Stairs Down:** Descending stairs (1,204 test windows per seed, $19.41\%$).
*Total test windows evaluated per seed:* $\mathbf{6{,}203 \text{ windows}}$.

### Windowing Parameters
- **Nominal Window Duration:** $1.0\text{ s}$ ($148$ samples at $148.15\text{ Hz}$; $1259$ samples at $1259.26\text{ Hz}$).
- **Stride:** $0.5\text{ s}$ ($50\%$ overlap between consecutive windows).
- **Trial Isolation:** Sliding windows are strictly constrained within individual continuous trials. No window crosses a trial or session boundary.

### Per-Participant Test Window Counts
| Fold | Test Participant | Test Windows | Majority Share (Walking %) |
|---|---|---|---|
| Fold 1 | P1 | 647 | 34.6% |
| Fold 2 | P2 | 568 | 39.4% |
| Fold 3 | P3 | 729 | 36.5% |
| Fold 4 | P4 | 696 | 35.8% |
| Fold 5 | P5 | 746 | 33.9% |
| Fold 6 | P6 | 722 | 34.5% |
| Fold 7 | P7 | 654 | 38.8% |
| Fold 8 | P8 | 690 | 37.1% |
| Fold 9 | P9 | 751 | 34.0% |
| **Total** | — | **6,203** | **36.0%** |

---

## 3. Cross-Validation & Seed Configuration

- **Cross-Validation Scheme:** 9-fold Leave-One-Participant-Out (LOSO / LOPO).
  - Each fold holds out all trials of one participant as the unseen test partition ($N_{\text{test}} \approx 568\text{--}751$ windows).
  - Training partition contains remaining 8 participants ($N_{\text{train}} \approx 5{,}452\text{--}5{,}635$ windows).
- **Random Seeds:** 5 fixed seeds: `42`, `123`, `2024`, `3407`, `7777`.
- **Total Experimental Runs:** 2 conditions $\times$ 9 folds $\times$ 5 seeds = $\mathbf{90 \text{ full training runs}}$.

---

## 4. Model Training Configuration

| Hyperparameter / Setting | Value |
|---|---|
| **Architecture** | `DualBranchCNN` (src/models.py) |
| **Total Parameters** | 330,052 (identical in E3-D and E4) |
| **Optimizer** | Adam ($\beta_1 = 0.9, \beta_2 = 0.999, \epsilon = 10^{-8}$) |
| **Initial Learning Rate** | $1 \times 10^{-3}$ |
| **Weight Decay** | $1 \times 10^{-4}$ |
| **Learning Rate Schedule** | Cosine Annealing to minimum $1 \times 10^{-5}$ across 50 epochs |
| **Epochs** | 50 epochs per fold |
| **Batch Size** | 64 |
| **Loss Function** | CrossEntropyLoss |
| **Data Normalization** | Channel-wise z-score computed on training fold only |

---

## 5. Statistical Methodology & Endpoints

### Primary Endpoint
- **Participant-Level Classification Accuracy:** The percentage of correctly predicted test windows for each participant, averaged across the 5 random seeds ($N = 9$ paired observations).
- **Primary Hypothesis Test:** Two-sided Wilcoxon signed-rank test on paired differences ($\text{RM} - \text{NR}$).
  - Observed test statistic: $W = 5$ ($W^+ = 40, W^- = 5$).
  - Exact two-sided $p$-value: $p = 2 \times 10 / 512 = \mathbf{0.0390625} \approx 0.039$.
  - Effect size: Matched-pairs rank-biserial correlation $r = (40 - 5) / 45 = \mathbf{+0.778}$.
- **Interval Estimation:** 95% Percentile Bootstrap Confidence Interval with $B = 10{,}000$ resamples of participant differences: $\mathbf{[1.27, 6.35] \text{ pp}}$.

### Sensitivity Analyses
1. **Exact Sign-Flip Permutation Test:** All $2^9 = 512$ sign permutations evaluated on participant mean differences. Exactly 16 permutations have mean difference $\ge 3.830$ pp; exact two-sided $p = 16 / 512 = \mathbf{0.03125} \approx 0.031$.
2. **Two-Stage Hierarchical Bootstrap:** 10,000 resamples resampling participants (outer), then seeds within participants (inner). 95% CI: $\mathbf{[1.07, 6.65] \text{ pp}}$.
3. **Leave-One-Seed-Out Sensitivity:** Recomputed using 4 seeds omitting one seed in turn: $p$-values range from **$0.012$ to $0.055$** (rate matching leads in 8/9 participants in every combination).
4. **Leave-One-Participant-Out Sensitivity:** Omitting P1 yields $p = 0.008$; omitting any other participant yields $p = 0.055\text{--}0.078$.
5. **Variance Components:** Seed-to-seed SD within a participant is $\mathbf{4.23 \text{ pp}}$; estimated between-participant SD is $\mathbf{3.66 \text{ pp}}$ (ICC = $\mathbf{0.43}$).

---

## 6. Methodological Limitations

1. **Cross-Validation Training Overlap:** In 9-fold LOSO, each training set shares 7 of its 8 participants with any other training set. As established by Bengio & Grandvalet (2004), no unbiased estimator of cross-validation variance exists. Inferential $p$-values reflect test participant variability and should be interpreted as approximate.
2. **Sample Size:** The sample size ($N = 9$) is determined by the public benchmark. A paired $t$-test at $\alpha = 0.05$ has $80\%$ statistical power only for standardized effect sizes $d_z \ge 1.07$.
3. **Generalization:** Findings apply to healthy young male individuals performing four ambulatory lower-limb activities and should not be extrapolated to clinical populations or upper-limb tasks without empirical testing.
