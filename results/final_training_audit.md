# Final Training Audit

**Generated:** 2026-09-07 12:59:29

---

## Completion Status

| Experiment | Folds Complete | Status |
|------------|---------------|--------|
| E1 | 9/9 | ✅ COMPLETE |
| E2 | 9/9 | ✅ COMPLETE |
| E3 | 9/9 | ✅ COMPLETE |
| E4 | 9/9 | ✅ COMPLETE |

**TOTAL: 36/36 folds complete**

---

## Per-Experiment Summary

### E1

- Folds: **9/9** ✅
- Parameters: 156,228
- Epochs per fold: 50
- Total training time: 2170.10 s
- Seed: 42
- Learning rate: 0.001
- Weight decay: 0.0001
- Batch size: 64

### E2

- Folds: **9/9** ✅
- Parameters: 174,148
- Epochs per fold: 50
- Total training time: 344.65 s
- Seed: 42
- Learning rate: 0.001
- Weight decay: 0.0001
- Batch size: 64

### E3

- Folds: **9/9** ✅
- Parameters: 177,732
- Epochs per fold: 50
- Total training time: 337.31 s
- Seed: 42
- Learning rate: 0.001
- Weight decay: 0.0001
- Batch size: 64

### E4

- Folds: **9/9** ✅
- Parameters: 330,052
- Epochs per fold: 50
- Total training time: 61995.63 s
- Seed: 42
- Learning rate: 0.001
- Weight decay: 0.0001
- Batch size: 64

---

## JSON Integrity Verification

All 36 `history.json` files verified:

- ✅ Exactly **50 train_loss** entries in every fold
- ✅ Exactly **50 train_acc** entries in every fold
- ✅ No `test_loss` keys present
- ✅ No `test_acc` keys present
- ✅ No `val_loss` keys present
- ✅ No `val_acc` keys present

All 36 `meta.json` files verified:

- ✅ Correct `experiment` field in every fold
- ✅ Correct `fold` number in every fold
- ✅ `epochs = 50` confirmed in every fold

---

## Preserved Files

- `results/final_training.log` — preserved, unmodified
- `results/experiment_manifest.csv` — updated with 36 fold records
- `results/final_results_checksums.sha256` — 110 SHA-256 entries

---

## Backup

- Full backup copied to: `results_backup/`

---

## Final Verdict

```
E1 = 9/9   ✅
E2 = 9/9   ✅
E3 = 9/9   ✅
E4 = 9/9   ✅
TOTAL = 36/36  ✅  ALL FOLDS COMPLETE
```

---

> **PRESERVATION COMPLETE — No folds were deleted, overwritten, renamed, or retrained.**
> Evaluation has NOT been run. Test metrics have NOT been computed.
> Manuscript has NOT been modified.
