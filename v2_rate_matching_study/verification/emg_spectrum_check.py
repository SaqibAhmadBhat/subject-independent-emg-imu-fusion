"""Fraction of raw sEMG power above the E3-D Nyquist frequency (74.07 Hz), per trial (read-only on raw SDALLE CSVs)."""
import sys, glob, json, numpy as np, pandas as pd
from scipy.signal import welch
root = sys.argv[1]; out = sys.argv[2]; per_act = int(sys.argv[3]) if len(sys.argv) > 3 else 2
fs = 1259.2593; res = []
subs = [int(v) for v in sys.argv[4].split(",")] if len(sys.argv) > 4 else range(1, 10)
for s in subs:
    for act in ["Walking", "Jogging", "Stairs_up", "Stairs_down"]:
        for f in sorted(glob.glob(f"{root}/Subject_{s}/{act}/*.csv"))[:per_act]:
            df = pd.read_csv(f, skiprows=7, header=None, usecols=list(range(0, 56, 7)))
            x = df.apply(pd.to_numeric, errors="coerce").dropna().to_numpy()
            fr, p = welch(x - x.mean(0), fs=fs, nperseg=512, axis=0)
            tot = p.sum(0)
            res.append(dict(subject=s, activity=act, file=f.split("/")[-1], n=len(x),
                            frac_above_74=float(np.mean(p[fr > 74.07].sum(0) / tot)),
                            frac_20_450=float(np.mean(p[(fr >= 20) & (fr <= 450)].sum(0) / tot)),
                            frac_below_20=float(np.mean(p[fr < 20].sum(0) / tot)),
                            mains50_ratio=float(np.median(p[np.argmin(np.abs(fr - 50.0))] / np.median(p[(fr > 38) & (fr < 62) & (np.abs(fr - 50.0) > 3.5)], axis=0))),
                            median_freq_hz=float(np.median([fr[np.searchsorted(np.cumsum(p[:, c]), tot[c] / 2)] for c in range(8)]))))
json.dump(res, open(out, "w"), indent=1)
a = np.array([r["frac_above_74"] for r in res]); m = np.array([r["median_freq_hz"] for r in res])
subj = [np.mean([r["frac_above_74"] for r in res if r["subject"] == s]) for s in range(1, 10)]
b = np.array([r["frac_below_20"] for r in res]); mr = np.array([r["mains50_ratio"] for r in res])
print(f"below20 mean={b.mean():.4f} sd={b.std(ddof=1):.4f}; mains50 ratio median={np.median(mr):.2f} p90={np.percentile(mr,90):.2f} max={mr.max():.2f} n>3={int((mr>3).sum())}")
print(f"trials={len(res)} frac>74Hz mean={a.mean():.4f} sd={a.std(ddof=1):.4f} min={a.min():.4f} max={a.max():.4f}; participant means mean={np.mean(subj):.4f} sd={np.std(subj,ddof=1):.4f}; median freq (Hz) mean={m.mean():.1f} range={m.min():.1f}-{m.max():.1f}")
