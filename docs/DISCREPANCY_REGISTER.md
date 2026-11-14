# Scientific Discrepancy Register

This register documents all technical, methodological, and historical discrepancies identified, investigated, and reconciled during the multi-phase audit of the research project across versions V1, V2, and V2.0.0.

---

## 1. Evidence Hierarchy

All empirical claims and documentation updates adhere to the following strict evidentiary hierarchy:
1. **Raw Sensor Recordings & Continuous Files**
2. **Deterministic Source Code**
3. **Frozen Inferences, Checkpoints, and `meta.json` Records**
4. **Canonical Tabular Outputs and Verification Scripts**
5. **Execution Validation Logs**
6. **Manuscript Evidence Dossiers**
7. **Historical Handover Notes & Summaries**

---

## 2. Reconciled Discrepancies (D1 – D27)

| # | Original Claim | Source of Claim | Independent Audit Result | Resolution | Scientific Implication |
|---|---|---|---|---|---|
| **D1** | Participants: "healthy adult volunteers" | AG drafts | Farouk *et al.* (2026) Table 2: ages 12–39; S9 is 12 years old; all male | **Corrected** | Explicit disclosure: "nine healthy male participants aged 12–39 years, one of whom was 12" + SAGER compliance. |
| **D2** | EMG muscles: tibialis anterior, gastrocnemius medialis, rectus femoris, biceps femoris | AG preliminary drafts | Raw CSV headers across all subjects: rectus femoris, vastus medialis, vastus lateralis, semitendinosus (bilateral). | **Corrected** | Adopted verified sensor placement matching raw physical headers. |
| **D3** | Random seeds: 42, 43, 44, 45, 46 | Early informal summaries | Exact seeds used in runs: `42, 123, 2024, 3407, 7777` (and evaluated across `42, 123, 456, 789, 101112`). | **Corrected** | Documented exact active random seeds in metadata. |
| **D4** | Receptive field: 28 samples "before final conv" vs 44 "including 4th conv" | Preliminary report | Receptive field is exactly 28 samples at the output of the 4th (final) convolution (189.0 ms on 148 Hz vs 22.2 ms on 1259 Hz). | **Corrected** | Established exact recursive receptive field derivation. |
| **D5** | Wilcoxon rank explanation inconsistent | Early report | Participant paired differences: P1 $|d| = 3.1530 \to$ rank 5, P9 $|d| = 3.1425 \to$ rank 4; $W = 5.0$, exact $p = 0.0390625$. | **Confirmed** | Complete rank table documented ($W^- = 5, W^+ = 40$). |
| **D6** | "$p < 0.05$ strictly robust across all subsets" | Initial claims | Leave-one-subject-out deletion reveals $p = 0.055\text{--}0.078$ for 8 of 9 deletions. | **Clarified** | Stated full cohort requirement ($N=9$) for nominal $p < 0.05$. |
| **D7** | BCa CI reported as [1.1950, 6.2394] | Prior notes | Percentile bootstrap yields $[1.27, 6.35]\text{ pp}$; two-stage hierarchical bootstrap yields $[1.07, 6.65]\text{ pp}$. | **Resolved** | Primary report uses percentile $[1.27, 6.35]$ and hierarchical $[1.07, 6.65]\text{ pp}$. |
| **D8** | Macro-F1 Wilcoxon $W = 5, p = 0.0391$ | Figure draft | Exact calculation on macro-F1 yields $W = 4, p = 0.0273$. | **Corrected** | Figures and tables updated to reflect exact macro-F1 statistic. |
| **D9** | Test window counts: 647, 652, 809... | Early text | Exact test window counts per fold: 647, 568, 729, 696, 746, 722, 654, 690, 751. | **Corrected** | All participant tables aligned with exact window totals. |
| **D10**| Participant macro-F1 values | Dossier | Verified against canonical prediction CSVs. | **Corrected** | Direct CSV ground truth adopted. |
| **D11**| Hypothesis formulated as "non-inferiority" | Preliminary notes | No non-inferiority margin was prespecified; hypothesis is a two-sided paired difference test. | **Corrected** | Formulated strictly as two-sided difference test. |
| **D12**| 5-seed aggregation prespecification | Draft README | Accuracy metric prespecified; 5-seed aggregation rule was post hoc. | **Clarified** | Explicit disclosure of post hoc multi-seed protocol. |
| **D13**| Preliminary single-seed exploratory runs | Unmentioned | Seed 42 preliminary run (30 Sep–4 Oct 2026): difference +1.8 pp (4/9 favored E3-D). | **Disclosed** | Fully disclosed in methods and historical provenance. |
| **D14**| "Sequential desktop CPU benchmark" | Early notes | Wall-clock times recorded on Apple M4 laptop. Maxima indicate system sleep/suspension. | **Corrected** | Wall-clock metrics labeled as descriptive execution times. |
| **D15**| Interpolation function | Draft text | Implemented via `scipy.interpolate.interp1d(kind='cubic', fill_value='extrapolate')`. | **Corrected** | Full algorithm specification documented in methods. |
| **D16**| Acquisition hardware discrepancies | Earlier documents | Delsys Trigno Discover (v1.7.0) with Avanti sensors confirmed from raw headers. | **Corrected** | Raw file headers established as authoritative. |
| **D17**| Super-Nyquist energy: 3.72% &plusmn; 1.99% | Early estimate | Welch PSD across all 361 raw trials reveals $19.0\% \pm 10.3\%$ super-Nyquist energy above 74.07 Hz. | **Corrected** | Cohort Welch PSD established as ground truth. |
| **D18**| Dataset citations | Mixed citations | Upstream works: El-Khoreby et al. (2026), Farouk et al. (2026), Ibrahim et al. (2025). | **Corrected** | Complete citations included in CITATION.cff and docs. |
| **D19**| Hardware synchronization | Assumed hardware clock | Raw CSV files do not contain hardware trigger channels; synchronization relies on Delsys software. | **Clarified** | Upstream synchronization caveats explicitly stated. |
| **D20**| Ethical committee approvals | Preliminary notes | ERUFE-MR-26-001 ethical approval details audited. | **Documented** | Ethics statements aligned with primary data source. |
| **D21**| Class-wise recall averaging | Conflicting notes | Macro recall computed as mean-of-runs across folds. | **Clarified** | Formula explicitly defined in documentation. |
| **D22**| Tier 3 end-to-end execution claim | Early handoff | Full dataset preprocessing requires raw SDALLE download from Zenodo. | **Clarified** | Tier 1 (fast audit) vs Tier 2 (from processed) vs Tier 3 (from raw) documented. |
| **D23**| Frozen archive SHA-256 sums | Stale hashes | Verified SHA-256 digests established for `v2_release_candidate_final.zip` and `v2_reproducibility_data_final.zip`. | **Reconciled** | Exact bit-level digests documented. |
| **D24**| E4 configuration difference between V1 and V2 | V1 vs V2 | V1 trained with `ReduceLROnPlateau`; V2 used cosine annealing learning rate schedule. | **Clarified** | Optimization schedule difference documented. |
| **D25**| Condition naming | E3-D / E4 | Internal labels mapped to Rate-Matched (RM) and Native-Rate (NR) for publications. | **Standardized** | Cross-mapping clearly explained in tables. |
| **D26**| Preliminary run outcome | Informal summary | Preliminary run was inconclusive (+1.8 pp, 4/9 favored E3-D); prompted 5-seed study. | **Documented** | Motivated rigorous multi-seed protocol. |
| **D27**| Compute environment | Generic desktop | Apple MacBook Air (M4, 16 GB RAM), macOS Darwin arm64, PyTorch 2.10.0. | **Documented** | Hardware environment accurately described. |

---

## 3. Methodological Disclosures (D28 – D31)

- **D28. Protocol Disclosures:** The initial protocol specified Leave-One-Subject-Out evaluation but did not prespecify the exact versus asymptotic Wilcoxon test, the hierarchical bootstrap, or seed aggregation rules. All inferential choices are fully disclosed and documented.
- **D29. Data Array Bit-Identical Integrity:** The processed data arrays generated on 6 November 2026 reproduce bit-identically across all 18 arrays from the raw files.
- **D30. Provenance of Scripts:** The final archived `robustness_train.py` and `src/models.py` incorporate defensive guards and verified random generators; exact mathematical equivalence to earlier versions is proven.
- **D31. Zenodo Concept DOI Continuity:** Release V2.0.0 is linked directly under the overarching Concept DOI `10.5281/zenodo.22649504`.
