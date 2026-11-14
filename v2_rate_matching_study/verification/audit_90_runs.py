"""Integrity audit of the 90 frozen run outputs (read-only). Usage: python3 audit_90_runs.py <V2_ROOT> <out.json>
model.pt files are optional (they are not part of the public release); if present they must be present for all runs.
Execution order and dates are taken from file times and are meaningful only for the original run records."""
import csv, hashlib, json, os, sys
from pathlib import Path
import numpy as np
root = Path(sys.argv[1]); out = sys.argv[2]
SEEDS = [42, 123, 2024, 3407, 7777]; ARMS = ["E3-D", "E4"]; NAMES = {0: "jogging", 1: "stairs_down", 2: "stairs_up", 3: "walking"}
EXP_N = [647, 568, 729, 696, 746, 722, 654, 690, 751]
issues = []; runs = []; lab_hash = {}; pred_hash = {}; hp_set = set(); mt = []
for s in SEEDS:
    for a in ARMS:
        for k in range(1, 10):
            d = root / f"seed_{s}" / a / f"fold_{k}"; tag = f"seed {s} {a} fold {k}"
            for f in ["predictions.csv", "meta.json", "history.json"]:
                if not (d / f).exists(): issues.append(f"{tag}: missing {f}")
            rows = list(csv.DictReader(open(d / "predictions.csv", newline="")))
            y = np.array([int(r["true_label"]) for r in rows]); p = np.array([int(r["pred_label"]) for r in rows])
            if [int(r["window_index"]) for r in rows] != list(range(len(rows))): issues.append(f"{tag}: window_index not sequential")
            if any(r["experiment"] != a or int(r["fold"]) != k or int(r["seed"]) != s for r in rows): issues.append(f"{tag}: identifier columns inconsistent")
            if any(int(r["correct"]) != int(r["true_label"] == r["pred_label"]) for r in rows): issues.append(f"{tag}: 'correct' column wrong")
            if any(NAMES[int(r["true_label"])] != r["true_name"] or NAMES[int(r["pred_label"])] != r["pred_name"] for r in rows): issues.append(f"{tag}: label names inconsistent")
            if y.min() < 0 or y.max() > 3 or p.min() < 0 or p.max() > 3: issues.append(f"{tag}: label out of range")
            if len(y) != EXP_N[k - 1]: issues.append(f"{tag}: {len(y)} windows, expected {EXP_N[k-1]}")
            lab_hash.setdefault(k, set()).add(hashlib.sha256(y.tobytes()).hexdigest())
            pred_hash.setdefault(k, []).append(hashlib.sha256(p.tobytes()).hexdigest())
            m = json.load(open(d / "meta.json")); h = json.load(open(d / "history.json"))
            cm = np.zeros((4, 4), int)
            for t, q in zip(y, p): cm[t, q] += 1
            if m["experiment"] != a or m["fold"] != k or m["seed"] != s: issues.append(f"{tag}: meta identifiers")
            if m["n_params"] != 330052 or m["epochs"] != 50: issues.append(f"{tag}: n_params/epochs")
            if abs(m["metrics"]["accuracy"] - np.mean(y == p)) > 1e-6: issues.append(f"{tag}: meta accuracy differs")
            if not np.array_equal(np.array(m["metrics"]["confusion_matrix"]), cm): issues.append(f"{tag}: confusion matrix differs")
            if len(h["train_loss"]) != 50 or len(h["train_acc"]) != 50 or not np.all(np.isfinite(h["train_loss"])): issues.append(f"{tag}: history length/finite")
            hp_set.add(json.dumps(m["hp"], sort_keys=True))
            mt.append((os.path.getmtime(d / "meta.json"), s, a, k, os.path.getsize(d / "model.pt") if (d / "model.pt").exists() else None))
            runs.append(dict(seed=s, arm=a, fold=k, n=len(y), acc=float(np.mean(y == p)), agree=None))
for k in range(1, 10):
    if len(lab_hash[k]) != 1: issues.append(f"fold {k}: true-label sequences differ across runs")
    if len(set(pred_hash[k])) != len(pred_hash[k]): issues.append(f"fold {k}: two runs have identical predictions")
# agreement between conditions per (seed, fold)
agree = []
for s in SEEDS:
    for k in range(1, 10):
        P = {}
        for a in ARMS:
            rows = list(csv.DictReader(open(root / f"seed_{s}" / a / f"fold_{k}" / "predictions.csv", newline="")))
            P[a] = np.array([int(r["pred_label"]) for r in rows])
        agree.append(float(np.mean(P["E3-D"] == P["E4"])))
n_models = sum(x[4] is not None for x in mt)
if 0 < n_models < len(mt): issues.append(f"model.pt present for only {n_models} of {len(mt)} runs")
mt.sort(key=lambda x: x[:4]); order = [(a, s, k) for _, s, a, k, _ in mt]
blocks = [order[0][:2]]
for o in order[1:]:
    if o[:2] != blocks[-1]: blocks.append(o[:2])
res = dict(n_runs=len(runs), issues=issues, distinct_hyperparameter_sets=len(hp_set), hyperparameters=json.loads(next(iter(hp_set))),
           model_files_present=n_models, model_file_sizes=sorted({x[4] for x in mt if x[4] is not None}), between_condition_prediction_agreement=dict(mean=float(np.mean(agree)), min=float(np.min(agree)), max=float(np.max(agree))),
           execution_order_blocks=[f"{a} seed {s}" for a, s in blocks],
           first_run=str(np.datetime64(int(mt[0][0]), "s")), last_run=str(np.datetime64(int(mt[-1][0]), "s")))
json.dump(res, open(out, "w"), indent=1); print(json.dumps(res, indent=0)[:1800])
