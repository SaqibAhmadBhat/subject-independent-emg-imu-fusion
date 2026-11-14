"""Regenerate the processed arrays from the raw SDALLE files with the study's preprocessing modules and compare
them with the stored arrays that the 90 runs used. Nothing is written to the research project.
Usage: python3 regenerate_arrays_check.py <PIPELINE_DIR> <RAW_SDALLE_DIR> <PROCESSED_DIR> <out.json> [folds, e.g. 1,5,9]
PIPELINE_DIR holds copies of dataset_loader.py, windower.py, normalizer.py and windower_v2.py.
Set TRIALS_CACHE to a pickle of the parsed trials to avoid re-reading the 361 CSV files on every call."""
import json, os, sys, hashlib
from pathlib import Path
import numpy as np
sys.dont_write_bytecode = True
pipe, raw, proc, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4]
folds = [int(v) for v in sys.argv[5].split(",")] if len(sys.argv) > 5 else list(range(1, 10))
sys.path.insert(0, pipe)
import dataset_loader
from normalizer import normalize_dual_branch
from windower import window_e4
from windower_v2 import window_e3d
import scipy

res = json.load(open(out)) if os.path.exists(out) else {}
res["environment"] = dict(numpy=np.__version__, scipy=scipy.__version__, python=sys.version.split()[0])
cache = os.environ.get("TRIALS_CACHE")          # optional pickle of the parsed trials, to split a long job into steps
if cache and os.path.exists(cache):
    import pickle
    trials = pickle.load(open(cache, "rb"))
else:
    trials = dataset_loader.load_all_trials(raw)
subjects = sorted(set(t.subject_id for t in trials))
res["n_trials"], res["subjects"] = len(trials), [str(s) for s in subjects]
for k in folds:
    sid = subjects[k - 1]
    tr = [t for t in trials if t.subject_id != sid]; te = [t for t in trials if t.subject_id == sid]
    for arm, fn in (("E3-D", window_e3d), ("E4", window_e4)):
        Xe_tr, Xi_tr, y_tr, _ = fn(tr); Xe_te, Xi_te, y_te, _ = fn(te)
        Xe_tr, Xe_te, Xi_tr, Xi_te, _, _ = normalize_dual_branch(Xe_tr, Xe_te, Xi_tr, Xi_te)
        new = {"X_emg_train": Xe_tr, "X_imu_train": Xi_tr, "y_train": y_tr, "X_emg_test": Xe_te, "X_imu_test": Xi_te, "y_test": y_te}
        old = np.load(proc / arm / f"dataset_fold_{k}.npz")
        r = {}
        for key, a in new.items():
            b = old[key]
            same_shape = a.shape == b.shape
            r[key] = dict(shape_equal=bool(same_shape), dtype_new=str(a.dtype), dtype_stored=str(b.dtype),
                          identical=bool(same_shape and np.array_equal(a, b)),
                          max_abs_diff=float(np.max(np.abs(a.astype(np.float64) - b.astype(np.float64)))) if same_shape else None)
        res[f"fold{k}_{arm}"] = r
        del new, old, Xe_tr, Xe_te, Xi_tr, Xi_te
        json.dump(res, open(out, "w"), indent=1)
res["all_identical"] = all(v[key]["identical"] for f, v in res.items() if f.startswith("fold") for key in v)
res["max_abs_diff_overall"] = max(v[key]["max_abs_diff"] or 0 for f, v in res.items() if f.startswith("fold") for key in v)
json.dump(res, open(out, "w"), indent=1); print("done")
