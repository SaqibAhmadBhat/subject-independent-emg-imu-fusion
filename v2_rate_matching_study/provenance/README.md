# Provenance copy of the training script

`robustness_train_2026-10-19.py` is the training script as stored in the authors' backup of 19 October 2026, when 80 of the 90 runs had been completed. The final version, `../V2_ROBUSTNESS_STUDY/robustness_train.py`, is dated 12 November 2026, after all runs.

Function-level comparison of the two versions (documentation strings ignored):

| Function | Difference |
|---|---|
| `set_seed`, `load_fold`, `compute_metrics`, `_confusion_matrix`, `_per_class_metrics` | Identical |
| `train_one_fold` | One addition: a guard that refuses to overwrite an existing `model.pt` |
| `evaluate_seed` | Fold numbers in the summary are taken from the run records |
| `main` | Resume logic added |
| `check_fold_status` | New (used by the resume logic) |
| Import path | The `src/` folder of the study is added |

No copy of the script as it stood on 6 and 7 November 2026, when the last ten runs were made, exists.
