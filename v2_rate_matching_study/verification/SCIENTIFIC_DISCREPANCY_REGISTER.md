# Scientific discrepancy register (2026-11-13, updated after the simulated reviews)

Evidence hierarchy applied, highest first:
1. Raw inputs.
2. Code.
3. Frozen predictions and meta.json.
4. Canonical tables and verification scripts.
5. Validation records.
6. Dossier.
7. Handover and summary reports.

"AG docs" means `CLAUDE_HANDOVER.md`, `AG_FINAL_HANDOFF.md`, `manuscript_evidence_dossier.md`, README and REPRODUCE, plus the earlier AG manuscript drafts in `research_audit/publication/`.

| # | Original claim | Source of claim | Independent result | Resolution | Manuscript implication |
|---|---|---|---|---|---|
| D1 | Participants: "healthy adult volunteers" | AG docs | Farouk *et al* 2026 Table 2: ages 12–39; S9 is 12 years old; all male | **Corrected** | "nine healthy male participants aged 12–39 years, one of whom was 12" + SAGER statement + ethics disclosure |
| D2 | EMG muscles: tibialis anterior, gastrocnemius medialis, rectus femoris, biceps femoris | AG drafts (TNSRE draft, signal-validation notes, figure 3) | Raw CSV headers (all subjects): rectus femoris, vastus medialis, vastus lateralis, semitendinosus, left and right. Same in (a) and (c) | **Corrected** | Use the raw-header muscle set; do not use AG's figure 3 (synthetic TA/GM traces) |
| D3 | Seeds 42, 43, 44, 45, 46 | "Comprehensive report" (as described by user) | Seeds 42, 123, 2024, 3407, 7777 (directories, meta.json, protocol §16) | **Corrected** | Report the actual seeds |
| D4 | Receptive field 28 samples "before final conv" vs 44 "including 4th conv" | Comprehensive report (as described by user) | 28 samples is the RF **at the output of the 4th (final) convolution**; it is 20 samples before it; 44 is not supported | **Corrected** | Define it as "theoretical RF of a final-convolution output position = 28 samples" |
| D5 | Wilcoxon rank explanation inconsistent | Comprehensive report (as described by user) | P1 \|d\| = 3.1530 → rank 5, P9 3.1425 → rank 4; W = 5, exact p = 0.0390625 | **Confirmed numbers; clarified ranking** | Report W− = 5, W+ = 40, exact p |
| D6 | p < 0.05 robust | AG docs ("strictly excludes zero", "very large effect") | Leave-one-out p = 0.055–0.078 for 8 of 9 deletions | **Added limitation** | Report the sensitivity; describe the evidence as modest |
| D7 | BCa CI [1.1950, 6.2394] | AG docs | Stored JSON [1.1971, 6.2413]; my reproduction [1.1950, 6.2394]; the difference is the z0 convention | **Resolved** | Report BCa as [1.2, 6.2] pp (sensitivity only); primary = percentile [1.27, 6.35] |
| D8 | Macro-F1 Wilcoxon W = 5, p = 0.0391 | AG Figure 2 | W = 4, p = 0.0273 | **Corrected** | Regenerate figures; report W = 4 |
| D9 | Per-participant test windows 647, 652, 809, … (range 464–962) | Dossier §7/§9 | 647, 568, 729, 696, 746, 722, 654, 690, 751 | **Corrected** | Table 2 uses the correct counts |
| D10 | Per-participant macro-F1 (e.g. P1 0.7674/0.7937) | Dossier §9 | 0.7555/0.8000 (matches the canonical CSV) | **Corrected** | Use the CSV |
| D11 | Hypothesis "non-inferior" | AG handoff §1, dossier §1 | No margin prespecified; the test is a two-sided difference test | **Corrected** | No non-inferiority language |
| D12 | Primary endpoint "prespecified … (5-seed average)" | README | Accuracy and the Wilcoxon test are prespecified (protocol §17–18); the 5-seed aggregation rule is **not** in the protocol | **Clarified** | Disclose that the aggregation is post hoc |
| D13 | (Undisclosed) preliminary single-seed runs | absent from AG summaries | `V2/results/raw` (seed 42, 30 Sep–4 Oct 2026): sEMG-only 49.4 %, IMU-only 67.6 %, single-stream rate-matched fusion 63.2 %, dual-branch rate-matched 69.7 %, dual-branch native-rate 67.9 %. The script (`V2/src/train_v2.py`, dated 30 Sep) used the same cosine schedule and hyperparameters as the main study; its stored settings carry unused plateau-schedule fields. It shuffled training data without a separately seeded generator. Protocol dated 8 Oct. **An earlier version of this entry said the preliminary runs used a plateau schedule; that was wrong** | **Added and corrected** | Disclosed in Methods §2.7, Results §3.6 and supplementary table S4 |
| D14 | "Sequential desktop CPU benchmark" | AG docs | Wall-clock times on the authors' laptop; maxima 42,027 s and 114,357 s indicate suspension; hardware not documented | **Corrected** | "Observed wall-clock times … descriptive" |
| D15 | Interpolation `scipy CubicSpline`, in robustness_train.py | Dossier §6 | `interp1d(kind='cubic', fill_value='extrapolate')`, per trial, in `V2/src/windower_v2.py` | **Corrected** | Methods text |
| D16 | Hardware: Delsys Trigno Avanti (stated as fact) | AG docs | Raw headers: "Trigno Discover (1.7.0)", "Avanti Sensor"; (c) says Delsys Trigno; (a) describes a custom DAQ with Raspberry Pi hub | **Conflict between sources** | Report what the file headers and (c) state, and note that (a) differs |
| D17 | Spectral power above 74.07 Hz = 3.72 % ± 1.99 % | AG docs | Welch estimate on all 361 raw trials (mean removed): 19.0 % ± 10.3 % above 74.07 Hz; 33.1 % ± 12.4 % below 20 Hz; median frequency 35.1 Hz; no prominent 50 Hz peak. (The first 72-trial sample happened to give almost the same mean, 19.0 % ± 10.3 %.) | **Not reproduced; replaced** | AG spectral numbers are not used. The manuscript reports the new estimate with its method (§2.9, §3.5, figure S4) |
| D18 | Dataset citation "SDALLE: A Multimodal Dataset …", Zenodo DOI attached to the article | README, CITATION.cff, dossier | Correct: El-Khoreby *et al* 2026 *Appl. Syst. Innov.* 9 13 (doi:10.3390/asi9010013); Abdellatif Hamed Ibrahim *et al* 2025 Zenodo doi:10.5281/zenodo.14841611; Farouk *et al* 2026 *Sci. Rep.* 16 26180 | **Corrected** | Cite all three correctly |
| D19 | Synchronisation | AG docs | Raw files carry no hardware timestamp or trigger channel; (c) says the streams were "inherently synchronised … common timestamp reference within the Trigno system" | **Clarified** | Report the claim in (c) and state that it cannot be independently verified from the released files |
| D20 | Ethics: ERUFE-MR-26-001 for the "original collection" | V1 records | Approval dated 13 May 2026, after the Feb 2025 collection; (a) names a different body | **Unresolved** | See ETHICS_AND_CONSENT_AUDIT |
| D21 | Class-wise recall values | Dossier | Mean-of-runs definition reproduced; pooled-window values differ by up to 1.1 pp | **Clarified** | State the definition |
| D22 | Tier 3 "CLI verified" | AG handoff | Only `--help` was run; training reads `../V2/data/processed`; the data-building code is not in the release | **Clarified** | Do not claim full end-to-end reproducibility |
| D23 | Archive hash 10bd9f20… | Dossier, executive summary | Current archive: 787ff472… (rewritten 13 Nov 06:48); companion archive 00ddeff0… | **Resolved** | Archive hashes are not cited in the manuscript |
| D24 | E4 is "the identical configuration" in V1 and V2 | V1/V2 documents | The V1 release (commit f2be710) trained with ReduceLROnPlateau on the training loss; the V2 preliminary and main runs used cosine annealing. Architecture and other hyperparameters are the same | **Clarified** | Explains part of the difference between V1's E4 result (71.65 %) and V2's (69.07 %). Relevant to the cover letter, not to the manuscript |
| D25 | Condition names E3-D and E4 | all project files | Internal labels | **Renamed** | The manuscript uses rate-matched (RM) and native-rate (NR). Data files in `05_TABLES` keep the internal labels |
| D26 | Preliminary run "showed E3-D ahead" | AG research history | Preliminary seed-42 run: mean difference +1.8 pp, rate-matched ahead in 4 of 9 participants | **Clarified** | Reported in §3.6 as inconclusive |
| D27 | Computing environment "desktop" | AG docs | Project log: Darwin arm64 (kernel build T8132), Python 3.13.12, torch 2.10.0; author states Apple MacBook Air M4 13-inch | **Corrected** | Methods §2.6 |

## Additions of 14 November 2026 (audit for manuscript v2.1)

- **D28. Analysis choices not in the protocol.** The protocol does not state a significance level, the exact or asymptotic test, the bootstrap type or the seed aggregation. The earliest dated copy of the analysis script that fixes them is from 19 October 2026, when 80 of 90 runs were complete. Resolved by disclosure: section 2.8, table 3 and supplementary section S3 label each analysis.
- **D29. Interrupted study and regenerated arrays.** 80 runs were completed on 8–15 October 2026; the last ten (RM fold 9 and NR folds 1–9, seed 7777) on 6–7 November 2026, after the processed arrays had been regenerated on 6 November. Tested: all 18 arrays regenerate bit-identically from the raw files; omitting seed 7777 gives +3.49 points, p = 0.039. Disclosed in section 2.9 and supplementary section S2. That the first 80 runs used identical arrays is an inference.
- **D30. Training script and model files postdate the runs.** The archived `robustness_train.py` and `src/models.py` are dated 12 November 2026. The 19 October version of the training script has the same data loading, seeding, training and metric code apart from an overwrite guard; the model classes are identical to the module imported during training. Documented in the release (`provenance/`, README).
- **D31. V1 Zenodo record appears to be a manual upload.** See `10_RELEASE_V2/RELEASE_AUDIT.md`, section 6. It decides the route by which V2 can stay under the Concept DOI 10.5281/zenodo.22649504.
- **No computational error was found** in the 90 runs, the processed arrays or the statistics (`STATISTICAL_AUDIT_90_RUNS.md`).
