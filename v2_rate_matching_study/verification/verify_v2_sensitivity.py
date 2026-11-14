"""Sensitivity and descriptive analyses for the V2 manuscript, from frozen outputs only (read-only).
Usage: python3 verify_v2_sensitivity.py --v2-root <path> --spectrum <json> --out <json>"""
import argparse, csv, itertools, json
from pathlib import Path
import numpy as np
from scipy import stats

SEEDS = [42, 123, 2024, 3407, 7777]; ARMS = ["E3-D", "E4"]

def wil(d):
    d = np.asarray(d, float); r = stats.rankdata(np.abs(d)); wp, wm = r[d > 0].sum(), r[d < 0].sum(); w = min(wp, wm); n = len(d)
    cnt = sum(1 for g in itertools.product([0, 1], repeat=n) if min(sum(r[i] for i in range(n) if g[i]), r.sum() - sum(r[i] for i in range(n) if g[i])) <= w)
    return dict(W=float(w), p=cnt / 2 ** n, n_pos=int((d > 0).sum()))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--v2-root", required=True); ap.add_argument("--spectrum", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(); root = Path(a.v2_root)
    acc = {m: np.zeros((5, 9)) for m in ARMS}; bal = {m: np.zeros((5, 9)) for m in ARMS}
    ftr = {m: [] for m in ARMS}; ftl = {m: [] for m in ARMS}; tt = {m: [] for m in ARMS}; ti = {m: [] for m in ARMS}
    class_counts = np.zeros(4, int)
    for si, s in enumerate(SEEDS):
        for m in ARMS:
            for k in range(1, 10):
                d = root / f"seed_{s}" / m / f"fold_{k}"
                rows = list(csv.DictReader(open(d / "predictions.csv", newline="")))
                y = np.array([int(r["true_label"]) for r in rows]); p = np.array([int(r["pred_label"]) for r in rows])
                acc[m][si, k - 1] = np.mean(y == p) * 100
                bal[m][si, k - 1] = np.mean([np.mean(p[y == c] == c) for c in range(4)]) * 100
                if s == 42 and m == "E4": class_counts += np.bincount(y, minlength=4)
                h = json.load(open(d / "history.json")); ftr[m].append(h["train_acc"][-1] * 100); ftl[m].append(h["train_loss"][-1])
                mt = json.load(open(d / "meta.json")); tt[m].append(mt["train_time_s"]); ti[m].append(mt["inf_time_s"])
    e3, e4 = acc["E3-D"].mean(0), acc["E4"].mean(0); d = e3 - e4; n = 9
    se = d.std(ddof=1) / np.sqrt(n); tcrit = stats.t.ppf(0.975, n - 1)
    walsh = np.sort([(d[i] + d[j]) / 2 for i in range(n) for j in range(i, n)])
    # exact null distribution of W+ for n=9 (no ties)
    cdf = lambda c: sum(1 for g in itertools.product([0, 1], repeat=n) if sum((i + 1) for i in range(n) if g[i]) <= c) / 2 ** n
    C = max(c for c in range(0, 23) if 2 * cdf(c) <= 0.05) + 1
    per_seed = {str(s): dict(wil(acc["E3-D"][i] - acc["E4"][i]), mean_diff=float((acc["E3-D"][i] - acc["E4"][i]).mean())) for i, s in enumerate(SEEDS)}
    med = np.median(acc["E3-D"], 0) - np.median(acc["E4"], 0)
    b3, b4 = bal["E3-D"].mean(0), bal["E4"].mean(0)
    spec = json.load(open(a.spectrum)); hf = np.array([np.mean([x["frac_above_74"] for x in spec if x["subject"] == s]) for s in range(1, 10)]) * 100
    rho = stats.spearmanr(hf, d)
    loo = {f"without_P{i+1}": dict(mean_diff=float(np.delete(d, i).mean()), p=wil(np.delete(d, i))["p"]) for i in range(n)}
    out = dict(
        t_interval_95=[float(d.mean() - tcrit * se), float(d.mean() + tcrit * se)],
        hodges_lehmann=dict(estimate=float(np.median(walsh)), ci=[float(walsh[C - 1]), float(walsh[len(walsh) - C])], coverage=float(1 - 2 * cdf(C - 1)), C=int(C)),
        per_seed_wilcoxon=per_seed,
        median_over_seeds=dict(diff=med.tolist(), mean=float(med.mean()), **wil(med)),
        balanced_accuracy={"E3-D": dict(mean=float(b3.mean()), sd=float(b3.std(ddof=1))), "E4": dict(mean=float(b4.mean()), sd=float(b4.std(ddof=1))),
                           "diff_mean": float((b3 - b4).mean()), **{"wilcoxon_" + k: v for k, v in wil(b3 - b4).items()}},
        class_counts_per_seed=dict(jogging=int(class_counts[0]), stairs_down=int(class_counts[1]), stairs_up=int(class_counts[2]), walking=int(class_counts[3]), total=int(class_counts.sum()), majority_share_pct=float(class_counts.max() / class_counts.sum() * 100)),
        final_epoch_training={m: dict(acc_mean=float(np.mean(ftr[m])), acc_sd=float(np.std(ftr[m], ddof=1)), acc_min=float(np.min(ftr[m])), loss_mean=float(np.mean(ftl[m]))) for m in ARMS},
        runtime={m: dict(train_min=float(np.min(tt[m])), train_median=float(np.median(tt[m])), train_q1=float(np.percentile(tt[m], 25)), train_q3=float(np.percentile(tt[m], 75)), infer_min=float(np.min(ti[m])), infer_median=float(np.median(ti[m]))) for m in ARMS},
        seed_range_within_participant={m: dict(median=float(np.median(acc[m].max(0) - acc[m].min(0))), max=float((acc[m].max(0) - acc[m].min(0)).max())) for m in ARMS},
        lowest_runs={m: sorted([(float(acc[m][i, k]), SEEDS[i], k + 1) for i in range(5) for k in range(9)])[:3] for m in ARMS},
        hf_fraction_pct_by_participant=hf.tolist(), spearman_hf_vs_diff=dict(rho=float(rho.statistic), p=float(rho.pvalue)),
        leave_one_out=loo)
    json.dump(out, open(a.out, "w"), indent=1); print(json.dumps(out, indent=0)[:4000])

if __name__ == "__main__":
    main()
