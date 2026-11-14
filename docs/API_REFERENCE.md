# Verification Scripts & CLI Reference

This document provides command-line reference documentation for all verification and audit utilities included in the repository.

---

## 1. Automated Master Verification Suite

### `scripts/verify_release.py`
Executes the master 5-stage release verification audit:
1. File structure & essential artifact presence.
2. Prediction file existence & row count integrity (90 files, 6,193 windows).
3. Primary statistical reproduction (Wilcoxon $W=5.0$, $p=0.039$, Permutation $p=0.031$).
4. Mathematical model architecture & parameter count verification (330,052 parameters).
5. SHA-256 archive checksum and digest validation.

```bash
# Run full verification suite
python3 scripts/verify_release.py

# Expected exit code: 0
```

---

## 2. Statistical Verification Utilities

### `v2_rate_matching_study/verification/verify_v2_statistics.py`
Computes the primary statistical tests, participant paired differences, Wilcoxon signed-rank test, matched-pairs rank-biserial correlation, and percentile bootstrap confidence interval:

```bash
python3 v2_rate_matching_study/verification/verify_v2_statistics.py
```

**Key Outputs:**
- Paired differences $d_k$ for subjects P1 through P9.
- Wilcoxon test statistic: $W^+ = 40, W^- = 5, W = 5, p_{\text{exact}} = 0.0390625$.
- Rank-biserial correlation: $r = +0.7778$.
- 95% Percentile bootstrap CI: $[1.2713, 6.3548]\text{ pp}$.

### `v2_rate_matching_study/verification/verify_v2_additional_stats.py`
Computes the post-hoc inferential robustness tests:
- Exact sign-flip permutation test ($p = 0.03125$).
- Two-stage hierarchical bootstrap resampling ($95\%\text{ CI: } [1.0671, 6.6489]\text{ pp}$).
- Variance components decomposition ($V_{\text{condition}}, V_{\text{participant}}, V_{\text{seed}}$).
- Leave-one-seed-out sensitivity.
- Leave-one-participant-out sensitivity.

```bash
python3 v2_rate_matching_study/verification/verify_v2_additional_stats.py
```

---

## 3. Spectral & Signal Processing Audits

### `v2_rate_matching_study/verification/emg_spectrum_check.py`
Computes the Welch Power Spectral Density across trials and measures super-Nyquist energy density ($>74.07\text{ Hz}$):

```bash
python3 v2_rate_matching_study/verification/emg_spectrum_check.py
```

**Key Outputs:**
- Cohort mean super-Nyquist energy: $19.00\% \pm 2.49\%$.
- Subject-by-subject energy fractions (P1 minimum at $13.51\%$).

---

## 4. Run Integrity & Array Checksums

### `v2_rate_matching_study/verification/audit_90_runs.py`
Audits all 90 run directories, checking training logs, epoch counts, convergence milestones, and predictions:

```bash
python3 v2_rate_matching_study/verification/audit_90_runs.py
```

### `v2_rate_matching_study/verification/regenerate_arrays_check.py`
Verifies that processed array tensors can be regenerated bit-identically from raw data recordings:

```bash
python3 v2_rate_matching_study/verification/regenerate_arrays_check.py
```
