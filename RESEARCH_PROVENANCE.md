# Research Provenance

This document describes the high-level lifecycle of the RP4 research project.

## 1. Dataset Identification and Audit

The SDALLE dataset was identified as a suitable benchmark for subject-independent lower-limb activity recognition due to its:
- Multi-sensor design (8 surface sensors with EMG + IMU)
- Dual sampling rate (EMG ~1259 Hz, IMU ~148 Hz)
- 9-subject design enabling LOSO cross-validation
- 4 locomotion activities
- Public availability via Zenodo

A critical audit of the original SDALLE benchmark paper identified that the published window-level evaluation protocol (random train/test window splits) permitted data leakage across subjects, making reported accuracies (~98–99%) non-generalisable.

## 2. Experiment Design

Four experiments were designed to answer the research question, comparing:
- E1: EMG-only baseline
- E2: IMU-only baseline
- E3: Rate-matched fusion (conventional approach)
- E4: Native-rate multirate fusion (proposed approach)

Key design decisions made before seeing any results:
- Leave-One-Subject-Out evaluation protocol
- Fixed 1D CNN architecture for all experiments
- Predetermined hyperparameters (lr=1e-3, wd=1e-4, batch=64, epochs=50, dropout=0.3, seed=42)
- No hyperparameter tuning on test data
- LR scheduler driven by training loss only

## 3. Training Implementation

The preprocessing pipeline was implemented with structural safeguards against data leakage:
- Normalisation statistics computed from training fold only (`normalizer.py`)
- Trial-level windowing preventing cross-trial contamination (`windower.py`)
- Explicit subject leakage assertions (`build_datasets.py`)

Training was executed for all 36 folds (4 experiments × 9 folds) using `run_all.sh`. The training loop records only training metrics; no test-fold signal influences any training decision.

## 4. Training Verification

After training, a verification step confirmed:
- All 36 folds completed (model.pt, history.json, meta.json present)
- Each history.json contains exactly 50 train_loss and 50 train_acc entries
- No test/validation metrics recorded during training
- Correct experiment and fold metadata in every meta.json

## 5. Frozen Artifact Preservation

The completed training artifacts were frozen:
- SHA-256 checksums generated for all model and metadata files
- Complete backup created (`results_backup/`)
- Training manifest and audit documents generated

After this point, no training artifact was modified.

## 6. Independent Evaluation

A self-contained evaluation pipeline (`run_evaluation.py`) was executed:
- Model checksums verified before inference
- Each of 36 folds evaluated exactly once
- Set-tracking assertions prevented duplicate evaluation
- The `results/` directory was read-only throughout evaluation

## 7. Statistical Analysis

Pairwise comparisons used:
- Wilcoxon signed-rank test (paired, non-parametric, n=9)
- Holm–Bonferroni correction for 6 comparisons
- Cohen's d effect size for paired differences

The statistical unit was the subject-fold (n=9), not individual windows.

## 8. Manuscript Preparation

The manuscript documents:
- The methodology critique of the original SDALLE evaluation protocol
- The corrected subject-independent evaluation
- All experimental results without cherry-picking
- The distinction between observed numerical superiority and statistical significance
- Honest reporting of non-significant comparisons

---

## Integrity Notes

- All four experiments used predetermined, identical training configurations
- No experiment was repeated with different settings after seeing results
- Non-significant results (E4 vs E2, E4 vs E3) are reported transparently
- The complete codebase, trained models, and evaluation outputs are preserved
