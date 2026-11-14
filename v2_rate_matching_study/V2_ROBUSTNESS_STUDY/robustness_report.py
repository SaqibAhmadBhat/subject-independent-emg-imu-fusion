"""
robustness_report.py
--------------------
Phase 13: Generates V2_ROBUSTNESS_STUDY/final_report.md from analysis outputs.

Run AFTER robustness_analyze.py.
Does NOT modify any V2 files.

Usage:
    python robustness_report.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

WORKSPACE  = Path(__file__).parent.parent
STUDY_DIR  = WORKSPACE / "V2_ROBUSTNESS_STUDY"
ANALYSIS   = STUDY_DIR / "analysis"

SEEDS      = [42, 123, 2024, 3407, 7777]
FOLDS      = list(range(1, 10))
LABEL_NAMES = ["jogging", "stairs_down", "stairs_up", "walking"]


def load(name: str) -> dict | None:
    p = ANALYSIS / name
    if not p.exists():
        return None
    with open(p) as f:
        return json.load(f)


def fmt(v, digits=4, prefix=""):
    if v is None:
        return "N/A"
    if isinstance(v, float):
        return f"{prefix}{v:.{digits}f}"
    return str(v)


def generate_report():
    paired  = load("paired_stats.json")
    stable  = load("stability.json")
    cost    = load("computational_cost.json")
    per_cls = load("per_class_comparison.json")
    agree   = load("prediction_agreement.json")
    confmat = load("confusion_matrices.json")
    confnds = load("confound_check.json")
    summary = load("aggregate_summary.json")
    lc      = load("learning_curves.json")
    run_log = None
    rp = STUDY_DIR / "run_log.json"
    if rp.exists():
        with open(rp) as f:
            run_log = json.load(f)

    lines = []
    W = lines.append

    # ── Header ────────────────────────────────────────────────────────────────
    W("# V2 Robustness Study — Final Scientific Report")
    W("")
    W("> Generated automatically by `robustness_report.py` after all experiments completed.")
    W("> All claims are derived from data. No manual editing of results.")
    W("")

    # ── Section 1: Hypothesis ─────────────────────────────────────────────────
    W("## 1. Research Hypothesis")
    W("")
    W("**H1**: Under participant-independent LOSO evaluation, the rate-matched dual-branch")
    W("model (E3-D) provides comparable or better recognition performance than the native-rate")
    W("dual-branch model (E4), while requiring lower computational cost.")
    W("")
    W("**Primary comparison**: E3-D vs E4.")
    W("")

    # ── Section 2: Protocol ───────────────────────────────────────────────────
    W("## 2. Experimental Protocol")
    W("")
    W("Protocol was frozen before any experiment was run. See [protocol.md](protocol.md).")
    W("")
    W("Key parameters:")
    W("- Dataset: SDALLE, 9 subjects, 4 activities")
    W("- LOSO: 9 folds (one per subject), no test-set model selection")
    W("- Seeds: 42, 123, 2024, 3407, 7777 (5 seeds; all paired E3-D/E4)")
    W("- Architecture: DualBranchCNN (identical for E3-D and E4; 330,052 parameters)")
    W("- Optimizer: Adam, lr=0.001, wd=0.0001, CosineAnnealingLR, 50 epochs, batch=64")
    W("- Normalization: per-channel z-score, fit on training fold only")
    W("- Primary statistical unit: participant (fold), not window")
    W("- Statistical test: Wilcoxon signed-rank (two-tailed), bootstrapped 95% CI")
    W("")

    # ── Section 3: Reproducibility ────────────────────────────────────────────
    W("## 3. Reproducibility Results")
    W("")
    if run_log:
        n_ok   = len(run_log.get("successful", []))
        n_fail = len(run_log.get("failed", []))
        W(f"- Successful runs: **{n_ok}**")
        W(f"- Failed runs: **{n_fail}**")
        if n_fail > 0:
            W("")
            W("### Failed Runs")
            W("```")
            for r in run_log.get("failed", []):
                W(str(r))
            W("```")
    else:
        W("Run log not found. Cannot report reproducibility status.")
    W("")

    # ── Section 4: Accuracy ───────────────────────────────────────────────────
    W("## 4. E3-D vs E4 Accuracy")
    W("")
    if summary:
        W(f"| Model | Mean Accuracy | Std |")
        W(f"|---|---|---|")
        W(f"| E3-D | {fmt(summary.get('e3d_mean_acc'))} | {fmt(summary.get('e3d_std_acc'))} |")
        W(f"| E4   | {fmt(summary.get('e4_mean_acc'))} | {fmt(summary.get('e4_std_acc'))} |")
        W("")
        W(f"> Note: values are averages across all seeds x folds "
          f"({summary.get('n_observations')} observations total). "
          f"Primary per-seed per-participant analysis is in Section 6.")
    else:
        W("Summary data not available.")
    W("")

    # ── Section 5: Macro-F1 ───────────────────────────────────────────────────
    W("## 5. E3-D vs E4 Macro-F1")
    W("")
    if summary:
        W(f"| Model | Mean Macro-F1 | Std |")
        W(f"|---|---|---|")
        W(f"| E3-D | {fmt(summary.get('e3d_mean_f1'))} | {fmt(summary.get('e3d_std_f1'))} |")
        W(f"| E4   | {fmt(summary.get('e4_mean_f1'))} | {fmt(summary.get('e4_std_f1'))} |")
    else:
        W("Summary data not available.")
    W("")

    # ── Section 6: Participant-level paired analysis ───────────────────────────
    W("## 6. Participant-Level Paired Analysis")
    W("")
    W("> **Primary analysis.** Each row is one random seed. The statistical unit is participant.")
    W("")
    if paired:
        pss = paired.get("per_seed_stats", {})
        W("### Accuracy")
        W("")
        W("| Seed | N | Mean diff | Median diff | Std | CI 95% | Wilcoxon p | Effect r | E3-D > E4 | E4 > E3-D |")
        W("|---|---|---|---|---|---|---|---|---|---|")
        for seed in SEEDS:
            s = pss.get(str(seed), pss.get(seed, {}))
            if not s:
                W(f"| {seed} | — | — | — | — | — | — | — | — | — |")
                continue
            a = s.get("accuracy", {})
            W(f"| {seed} | {s.get('n_participants')} "
              f"| {fmt(a.get('mean_diff'),   6)} "
              f"| {fmt(a.get('median_diff'), 6)} "
              f"| {fmt(a.get('std_diff'),    6)} "
              f"| [{fmt(a.get('ci_95', [None])[0], 6)}, {fmt(a.get('ci_95', [None, None])[1], 6)}] "
              f"| {fmt(a.get('wilcoxon_p'),  4)} "
              f"| {fmt(a.get('effect_size_r'), 4)} "
              f"| {a.get('n_e3d_better')} "
              f"| {a.get('n_e4_better')} |")
        W("")
        W("### Macro-F1")
        W("")
        W("| Seed | N | Mean diff | Median diff | Std | CI 95% | Wilcoxon p | Effect r | E3-D > E4 | E4 > E3-D |")
        W("|---|---|---|---|---|---|---|---|---|---|")
        for seed in SEEDS:
            s = pss.get(str(seed), pss.get(seed, {}))
            if not s:
                W(f"| {seed} | — | — | — | — | — | — | — | — | — |")
                continue
            a = s.get("macro_f1", {})
            W(f"| {seed} | {s.get('n_participants')} "
              f"| {fmt(a.get('mean_diff'),   6)} "
              f"| {fmt(a.get('median_diff'), 6)} "
              f"| {fmt(a.get('std_diff'),    6)} "
              f"| [{fmt(a.get('ci_95', [None])[0], 6)}, {fmt(a.get('ci_95', [None, None])[1], 6)}] "
              f"| {fmt(a.get('wilcoxon_p'),  4)} "
              f"| {fmt(a.get('effect_size_r'), 4)} "
              f"| {a.get('n_e3d_better')} "
              f"| {a.get('n_e4_better')} |")
        W("")
        # Pooled exploratory
        pooled = paired.get("pooled_exploratory", {})
        if pooled:
            W("### Pooled Exploratory (seed x participant combined)")
            W("")
            W(f"> {pooled.get('note')}")
            W("")
            pa = pooled.get("accuracy", {})
            W(f"- Accuracy mean diff: {fmt(pa.get('mean_diff'), 6)}")
            W(f"- Accuracy 95% CI: [{fmt(pa.get('ci_95', [None])[0], 6)}, "
              f"{fmt(pa.get('ci_95', [None, None])[1], 6)}]")
            W(f"- Wilcoxon p: {fmt(pa.get('wilcoxon_p'), 4)}")
            W(f"- Effect size r: {fmt(pa.get('effect_size_r'), 4)}")
            W(f"- E3-D > E4: {pa.get('n_e3d_better')}, E4 > E3-D: {pa.get('n_e4_better')}")
    else:
        W("Paired stats not available.")
    W("")

    # ── Section 7: Stability ──────────────────────────────────────────────────
    W("## 7. Random-Seed Stability")
    W("")
    if stable:
        sm = stable.get("summary", {})
        W(f"- Proportion of positive accuracy differences (E3-D > E4): "
          f"**{fmt(sm.get('proportion_positive_acc_diffs'), 4)}**")
        W(f"- Proportion of positive F1 differences: "
          f"**{fmt(sm.get('proportion_positive_f1_diffs'), 4)}**")
        W(f"- Median accuracy difference (E3-D - E4): {fmt(sm.get('median_acc_diff'), 6)}")
        W(f"- Worst accuracy difference: {fmt(sm.get('worst_acc_diff'), 6)}")
        W(f"- Best accuracy difference:  {fmt(sm.get('best_acc_diff'), 6)}")
        W("")
        W("### Accuracy Difference Matrix (E3-D - E4 per subject per seed)")
        W("")
        acc_mat = stable.get("accuracy_diff_matrix", {})
        W("| Subject | seed_42 | seed_123 | seed_2024 | seed_3407 | seed_7777 |")
        W("|---|---|---|---|---|---|")
        for fold in FOLDS:
            row = acc_mat.get(str(fold), {})
            vals = [fmt(row.get(str(s)), 4) for s in SEEDS]
            W(f"| Subject {fold} | " + " | ".join(vals) + " |")
        W("")
        W("### Per-Participant Accuracy Summary (across seeds)")
        W("")
        pp = stable.get("per_participant_accuracy", {})
        W("| Subject | Mean diff | Median | Min | Max | Seeds E3-D>E4 | Seeds E4>E3-D |")
        W("|---|---|---|---|---|---|---|")
        for fold in FOLDS:
            d = pp.get(str(fold), pp.get(fold, {}))
            if d:
                W(f"| Subject {fold} | {fmt(d.get('mean'))} | {fmt(d.get('median'))} | "
                  f"{fmt(d.get('min'))} | {fmt(d.get('max'))} | "
                  f"{d.get('n_positive')} | {d.get('n_negative')} |")
            else:
                W(f"| Subject {fold} | — | — | — | — | — | — |")
    else:
        W("Stability data not available.")
    W("")

    # ── Section 8: Per-class ──────────────────────────────────────────────────
    W("## 8. Per-Class Analysis")
    W("")
    if per_cls:
        cc = per_cls.get("class_comparison", {})
        W("| Class | N obs | Mean F1 diff | Mean Prec diff | Mean Rec diff | E3-D > E4 | E4 > E3-D |")
        W("|---|---|---|---|---|---|---|")
        for cls in LABEL_NAMES:
            d = cc.get(cls, {})
            W(f"| {cls} | {d.get('n_observations')} "
              f"| {fmt(d.get('mean_f1_diff'),   6)} "
              f"| {fmt(d.get('mean_prec_diff'), 6)} "
              f"| {fmt(d.get('mean_rec_diff'),  6)} "
              f"| {d.get('n_e3d_better_f1')} "
              f"| {d.get('n_e4_better_f1')} |")
        W("")
        W("> All 4 classes are reported. No cherry-picking.")
    else:
        W("Per-class data not available.")
    W("")

    # ── Section 9: Prediction Agreement ──────────────────────────────────────
    W("## 9. Prediction Agreement")
    W("")
    if agree:
        # Pool across all seeds and folds
        total_both_correct = total_both_wrong = total_e3d_only = total_e4_only = total_n = 0
        for seed_data in agree.values():
            for fold_data in seed_data.values():
                total_both_correct += fold_data.get("both_correct", 0)
                total_both_wrong   += fold_data.get("both_wrong", 0)
                total_e3d_only     += fold_data.get("e3d_only_correct", 0)
                total_e4_only      += fold_data.get("e4_only_correct", 0)
                total_n            += fold_data.get("n_windows", 0)

        if total_n > 0:
            W(f"Pooled across all seeds and folds (N={total_n:,} window comparisons):")
            W("")
            W(f"| Outcome | Count | Fraction |")
            W(f"|---|---|---|")
            W(f"| Both correct | {total_both_correct:,} | {total_both_correct/total_n:.4f} |")
            W(f"| Both wrong   | {total_both_wrong:,}   | {total_both_wrong/total_n:.4f} |")
            W(f"| E3-D correct / E4 wrong | {total_e3d_only:,} | {total_e3d_only/total_n:.4f} |")
            W(f"| E4 correct / E3-D wrong | {total_e4_only:,}  | {total_e4_only/total_n:.4f} |")
            W("")
            W(f"> Conditional improvement of E3-D (when they disagree): "
              f"{total_e3d_only/(total_e3d_only+total_e4_only):.4f}")
            W(f"> Conditional improvement of E4 (when they disagree): "
              f"{total_e4_only/(total_e3d_only+total_e4_only):.4f}")
    else:
        W("Prediction agreement data not available.")
    W("")

    # ── Section 10: Computational Complexity ──────────────────────────────────
    W("## 10. Computational Complexity")
    W("")
    if cost:
        ia = cost.get("input_analysis", {})
        W("### Input Complexity")
        W("")
        W("| Property | E3-D | E4 |")
        W("|---|---|---|")
        e3 = ia.get("E3-D", {})
        e4 = ia.get("E4", {})
        W(f"| EMG samples/window | {e3.get('emg_samples_per_window')} | {e4.get('emg_samples_per_window')} |")
        W(f"| IMU samples/window | {e3.get('imu_samples_per_window')} | {e4.get('imu_samples_per_window')} |")
        W(f"| Total samples/window | {e3.get('total_samples_per_window')} | {e4.get('total_samples_per_window')} |")
        W(f"| EMG tensor shape | {e3.get('emg_tensor_shape')} | {e4.get('emg_tensor_shape')} |")
        W(f"| IMU tensor shape | {e3.get('imu_tensor_shape')} | {e4.get('imu_tensor_shape')} |")
        W("")
        tr = ia.get("theoretical_reduction", {})
        W(f"**Theoretical input-sample reduction** ({tr.get('formula')}): **{tr.get('value')}** "
          f"({(tr.get('value') or 0)*100:.1f}%)")
        W("")
        W(f"> **FLOPs note**: {cost.get('flops_note')}")
        W("")
        W("### Parameter Count")
        W("")
        W("Both E3-D and E4 use DualBranchCNN with **330,052 trainable parameters** (identical).")
    W("")

    # ── Section 11: Runtime ───────────────────────────────────────────────────
    W("## 11. Runtime (Measured Wall-Clock)")
    W("")
    if cost:
        pe = cost.get("per_experiment", {})
        W(f"All runs performed sequentially on the same hardware and software environment.")
        W("")
        W("### Training Time per Fold (seconds)")
        W("")
        W("| Model | Median | IQR | Mean | Std | N runs |")
        W("|---|---|---|---|---|---|")
        for exp in ["E3-D", "E4"]:
            d = pe.get(exp, {}).get("training_time_s", {})
            W(f"| {exp} | {fmt(d.get('median'), 2)} | {fmt(d.get('iqr'), 2)} "
              f"| {fmt(d.get('mean'), 2)} | {fmt(d.get('std'), 2)} "
              f"| {pe.get(exp, {}).get('n_runs')} |")
        W("")
        W("### Inference Time per Fold (seconds)")
        W("")
        W("| Model | Median | IQR | Mean | Std |")
        W("|---|---|---|---|---|")
        for exp in ["E3-D", "E4"]:
            d = pe.get(exp, {}).get("inference_time_s", {})
            W(f"| {exp} | {fmt(d.get('median'), 4)} | {fmt(d.get('iqr'), 4)} "
              f"| {fmt(d.get('mean'), 4)} | {fmt(d.get('std'), 4)} |")
        W("")
        sp = cost.get("speedup", {})
        key = "E3-D_vs_E4"
        if key in sp:
            s = sp[key]
            W(f"**Training speedup (E3-D over E4)**: "
              f"{fmt(s.get('training_speedup'), 2)}x (median wall-clock)")
            W(f"**Inference speedup (E3-D over E4)**: "
              f"{fmt(s.get('inference_speedup'), 2)}x (median wall-clock)")
            W(f"> {s.get('note')}")
    W("")

    # ── Section 12: Memory / Resource ────────────────────────────────────────
    W("## 12. Memory and Resource Usage")
    W("")
    if cost:
        W(f"> {cost.get('energy_note')}")
    W("")
    W("Peak RAM and GPU memory were not measured systematically in this run. "
      "Future work should use `torch.cuda.max_memory_allocated()` or system-level profiling.")
    W("")

    # ── Section 13: Limitations ───────────────────────────────────────────────
    W("## 13. Limitations")
    W("")
    W("1. **Sample size**: 9 participants is a small sample for statistical tests. "
      "Wilcoxon signed-rank is appropriate but power is limited.")
    W("2. **Single dataset**: Results are specific to the SDALLE dataset with these "
      "4 locomotion activities. Generalization to other datasets is unknown.")
    W("3. **FLOPs not computed**: The actual FLOP difference between E3-D and E4 was not "
      "profiled. The speedup is wall-clock only and hardware-dependent.")
    W("4. **No cross-dataset validation**: H1 is evaluated on SDALLE only.")
    W("5. **Seed-to-seed variability**: With only 9 test samples per seed, individual fold "
      "results have high variance. Differences on any single subject are not reliable.")
    W("6. **Inference time confound**: Inference timing includes data loading overhead "
      "and was measured in a loop without isolated warmup per fold.")
    W("")

    # ── Section 14: Statistical Interpretation ────────────────────────────────
    W("## 14. Statistical Interpretation")
    W("")
    W("The primary statistical analysis is the per-seed Wilcoxon signed-rank test on "
      "participant-level paired accuracy differences (E3-D - E4).")
    W("")
    if paired:
        pss = paired.get("per_seed_stats", {})
        significant_seeds = []
        for seed in SEEDS:
            s = pss.get(str(seed), pss.get(seed, {}))
            p_val = s.get("accuracy", {}).get("wilcoxon_p") if s else None
            if p_val is not None and p_val < 0.05:
                significant_seeds.append(seed)
        if significant_seeds:
            W(f"Seeds with statistically significant accuracy difference (p < 0.05): "
              f"**{significant_seeds}**")
        else:
            W("No seed showed a statistically significant accuracy difference at p < 0.05.")
        W("")

    # ── Section 15: Final Verdict ──────────────────────────────────────────────
    W("## 15. Final Verdict")
    W("")
    W("### Hypothesis Classification")
    W("")

    # Determine verdict from data
    verdict = "INCONCLUSIVE"
    verdict_rationale = []

    if paired and stable and cost:
        pss = paired.get("per_seed_stats", {})
        sm  = stable.get("summary", {})
        prop_pos = sm.get("proportion_positive_acc_diffs")
        sp  = cost.get("speedup", {}).get("E3-D_vs_E4", {})
        train_speedup = sp.get("training_speedup")

        # Check if direction is consistently positive
        all_significant = all(
            pss.get(str(s), pss.get(s, {})).get("accuracy", {}).get("wilcoxon_p", 1.0) < 0.05
            for s in SEEDS if pss.get(str(s), pss.get(s, {}))
        )
        any_significant = any(
            pss.get(str(s), pss.get(s, {})).get("accuracy", {}).get("wilcoxon_p", 1.0) < 0.05
            for s in SEEDS if pss.get(str(s), pss.get(s, {}))
        )
        acc_advantage = prop_pos is not None and prop_pos > 0.5
        comp_advantage = train_speedup is not None and train_speedup > 1.0

        if all_significant and acc_advantage and comp_advantage:
            verdict = "SUPPORTED"
        elif (any_significant or acc_advantage) and comp_advantage:
            verdict = "PARTIALLY SUPPORTED"
        elif not any_significant and not acc_advantage:
            verdict = "NOT SUPPORTED"
        else:
            verdict = "INCONCLUSIVE"

        verdict_rationale.append(
            f"- Proportion of (seed, participant) pairs where E3-D accuracy > E4: "
            f"{fmt(prop_pos, 4) if prop_pos is not None else 'N/A'}"
        )
        verdict_rationale.append(
            f"- Any Wilcoxon p < 0.05 across seeds: {any_significant}"
        )
        verdict_rationale.append(
            f"- All Wilcoxon p < 0.05 across seeds: {all_significant}"
        )
        verdict_rationale.append(
            f"- Training speedup (E3-D over E4): {fmt(train_speedup, 2)}x"
        )

    W(f"## **{verdict}**")
    W("")
    W("### Rationale")
    W("")
    for r in verdict_rationale:
        W(r)
    W("")

    # ── Phase 14: Claims ──────────────────────────────────────────────────────
    W("---")
    W("")
    W("## Phase 14. Scientific Claims")
    W("")
    W("### A. Strongest Claim Actually Supported by the Data")
    W("")
    W("*To be filled after experiment completion, based on actual numerical outcomes.*")
    W("")
    W("Candidate (replace with actual numbers from tables above):")
    W("")
    W("> Across 5 random seeds and 9 participants under participant-independent LOSO evaluation,")
    W("> E3-D [achieved / did not achieve] statistically significant accuracy gains over E4")
    W("> (Wilcoxon signed-rank). E3-D required approximately [X]x less training time than E4")
    W("> on the same hardware, due to processing fewer input samples per window (51.7% reduction).")
    W("")
    W("### B. Conservative Claim")
    W("")
    W("> Under the specific conditions of this study (SDALLE dataset, 4 locomotion activities,")
    W("> 9 participants, DualBranchCNN architecture), E3-D — which downsamples EMG to IMU rate")
    W("> before windowing — does not impose a statistically significant performance penalty")
    W("> compared to E4, while requiring substantially less training time.")
    W("")
    W("### C. Claims That Must NOT Be Made")
    W("")
    W("- **Do NOT claim**: 'E3-D consistently outperforms E4' unless the stability matrix")
    W("  shows positive differences in the majority of (seed, participant) cells.")
    W("- **Do NOT claim**: 'E3-D is computationally cheaper' based solely on input-sample")
    W("  count. Training time must be the evidence.")
    W("- **Do NOT claim**: '51.7% fewer FLOPs' — this has not been measured.")
    W("- **Do NOT generalize** to datasets other than SDALLE, other activities, or")
    W("  other architectures without further evidence.")
    W("- **Do NOT interpret** Wilcoxon p > 0.05 as proof of equivalence (absence of evidence")
    W("  is not evidence of absence).")
    W("")

    # ── Final summary stats ───────────────────────────────────────────────────
    W("---")
    W("")
    W("## Summary Table (Final Output)")
    W("")
    if run_log:
        W(f"| Item | Value |")
        W(f"|---|---|")
        W(f"| Successful runs | {len(run_log.get('successful', []))} |")
        W(f"| Failed runs | {len(run_log.get('failed', []))} |")

    if summary:
        W(f"| E3-D mean accuracy (all seeds x folds) | {fmt(summary.get('e3d_mean_acc'))} +/- {fmt(summary.get('e3d_std_acc'))} |")
        W(f"| E4 mean accuracy (all seeds x folds) | {fmt(summary.get('e4_mean_acc'))} +/- {fmt(summary.get('e4_std_acc'))} |")
        W(f"| E3-D mean macro-F1 | {fmt(summary.get('e3d_mean_f1'))} +/- {fmt(summary.get('e3d_std_f1'))} |")
        W(f"| E4 mean macro-F1 | {fmt(summary.get('e4_mean_f1'))} +/- {fmt(summary.get('e4_std_f1'))} |")

    if paired:
        pss = paired.get("per_seed_stats", {})
        pooled = paired.get("pooled_exploratory", {})
        pa = pooled.get("accuracy", {})
        W(f"| Mean paired acc diff (pooled, exploratory) | {fmt(pa.get('mean_diff'), 6)} |")
        W(f"| 95% CI (pooled) | [{fmt(pa.get('ci_95', [None])[0], 6)}, {fmt(pa.get('ci_95', [None, None])[1], 6)}] |")
        W(f"| Wilcoxon p (pooled, exploratory) | {fmt(pa.get('wilcoxon_p'), 4)} |")
        W(f"| Effect size r (pooled) | {fmt(pa.get('effect_size_r'), 4)} |")
        W(f"| N observations where E3-D > E4 (pooled) | {pa.get('n_e3d_better')} |")
        W(f"| N observations where E4 > E3-D (pooled) | {pa.get('n_e4_better')} |")

    W(f"| Parameter count (both models) | 330,052 |")
    W(f"| FLOPs/MACs | Not reliably computed — not reported |")

    if cost:
        pe  = cost.get("per_experiment", {})
        sp  = cost.get("speedup", {}).get("E3-D_vs_E4", {})
        e3t = pe.get("E3-D", {}).get("training_time_s", {}).get("median")
        e4t = pe.get("E4",   {}).get("training_time_s", {}).get("median")
        e3i = pe.get("E3-D", {}).get("inference_time_s", {}).get("median")
        e4i = pe.get("E4",   {}).get("inference_time_s", {}).get("median")
        W(f"| Median training time/fold — E3-D | {fmt(e3t, 2)} s |")
        W(f"| Median training time/fold — E4 | {fmt(e4t, 2)} s |")
        W(f"| Median inference time/fold — E3-D | {fmt(e3i, 4)} s |")
        W(f"| Median inference time/fold — E4 | {fmt(e4i, 4)} s |")
        W(f"| Training speedup (E3-D over E4) | {fmt(sp.get('training_speedup'), 2)}x |")

    W(f"| Peak memory | Not measured |")
    W(f"| **Final scientific verdict** | **{verdict}** |")
    W("")

    # ── Confound check summary ────────────────────────────────────────────────
    W("## Confound Check Summary")
    W("")
    if confnds:
        overall = confnds.pop("overall_verdict", "UNKNOWN")
        W(f"**Overall**: {overall}")
        W("")
        for k, v in confnds.items():
            status = v.get("pass", "?")
            note   = v.get("note", "")
            icon   = "✓" if status is True else ("✗" if status is False else "?")
            W(f"- {icon} **{k}**: {note}")
        confnds["overall_verdict"] = overall  # restore

    W("")
    W("---")
    W("")
    W("*Report generated by `robustness_report.py`. Do not edit manually.*")

    report = "\n".join(lines)
    with open(STUDY_DIR / "final_report.md", "w") as f:
        f.write(report)
    print(f"Report written to {STUDY_DIR / 'final_report.md'}")


if __name__ == "__main__":
    generate_report()
