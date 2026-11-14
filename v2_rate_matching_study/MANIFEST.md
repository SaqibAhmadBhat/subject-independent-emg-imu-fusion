# Manifest of `v2_rate_matching_study/`

Files: 319 (of which 270 are outputs of the 90 runs). Full checksums are in `SHA256SUMS`.

## Origins

- **frozen archive**: byte-identical to the member of the same name in the authors' frozen archive `v2_release_candidate_final.zip` (SHA-256 `787ff47226c4c237a8110fbe35bb085c316642a3743750a2e599265748bd46a0`), made on 13 November 2026.
- **authors' workspace (preprocessing module)**: byte-identical to the module that built the input arrays.
- **authors' backup of 19 October 2026**: byte-identical to the file in that backup.
- **verification script / verification output**: written in November 2026 to check the study independently of its own analysis code.
- **release documentation**: written for version 2.0.0.

## Members of the frozen archive that are not in this release

| Member | Reason |
|---|---|
| `CITATION.cff` | replaced by CITATION.cff at the repository root (placeholders in the archived file) |
| `README.md` | replaced by new documentation (placeholders in the archived file) |
| `REPRODUCE.md` | replaced by new documentation |
| `analysis/figures/fig1_paired_accuracy.pdf` | figure of the earlier analysis, superseded; two of the five contain known labelling errors |
| `analysis/figures/fig1_paired_accuracy.png` | figure of the earlier analysis, superseded; two of the five contain known labelling errors |
| `analysis/figures/fig2_paired_macro_f1.pdf` | figure of the earlier analysis, superseded; two of the five contain known labelling errors |
| `analysis/figures/fig2_paired_macro_f1.png` | figure of the earlier analysis, superseded; two of the five contain known labelling errors |
| `analysis/figures/fig3_receptive_field_gait.pdf` | figure of the earlier analysis, superseded; two of the five contain known labelling errors |
| `analysis/figures/fig3_receptive_field_gait.png` | figure of the earlier analysis, superseded; two of the five contain known labelling errors |
| `analysis/figures/fig4_seed_stability.pdf` | figure of the earlier analysis, superseded; two of the five contain known labelling errors |
| `analysis/figures/fig4_seed_stability.png` | figure of the earlier analysis, superseded; two of the five contain known labelling errors |
| `analysis/figures/fig5_per_class_sensitivity.pdf` | figure of the earlier analysis, superseded; two of the five contain known labelling errors |
| `analysis/figures/fig5_per_class_sensitivity.png` | figure of the earlier analysis, superseded; two of the five contain known labelling errors |
| `analysis/scripts/README.md` | describes files that are not in this release |
| `analysis/scripts/generate_phase3_17_figures.py` | draws the excluded figures |

## Files other than run outputs

| Path | Bytes | SHA-256 (first 16) | Origin |
|---|---|---|---|
| `.gitignore` | 106 | `ff329740a0d113e2` | release documentation |
| `LICENSE` | 1101 | `fadf84b33841eaba` | frozen archive |
| `PREPROCESSING.md` | 1694 | `c7ce10079963a98f` | release documentation |
| `README.md` | 11315 | `873b383462baee63` | release documentation |
| `REPRODUCE.md` | 6305 | `753548ba2f1db655` | release documentation |
| `V2/src/build_datasets_v2.py` | 3789 | `c9228803f3ddd159` | authors' workspace (preprocessing module) |
| `V2/src/windower_v2.py` | 2592 | `4bdcc5f1363ee3b5` | authors' workspace (preprocessing module) |
| `V2_ROBUSTNESS_STUDY/analysis/scripts/independent_source_validation.py` | 15614 | `c34fb09551622d46` | frozen archive |
| `V2_ROBUSTNESS_STUDY/analysis/scripts/validate_predictions_from_source.py` | 16494 | `9da9c0312ddba1f2` | frozen archive |
| `V2_ROBUSTNESS_STUDY/analysis/tables/accuracy_bootstrap_ci.json` | 645 | `1cbac74c4304c647` | frozen archive |
| `V2_ROBUSTNESS_STUDY/analysis/tables/accuracy_bootstrap_independent.json` | 645 | `1cbac74c4304c647` | frozen archive |
| `V2_ROBUSTNESS_STUDY/analysis/tables/canonical_participant_results.csv` | 1156 | `17aa4763250348e3` | frozen archive |
| `V2_ROBUSTNESS_STUDY/analysis/tables/canonical_v2_results.csv` | 32516 | `34f9740ff888b434` | frozen archive |
| `V2_ROBUSTNESS_STUDY/analysis/tables/prediction_validation_by_run.csv` | 28849 | `964eb7f8c24d1de2` | frozen archive |
| `V2_ROBUSTNESS_STUDY/analysis/tables/prediction_validation_independent.csv` | 22751 | `6360e3284e35eea1` | frozen archive |
| `V2_ROBUSTNESS_STUDY/analysis/tables/prediction_validation_summary.json` | 1589 | `d00b1381fae2e20a` | frozen archive |
| `V2_ROBUSTNESS_STUDY/analysis/tables/prediction_validation_summary_independent.json` | 918 | `25861b8d5638ee9c` | frozen archive |
| `V2_ROBUSTNESS_STUDY/analysis/tables/seed_stability_recalculated.csv` | 1418 | `32b26fd08507860b` | frozen archive |
| `V2_ROBUSTNESS_STUDY/protocol.md` | 7994 | `0559251410f35815` | frozen archive |
| `V2_ROBUSTNESS_STUDY/requirements.txt` | 687 | `0045232f900b5368` | frozen archive |
| `V2_ROBUSTNESS_STUDY/robustness_analyze.py` | 32098 | `da35213a7608abef` | frozen archive |
| `V2_ROBUSTNESS_STUDY/robustness_report.py` | 27194 | `2c74218778942412` | frozen archive |
| `V2_ROBUSTNESS_STUDY/robustness_train.py` | 23196 | `c1aa5a00eaa8b238` | frozen archive |
| `V2_ROBUSTNESS_STUDY/run_study.sh` | 3986 | `188182ec59d05040` | frozen archive |
| `V2_ROBUSTNESS_STUDY/src/models.py` | 5284 | `3df64b655702f4ec` | frozen archive |
| `V2_ROBUSTNESS_STUDY/src/models_v2.py` | 279 | `3244342aee446212` | frozen archive |
| `provenance/README.md` | 946 | `95a14a3d9b248cee` | release documentation |
| `provenance/robustness_train_2026-10-19.py` | 15146 | `ae2c00d4b21facaf` | authors' backup of 19 October 2026 |
| `src/dataset_loader.py` | 5619 | `06c107f784fc6c15` | authors' workspace (preprocessing module) |
| `src/normalizer.py` | 3063 | `f05b4424ff7e4926` | authors' workspace (preprocessing module) |
| `src/windower.py` | 5518 | `30097fa171475a49` | authors' workspace (preprocessing module) |
| `verification/README.md` | 7856 | `65ee85ce23dfa391` | release documentation |
| `verification/array_content_digests.py` | 928 | `05277b42fae1c5b4` | verification script |
| `verification/audit_90_runs.py` | 4908 | `8481758c9273c6c3` | verification script |
| `verification/audit_processed_arrays.py` | 3131 | `8c70b681698bf04d` | verification script |
| `verification/emg_spectrum_check.py` | 2257 | `c104948bd75b49bd` | verification script |
| `verification/outputs/additional_statistics_output.json` | 1880 | `03d22619e7bbd9ae` | verification output |
| `verification/outputs/audit_90_runs_output.json` | 678 | `eab78de5b1e6b5a0` | verification output |
| `verification/outputs/audit_processed_arrays_output.json` | 10407 | `9261522dbbd49971` | verification output |
| `verification/outputs/emg_spectrum_check_all_trials.json` | 101812 | `32bc57809fe495cc` | verification output |
| `verification/outputs/preliminary_single_seed_runs.json` | 2569 | `d0065583d10b92fa` | verification output |
| `verification/outputs/processed_array_content_digests.json` | 18236 | `d0dcab448f8d9b89` | verification output |
| `verification/outputs/regeneration_check_output.json` | 16438 | `5a2d321ac8ffa308` | verification output |
| `verification/outputs/sensitivity_analysis_output.json` | 3736 | `4133c934fd815fd5` | verification output |
| `verification/outputs/statistical_verification_output.json` | 5456 | `bcac6d5737a72f32` | verification output |
| `verification/regenerate_arrays_check.py` | 2968 | `ff6be9e1fa0dfaed` | verification script |
| `verification/verify_v2_additional_stats.py` | 3601 | `34fb57a85294780e` | verification script |
| `verification/verify_v2_sensitivity.py` | 5046 | `1c56391624f0bf55` | verification script |
| `verification/verify_v2_statistics.py` | 6700 | `9aeddec3f5f9b7ff` | verification script |

## Run outputs

`V2_ROBUSTNESS_STUDY/seed_<seed>/<condition>/fold_<k>/{predictions.csv, meta.json, history.json}` for seeds 42, 123, 2024, 3407, 7777, conditions `E3-D` and `E4`, folds 1 to 9: 270 files, all from the frozen archive.
