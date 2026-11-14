# V2: rate-matched versus native-rate sEMG in dual-branch EMG–IMU fusion

This folder holds the code, the protocol and the frozen outputs of a 90-run study on the public SDALLE dataset. It is version 2.0.0 of this repository. Version 1.0.0, at the repository root, is a different study and is not changed by this folder.

## Question

Surface EMG (sEMG) and inertial sensors are sampled at very different rates (1259.26 Hz and 148.15 Hz in SDALLE). Fusion pipelines often resample sEMG to the inertial rate. Does that choice change participant-independent recognition of lower-limb activities when the network is held constant?

## Design

| Item | Value |
|---|---|
| Data | SDALLE, 9 healthy male participants aged 12–39 years, 361 trials; walking, jogging, stair ascent, stair descent |
| Signals | 8 thigh sEMG channels (1259.26 Hz), 48 inertial channels (148.15 Hz) |
| Condition RM (`E3-D` in file names) | Raw sEMG cubic-interpolated to the inertial time base, no anti-aliasing filter; sEMG input 8 × 148 |
| Condition NR (`E4` in file names) | sEMG kept at its native rate; sEMG input 8 × 1259 |
| Network | The same dual-branch 1D convolutional network for both conditions, 330,052 parameters |
| Windows | Nominally 1.0 s, stride 0.5 s, within trials; per-channel z-score from the training participants only |
| Training | Adam, learning rate 1e-3, weight decay 1e-4, cosine schedule, 50 epochs, batch 64; no validation set, no early stopping, no tuning |
| Evaluation | Leave-one-participant-out (9 folds) × 5 seeds (42, 123, 2024, 3407, 7777) × 2 conditions = 90 runs |
| Unit of analysis | The participant (N = 9); accuracy averaged over the five seeds |

## Main result

| Quantity | RM | NR |
|---|---|---|
| Accuracy, mean (SD) over 9 participants | 72.90% (9.24) | 69.07% (10.80) |
| Macro-F1, mean (SD) | 0.710 (0.097) | 0.671 (0.110) |
| Median training time per run | 1525 s | 6621 s |

Paired difference in accuracy (RM − NR): +3.83 percentage points; higher with RM in 8 of 9 participants; exact two-sided Wilcoxon signed-rank test W = 5, p = 0.039; matched-pairs rank-biserial correlation 0.78; 95% percentile bootstrap interval 1.27 to 6.35 points.

This primary outcome represents a **protocol-specified primary analysis (not fully prespecified)**, because four execution details (exact null distribution of the signed-rank statistic, percentile form of the bootstrap interval, seed averaging, and reference significance level of 0.05) were fixed in the analysis script rather than in the protocol text itself.

**Read this result with its limits (preserved from manuscript v2.1).** The evidence is suggestive, not firm:
- **Sample size and power:** The sample size was fixed by the public dataset (N = 9 healthy male participants); a paired t-test at two-sided alpha = 0.05 has 80% power only for large effect sizes (Cohen's d_z >= 1.07), so the design could detect only large effects.
- **Participant sensitivity:** Post hoc sensitivity analyses give p between 0.055 and 0.078 when any single one of the eight participants who favoured RM is left out (e.g., p = 0.055 omitting P3, p = 0.078 omitting P6).
- **Seed sensitivity:** Only 2 of the 5 seeds alone yield p < 0.05 (seeds 3407 and 7777, both p = 0.004; seeds 42, 123, 2024 have p = 0.098, 0.129, 0.359). Aggregating by the median over seeds gives +2.83 points, p = 0.055.
- **Confounded mechanisms:** The two conditions differ both in sEMG input length and in the duration of the convolutional receptive field (189 ms in RM against 22.2 ms in NR), and the resampling was unfiltered cubic interpolation, so the design does not isolate an underlying biological or filtering mechanism.
- **Cross-validation structure:** Leave-one-participant-out folds share seven of their eight training participants, so the nine paired differences are not strictly independent and p-values and confidence intervals must be read as approximate.
- **Multiplicity:** Sensitivity and exploratory analyses were not adjusted for multiplicity; they describe the robustness of a single result rather than independent tests.
- **Scope:** The study does not show equivalence or non-inferiority, and it does not show that rate matching is better in general. The full list of analyses and their status is in `verification/README.md`.

## The Three Zenodo Archives and GitHub Repository Tree

The study is archived and version-controlled across distinct components:

### The Three Zenodo Archives (Option A Deposition)
Zenodo deposition under Concept DOI [10.5281/zenodo.22649504](https://doi.org/10.5281/zenodo.22649504) contains exactly three prepared archives:
1. **Primary archive (`v2_release_candidate_final.zip`, 305 files, 1.95 MB):** Internal protocol, training and analysis code, per-window predictions (`predictions.csv`), run records (`meta.json`), training curves (`history.json`) for all 90 runs, and canonical result tables and figures.
2. **Reproducibility archive (`v2_reproducibility_data_final.zip`, 18 files, 2.38 GB):** 18 preprocessed input arrays (9 LOPO folds × 2 conditions) enabling direct retraining and array-level auditing without downloading the raw SDALLE files.
3. **Verification archive (`v2_verification_audit.zip`, 23 files, 68 kB):** Independent verification scripts, statistical outputs, spectral analysis of all 361 raw trials, array content digests, and scientific discrepancy register.

### The GitHub Repository Tree
The GitHub release `v2.0.0` at [https://github.com/SaqibAhmadBhat/subject-independent-emg-imu-fusion](https://github.com/SaqibAhmadBhat/subject-independent-emg-imu-fusion) maintains the complete version-controlled study tree (`v2_rate_matching_study/`, 321 files), including preprocessing source modules (`src/`, `V2/src/`) that rebuild the input arrays bit-identically from raw SDALLE files. GitHub automatically generates source code archives for release assets; do not confuse these with the three Zenodo archives.

## Contents of this folder

The folder mirrors the layout of the authors' workspace, so the study's scripts run without modification.

| Path | Content |
|---|---|
| `V2_ROBUSTNESS_STUDY/protocol.md` | Internal protocol, written before the 90 runs (not publicly registered) |
| `V2_ROBUSTNESS_STUDY/robustness_train.py`, `robustness_analyze.py`, `robustness_report.py`, `run_study.sh` | Training and analysis code |
| `V2_ROBUSTNESS_STUDY/src/` | Model definitions |
| `V2_ROBUSTNESS_STUDY/seed_<seed>/<condition>/fold_<k>/` | `predictions.csv` (one row per test window), `meta.json` (run record), `history.json` (training curve) for each of the 90 runs |
| `V2_ROBUSTNESS_STUDY/analysis/tables/` | Result tables written by the study's analysis scripts |
| `V2_ROBUSTNESS_STUDY/analysis/scripts/` | The study's two validation scripts |
| `V2_ROBUSTNESS_STUDY/requirements.txt` | Package versions used for training |
| `src/`, `V2/src/` | Preprocessing modules that build the input arrays from the raw SDALLE files (see `PREPROCESSING.md`) |
| `verification/` | Scripts that recompute every reported statistic from the predictions, audit arrays, and verify spectral properties |
| `provenance/` | The training script as it stood on 19 October 2026, when 80 of the 90 runs were complete |
| `MANIFEST.md`, `SHA256SUMS` | Origin and checksum of every file in this folder |
| `REPRODUCE.md` | How to verify, regenerate and retrain |

Fold *k* holds out participant *k*. Class labels: 0 jogging, 1 stair descent, 2 stair ascent, 3 walking.

## Quick check

Requires Python 3 with NumPy and SciPy. From this folder:

```bash
sha256sum -c SHA256SUMS      # on macOS: shasum -a 256 -c SHA256SUMS
python3 verification/audit_90_runs.py V2_ROBUSTNESS_STUDY audit.json
python3 verification/verify_v2_statistics.py --v2-root V2_ROBUSTNESS_STUDY --out statistics.json
```

The first command checks the files. The second checks the 90 runs for completeness and internal consistency. The third recomputes the main result from the per-window predictions.

## What is not included

- **The SDALLE dataset.** Obtain it from https://doi.org/10.5281/zenodo.14841611 (CC BY 4.0) and cite its authors.
- **The processed input arrays** (18 files, 2.38 GB). Provided in the separate reproducibility archive (`v2_reproducibility_data_final.zip`) and regenerable bit-identically from the raw files with the included preprocessing modules (see `PREPROCESSING.md` and `REPRODUCE.md`).
- **Frozen model checkpoint weights (`.pt`).** Trained network weights (90 files, ~117 MB total) are **not included in any public release component** (neither in the primary archive, nor in the reproducibility archive, nor in the verification archive, nor in the GitHub repository tree). They are preserved offline and available from the authors upon request. As detailed in `REPRODUCE.md`, **stored prediction reproducibility** (Level 1) allows full independent verification of all reported statistics from frozen predictions without checkpoints or GPU compute; **retraining reproducibility** (Level 3) reproduces the scientific findings within expected seed/fold variation; **exact checkpoint reproduction** across different hardware and PyTorch builds is subject to platform-dependent floating-point non-determinism.

## Notes on the records

- The runs were executed sequentially. Eighty were completed between 8 and 15 October 2026. After an interruption, the last ten (RM fold 9 and NR folds 1–9, seed 7777) were completed on 6 and 7 November 2026, after the input arrays had been regenerated. Regenerating the arrays again reproduced the stored arrays exactly, and leaving out seed 7777 gives a similar result (+3.49 points, p = 0.039).
- Some runs were interrupted by suspension of the computer, so the wall-clock times in `meta.json` are not benchmarks.
- `robustness_report.py` writes a text report. Its wording predates the final analysis; the statistics in `verification/` are the reference.
- **Code versions.** The files in `V2_ROBUSTNESS_STUDY/` are the final versions of 12 November 2026, after the runs. The training script of 19 October 2026 (80 runs complete) is in `provenance/`; the final version differs from it by a guard against overwriting a finished run, by resume logic and by bookkeeping of fold numbers, and the functions that load the data, set the seeds, train a fold and compute the metrics are otherwise identical. During training the network classes were imported from `src/models.py` at the repository root (unchanged since tag `v1.0.0`). `V2_ROBUSTNESS_STUDY/src/models.py` is a self-contained copy made after the runs; its class definitions are identical and only its comments and model factory differ.
- The training and analysis code was written with the assistance of an AI coding agent, and the verification scripts with the assistance of a second AI tool. The authors ran the experiments and checked the results.

## Licence and citation

- **Software code:** MIT License (`LICENSE`).
- **Documentation, figures, result tables, and derived outputs:** Creative Commons Attribution 4.0 International (CC-BY 4.0) where rights permit (preserving upstream SDALLE CC-BY 4.0 attribution).
- **Citation:** To cite, use `CITATION.cff` at the repository root and the Concept DOI [10.5281/zenodo.22649504](https://doi.org/10.5281/zenodo.22649504). Please also cite the SDALLE dataset.
