"""Additional post hoc analyses from the frozen predictions (read-only): sign-flip permutation test, hierarchical bootstrap,
leave-one-seed-out, variance components of the seed-level paired differences. Usage: python3 verify_v2_additional_stats.py <V2_ROOT> <out.json>"""
import csv, itertools, json, sys
from pathlib import Path
import numpy as np
from scipy import stats
root = Path(sys.argv[1]); out = sys.argv[2]
SEEDS = [42, 123, 2024, 3407, 7777]
def wil(d):
    d = np.asarray(d, float); r = stats.rankdata(np.abs(d)); n = len(d); w = min(r[d > 0].sum(), r[d < 0].sum())
    cnt = sum(1 for g in itertools.product([0, 1], repeat=n) if min(sum(r[i] for i in range(n) if g[i]), r.sum() - sum(r[i] for i in range(n) if g[i])) <= w)
    return float(w), cnt / 2 ** n
A = {a: np.zeros((5, 9)) for a in ["E3-D", "E4"]}; correct = {a: 0 for a in A}; total = 0
for i, s in enumerate(SEEDS):
    for a in A:
        for k in range(1, 10):
            rows = list(csv.DictReader(open(root / f"seed_{s}" / a / f"fold_{k}" / "predictions.csv", newline="")))
            c = sum(r["correct"] == "1" for r in rows); A[a][i, k - 1] = c / len(rows) * 100; correct[a] += c
            if a == "E4": total += len(rows)
D = A["E3-D"] - A["E4"]            # seed x participant paired differences (pp)
d = D.mean(0); n = 9; obs = d.mean()
# exact sign-flip permutation test on the mean of the participant differences
perm = np.array([np.mean(d * np.array(sg)) for sg in itertools.product([1, -1], repeat=n)])
p_perm = float(np.mean(np.abs(perm) >= abs(obs) - 1e-12))
# hierarchical bootstrap: resample participants, then seeds within each resampled participant
rng = np.random.default_rng(42); B = 10000; bm = np.empty(B)
for b in range(B):
    ps = rng.integers(0, n, n); bm[b] = np.mean([D[rng.integers(0, 5, 5), p].mean() for p in ps])
hb = [float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5))]
# leave one seed out
loso = {}
for i, s in enumerate(SEEDS):
    dd = np.delete(D, i, axis=0).mean(0); w, p = wil(dd); loso[str(s)] = dict(mean_diff=float(dd.mean()), W=w, p=p, n_pos=int((dd > 0).sum()))
# variance components (one-way random effects, participants as groups, seeds as replicates)
ms_b = 5 * d.var(ddof=1); ms_w = float(np.mean(D.var(axis=0, ddof=1)))
var_between = max((ms_b - ms_w) / 5, 0.0); icc = var_between / (var_between + ms_w)
se_mixed = float(np.sqrt(ms_b / (5 * 9))); se_t = float(d.std(ddof=1) / np.sqrt(9))
# two-way decomposition (participant, seed, residual)
gm = D.mean(); ss_p = 5 * np.sum((D.mean(0) - gm) ** 2); ss_s = 9 * np.sum((D.mean(1) - gm) ** 2); ss_t = np.sum((D - gm) ** 2); ss_r = ss_t - ss_p - ss_s
res = dict(
    mean_diff=float(obs), sign_flip_permutation_p=p_perm,
    hierarchical_bootstrap_ci=hb,
    leave_one_seed_out=loso,
    variance_components=dict(sd_between_participants=float(np.sqrt(var_between)), sd_within_participant_between_seeds=float(np.sqrt(ms_w)), icc=float(icc),
                             se_of_participant_mean_from_seed_noise=float(np.sqrt(ms_w / 5))),
    balanced_mixed_model_check=dict(se_from_random_intercept_model=se_mixed, se_from_paired_t=se_t),
    sum_of_squares_share=dict(participant=float(ss_p / ss_t), seed=float(ss_s / ss_t), residual=float(ss_r / ss_t)),
    seed_level_differences_pp=D.round(3).tolist(),
    n_seed_participant_pairs_positive=int((D > 0).sum()), n_pairs=45,
    pooled_window_accuracy_pct={a: correct[a] / total * 100 for a in A}, windows_per_condition=total)
json.dump(res, open(out, "w"), indent=1); print(json.dumps({k: v for k, v in res.items() if k != "seed_level_differences_pp"}, indent=0))
