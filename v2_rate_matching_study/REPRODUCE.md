# Reproducing the V2 study

Three levels, from quickest to slowest. Commands are run from this folder (`v2_rate_matching_study/`).

The primary comparison between rate-matched and native-rate sEMG represents a **protocol-specified primary analysis (not fully prespecified)**, because four execution details (exact null distribution of the signed-rank statistic, percentile form of the bootstrap interval, seed averaging, and reference significance level of 0.05) were fixed in the analysis script rather than in the protocol text itself.

## Model Checkpoints and Reproducibility Tiers

Frozen model checkpoint weights (`.pt`, ~117 MB total across 90 runs) are **not included in any public release component** (neither in the primary archive, nor in the reproducibility archive, nor in the verification archive, nor in the GitHub repository tree). They are preserved offline and available from the authors upon request.

We distinguish three tiers of reproduction:
1. **Stored prediction reproducibility (Level 1):** Exact recomputation of all reported metrics, bootstrap confidence intervals, and hypothesis tests from the frozen per-window predictions (`predictions.csv`) using the released verification scripts without PyTorch or GPU hardware.
2. **Retraining reproducibility (Level 3):** End-to-end retraining from preprocessed input arrays (`.npz`) using the training code and fixed seeds, which reproduces the scientific findings within expected seed and fold variation.
3. **Exact checkpoint reproduction:** Bit-identical reproduction of the original trained `.pt` model weights is subject to platform- and library-dependent floating-point non-determinism across disparate hardware architectures and compiler backends. The study's scientific claims rest on participant-level statistical outcomes, not on bit-identical floating-point weight matrices.

## Licensing

- **Software code (scripts):** MIT License (`LICENSE`).
- **Documentation, figures, tables, and derived outputs:** Creative Commons Attribution 4.0 International (CC-BY 4.0).

---

## Level 1: verify the statistics from the stored predictions (minutes)

Needs Python 3 with NumPy and SciPy. No dataset, no PyTorch, and no checkpoint weights required.

```bash
sha256sum -c SHA256SUMS      # on macOS: shasum -a 256 -c SHA256SUMS
python3 verification/audit_90_runs.py V2_ROBUSTNESS_STUDY out_audit.json
python3 verification/verify_v2_statistics.py --v2-root V2_ROBUSTNESS_STUDY --out out_statistics.json
python3 verification/verify_v2_sensitivity.py --v2-root V2_ROBUSTNESS_STUDY --spectrum verification/outputs/emg_spectrum_check_all_trials.json --out out_sensitivity.json
python3 verification/verify_v2_additional_stats.py V2_ROBUSTNESS_STUDY out_additional.json
```

Compare the outputs with the files in `verification/outputs/`. On 14 November 2026 these four commands, run on this folder, reproduced the stored outputs exactly. Expected headline values: mean accuracy 72.90% (RM, `E3-D`) and 69.07% (NR, `E4`); paired difference +3.83 points; Wilcoxon W = 5, exact p = 0.0390625; percentile bootstrap interval 1.2713 to 6.3548.

*Note on verification categories:*
- `audit_90_runs.py`, `verify_v2_statistics.py`, `verify_v2_sensitivity.py`, and `verify_v2_additional_stats.py` derive statistical outputs strictly from frozen predictions (`predictions.csv`) and run metadata.
- In contrast, `verification/outputs/emg_spectrum_check_all_trials.json` is a precomputed spectral analysis calculated directly from the original 361 raw recording trials of the SDALLE dataset via `verification/emg_spectrum_check.py`. It confirms the presence of raw sEMG high-frequency energy (> 74 Hz) that is aliased during unfiltered cubic resampling.

The bootstrap uses `numpy.random.default_rng(42)` with 10,000 resamples. Interval limits can differ in the last digits between NumPy versions.

## Level 2: regenerate the input arrays from SDALLE (needs the dataset; writes 2.38 GB)

Alternatively, the 18 preprocessed arrays are available directly in the reproducibility archive (`v2_reproducibility_data_final.zip`). To regenerate them from scratch:

1. Download SDALLE from https://doi.org/10.5281/zenodo.14841611 and extract it so that the trial files are at `data/raw/SDALLE/Subject_<n>/<Activity>/Trial_<m>.csv` inside this folder.
2. Build the arrays for the two conditions:

```bash
python3 V2/src/build_datasets_v2.py E3-D E4
```

This writes `V2/data/processed/E3-D/dataset_fold_<k>.npz` and `V2/data/processed/E4/dataset_fold_<k>.npz`.

3. Compute content digests of the arrays and compare them with the digests of the arrays the study used:

```bash
python3 verification/array_content_digests.py V2/data/processed out_digests.json
```

Compare `out_digests.json` with `verification/outputs/processed_array_content_digests.json`. Compare array content, not file checksums: the `.npz` container stores time stamps, so two files with identical arrays have different file checksums.

The authors' check (Python 3.10.12, NumPy 2.2.6, SciPy 1.15.3, Linux) reproduced all 18 arrays bit-identically from the raw files.

## Level 3: retrain (about four days of computation on a laptop CPU)

Needs the packages in `V2_ROBUSTNESS_STUDY/requirements.txt` (PyTorch 2.10.0) and the arrays from level 2 in `V2/data/processed/`.

Train in a clean copy of the code, so that the stored outputs are not touched:

```bash
mkdir -p retrain/V2_ROBUSTNESS_STUDY
cp -R src V2 retrain/
cp -R V2_ROBUSTNESS_STUDY/src V2_ROBUSTNESS_STUDY/*.py V2_ROBUSTNESS_STUDY/run_study.sh retrain/V2_ROBUSTNESS_STUDY/
cd retrain && bash V2_ROBUSTNESS_STUDY/run_study.sh
```

The new outputs appear in `retrain/V2_ROBUSTNESS_STUDY/seed_<seed>/<condition>/fold_<k>/`. Compare them with the stored ones, for example by running the level 1 scripts on `retrain/V2_ROBUSTNESS_STUDY`.

Training used the CPU of an Apple MacBook Air (M4, arm64) with Python 3.13.12 and PyTorch 2.10.0. Seeds are fixed, but bit-identical predictions or checkpoint weights on other hardware or library builds are not guaranteed. Judge a rerun by whether its participant-level results agree with the stored ones within the seed-to-seed variation reported in `verification/README.md`, not by identical predictions or identical model weights.

Level 3 was not re-run for this release. Levels 1 and 2 were.
