# Release Notes — Version 2.0.0

**Release Tag:** `v2.0.0`  
**Publication Date:** November 2026  
**Concept DOI (all versions):** [10.5281/zenodo.22649504](https://doi.org/10.5281/zenodo.22649504)  
**Version 1.0.0 DOI:** [10.5281/zenodo.22649505](https://doi.org/10.5281/zenodo.22649505)  
**Version 2.0.0 Draft Record:** [10.5281/zenodo.24220130](https://doi.org/10.5281/zenodo.24220130)  
**Upstream SDALLE Benchmark DOI:** [10.5281/zenodo.14841611](https://doi.org/10.5281/zenodo.14841611)

---

## 1. Executive Summary

Version 2.0.0 introduces the **Multimodal EMG–IMU Robustness Study (Study V2)** to the repository. While Version 1.0.0 evaluated sensor fusion across differing branch capacities with a single random seed, Version 2.0.0 conducts a strictly parameter-matched comparison (330,052 parameters) between:
1. **Rate-Matched Fusion (Condition E3-D):** sEMG cubic-interpolated to the IMU sampling rate (148.15 Hz) without anti-aliasing pre-filtering.
2. **Native-Rate Fusion (Condition E4):** sEMG processed at its native acquisition frequency (1259.26 Hz), with IMU at 148.15 Hz.

Both conditions are evaluated across 9-fold leave-one-participant-out (LOSO) cross-validation repeated across 5 random seeds (42, 123, 2024, 3407, 7777), comprising 90 full training runs.

---

## 2. Key Findings & Audited Baseline

- **Primary Classification Accuracy:** Rate-matched fusion achieved a mean participant accuracy of **72.90% $\pm$ 9.24%** versus **69.07% $\pm$ 10.80%** for native-rate fusion (mean paired difference: **+3.83 pp**, SD: 4.12 pp, median: +3.14 pp; 8 of 9 participants positive).
- **Hypothesis Testing:** Protocol-specified two-sided Wilcoxon signed-rank test yields $W = 5$ ($W^+ = 40, W^- = 5$), exact $p = \mathbf{0.039}$, rank-biserial correlation $r = \mathbf{+0.78}$, 95% percentile bootstrap CI: $\mathbf{[1.27, 6.35] \text{ pp}}$.
- **Sensitivity Analyses:**
  - Exact sign-flip permutation test: $p = \mathbf{0.031}$ (16 / 512 permutations).
  - Two-stage hierarchical bootstrap 95% CI: $\mathbf{[1.07, 6.65] \text{ pp}}$.
  - Leave-one-seed-out sensitivity: $p$-values range between **$0.012$ and $0.055$**.
  - Leave-one-participant-out sensitivity: omitting P1 yields $p = 0.008$; omitting any other participant yields $p = 0.055\text{--}0.078$, reflecting inferential fragility under small cohort size ($N = 9$).
- **Variance Decomposition:** Standard deviation between seeds within a participant was **4.23 pp**, exceeding between-participant standard deviation (**3.66 pp**, ICC = **0.43**). Multi-seed averaging reduced seed-noise standard error to 1.89 pp.
- **Spectral Signal Audit (All 361 Raw Trials):** $19.0\% \pm 10.3\%$ of sEMG power lay above 74.07 Hz (the rate-matched Nyquist limit), and $33.1\% \pm 12.4\%$ lay below 20 Hz. Super-Nyquist power fraction did not correlate with accuracy differences ($\rho = 0.12, p = 0.77$).
- **Computational Cost:** Median wall-clock training time was **1,525.5 s** for rate matching versus **6,621.2 s** for native-rate (a **4.34× speedup**).

---

## 3. Structural & Architectural Additions

### Added in `v2_rate_matching_study/`
- `V2/src/`: Data preprocessing pipeline (`build_datasets_v2.py`, `windower_v2.py`) with cubic-spline interpolation.
- `src/`: Deep learning architecture modules (`models.py`, `dataset_loader.py`, `normalizer.py`).
- `V2_ROBUSTNESS_STUDY/`:
  - 90 run records across 5 seeds: `predictions.csv`, `history.json`, `meta.json`.
  - Canonical result tables (`analysis/tables/`).
  - Study execution harness (`run_study.sh`, `robustness_train.py`, `robustness_analyze.py`).
- `verification/`:
  - Complete independent verification suite (`verify_v2_statistics.py`, `verify_v2_additional_stats.py`, `verify_v2_sensitivity.py`).
  - Full-cohort spectral analysis (`emg_spectrum_check.py`).
  - 9 verification output JSON files.
  - Complete scientific discrepancy register (`SCIENTIFIC_DISCREPANCY_REGISTER.md`).
- `provenance/`: Archival copies of original training scripts.

### Added at Repository Root
- `docs/`: Comprehensive technical documentation (`ARCHITECTURE.md`, `RESEARCH_WORKFLOW.md`, `EXPERIMENT_DESIGN.md`, `REPRODUCIBILITY.md`, `INSTALLATION.md`, `EXECUTION_GUIDE.md`, `DATASET_GUIDE.md`, `STATISTICAL_ANALYSIS.md`, `RELEASE_NOTES.md`).
- `tests/`: Automated test suite for architecture, parameter count, receptive field, and statistical reproducibility.
- `scripts/`: Release verification and checksum integrity tools.
- `.github/workflows/ci.yml`: Continuous integration workflow.
- `CONTRIBUTING.md` & `SECURITY.md`.

---

## 4. Preservation of Version 1.0.0

- All Version 1.0.0 files at the repository root remain **100% bit-identical** to commit `f2be710e8dd50279d39813320930a2ae4a42c728`.
- Tag `v1.0.0` and Zenodo DOI `10.5281/zenodo.22649505` continue to reference the original single-seed multirate fusion study.
- V1 and V2 maintain separate namespaces to prevent experimental cross-contamination.

---

## 5. Frozen Archive Verification Hashes

| Archive | File Size | SHA-256 Checksum |
|---|---|---|
| `v2_release_candidate_final.zip` | 1,995,409 bytes | `787ff47226c4c237a8110fbe35bb085c316642a3743750a2e599265748bd46a0` |
| `v2_reproducibility_data_final.zip` | 2,382,660,603 bytes | `00ddeff0ead81d394a5e516f584ef52a5d5ef97b35fbc44e69bb921dacb939a2` |
| `v2_verification_audit.zip` | 67,848 bytes | `c80e46a3fc46e0fb56008c8db48ce63c7e87922a645dfb7ff72fd0667f4b364d` |
