# Verification scripts and outputs

These scripts were written separately from the training and analysis code. They read the stored run outputs or raw dataset files and recompute what is reported. They need NumPy and SciPy only, except where noted. The usage line at the top of each script gives its arguments; `../REPRODUCE.md` lists the commands.

## Three Categories of Verification Artifacts

The verification suite distinguishes three distinct types of operations and outputs:

### 1. Statistical outputs derived from frozen predictions
These scripts read the frozen per-window predictions (`predictions.csv`) and run records (`meta.json`, `history.json`) across the 90 runs. They require no PyTorch installation, no GPU hardware, and no raw data:
- `audit_90_runs.py` &rarr; `audit_90_runs_output.json`: Completeness and internal consistency of the 90 runs.
- `verify_v2_statistics.py` &rarr; `statistical_verification_output.json`: Main analysis (mean accuracy 72.90% vs 69.07%, paired difference +3.83 points, exact Wilcoxon signed-rank test W = 5, p = 0.0390625, matched-pairs rank-biserial correlation 0.78, percentile bootstrap 95% interval 1.27 to 6.35).
- `verify_v2_sensitivity.py` &rarr; `sensitivity_analysis_output.json`: Robustness across analytical choices (t-interval, Hodges–Lehmann estimate, sign test, per-seed tests, median over seeds, balanced accuracy).
- `verify_v2_additional_stats.py` &rarr; `additional_statistics_output.json`: Sign-flip permutation test, two-stage bootstrap (participants, then seeds), leave-one-seed-out, and variance components.

### 2. Spectral results calculated from original raw SDALLE trials
- `emg_spectrum_check.py` &rarr; `emg_spectrum_check_all_trials.json`: Calculates Welch power spectral densities, median frequencies, bandwidths, and power above 74 Hz directly from the raw surface EMG signals across **all 361 recording trials** of the 9 SDALLE participants (needs the raw SDALLE CSV dataset). This demonstrates that raw surface EMG contains significant energy above the 74.07 Hz Nyquist boundary of the 148.15 Hz inertial sampling rate, establishing that unfiltered cubic resampling introduces aliasing.

### 3. Array integrity and regeneration verification
- `audit_processed_arrays.py` &rarr; `audit_processed_arrays_output.json`: Audits train/test separation, class labels, normalisation, and window overlap in the 18 processed arrays (needs the arrays from `v2_reproducibility_data_final.zip` or regenerated locally).
- `array_content_digests.py` &rarr; `processed_array_content_digests.json`: Computes SHA-256 digests of array data contents for bit-identical verification.
- `regenerate_arrays_check.py` &rarr; `regeneration_check_output.json`: Rebuilds arrays from raw files in memory and compares them with stored arrays.

`outputs/preliminary_single_seed_runs.json` summarises preliminary single-seed runs that preceded the protocol (sEMG only, IMU only, single-stream fusion and the two dual-branch conditions). Their run files are not part of this release.

In `audit_90_runs_output.json`, the execution order and dates come from file times of the original run records. They cannot be recomputed from a clone of the repository, where file times are those of the checkout.

## Model Checkpoint Weights Note

Frozen model checkpoint weights (`.pt`, ~117 MB total) are **not included in any public release component**; they remain archived offline and are available from the authors upon request. Stored prediction reproducibility (Level 1) allows full verification of all statistical findings directly from predictions; retraining reproducibility (Level 3) reproduces findings within expected seed/fold variation; exact checkpoint reproduction is subject to hardware-dependent floating-point non-determinism.

## Licensing

- **Verification scripts (`.py`):** Licensed under the **MIT License** (`../LICENSE`).
- **Verification outputs (`.json`) and documentation (`.md`):** Shared under **Creative Commons Attribution 4.0 International (CC-BY 4.0)** where rights permit (preserving upstream SDALLE CC-BY 4.0 attribution).

## Status of the analyses

The protocol (`../V2_ROBUSTNESS_STUDY/protocol.md`) was written before the 90 runs and was not publicly registered. It names the participant as the statistical unit, a two-sided Wilcoxon signed-rank test on the paired accuracy differences, the matched-pairs rank-biserial correlation and a bootstrap 95% interval with 10,000 resamples. It does not state a significance level, the exact or asymptotic form of the test, the type of bootstrap interval or how the five seeds are combined. Those choices were fixed in `../V2_ROBUSTNESS_STUDY/robustness_analyze.py`; the earliest dated copy of that script is from 19 October 2026, when 80 of the 90 runs were complete, so it cannot be shown that they were made before results were available.

We therefore describe this analysis as a **protocol-specified primary analysis (not fully prespecified)**.

| Status | Analysis | Result |
|---|---|---|
| Protocol-specified primary analysis (not fully prespecified) | Wilcoxon signed-rank test on participant differences (mean over seeds) | W = 5, exact p = 0.039 |
| Protocol-specified primary analysis (not fully prespecified) | Rank-biserial correlation | 0.78 |
| Protocol-specified primary analysis (not fully prespecified) | Percentile bootstrap 95% interval of the mean difference | 1.27 to 6.35 points |
| Post hoc sensitivity | BCa bootstrap interval | 1.2 to 6.2 |
| Post hoc sensitivity | Two-stage bootstrap (participants, then seeds) | 1.07 to 6.65 |
| Post hoc sensitivity | t-interval; paired t-test; Cohen's d_z | 0.67 to 7.00; p = 0.024; 0.93 |
| Post hoc sensitivity | Hodges–Lehmann estimate; exact interval (96.1%) | 3.75; 0.67 to 7.36 |
| Post hoc sensitivity | Sign test; exact sign-flip permutation test | p = 0.039; p = 0.031 |
| Post hoc sensitivity | One participant omitted | p = 0.008 (P1 omitted); 0.055 to 0.078 (others) |
| Post hoc sensitivity | One seed omitted (42, 123, 2024, 3407, 7777) | p = 0.012, 0.039, 0.020, 0.055, 0.039 |
| Post hoc sensitivity | Each seed alone | p = 0.098, 0.129, 0.359, 0.004, 0.004 |
| Post hoc sensitivity | Median over seeds | 2.83 points; p = 0.055 |
| Post hoc, descriptive | Variance of seed-level differences | SD between seeds within a participant 4.23; SD between participants 3.66; intraclass correlation 0.43 |
| Exploratory | Macro-F1 difference | +0.039; p = 0.027 |
| Exploratory | Balanced accuracy difference | +3.7 points; p = 0.020 |

## Statistical limitations (preserved from manuscript v2.1)

- **Power and sample size:** The unit of analysis is the participant (N = 9). A paired t-test at two-sided alpha = 0.05 has 80% power only for standardised differences d_z >= 1.07, so the study was powered only for large effects.
- **Sensitivity:** Omitting any one of the eight participants who favoured RM shifts the two-sided p-value above 0.05 (p = 0.055 to 0.078). Seed-level analysis shows that only two of five seeds alone reach p < 0.05, and aggregating by the median over seeds yields p = 0.055.
- **Confounded mechanisms:** Resampling raw sEMG via cubic interpolation without anti-aliasing filtering confounds rate matching with aliasing and receptive-field duration (189 ms in RM vs 22.2 ms in NR). The design does not isolate an underlying physiological or filtering mechanism.
- **Non-independent folds:** Leave-one-participant-out cross-validation folds share seven of their eight training participants. Because observations are not strictly independent, p-values and confidence intervals must be interpreted as approximate.
- **Multiplicity:** No analysis was corrected for multiplicity. The post hoc analyses are not independent tests; they evaluate how far the outcome depends on analytical choices, individual participants, and individual seeds.
