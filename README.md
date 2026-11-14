# Subject-Independent EMG–IMU Sensor Fusion for Human Activity Recognition

[![DOI: 10.5281/zenodo.22649504](https://zenodo.org/badge/DOI/10.5281/zenodo.22649504.svg)](https://doi.org/10.5281/zenodo.22649504)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Data License: CC BY 4.0](https://img.shields.io/badge/Data_License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![PyTorch 2.x](https://img.shields.io/badge/PyTorch-2.x-ee4c2c.svg)](https://pytorch.org/)
[![CI](https://github.com/SaqibAhmadBhat/subject-independent-emg-imu-fusion/actions/workflows/ci.yml/badge.svg)](https://github.com/SaqibAhmadBhat/subject-independent-emg-imu-fusion/actions/workflows/ci.yml)

An open-source, reproducible research software repository for subject-independent human activity recognition (HAR) combining surface electromyography (sEMG) and inertial measurement units (IMUs) from the public [SDALLE dataset](https://doi.org/10.5281/zenodo.14841611).

This repository contains two completed, permanently archived research studies:
- **Version 1.0.0 (Multirate Fusion Study):** Evaluated multirate late fusion against unimodal baselines and early rate-matched fusion using single-seed leave-one-subject-out cross-validation.
- **Version 2.0.0 (Rate-Matching Robustness Study):** A strictly parameter-matched evaluation (330,052 parameters) comparing rate-matched sEMG against native-rate sEMG across 9 leave-one-participant-out folds repeated over 5 random seeds (90 full runs).

---

## Studies in this Repository

| Version | Tag | Focus & Scope | Model Capacity | Cross-Validation | Location | Archive DOI |
|---|---|---|---|---|---|---|
| **v1.0.0** | `v1.0.0` | Multirate late fusion vs unimodal baselines | Differing branch sizes | 9 folds $\times$ 1 seed (36 runs) | Repository root (`src/`, `results/`) | [10.5281/zenodo.22649505](https://doi.org/10.5281/zenodo.22649505) |
| **v2.0.0** | `v2.0.0` | Rate-matched vs native-rate sEMG robustness | Exactly 330,052 parameters | 9 folds $\times$ 5 seeds (90 runs) | [`v2_rate_matching_study/`](v2_rate_matching_study/) | [10.5281/zenodo.22649504](https://doi.org/10.5281/zenodo.22649504) (Draft: `24220130`) |

> **Methodological Separation:** Version 1.0.0 and Version 2.0.0 investigate different research questions. Version 1.0.0 compared distinct fusion architectures. Version 2.0.0 holds model capacity strictly constant to isolate the effect of sampling rate harmonization. Their numerical results must not be directly merged.

---

## What Version 2.0.0 Investigates

In multimodal wearable sensing, sEMG signals are typically acquired at kilohertz rates (~1259 Hz) to capture muscle action potentials, whereas IMUs sample kinematics at lower frequencies (~148 Hz). A prevalent practice is **rate matching**—downsampling sEMG via cubic spline interpolation to match the inertial sampling frequency—which discards high-frequency spectral content and aliases frequencies above the 74.07 Hz Nyquist boundary.

**Core Research Question:**
> Does native-rate sEMG processing preserve task-relevant neuromuscular information that improves subject-independent lower-limb activity recognition compared to rate-matched sEMG, when evaluated inside a dual-branch neural network of identical capacity?

### Key Findings (Study V2)
- **Protocol-Specified Primary Outcome:** Rate-matched fusion reached a mean participant accuracy of **72.90% $\pm$ 9.24%** versus **69.07% $\pm$ 10.80%** for native-rate fusion (mean paired difference: **+3.83 pp**, SD: 4.12 pp, median: +3.14 pp; rate matching ahead in 8 of 9 participants).
- **Hypothesis Testing:** Two-sided Wilcoxon signed-rank test yields $W = 5$ ($W^+ = 40, W^- = 5$), exact $p = \mathbf{0.039}$, matched-pairs rank-biserial correlation $r = \mathbf{+0.78}$, 95% percentile bootstrap CI: $\mathbf{[1.27, 6.35] \text{ pp}}$.
- **Sensitivity & Robustness:**
  - Exact sign-flip permutation test on participant mean differences: $p = \mathbf{0.031}$ (16 of 512 sign assignments).
  - Two-stage hierarchical bootstrap 95% CI (participants then seeds): $\mathbf{[1.07, 6.65] \text{ pp}}$.
  - Leave-one-seed-out sensitivity: $p$ ranges from **$0.012$ to $0.055$** (rate matching ahead in 8/9 participants in every combination).
  - Leave-one-participant-out sensitivity: omitting P1 yields $p = 0.008$; omitting any other participant yields $p = 0.055\text{--}0.078$, indicating the inferential fragility of an $N=9$ cohort.
- **Variance Decomposition:** Standard deviation between seeds within a participant was **4.23 pp**, exceeding between-participant standard deviation (**3.66 pp**, ICC = **0.43**), proving that multi-seed replication is necessary in wearable deep learning.
- **Spectral Signal Audit (All 361 Raw Trials):** $19.0\% \pm 10.3\%$ of sEMG power lay above 74.07 Hz (the rate-matched Nyquist limit), and $33.1\% \pm 12.4\%$ lay below 20 Hz. Super-Nyquist power fraction was not associated with accuracy differences ($\rho = 0.12, p = 0.77$).
- **Computational Efficiency:** Rate matching trains **4.34× faster** (median 1,525.5 s vs 6,621.2 s per fold) and classifies 4.3× faster at inference.

---

## Repository Structure

```text
subject-independent-emg-imu-fusion/
├── docs/                               <-- Comprehensive Technical Documentation
│   ├── ARCHITECTURE.md                 <-- Network architecture, layer budgets & RF
│   ├── RESEARCH_WORKFLOW.md            <-- End-to-end experimental lifecycle
│   ├── EXPERIMENT_DESIGN.md            <-- Demographics, segmentation & protocol
│   ├── REPRODUCIBILITY.md              <-- 3-tier reproduction framework
│   ├── INSTALLATION.md                 <-- Setup & GPU configuration guide
│   ├── EXECUTION_GUIDE.md              <-- CLI execution commands
│   ├── DATASET_GUIDE.md                <-- SDALLE sensor layout & synchronization
│   ├── STATISTICAL_ANALYSIS.md         <-- Exact formulas & hypothesis tests
│   └── RELEASE_NOTES.md                <-- v2.0.0 release notes
│
├── v2_rate_matching_study/             <-- Authoritative V2 Study Release
│   ├── README.md                       <-- V2 study overview
│   ├── REPRODUCE.md                    <-- Step-by-step reproduction guide
│   ├── MANIFEST.md                     <-- File manifest & data checksums
│   ├── PREPROCESSING.md                <-- Cubic-spline windowing specification
│   ├── SHA256SUMS                      <-- Checksums of all V2 files
│   ├── V2/src/                         <-- Dataset builder & windowing modules
│   ├── src/                            <-- Core data loaders & model modules
│   ├── provenance/                     <-- Archival copy of run scripts
│   ├── verification/                   <-- Standalone Verification Suite
│   │   ├── README.md                   <-- Verification instructions
│   │   ├── verify_v2_statistics.py     <-- Primary statistical recomputation
│   │   ├── verify_v2_additional_stats.py<-- Permutation & bootstrap recomputation
│   │   ├── emg_spectrum_check.py       <-- 361-trial Welch PSD spectral check
│   │   ├── audit_90_runs.py            <-- 90-run prediction integrity audit
│   │   ├── SCIENTIFIC_DISCREPANCY_REGISTER.md <-- Register of all resolutions
│   │   └── outputs/                    <-- Canonical JSON verification outputs
│   └── V2_ROBUSTNESS_STUDY/            <-- 90 Run Prediction Records & Tables
│       ├── seed_{42,123,2024,3407,7777}/<-- predictions.csv, meta.json, history.json
│       └── analysis/tables/            <-- Canonical CSV & JSON metric tables
│
├── tests/                              <-- Automated Test Suite (pytest)
│   ├── test_model_architecture.py      <-- Parameter count & receptive field tests
│   ├── test_prediction_integrity.py    <-- Run completeness & label consistency
│   ├── test_statistical_reproducibility.py <-- Recomputation of exact findings
│   └── test_archive_checksums.py       <-- Verification of frozen ZIP checksums
│
├── scripts/                            <-- Utility & Release Verification Scripts
│   └── verify_release.py               <-- One-step release health audit
│
├── .github/workflows/ci.yml            <-- Continuous Integration Workflow
├── CITATION.cff                        <-- Machine-readable citation metadata
├── LICENSE                             <-- MIT License (c) 2025 Saqib Ahmad Bhat et al.
├── CHANGELOG.md                        <-- Version history
├── CONTRIBUTING.md                     <-- Contribution guidelines
└── SECURITY.md                         <-- Security & disclosure policy
```

---

## Quick-Start: Reproduce Findings in Under 10 Seconds

All 90 run predictions are committed in the repository. No GPU or training required to verify all statistics:

```bash
# 1. Clone repository
git clone https://github.com/SaqibAhmadBhat/subject-independent-emg-imu-fusion.git
cd subject-independent-emg-imu-fusion

# 2. Run primary statistical verification
python3 v2_rate_matching_study/verification/verify_v2_statistics.py \
    v2_rate_matching_study/V2_ROBUSTNESS_STUDY \
    /tmp/stat_check.json

# 3. Run sensitivity & permutation verification
python3 v2_rate_matching_study/verification/verify_v2_additional_stats.py \
    v2_rate_matching_study/V2_ROBUSTNESS_STUDY \
    /tmp/additional_check.json

# 4. Run automated test suite
pip install pytest
pytest tests/ -v
```

See [`docs/EXECUTION_GUIDE.md`](docs/EXECUTION_GUIDE.md) and [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) for full reproduction details.

---

## Zenodo Distribution Architecture

The V2 release is archived under the Concept DOI [10.5281/zenodo.22649504](https://doi.org/10.5281/zenodo.22649504) across three frozen components:

1. **`v2_release_candidate_final.zip` (1,995,409 bytes / ~1.90 MiB):** Complete software source code, training harness, 90 run configurations, per-window prediction CSVs, metric tables, figures, test suite, and execution instructions.  
   *SHA-256:* `787ff47226c4c237a8110fbe35bb085c316642a3743750a2e599265748bd46a0`
2. **`v2_reproducibility_data_final.zip` (2,382,660,603 bytes / ~2.22 GiB):** Companion preprocessed windowed array archive containing 18 NumPy array files (`data/processed/{E3-D,E4}/dataset_fold_{1..9}.npz`) to enable model retraining without raw CSV windowing.  
   *SHA-256:* `00ddeff0ead81d394a5e516f584ef52a5d5ef97b35fbc44e69bb921dacb939a2`
3. **`v2_verification_audit.zip` (67,848 bytes / ~66.3 KiB):** Supplementary independent verification suite containing statistical verification scripts, full-cohort spectral analysis outputs across all 361 trials, and the complete scientific discrepancy register.  
   *SHA-256:* `c80e46a3fc46e0fb56008c8db48ce63c7e87922a645dfb7ff72fd0667f4b364d`

---

## Citation & Academic Attribution

If you use this codebase, models, or prediction records, please cite:

```bibtex
@software{bhat2026sdalle_v2,
  author       = {Bhat, Saqib Ahmad and G, Sona and Karuvelam, P. Subha},
  title        = {{Subject-Independent EMG-IMU Fusion for Lower-Limb Activity Recognition: Code and Frozen Results}},
  month        = nov,
  year         = 2026,
  publisher    = {Zenodo},
  version      = {2.0.0},
  doi          = {10.5281/zenodo.22649504},
  url          = {https://github.com/SaqibAhmadBhat/subject-independent-emg-imu-fusion}
}
```

Please also cite the underlying benchmark dataset:
```bibtex
@dataset{ibrahim2025sdalle,
  author       = {Ibrahim, Abdellatif Hamed and Ali, Mohamed and Mohsen, Reham and El-Khoreby, Ahmed and Farouk, Hossam},
  title        = {{SDALLE: A Multimodal Dataset for Human Activity Recognition using EMG and IMU Sensors}},
  month        = feb,
  year         = 2025,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.14841611}
}
```

---

## Licensing

- **Software Source Code:** Licensed under the [MIT License](LICENSE) (`Copyright (c) 2025 Saqib Ahmad Bhat, Sona G, P. Subha Karuvelam`).
- **Documentation, Result Tables, Figures, and Derived Arrays:** Shared under the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).
- **Upstream Dataset:** SDALLE is licensed under [CC BY 4.0](https://doi.org/10.5281/zenodo.14841611).
