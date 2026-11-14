# Execution Guide & CLI Reference

This document provides exact, tested CLI commands for all research operations in the V2 repository.

---

## 1. Quick Verification Commands (No Training Needed)

All 90 run predictions are committed in the repository. You can verify all results in seconds.

### A. Verify Primary Statistical Findings
```bash
python3 v2_rate_matching_study/verification/verify_v2_statistics.py \
    v2_rate_matching_study/V2_ROBUSTNESS_STUDY \
    /tmp/stat_output.json
```
**Checks performed:**
- Loads all 90 `predictions.csv` files across both conditions (`E3-D`, `E4`), 9 folds, and 5 seeds.
- Computes participant-level mean accuracy for both conditions ($N = 9$).
- Runs two-sided Wilcoxon signed-rank test (exact null distribution).
- Computes matched-pairs rank-biserial correlation ($r = 0.78$).
- Computes 95% percentile bootstrap confidence interval ($B = 10{,}000$).
- Validates macro-F1 and per-class recall metrics.

### B. Verify Post Hoc Sensitivity Analyses
```bash
python3 v2_rate_matching_study/verification/verify_v2_additional_stats.py \
    v2_rate_matching_study/V2_ROBUSTNESS_STUDY \
    /tmp/additional_output.json
```
**Checks performed:**
- Computes exact sign-flip permutation test across all 512 sign permutations ($p = 0.031$).
- Computes two-stage hierarchical bootstrap confidence interval ($[1.07, 6.65]$ pp).
- Evaluates leave-one-seed-out sensitivity ($p = 0.012$ to $0.055$).
- Decomposes variance components: seed SD ($4.23$ pp) vs. between-participant SD ($3.66$ pp).

### C. Run Complete 90-Run Integrity Audit
```bash
python3 v2_rate_matching_study/verification/audit_90_runs.py \
    v2_rate_matching_study/V2_ROBUSTNESS_STUDY \
    /tmp/audit_report.json
```
**Checks performed:**
- Verifies that all 90 runs have exact, uncorrupted `predictions.csv`, `history.json`, and `meta.json`.
- Confirms zero missing folds, zero missing seeds, and identical test labels across conditions.

---

## 2. Running Automated Unit & Quality Tests

The repository contains an automated test suite verifying model architectures, parameter budgets, theoretical receptive fields, and prediction integrity.

```bash
# Run the full test suite with pytest
pytest tests/ -v

# Run with test coverage report
pytest tests/ -v --cov=v2_rate_matching_study/src
```

---

## 3. Retraining Commands (Tier 2)

### A. Retraining a Single Fold
To retrain a single model fold (for example, Seed 42, Fold 1, Condition E3-D):
```bash
python3 v2_rate_matching_study/V2_ROBUSTNESS_STUDY/robustness_train.py \
    --seed 42 \
    --condition E3-D \
    --fold 1 \
    --epochs 50 \
    --device cpu \
    --batch_size 64
```

### B. Retraining a Full Seed (9 Folds)
```bash
for fold in $(seq 1 9); do
    python3 v2_rate_matching_study/V2_ROBUSTNESS_STUDY/robustness_train.py \
        --seed 42 \
        --condition E3-D \
        --fold $fold \
        --epochs 50
done
```

### C. Aggregating Results from Fresh Retraining
After completing training runs, run the analysis pipeline:
```bash
python3 v2_rate_matching_study/V2_ROBUSTNESS_STUDY/robustness_analyze.py \
    --results_dir v2_rate_matching_study/V2_ROBUSTNESS_STUDY \
    --output_dir /tmp/analysis_output
```

---

## 4. Signal Processing & Spectral Audit

To verify the sEMG power spectral distribution across the 361 raw continuous SDALLE trials:
```bash
# Requires access to raw SDALLE CSV dataset
python3 v2_rate_matching_study/verification/emg_spectrum_check.py \
    /path/to/SDALLE_dataset \
    /tmp/spectrum_summary.json \
    10 \
    1,2,3,4,5,6,7,8,9
```
*Expected findings:*
- Mean sEMG power above 74.07 Hz: $19.0\% \pm 10.3\%$.
- Mean sEMG power below 20 Hz: $33.1\% \pm 12.4\%$.
- Median frequency: $35.1\text{ Hz}$.
- 50 Hz mains ratio median: $1.2$ (no prominent mains hum).
