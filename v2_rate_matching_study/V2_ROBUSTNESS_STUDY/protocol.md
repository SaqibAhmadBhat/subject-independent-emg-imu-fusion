# V2 Robustness Study — Frozen Experimental Protocol

> **FROZEN**: Written before any robustness-study experiment was run.
> Must NOT be modified after Phase 0. All claims must be traceable to this protocol.

---

## 1. Research Hypothesis

**H1**: Under participant-independent LOSO evaluation, the rate-matched dual-branch model
(E3-D) provides comparable or better recognition performance than the native-rate dual-branch
model (E4), while requiring lower computational cost.

**Primary comparison**: E3-D vs E4.

---

## 2. Dataset

| Property | Value |
|---|---|
| Dataset name | SDALLE |
| Dataset directory | `data/raw/SDALLE/` |
| Loader | `src/dataset_loader.py` |
| Data start line in CSV | Line 8 (0-indexed row 7) |
| Total columns per CSV | 56 (8 sensors x 7 columns each) |
| EMG column indices | Every 7th column: 0, 7, 14, 21, 28, 35, 42, 49 |
| IMU column indices | All other columns (6 per sensor x 8 = 48) |

---

## 3. Subjects

| Property | Value |
|---|---|
| Number of subjects | 9 |
| Subject IDs | 1-9 (inferred from directory `Subject_N`) |
| LOSO folds | 9 (one per subject) |
| Fold k test subject | Subject k |
| Fold k train subjects | All subjects except k |

---

## 4. Activities

| Label | Activity |
|---|---|
| 0 | jogging |
| 1 | stairs_down |
| 2 | stairs_up |
| 3 | walking |

---

## 5. Sampling Rates

| Signal | Rate (Hz) | Source |
|---|---|---|
| EMG | 1259.2593 | `EXPECTED_EMG_RATE` in `dataset_loader.py` |
| IMU | 148.1481 | `EXPECTED_IMU_RATE` in `dataset_loader.py` |
| Ratio | approx 8.5x | Derived |

---

## 6. Window Parameters

| Parameter | Value | Source |
|---|---|---|
| Window duration | 1.0 s | `WINDOW_SEC = 1.0` in `windower.py` |
| Stride / overlap | 0.5 s (50% overlap) | `STRIDE_SEC = 0.5` in `windower.py` |
| EMG samples/window (E4) | 1259 | `EMG_WIN = int(1.0 * 1259.2593)` |
| IMU samples/window | 148 | `IMU_WIN = int(1.0 * 148.1481)` |
| EMG stride samples | 629 | `EMG_STRIDE = int(0.5 * 1259.2593)` |
| IMU stride samples | 74 | `IMU_STRIDE = int(0.5 * 148.1481)` |

---

## 7. E3-D Preprocessing (Rate-matched dual-branch)

1. Construct time axes `t_emg` and `t_imu` using respective nominal sampling rates.
2. Clip to shorter duration: `max_time = min(t_emg[-1], t_imu[-1])`.
3. Fit cubic spline (scipy `interp1d`, `kind='cubic'`) to entire trial EMG; evaluate at IMU time points -> `emg_resampled_global` shape `(N_imu_valid, 8)`.
4. Pair with `imu_valid` (same time axis, shape `(N_imu_valid, 48)`).
5. `n_pairs = min((n_emg-EMG_WIN)//EMG_STRIDE+1, (n_imu-IMU_WIN)//IMU_STRIDE+1)`.
6. Slide with `stride=IMU_STRIDE(74)`, `window=IMU_WIN(148)`.
7. EMG tensor per window: `(148, 8)` -> permute -> `(8, 148)`.
8. IMU tensor per window: `(148, 48)` -> permute -> `(48, 148)`.
9. Total input scalars/window: `8x148 + 48x148 = 1184 + 7104 = 8288`.

Source: `V2/src/windower_v2.py::window_e3d()`

---

## 8. E4 Preprocessing (Native-rate dual-branch)

1. Slide EMG and IMU independently, paired to same physical time.
2. Window i: `emg_start=i*629`, `imu_start=i*74`.
3. EMG tensor per window: `(1259, 8)` -> permute -> `(8, 1259)`.
4. IMU tensor per window: `(148, 48)` -> permute -> `(48, 148)`.
5. Total input scalars/window: `8x1259 + 48x148 = 10072 + 7104 = 17176`.
6. Window count per trial: identical to E3-D (same `n_pairs` formula).

Source: `src/windower.py::window_e4()`

---

## 9. Theoretical Input-Sample Reduction (E3-D vs E4)

```
(17176 - 8288) / 17176 = 8888 / 17176 = approx 51.7%
```

> **IMPORTANT CAVEAT**: Fewer input scalars does not automatically mean fewer FLOPs.
> `AdaptiveAvgPool1d(1)` collapses all time to 1 regardless of input length.
> FLOP difference must be verified against measured runtime, not assumed.

---

## 10. Normalization Procedure

| Property | Value |
|---|---|
| Method | Per-channel z-score |
| Fit scope | **Training fold ONLY** (no test leakage) |
| Constant channels | std replaced with 1.0 |
| Dual-branch | Two independent scalers (EMG and IMU) |
| Implementation | `src/normalizer.py::normalize_dual_branch()` |

---

## 11. Model Architecture

Both E3-D and E4 use `DualBranchCNN` — the identical class from `src/models.py`.

```
EMG branch (_Encoder, in_channels=8):
  _ConvBlock(8->64,k=7,k=5) -> MaxPool1d(2,2) -> _ConvBlock(64->128,k=5,k=5)
  -> AdaptiveAvgPool1d(1) -> (batch, 128)

IMU branch (_Encoder, in_channels=48):
  _ConvBlock(48->64,k=7,k=5) -> MaxPool1d(2,2) -> _ConvBlock(64->128,k=5,k=5)
  -> AdaptiveAvgPool1d(1) -> (batch, 128)

Fusion: cat -> (batch, 256)
Head:   Linear(256,64) -> GELU -> Dropout(0.3) -> Linear(64,4)
```

The **ONLY** difference between E3-D and E4 is the EMG branch input length (148 vs 1259).

---

## 12. Parameter Count

| Model | Trainable parameters |
|---|---|
| DualBranchCNN (E3-D) | **330,052** |
| DualBranchCNN (E4) | **330,052** |

Verified programmatically. Asserted at runtime in `train_v2.py` line 95.

---

## 13. Optimizer

| Hyperparameter | Value |
|---|---|
| Algorithm | Adam |
| Learning rate | 0.001 |
| Weight decay | 0.0001 |
| Scheduler | CosineAnnealingLR (T_max=epochs) |
| Loss function | CrossEntropyLoss (no class weighting) |
| Dropout | 0.3 |

---

## 14. Training Budget

| Parameter | Value |
|---|---|
| Epochs | 50 |
| Batch size | 64 |
| Shuffle | True (train), False (test) |

---

## 15. LOSO Procedure

```python
for k in range(1, 10):
    train_trials = [t for t in all_trials if t.subject_id != k]
    test_trials  = [t for t in all_trials if t.subject_id == k]
    assert k not in {t.subject_id for t in train_trials}  # leakage check
```

Source: `V2/src/build_datasets_v2.py` and `train_v2.py`.

---

## 16. Random Seed Policy

Five seeds: **42, 123, 2024, 3407, 7777**.

| Seed | Rationale |
|---|---|
| 42 | Original V2 seed — reproducibility baseline |
| 123 | Conventional alternative |
| 2024 | Year-based, widely used in recent literature |
| 3407 | Popular ML benchmark seed |
| 7777 | Additional variation |

Applied via: `random.seed(s); np.random.seed(s); torch.manual_seed(s)`.
`cudnn.deterministic=True; cudnn.benchmark=False`.

**PAIRED CONSTRAINT**: For every (seed, fold) pair, E3-D and E4 use the **identical seed**.

---

## 17. Evaluation Metrics

| Metric | Definition | Primary unit |
|---|---|---|
| Accuracy | Correct / total windows | Per fold (participant) |
| Macro-F1 | Unweighted mean F1 across 4 classes | Per fold (participant) |
| Per-class metrics | Precision, recall, F1 | Per class per fold |
| Confusion matrix | 4x4 counts | Per fold and aggregate |

**PRIMARY STATISTICAL UNIT**: PARTICIPANT (fold), not window.

---

## 18. Statistical Analysis Plan (pre-specified)

1. Paired difference per participant: `d_k = acc(E3-D,k) - acc(E4,k)`.
2. Wilcoxon signed-rank test (two-tailed) on paired differences. Non-parametric.
3. Effect size: matched-pairs rank-biserial correlation (r).
4. 95% CI: bootstrapped (10,000 resamples) on mean paired difference.
5. No model selection using test set.

---

## 19. Pre-Registered Confound Checks (Phase 12)

Within every (seed, fold) pair, verify E3-D and E4 have:
1. Identical parameter count (330,052)
2. Identical architecture (DualBranchCNN)
3. Same training window count (same n_pairs formula)
4. Same test window count
5. Same labels
6. Same subjects and LOSO folds
7. Same optimizer, epochs, batch size, loss
8. Same normalization (fit on train only)
9. Same random seed
10. No test information in training
11. No test-based model selection
12. No augmentation
13. No class weighting

---

## 20. Output Structure

```
V2_ROBUSTNESS_STUDY/
  protocol.md
  seed_{S}/
    E3-D/
      fold_{k}/  meta.json, history.json, predictions.csv
      eval_summary.json
    E4/ (same structure)
  analysis/
    participant_matrix_accuracy.csv
    participant_matrix_f1.csv
    paired_stats.json
    per_class_comparison.json
    prediction_agreement.json
    learning_curves.json
    computational_cost.json
  final_report.md
```

---

*Protocol frozen: 2026-10-08. Experiments must not alter this file.*
