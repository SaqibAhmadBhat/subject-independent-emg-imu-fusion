"""Independent recomputation of V2 results from the frozen per-run predictions.

Reads (read-only): <V2_ROOT>/seed_*/{E3-D,E4}/fold_*/{predictions.csv,meta.json}
                   <V2_ROOT>/analysis/tables/accuracy_bootstrap_ci.json
Writes: JSON summary to the path given by --out (inside the pm workspace).
Usage: python3 verify_v2_statistics.py --v2-root <path> --out <json>
"""
import argparse, csv, itertools, json
from pathlib import Path
import numpy as np
from scipy import stats

SEEDS = [42, 123, 2024, 3407, 7777]
ARMS = ["E3-D", "E4"]
CLASSES = ["jogging", "stairs_down", "stairs_up", "walking"]


def load(root):
    acc = {a: np.zeros((5, 9)) for a in ARMS}
    f1 = {a: np.zeros((5, 9)) for a in ARMS}
    cm = {a: np.zeros((4, 4), dtype=int) for a in ARMS}
    n_win = np.zeros(9, dtype=int)
    rt = {a: {"train": [], "infer": []} for a in ARMS}
    for si, s in enumerate(SEEDS):
        for a in ARMS:
            for k in range(1, 10):
                d = root / f"seed_{s}" / a / f"fold_{k}"
                rows = list(csv.DictReader(open(d / "predictions.csv", newline="")))
                y = np.array([int(r["true_label"]) for r in rows]); p = np.array([int(r["pred_label"]) for r in rows])
                n_win[k - 1] = len(y)
                acc[a][si, k - 1] = np.mean(y == p)
                c = np.zeros((4, 4), dtype=int)
                for t, q in zip(y, p): c[t, q] += 1
                cm[a] += c
                tp = np.diag(c); prec = np.divide(tp, c.sum(0), out=np.zeros(4), where=c.sum(0) > 0)
                rec = tp / c.sum(1); f = np.divide(2 * prec * rec, prec + rec, out=np.zeros(4), where=(prec + rec) > 0)
                f1[a][si, k - 1] = f.mean()
                m = json.load(open(d / "meta.json"))
                rt[a]["train"].append(m["train_time_s"]); rt[a]["infer"].append(m["inf_time_s"])
    return acc, f1, cm, n_win, rt


def wilcoxon_exact(d):
    r = stats.rankdata(np.abs(d)); wp, wm = r[d > 0].sum(), r[d < 0].sum(); w = min(wp, wm)
    cnt = sum(1 for g in itertools.product([0, 1], repeat=len(d)) if min(sum(r[i] for i in range(len(d)) if g[i]), r.sum() - sum(r[i] for i in range(len(d)) if g[i])) <= w)
    return dict(W=w, W_plus=wp, W_minus=wm, p_exact_two_sided=cnt / 2 ** len(d), rank_biserial=(wp - wm) / r.sum(), ranks_abs=r.tolist())


def bootstrap(d, B=10000, seed=42):
    rng = np.random.default_rng(seed); n = len(d); m = d.mean()
    bm = np.array([np.mean(rng.choice(d, size=n, replace=True)) for _ in range(B)])
    lo, hi = np.percentile(bm, [2.5, 97.5])
    z0 = stats.norm.ppf(np.mean(bm < m))
    jk = np.array([np.delete(d, i).mean() for i in range(n)]); jb = jk.mean()
    a = np.sum((jb - jk) ** 3) / (6 * np.sum((jb - jk) ** 2) ** 1.5)
    zl, zh = stats.norm.ppf(0.025), stats.norm.ppf(0.975)
    a1 = stats.norm.cdf(z0 + (z0 + zl) / (1 - a * (z0 + zl))); a2 = stats.norm.cdf(z0 + (z0 + zh) / (1 - a * (z0 + zh)))
    blo, bhi = np.percentile(bm, [a1 * 100, a2 * 100])
    return dict(percentile=[lo, hi], bca=[blo, bhi], z0=z0, a=a)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--v2-root", required=True); ap.add_argument("--out", required=True)
    args = ap.parse_args(); root = Path(args.v2_root)
    acc, f1, cm, n_win, rt = load(root)
    e3, e4 = acc["E3-D"].mean(0) * 100, acc["E4"].mean(0) * 100; d = e3 - e4
    q3, q4 = f1["E3-D"].mean(0), f1["E4"].mean(0); df = q3 - q4
    t = stats.ttest_rel(e3, e4); tf = stats.ttest_rel(q3, q4)
    sign_p = stats.binomtest(int((d > 0).sum()), 9, 0.5).pvalue
    loo = {f"without_P{i+1}": wilcoxon_exact(np.delete(d, i))["p_exact_two_sided"] for i in range(9)}
    seed_mean = {a: (acc[a].mean(1) * 100).tolist() for a in ARMS}
    stored = json.load(open(root / "analysis/tables/accuracy_bootstrap_ci.json"))
    boot = bootstrap(d)
    recall = {a: {c: cm[a][i, i] / cm[a][i].sum() for i, c in enumerate(CLASSES)} for a in ARMS}
    prec = {a: {c: cm[a][i, i] / cm[a][:, i].sum() for i, c in enumerate(CLASSES)} for a in ARMS}
    tr = {a: np.array(rt[a]["train"]) for a in ARMS}; inf = {a: np.array(rt[a]["infer"]) for a in ARMS}
    out = dict(
        test_windows_per_participant=n_win.tolist(), total_windows_per_seed=int(n_win.sum()),
        accuracy_pct={"E3-D": dict(mean=e3.mean(), sd=e3.std(ddof=1), per_participant=e3.tolist()),
                      "E4": dict(mean=e4.mean(), sd=e4.std(ddof=1), per_participant=e4.tolist())},
        paired_difference_pp=dict(per_participant=d.tolist(), mean=d.mean(), sd=d.std(ddof=1), median=float(np.median(d)),
                                  min=d.min(), max=d.max(), q1=float(np.percentile(d, 25)), q3=float(np.percentile(d, 75)),
                                  mean_abs=np.abs(d).mean(), n_positive=int((d > 0).sum())),
        wilcoxon=wilcoxon_exact(d), sign_test_p_two_sided=sign_p,
        wilcoxon_leave_one_participant_out_p=loo,
        paired_t=dict(t=t.statistic, df=8, p=t.pvalue, dz=d.mean() / d.std(ddof=1)),
        bootstrap_recomputed=boot,
        bootstrap_stored_json=dict(percentile=[stored["lower_exact"], stored["upper_exact"]],
                                   bca=[stored["bca_sensitivity_interval"]["lower_exact"], stored["bca_sensitivity_interval"]["upper_exact"]]),
        macro_f1={"E3-D": dict(mean=q3.mean(), sd=q3.std(ddof=1), per_participant=q3.tolist()),
                  "E4": dict(mean=q4.mean(), sd=q4.std(ddof=1), per_participant=q4.tolist()),
                  "diff_mean": df.mean(), "n_positive": int((df > 0).sum()), "paired_t": [tf.statistic, tf.pvalue],
                  "wilcoxon": wilcoxon_exact(df)},
        seed_cohort_mean_accuracy_pct=seed_mean,
        seed_delta_pp=(np.array(seed_mean["E3-D"]) - np.array(seed_mean["E4"])).tolist(),
        seed_sd_pp={a: float(np.std(seed_mean[a], ddof=1)) for a in ARMS},
        pooled_recall=recall, pooled_precision=prec,
        pooled_confusion_matrix={a: cm[a].tolist() for a in ARMS},
        runtime_s={a: dict(train_median=float(np.median(tr[a])), train_min=float(tr[a].min()), train_max=float(tr[a].max()),
                           n_over_36000=int((tr[a] >= 36000).sum()), train_mean_under_36000=float(tr[a][tr[a] < 36000].mean()),
                           train_sd_under_36000=float(tr[a][tr[a] < 36000].std(ddof=1)), infer_median=float(np.median(inf[a])))
                   for a in ARMS},
    )
    json.dump(out, open(args.out, "w"), indent=1, default=float)
    print(json.dumps({k: out[k] for k in ["paired_difference_pp", "wilcoxon", "sign_test_p_two_sided", "bootstrap_recomputed", "bootstrap_stored_json", "pooled_recall", "seed_delta_pp", "wilcoxon_leave_one_participant_out_p"]}, default=float, indent=0)[:3500])


if __name__ == "__main__":
    main()
