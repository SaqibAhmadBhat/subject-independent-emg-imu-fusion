# Reproducibility Guide

This document provides the exact commands needed to reproduce all results from raw data to final evaluation.

## Prerequisites

- Python 3.10+ (tested with Python 3.13)
- macOS, Linux, or Windows with appropriate PyTorch support
- ~6 GB disk space for processed data and results
- The SDALLE dataset (see [data/README.md](data/README.md))

## Pipeline Overview

```
SDALLE raw CSVs
  ↓  dataset_loader.py (parse)
  ↓  windower.py (segment)
  ↓  normalizer.py (z-score, training-fold only)
  ↓  build_datasets.py (orchestrate all above)
Processed .npz files (data/processed/)
  ↓  train.py (train one fold)
  ↓  run_all.sh (orchestrate 36 folds)
Frozen model checkpoints (results/)
  ↓  run_evaluation.py (inference + metrics + stats + figures)
Evaluation outputs (evaluation/)
```

---

## Step 1: Obtain the SDALLE Dataset

Download from [https://zenodo.org/records/14841611](https://zenodo.org/records/14841611) and extract:

```bash
# Expected structure after extraction:
# data/raw/SDALLE/Subject_1/jogging_1.csv
# data/raw/SDALLE/Subject_1/jogging_2.csv
# ...
# data/raw/SDALLE/Subject_9/walking_2.csv
```

## Step 2: Set Up the Environment

```bash
python3 -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Step 3: Build Processed Datasets

This step creates the 9-fold LOSO splits for all four experiments, applying windowing and normalisation:

```bash
python3 src/build_datasets.py
```

**What it does:**
1. Parses all SDALLE trial CSVs
2. For each of the 9 folds (holding out one subject):
   - Creates E1 (EMG-only) windows at 1259 Hz
   - Creates E2 (IMU-only) windows at 148 Hz
   - Creates E3 (rate-matched) windows with cubic-interpolated EMG
   - Creates E4 (multirate) paired EMG + IMU windows
3. Normalises each split using only training-fold statistics
4. Saves to `data/processed/<experiment>/fold_<N>/dataset.npz`

**Assertions enforced:**
- EMG has exactly 8 channels
- IMU has exactly 48 channels
- No test subject appears in training data
- Normalisation parameters derived from training data only

**Output:** `data/processed/` (~3.6 GB)

## Step 4: Train All Models

```bash
# Train all 36 folds (E1–E4 × folds 1–9)
bash run_all.sh
```

**Or train individual folds:**

```bash
python3 src/train.py --exp E1 --fold 1 --epochs 50 --device cpu
python3 src/train.py --exp E4 --fold 3 --epochs 50 --device mps  # Apple Silicon
```

**Training details:**
- Each fold trains for exactly 50 epochs
- LR scheduler monitors training loss only (no test signal)
- No early stopping, no checkpoint selection using test data
- Each fold saves: `model.pt`, `history.json`, `meta.json`

**Output:** `results/<EXP>/fold_<N>/` (36 folds, ~30 MB total)

**Note:** `run_all.sh` is resumable — it skips folds that already have valid output files.

## Step 5: Evaluate All Models

```bash
python3 run_evaluation.py
```

**What it does:**
1. Verifies all 36 model checksums
2. Runs inference on each fold's test set using the frozen model
3. Computes per-fold metrics (accuracy, macro P/R/F1, confusion matrix)
4. Computes experiment-level summaries (mean, std, median, min, max)
5. Runs Wilcoxon signed-rank tests with Holm–Bonferroni correction
6. Generates publication-quality figures
7. Writes evaluation manifest and audit

**Output:** `evaluation/` (~1.7 MB)

---

## Verification

After completing all steps, verify your results match:

```bash
# Check all 36 folds were trained
python3 verify_folds.py

# Check evaluation output
wc -l evaluation/final_metrics.csv        # Should show 37 (36 data + 1 header)
wc -l evaluation/evaluation_manifest.csv  # Should show 37
```

Expected experiment-level results (mean accuracy ± std):

| Experiment | Expected |
|---|---|
| E1 | 0.471 ± 0.126 |
| E2 | 0.679 ± 0.063 |
| E3 | 0.634 ± 0.139 |
| E4 | 0.717 ± 0.074 |

**Note:** Results should be exactly reproducible when using the same random seed (42), Python version, and PyTorch version. Minor floating-point differences may occur across different hardware or PyTorch versions.

---

## Software Versions Used

The original experiments were conducted with:

| Package | Version |
|---|---|
| Python | 3.13 |
| PyTorch | 2.x |
| NumPy | 2.5.2 |
| SciPy | 1.18.1 |
| matplotlib | 3.11.1 |
| seaborn | 0.13.2 |
| scikit-learn | 1.9.0 |

## Hardware

Training was performed on Apple Silicon (MPS backend). Evaluation was performed on CPU for reproducibility.
