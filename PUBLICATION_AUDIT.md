# Publication Audit

Pre-release audit for the public GitHub repository `subject-independent-emg-imu-fusion`.

**Audit date:** 2025-09-07

---

## 1. File Classification

### A. Safe / Public Source Code

| File | Status | Notes |
|---|---|---|
| `src/build_datasets.py` | ✅ Safe | No personal paths |
| `src/dataset_loader.py` | ✅ Safe | No personal paths |
| `src/models.py` | ✅ Safe | No personal paths |
| `src/normalizer.py` | ✅ Safe | No personal paths |
| `src/train.py` | ✅ Safe | No personal paths |
| `src/evaluate.py` | ✅ Safe | Original evaluation module |
| `src/windower.py` | ✅ Safe | No personal paths |
| `src/inspect_dataset.py` | ✅ Safe | Utility script |
| `src/sanity_test.py` | ✅ Safe | Utility script |
| `run_all.sh` | ✅ Fixed | Personal path replaced with portable `$(dirname "$0")` |
| `run_evaluation.py` | ✅ Safe | Uses `__file__`-relative paths |
| `preserve_results.py` | ✅ Fixed | Personal path replaced with `os.path.abspath(__file__)` |
| `verify_folds.py` | ✅ Safe | Uses relative paths |
| `requirements.txt` | ✅ Cleaned | Reduced from full pip freeze to core dependencies |

### B. Frozen Research Artifacts (results/)

| File | Status | Notes |
|---|---|---|
| `results/E*/fold_*/model.pt` | ✅ Include | 36 frozen trained models (~700 KB–1.3 MB each) |
| `results/E*/fold_*/history.json` | ✅ Include | Training loss/accuracy curves |
| `results/E*/fold_*/meta.json` | ✅ Include | Training metadata |
| `results/final_training.log` | ⚠️ Include with note | Contains personal machine paths in Python tracebacks. This is a frozen training artifact and should not be modified. The paths are in error tracebacks from early debugging and do not affect reproducibility. |
| `results/experiment_manifest.csv` | ✅ Include | Generated during preservation |
| `results/final_results_checksums.sha256` | ✅ Include | Integrity verification |
| `results/final_training_audit.md` | ✅ Include | Training completion audit |
| `results/E*/eval_summary.json` | ✅ Include | Legacy evaluation output |
| `results/E*/aggregate_cm.npy` | ✅ Include | Legacy aggregate confusion matrices |
| `results/E*/predictions.csv` | ✅ Include | Legacy predictions |

### C. Evaluation Artifacts (evaluation/)

| File | Status | Notes |
|---|---|---|
| `evaluation/final_metrics.csv` | ✅ Include | Per-fold metrics |
| `evaluation/evaluation_manifest.csv` | ✅ Include | Evaluation tracking |
| `evaluation/evaluation_audit.md` | ✅ Include | Evaluation protocol audit |
| `evaluation/metrics/*.json` | ✅ Include | Per-fold and summary metrics |
| `evaluation/predictions/*.csv` | ✅ Include | Window-level predictions |
| `evaluation/figures/*.png` | ✅ Include | Publication-quality figures |
| `evaluation/tables/*.csv` | ✅ Include | Summary and statistical tables |
| `evaluation/evaluation_run.log` | ❌ Exclude | Contains personal machine paths (gitignored) |

### D. Manuscript (paper/)

| File | Status | Notes |
|---|---|---|
| `paper/main.tex` | ✅ Include | Manuscript source (contains author names/emails — these are intentional) |
| `paper/main.pdf` | ✅ Include | Compiled manuscript |
| `paper/references.bib` | ✅ Include | Bibliography |
| `paper/figures/*.png` | ✅ Include | Manuscript figures |

### E. Files to EXCLUDE from Public Repository

| File | Reason |
|---|---|
| `data/raw/SDALLE/` | Third-party dataset, not redistributable without explicit permission |
| `data/processed/` | Derived from SDALLE (~3.6 GB), can be regenerated |
| `results_backup/` | Local backup, redundant with results/ |
| `.venv/` | Virtual environment (~1.2 GB) |
| `Infrasence Udyam Registration Certificate.pdf` | Personal business document, unrelated to research |
| `extracted.txt` | Working notes / paper extracts |
| `evaluation/evaluation_run.log` | Contains personal machine paths |
| `.DS_Store` | macOS metadata |
| `__pycache__/` | Python bytecode cache |
| `notebooks/` | Empty directory |
| `models/` | Empty directory |
| `figures/` | Empty directory (figures are in evaluation/figures/ and paper/figures/) |

---

## 2. Dataset Protection

| Check | Status |
|---|---|
| `data/raw/SDALLE/` excluded via .gitignore | ✅ |
| `data/processed/` excluded via .gitignore | ✅ |
| `data/README.md` documents how to obtain SDALLE | ✅ |
| No dataset content embedded in source code | ✅ |
| No dataset licensing terms invented | ✅ — refers to official Zenodo page |

---

## 3. Personal / Machine-Specific Information

### Found and addressed:

| Location | Content | Action |
|---|---|---|
| `run_all.sh` (line 23) | Hardcoded `/Users/saqibahmadbhat/Desktop/RP/RP4` | **Fixed** → portable `$(dirname "$0")` |
| `preserve_results.py` (line 17) | Hardcoded absolute path | **Fixed** → `os.path.abspath(__file__)` |
| `results/final_training.log` | Python tracebacks with personal paths | **Noted** — frozen artifact, not modified |
| `evaluation/evaluation_run.log` | Saved file paths with personal paths | **Excluded** via .gitignore |
| `results_backup/final_training.log` | Same as results/ version | **Excluded** — entire backup dir gitignored |

### Author information (intentionally retained):

| Location | Content | Decision |
|---|---|---|
| `paper/main.tex` | Author names, emails, ORCIDs, affiliation | Intentional — part of the manuscript |
| `CITATION.cff` | Author names, ORCIDs | Intentional — standard citation metadata |
| `LICENSE` | Author names | Intentional — standard license |
| `README.md` | Author names in citation block | Intentional |

---

## 4. Secrets Scan

| Check | Status |
|---|---|
| API keys | ✅ None found |
| Tokens | ✅ None found (only `asttokens` package name — false positive) |
| Passwords | ✅ None found |
| SSH keys | ✅ None found |
| Cloud credentials | ✅ None found |
| Database credentials | ✅ None found |
| Personal access tokens | ✅ None found |

---

## 5. Large File Analysis

| Path | Size | Decision |
|---|---|---|
| `data/raw/SDALLE/` | ~1.1 GB | ❌ Excluded (third-party dataset) |
| `data/processed/` | ~3.6 GB | ❌ Excluded (can be regenerated) |
| `.venv/` | ~1.2 GB | ❌ Excluded (virtual environment) |
| `results/` (all 36 folds) | ~30 MB | ✅ Include in Git (under 50 MB threshold) |
| `results_backup/` | ~30 MB | ❌ Excluded (redundant backup) |
| `evaluation/` | ~1.7 MB | ✅ Include in Git |
| `paper/` | ~1.0 MB | ✅ Include in Git |
| Individual `model.pt` files | 700 KB–1.3 MB each | ✅ Fine for regular Git |

**No files exceed 50 MB in the tracked set. Git LFS is not required.**

---

## 6. License Analysis

| Component | License | Notes |
|---|---|---|
| Original source code | MIT | Applied via LICENSE file |
| SDALLE dataset | Dataset author's terms | Not relicensed — users directed to Zenodo |
| PyTorch, NumPy, SciPy, etc. | Various OSS licenses | Dependencies only — not redistributed |

---

## 7. Reproducibility Status

| Step | Working | Notes |
|---|---|---|
| Dataset documentation | ✅ | `data/README.md` with download instructions |
| Environment setup | ✅ | `requirements.txt` tested |
| `build_datasets.py` | ✅ | Requires raw SDALLE dataset |
| `run_all.sh` | ✅ | Portable path handling |
| `run_evaluation.py` | ✅ | Portable, tested |
| `verify_folds.py` | ✅ | Tested |

---

## 8. Unresolved Issues

1. **`results/final_training.log` contains personal paths** in Python tracebacks from early debugging runs. These are in a frozen artifact that should not be modified. The paths are benign (file locations on the development machine) and do not affect reproducibility. Documented here for transparency.

2. **The `Infrasence Udyam Registration Certificate.pdf`** is present in the working directory. It is unrelated to the research and is excluded via .gitignore (`*.pdf` excluding `paper/*.pdf`). It should be removed from the working directory before creating the first commit, or at minimum confirmed to be gitignored.

3. **Empty directories** (`notebooks/`, `models/`, `figures/`) are present in the working directory but will not be tracked by Git (Git does not track empty directories).
