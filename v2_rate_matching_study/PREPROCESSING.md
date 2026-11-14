# Preprocessing modules

These five files are byte-for-byte copies of the modules that built the input arrays of the 90 runs. They keep their original relative locations.

| File | Role |
|---|---|
| `src/dataset_loader.py` | Reads the SDALLE trial files; nominal rates 1259.2593 Hz (sEMG) and 148.1481 Hz (inertial) |
| `src/windower.py` | 1.0 s windows with 0.5 s stride within trials; `window_e4` builds the native-rate condition (NR, `E4`) |
| `src/normalizer.py` | Per-channel z-score fitted on the training participants only, separately for sEMG and inertial channels |
| `V2/src/windower_v2.py` | `window_e3d` builds the rate-matched condition (RM, `E3-D`): per trial, cubic interpolation (`scipy.interpolate.interp1d(kind="cubic", fill_value="extrapolate")`) of each sEMG channel onto the inertial time axis, with no anti-aliasing filter |
| `V2/src/build_datasets_v2.py` | Builds `dataset_fold_<k>.npz` for each condition, with an assertion that the test participant is absent from the training set |

`src/windower.py` is the working copy used for this study. It differs from the file of the same name at the repository root (tag `v1.0.0`) in the function `window_e3`, which this study does not use. `src/dataset_loader.py` and `src/normalizer.py` are identical to the files at the repository root.

## Verified

On 14 November 2026 all 18 arrays (9 folds × 2 conditions) were rebuilt from the 361 raw trial files with these modules in a different environment (Python 3.10.12, NumPy 2.2.6, SciPy 1.15.3, Linux) and compared with the arrays the runs used. Every array was bit-identical. See `verification/outputs/regeneration_check_output.json`.

## Use

See `REPRODUCE.md`, level 2.
