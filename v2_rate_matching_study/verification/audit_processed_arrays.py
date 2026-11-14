"""Leakage and consistency audit of the processed arrays used for training (read-only).
Usage: python3 audit_processed_arrays.py <PROCESSED_DIR> <V2_ROOT> <out.json>"""
import csv, hashlib, json, sys
from pathlib import Path
import numpy as np
proc, root, out = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
FOLDS = [int(v) for v in sys.argv[4].split(",")] if len(sys.argv) > 4 else list(range(1, 10))
import os
EXP_N = [647, 568, 729, 696, 746, 722, 654, 690, 751]; TOTAL = 6203
def hset(a): return {hashlib.blake2b(np.ascontiguousarray(x).tobytes(), digest_size=12).digest() for x in a}
res = json.load(open(out)) if os.path.exists(out) else {}; imu_hash = {}
for k in FOLDS:
    for arm in ["E3-D", "E4"]:
        z = np.load(proc / arm / f"dataset_fold_{k}.npz", allow_pickle=False)
        Xi_tr, Xi_te, Xe_tr, Xe_te, y_tr, y_te = z["X_imu_train"], z["X_imu_test"], z["X_emg_train"], z["X_emg_test"], z["y_train"], z["y_test"]
        rows = list(csv.DictReader(open(root / "seed_42" / arm / f"fold_{k}" / "predictions.csv", newline="")))
        y_pred_file = np.array([int(r["true_label"]) for r in rows])
        half = Xi_tr.shape[1] // 2
        tr_halves = hset(Xi_tr[:, :half]) | hset(Xi_tr[:, half:2 * half]); te_halves = hset(Xi_te[:, :half]) | hset(Xi_te[:, half:2 * half])
        chained = float(np.mean([np.array_equal(Xi_te[i, half:2 * half], Xi_te[i + 1, :half]) for i in range(len(Xi_te) - 1)]))
        r = dict(n_train=int(len(y_tr)), n_test=int(len(y_te)), counts_ok=bool(len(y_tr) + len(y_te) == TOTAL and len(y_te) == EXP_N[k - 1]),
                 labels_match_predictions=bool(np.array_equal(y_te, y_pred_file)),
                 emg_shape=list(Xe_tr.shape[1:]), imu_shape=list(Xi_tr.shape[1:]),
                 shared_imu_half_windows_train_test=len(tr_halves & te_halves),
                 identical_emg_windows_train_test=len(hset(Xe_tr) & hset(Xe_te)),
                 test_consecutive_half_overlap_fraction=chained,
                 train_abs_mean_max=float(max(np.abs(Xi_tr.mean((0, 1))).max(), np.abs(Xe_tr.mean((0, 1))).max())),
                 train_std_dev_from_1_max=float(max(np.abs(Xi_tr.std((0, 1)) - 1).max(), np.abs(Xe_tr.std((0, 1)) - 1).max())),
                 test_abs_mean_max=float(max(np.abs(Xi_te.mean((0, 1))).max(), np.abs(Xe_te.mean((0, 1))).max())),
                 test_std_range=[float(min(Xi_te.std((0, 1)).min(), Xe_te.std((0, 1)).min())), float(max(Xi_te.std((0, 1)).max(), Xe_te.std((0, 1)).max()))],
                 any_nan=bool(np.isnan(Xi_tr).any() or np.isnan(Xe_tr).any() or np.isnan(Xi_te).any() or np.isnan(Xe_te).any()))
        imu_hash[(k, arm)] = (hashlib.sha256(Xi_tr.tobytes()).hexdigest(), hashlib.sha256(Xi_te.tobytes()).hexdigest(), hashlib.sha256(y_tr.tobytes()).hexdigest())
        res[f"fold{k}_{arm}"] = r
        json.dump(res, open(out, "w"), indent=1)
res.setdefault("imu_and_labels_identical_between_conditions", {}).update({f"fold{k}": bool(imu_hash[(k, "E3-D")] == imu_hash[(k, "E4")]) for k in FOLDS})
res["done"] = all(f"fold{k}_{a}" in res for k in range(1, 10) for a in ["E3-D", "E4"])
json.dump(res, open(out, "w"), indent=1)
