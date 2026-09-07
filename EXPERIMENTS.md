# Experiments

This document defines the four experiments (E1–E4) evaluated in this project. All design decisions were predetermined before seeing any results.

## Common Configuration

All experiments share:

| Parameter | Value |
|---|---|
| Architecture | 1D CNN (2 conv blocks, AdaptiveAvgPool, classifier head) |
| Conv filters | [64, 128] |
| Kernel sizes | 7 (first conv), 5 (subsequent) |
| Activation | GELU |
| Dropout | 0.3 |
| Classifier head | Linear(latent, 64) → GELU → Dropout(0.3) → Linear(64, 4) |
| Window duration | 1.0 s |
| Stride | 0.5 s (50% overlap) |
| Trial isolation | No window crosses a trial boundary |
| Normalisation | Per-fold z-score, fitted on training data only |
| Evaluation | 9-fold LOSO (one subject held out per fold) |
| Classes | jogging (0), stairs_down (1), stairs_up (2), walking (3) |

---

## E1 — EMG Only

**Research purpose:** Establish a baseline using only neuromuscular activation signals.

| Property | Value |
|---|---|
| Input modality | EMG |
| Channels | 8 (one per sensor) |
| Sampling rate | ~1259 Hz (native) |
| Window shape | (1259, 8) → permuted to (8, 1259) for Conv1d |
| Model | `SingleBranchCNN(in_channels=8)` |
| Parameters | 156,228 |
| Fusion | None (single modality) |

**Preprocessing:** EMG columns extracted from SDALLE CSV (column indices: 0, 7, 14, 21, 28, 35, 42, 49). Sliding windows applied at native EMG rate. Z-score normalised per fold.

---

## E2 — IMU Only

**Research purpose:** Establish a baseline using only inertial (accelerometer + gyroscope) signals.

| Property | Value |
|---|---|
| Input modality | IMU (accelerometer + gyroscope) |
| Channels | 48 (6 per sensor × 8 sensors) |
| Sampling rate | ~148 Hz (native) |
| Window shape | (148, 48) → permuted to (48, 148) for Conv1d |
| Model | `SingleBranchCNN(in_channels=48)` |
| Parameters | 174,148 |
| Fusion | None (single modality) |

**Preprocessing:** IMU columns extracted from SDALLE CSV (all non-EMG columns). Sliding windows applied at native IMU rate. Z-score normalised per fold.

---

## E3 — Rate-Matched EMG + IMU Fusion

**Research purpose:** Evaluate concatenation-based sensor fusion where EMG is resampled to match the IMU rate before fusion.

| Property | Value |
|---|---|
| Input modality | EMG (resampled) + IMU |
| Channels | 56 (8 EMG resampled + 48 IMU) |
| Sampling rate | ~148 Hz (EMG resampled to IMU rate) |
| Window shape | (148, 56) → permuted to (56, 148) for Conv1d |
| Model | `SingleBranchCNN(in_channels=56)` |
| Parameters | 177,732 |
| Fusion | Early fusion (channel concatenation after resampling) |

**Preprocessing:** For each trial, the full EMG signal is resampled to the IMU rate using cubic interpolation (`scipy.interpolate.interp1d`). The resampled EMG and native IMU are concatenated along the channel dimension (56 channels). Sliding windows applied at IMU rate. Z-score normalised per fold.

**Key detail:** Resampling is performed on the entire trial before windowing, not per-window. This avoids artefacts at window boundaries.

---

## E4 — Native-Rate Multirate EMG + IMU Fusion

**Research purpose:** Evaluate whether preserving native sampling rates through independent encoder branches improves recognition compared with rate-matched fusion.

| Property | Value |
|---|---|
| Input modality | EMG (native rate) + IMU (native rate) |
| EMG channels | 8 |
| IMU channels | 48 |
| EMG sampling rate | ~1259 Hz (preserved) |
| IMU sampling rate | ~148 Hz (preserved) |
| EMG window shape | (1259, 8) → (8, 1259) |
| IMU window shape | (148, 48) → (48, 148) |
| Model | `DualBranchCNN()` |
| Parameters | 330,052 |
| Fusion | Late fusion (feature concatenation after independent encoding) |

**Preprocessing:** EMG and IMU windows are extracted independently at their respective native rates, with paired indexing to ensure temporal alignment. Each modality is z-score normalised independently per fold. The model uses two independent `_Encoder` branches (each producing a 128-dimensional feature vector), whose outputs are concatenated (256-d) before the shared classifier head.

**Key detail:** No resampling is performed. The EMG branch processes 1259-sample windows while the IMU branch simultaneously processes 148-sample windows from the same physical time interval.

---

## Model Architecture Details

### Single-Branch CNN (E1, E2, E3)

```
Input (batch, C, T)
  → ConvBlock1: Conv1d(C, 64, k=7) → BN → GELU → Conv1d(64, 64, k=5) → BN → GELU
  → MaxPool1d(2)
  → ConvBlock2: Conv1d(64, 128, k=5) → BN → GELU → Conv1d(128, 128, k=5) → BN → GELU
  → AdaptiveAvgPool1d(1) → squeeze → (batch, 128)
  → Linear(128, 64) → GELU → Dropout(0.3) → Linear(64, 4)
```

### Dual-Branch CNN (E4)

```
EMG Input (batch, 8, 1259)  → EMG Encoder → (batch, 128)
IMU Input (batch, 48, 148)  → IMU Encoder → (batch, 128)
  → concatenate → (batch, 256)
  → Linear(256, 64) → GELU → Dropout(0.3) → Linear(64, 4)
```

Each encoder uses the same architecture as the single-branch encoder above.

---

## Source Code References

| Component | File |
|---|---|
| Model definitions | [`src/models.py`](src/models.py) |
| Dataset preprocessing | [`src/build_datasets.py`](src/build_datasets.py) |
| Windowing | [`src/windower.py`](src/windower.py) |
| Normalisation | [`src/normalizer.py`](src/normalizer.py) |
| Training loop | [`src/train.py`](src/train.py) |
| Evaluation | [`run_evaluation.py`](run_evaluation.py) |
