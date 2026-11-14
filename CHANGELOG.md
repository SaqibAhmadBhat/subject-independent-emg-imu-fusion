# Changelog

All notable changes to this repository are recorded here. Versions follow semantic versioning. Each version is a Git tag and a Zenodo version under the Concept DOI [10.5281/zenodo.22649504](https://doi.org/10.5281/zenodo.22649504).

## 2.0.0

Adds the V2 rate-matching study (protocol-specified primary analysis, not fully prespecified). Distributed across three frozen archives on Zenodo (primary, reproducibility, verification) and this repository overlay. Nothing from version 1.0.0 is changed or removed.

### Added
- `v2_rate_matching_study/`: rate-matched versus native-rate surface EMG in a dual-branch EMG–IMU network of fixed size (330,052 parameters; 9 LOPO folds × 5 seeds = 90 runs).
  - Internal protocol (`protocol.md`), training and analysis code, model definitions.
  - Preprocessing modules used to build the input arrays (`src/`, `V2/src/`).
  - Per-window predictions, run records and training histories of all 90 runs (`V2_ROBUSTNESS_STUDY/seed_*/`).
  - Canonical result tables as produced by the study's analysis scripts (`V2_ROBUSTNESS_STUDY/analysis/`).
  - Verification scripts and their outputs (`verification/`), distinguishing statistical outputs derived from frozen predictions from spectral results calculated from the original 361 SDALLE trials.
  - `SHA256SUMS` and `MANIFEST.md` for the folder.
- `CHANGELOG.md` and `.zenodo.json` at the repository root.

### Changed
- `README.md`: new section "Versions in this repository". The description of version 1.0.0 is unchanged.
- `CITATION.cff`: version 2.0.0, three authors, Concept DOI and version 1.0.0 DOI. Clarifies that the MIT License governs software code, while non-software contents are shared under CC-BY 4.0.

### Licensing
- Software code: MIT License (`LICENSE`).
- Documentation, figures, result tables, and derived outputs: Creative Commons Attribution 4.0 International (CC-BY 4.0) where rights permit.

### Excluded from Public Distribution
- Frozen model checkpoint weights (`.pt`, ~117 MB) are not included in any public release component (available on request). Stored prediction reproducibility (Level 1) allows complete verification of all statistics without checkpoints or GPU compute.
- Processed input arrays (18 `.npz` files, 2.38 GB) are distributed in a dedicated reproducibility archive (`v2_reproducibility_data_final.zip`) and regenerable via preprocessing modules.

### Not changed
- All files of version 1.0.0 at the repository root (`src/`, `evaluation/`, `results/`, `data/`, `paper/` and the top-level scripts and documents other than `README.md` and `CITATION.cff`).
- Tag `v1.0.0` (commit `f2be710`) and its Zenodo record [10.5281/zenodo.22649505](https://doi.org/10.5281/zenodo.22649505).

## 1.0.0 (2026-09-07)

Initial release: subject-independent multirate EMG–IMU fusion study (sEMG-only, IMU-only, rate-matched and native-rate fusion; leave-one-subject-out; one seed). Archived on Zenodo as [10.5281/zenodo.22649505](https://doi.org/10.5281/zenodo.22649505), published 8 September 2026.
