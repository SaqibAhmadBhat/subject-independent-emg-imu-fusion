# Subject-Independent Multirate EMG–IMU Fusion for Lower Limb Activity Recognition

A reproducible evaluation of native-rate multirate sensor fusion versus individual modalities and rate-matched fusion for subject-independent lower-limb activity recognition, using the SDALLE dataset.

## Research Question

> Can native-rate multirate fusion of EMG and IMU signals improve subject-independent lower-limb activity recognition compared with individual modalities and rate-matched fusion?

## Study Overview

Surface electromyography (EMG) and inertial measurement unit (IMU) signals provide complementary information about human movement. EMG captures neuromuscular activation at high temporal resolution (~1259 Hz), while IMU sensors capture kinematic patterns at a lower rate (~148 Hz). Most prior fusion approaches resample both modalities to a common rate, potentially discarding information. This project investigates whether preserving the native sampling rates through a dual-branch architecture improves subject-independent activity recognition.

## Experiments

| Experiment | Input Modality | Channels | Sampling Rate | Fusion Strategy |
|:---:|---|:---:|:---:|---|
| **E1** | EMG only | 8 | 1259 Hz | — |
| **E2** | IMU only | 48 | 148 Hz | — |
| **E3** | EMG + IMU (rate-matched) | 56 | 148 Hz | Resample EMG → IMU rate, concatenate |
| **E4** | EMG + IMU (multirate) | 8 + 48 | 1259 Hz + 148 Hz | Dual-branch CNN, late fusion |

All four experiments use the same 1D CNN architecture (two convolutional blocks with batch normalisation, GELU activations, adaptive average pooling, and a shared classifier head). E4 uses two independent encoder branches whose outputs are concatenated before classification.

## Dataset

This project uses the **SDALLE** (Surface-electrode Dataset for Activity recognition of the Lower Limb Extremities) dataset:

- **Source:** [Zenodo Record 14841611](https://zenodo.org/records/14841611)
- **Subjects:** 9
- **Activities:** 4 (jogging, stairs down, stairs up, walking)
- **Sensors:** 8 surface sensors, each providing 1 EMG + 6 IMU channels (56 total)
- **EMG sampling rate:** ~1259 Hz
- **IMU sampling rate:** ~148 Hz

> **Note:** The raw SDALLE dataset is **not redistributed** in this repository. See [`data/README.md`](data/README.md) for instructions on obtaining the dataset from the official source.

## Evaluation Protocol

- **Leave-One-Subject-Out (LOSO):** 9 folds, each holding out one subject as the test set
- **Window size:** 1.0 s
- **Stride:** 0.5 s (50% overlap)
- **Trial isolation:** No window crosses a trial boundary
- **Normalisation:** Per-fold z-score using only training-fold statistics (no test data leakage)
- **Statistical unit:** Subject-fold (n = 9 per experiment), not individual windows

## Training Configuration

| Parameter | Value |
|---|---|
| Optimizer | Adam |
| Learning rate | 1 × 10⁻³ |
| Weight decay | 1 × 10⁻⁴ |
| Batch size | 64 |
| Epochs | 50 |
| LR scheduler | ReduceLROnPlateau (patience=5, factor=0.5, monitors training loss) |
| Dropout | 0.3 |
| Random seed | 42 |
| Loss | CrossEntropyLoss |

No test-fold signal was used for LR scheduling, early stopping, or checkpoint selection.

## Results

| Experiment | Accuracy (Mean ± Std) | Macro F1 (Mean ± Std) |
|:---:|:---:|:---:|
| E1 — EMG only | 47.1 ± 12.6% | 37.9 ± 12.3% |
| E2 — IMU only | 67.9 ± 6.3% | 66.5 ± 6.3% |
| E3 — Rate-matched | 63.4 ± 13.9% | 62.2 ± 13.0% |
| E4 — Multirate | 71.7 ± 7.4% | 69.8 ± 7.3% |

E4 achieved the highest observed mean accuracy and F1 score. However, **the advantage of E4 over E2 and E3 was not statistically significant** after Holm–Bonferroni correction for multiple comparisons (Wilcoxon signed-rank test, n = 9 folds):

| Comparison | p (Holm-corrected) | Significant (α = 0.05) |
|---|:---:|:---:|
| E1 vs E2 | 0.039 | ✓ |
| E1 vs E3 | 0.078 | — |
| E1 vs E4 | 0.023 | ✓ |
| E2 vs E3 | 0.641 | — |
| E2 vs E4 | 0.148 | — |
| E3 vs E4 | 0.082 | — |

Full per-fold results and statistical analysis are in [`RESULTS.md`](RESULTS.md) and [`evaluation/`](evaluation/).

## Reproducibility

See [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) for the complete pipeline. In brief:

```bash
# 1. Obtain SDALLE from https://zenodo.org/records/14841611
#    Extract to data/raw/SDALLE/

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Build processed datasets (LOSO splits)
python3 src/build_datasets.py

# 4. Train all 36 folds
bash run_all.sh

# 5. Evaluate all 36 folds
python3 run_evaluation.py
```

## Repository Structure

```
├── src/                    # Source code
│   ├── build_datasets.py   # Preprocessing, windowing, LOSO split construction
│   ├── dataset_loader.py   # Raw SDALLE CSV parser
│   ├── models.py           # 1D CNN architectures (single-branch + dual-branch)
│   ├── normalizer.py       # Per-fold z-score normalisation
│   ├── train.py            # Training loop
│   ├── evaluate.py         # Original evaluation module
│   └── windower.py         # Sliding window segmentation
├── results/                # Frozen training artifacts (36 folds)
├── evaluation/             # Evaluation outputs (metrics, figures, tables)
├── paper/                  # Manuscript (LaTeX)
├── data/                   # Dataset directory (raw data not included)
├── run_all.sh              # Training orchestration script
├── run_evaluation.py       # Full evaluation pipeline
├── EXPERIMENTS.md          # Detailed experiment definitions
├── RESULTS.md              # Comprehensive results documentation
├── REPRODUCIBILITY.md      # Step-by-step reproduction guide
├── RESEARCH_PROVENANCE.md  # Research lifecycle documentation
└── requirements.txt        # Python dependencies
```

## Citation

If you use this code or reference these results, please cite:

```bibtex
@misc{bhat2025emgimu,
  author       = {Bhat, Saqib Ahmad and Karuvelam, P. Subha},
  title        = {Subject-Independent Multirate {EMG}--{IMU} Fusion for
                  Lower Limb Activity Recognition: A Reproducible
                  Evaluation on the {SDALLE} Dataset},
  year         = {2025},
  howpublished = {\url{https://github.com/SaqibAhmadBhat/subject-independent-emg-imu-fusion}}
}
```

## License

This project's original source code is released under the [MIT License](LICENSE). The SDALLE dataset is subject to its own license terms as specified by its authors on [Zenodo](https://zenodo.org/records/14841611).
