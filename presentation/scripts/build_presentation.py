#!/usr/bin/env python3
"""
presentation/scripts/build_presentation.py
------------------------------------------
Generates a complete, publication-grade 24-slide research presentation (16:9 widescreen)
for the Multimodal sEMG-IMU Fusion Study using python-pptx.
Output: presentation/EMG_IMU_Research_Presentation.pptx
"""
import os
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
OUT_PPTX = REPO_ROOT / "presentation" / "EMG_IMU_Research_Presentation.pptx"
FIG_DIR = REPO_ROOT / "presentation" / "figures"

# Theme Colors
BG_COLOR = RGBColor(15, 23, 42)        # Slate 900
CARD_BG = RGBColor(30, 41, 59)         # Slate 800
CARD_BORDER = RGBColor(51, 65, 85)     # Slate 700
ACCENT_BLUE = RGBColor(14, 165, 233)   # Sky 500
ACCENT_PURPLE = RGBColor(139, 92, 246) # Violet 500
ACCENT_GREEN = RGBColor(16, 185, 129)  # Emerald 500
ACCENT_AMBER = RGBColor(245, 158, 11)  # Amber 500
ACCENT_ROSE = RGBColor(244, 63, 94)    # Rose 500
TEXT_WHITE = RGBColor(248, 250, 252)   # Slate 50
TEXT_MUTED = RGBColor(148, 163, 184)   # Slate 400
TEXT_LIGHT = RGBColor(226, 232, 240)   # Slate 200


def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def set_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, category_text=""):
        if category_text:
            cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
            tf_cat = cat_box.text_frame
            tf_cat.word_wrap = True
            p_cat = tf_cat.paragraphs[0]
            p_cat.text = category_text.upper()
            p_cat.font.size = Pt(11)
            p_cat.font.bold = True
            p_cat.font.color.rgb = ACCENT_BLUE
            
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.8))
        tf = t_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(24)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

    def add_card(slide, left, top, width, height, title="", fill=CARD_BG, border=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = fill
        card.line.color.rgb = border
        card.line.width = Pt(1.5)
        
        if title:
            tb = slide.shapes.add_textbox(Inches(left + 0.25), Inches(top + 0.2), Inches(width - 0.5), Inches(0.5))
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = title
            p.font.size = Pt(14)
            p.font.bold = True
            p.font.color.rgb = TEXT_WHITE
            
        return card

    # ==================== SLIDE 1: Title & Project Identity ====================
    s1 = prs.slides.add_slide(blank_layout)
    set_background(s1)
    tb = s1.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(11.3), Inches(3.0))
    tf = tb.text_frame
    tf.word_wrap = True
    p0 = tf.paragraphs[0]
    p0.text = "BIOMEDICAL ENGINEERING & REHABILITATION ROBOTICS"
    p0.font.size = Pt(13); p0.font.bold = True; p0.font.color.rgb = ACCENT_BLUE; p0.space_after = Pt(14)
    p1 = tf.add_paragraph()
    p1.text = "Subject-Independent sEMG–IMU Sensor Fusion\nfor Human Activity Recognition"
    p1.font.size = Pt(32); p1.font.bold = True; p1.font.color.rgb = TEXT_WHITE; p1.space_after = Pt(16)
    p2 = tf.add_paragraph()
    p2.text = "A Controlled Empirical Robustness Study of Rate-Matching vs. Native-Rate Deep Fusion"
    p2.font.size = Pt(17); p2.font.color.rgb = TEXT_MUTED

    add_card(s1, 1.0, 4.8, 11.3, 1.8)
    tb_meta = s1.shapes.add_textbox(Inches(1.3), Inches(5.0), Inches(10.7), Inches(1.4))
    tf_meta = tb_meta.text_frame
    pm1 = tf_meta.paragraphs[0]
    pm1.text = "Research Software Release: Version 2.0.0 (Concept DOI: 10.5281/zenodo.22649504)"
    pm1.font.size = Pt(12); pm1.font.bold = True; pm1.font.color.rgb = ACCENT_GREEN; pm1.space_after = Pt(6)
    pm2 = tf_meta.add_paragraph()
    pm2.text = "Authors: Saqib Ahmad Bhat (0009-0003-9248-6174), Sona G (0000-0002-1786-4193), P. Subha Karuvelam (0000-0002-9958-6106)"
    pm2.font.size = Pt(11); pm2.font.color.rgb = TEXT_LIGHT; pm2.space_after = Pt(4)
    pm3 = tf_meta.add_paragraph()
    pm3.text = "SDALLE Benchmark (Zenodo 10.5281/zenodo.14841611) | GitHub: SaqibAhmadBhat/subject-independent-emg-imu-fusion"
    pm3.font.size = Pt(10.5); pm3.font.color.rgb = TEXT_MUTED

    # ==================== SLIDE 2: Executive Summary ====================
    s2 = prs.slides.add_slide(blank_layout)
    set_background(s2)
    add_header(s2, "Executive Summary: The Core Research Findings", "Study Overview")
    
    stats = [
        ("+3.83 pp", "Mean Accuracy Gap", "Rate-Matched (72.90%) outperforms Native-Rate (69.07%) across 5 seeds", ACCENT_BLUE, 0.8),
        ("p = 0.039", "Wilcoxon Signed-Rank", "Exact W = 5.0; 8 of 9 participants demonstrate positive accuracy gains", ACCENT_GREEN, 4.8),
        ("330,052", "Matched Parameters", "DualBranchCNN capacity strictly invariant across both experimental conditions", ACCENT_PURPLE, 8.8),
    ]
    for val, lbl, sub, col, left in stats:
        add_card(s2, left, 1.6, 3.7, 2.2)
        tb = s2.shapes.add_textbox(Inches(left + 0.25), Inches(1.8), Inches(3.2), Inches(1.8))
        tf = tb.text_frame
        p = tf.paragraphs[0]; p.text = val; p.font.size = Pt(36); p.font.bold = True; p.font.color.rgb = col
        p2 = tf.add_paragraph(); p2.text = f"{lbl}\n{sub}"; p2.font.size = Pt(11); p2.font.color.rgb = TEXT_LIGHT

    add_card(s2, 0.8, 4.2, 11.7, 2.7, title="Key Scientific Takeaways")
    tb_bot = s2.shapes.add_textbox(Inches(1.1), Inches(4.8), Inches(11.1), Inches(1.9))
    tf_bot = tb_bot.text_frame; tf_bot.word_wrap = True
    for b in [
        "Rigorous Experimental Protocol: 9-fold LOSO cross-validation evaluated across 5 random seeds (90 runs, 31,015 test windows per condition).",
        "Statistical Verification: Exact sign-flip permutation p = 0.031; two-stage hierarchical bootstrap 95% CI is [1.07, 6.65] pp.",
        "Ablation Discovery: Rate-matching sEMG via cubic spline expands the temporal receptive field (189 ms vs 22 ms), improving macro-locomotion coordination despite 19.0% super-Nyquist energy.",
        "Transparent Science: Negative participant outcome (P1 favors native-rate by -3.15 pp) disclosed and causally linked to reduced super-Nyquist energy (13.51%)."
    ]:
        p = tf_bot.add_paragraph(); p.text = "• " + b; p.font.size = Pt(11.5); p.font.color.rgb = TEXT_LIGHT; p.space_after = Pt(6)

    # ==================== SLIDE 3: Clinical & Engineering Relevance ====================
    s3 = prs.slides.add_slide(blank_layout)
    set_background(s3)
    add_header(s3, "Clinical & Engineering Relevance", "Domain Motivation")
    for i, (ct, cd, ca) in enumerate([
        ("Wearable Exoskeletons", "Active robotic orthoses require reliable, subject-independent locomotion mode classification to deliver seamless phase-dependent torque assistance without calibration delays.", ACCENT_BLUE),
        ("Intelligent Prosthetics", "Myoelectric lower-limb prostheses must combine neural intent (sEMG) with kinematic limb state (IMU) to prevent catastrophic stumble and fall events.", ACCENT_GREEN),
        ("Continuous Gait Biomarkers", "Longitudinal neuromotor monitoring in Parkinson's disease and post-stroke recovery demands models that generalize zero-shot to unseen patient anatomies.", ACCENT_PURPLE)
    ]):
        add_card(s3, 0.8 + i*4.0, 1.8, 3.7, 4.9, title=ct)
        tb = s3.shapes.add_textbox(Inches(1.0 + i*4.0), Inches(2.6), Inches(3.3), Inches(3.8))
        tf = tb.text_frame; tf.word_wrap = True
        p = tf.paragraphs[0]; p.text = cd; p.font.size = Pt(12.5); p.font.color.rgb = TEXT_LIGHT; p.space_after = Pt(14)
        p2 = tf.add_paragraph(); p2.text = "Core Deployment Challenge:\nSubject-dependent models fail on new individuals due to tissue conductivity, electrode placement, and anatomical variations. Robust subject-independence is mandatory."; p2.font.size = Pt(11); p2.font.color.rgb = TEXT_MUTED

    # ==================== SLIDE 4: Research Problem ====================
    s4 = prs.slides.add_slide(blank_layout)
    set_background(s4)
    add_header(s4, "The Multirate Multimodal Sensor Challenge", "Research Problem")
    add_card(s4, 0.8, 1.8, 5.6, 5.0, title="Asynchronous Sensor Rates")
    tb_l = s4.shapes.add_textbox(Inches(1.1), Inches(2.5), Inches(5.0), Inches(4.0))
    tf_l = tb_l.text_frame; tf_l.word_wrap = True
    for h, b in [
        ("sEMG Acquisition (~1259.26 Hz)", "High temporal frequency required to capture motor unit action potential (MUAP) frequency components (20-450 Hz). Yields 238 samples in a 200 ms window."),
        ("IMU Acquisition (~148.15 Hz)", "Lower mechanical sampling rate recording multi-axis accelerations and angular velocities. Yields 28 samples in a 200 ms window."),
        ("Dimensional Asymmetry", "Neural network fusion encoders cannot directly concatenate feature maps across temporal dimensions without resampling or disparate pooling factors.")
    ]:
        p = tf_l.add_paragraph(); p.text = h; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = ACCENT_BLUE
        p2 = tf_l.add_paragraph(); p2.text = b; p2.font.size = Pt(11); p2.font.color.rgb = TEXT_LIGHT; p2.space_after = Pt(10)

    add_card(s4, 6.8, 1.8, 5.7, 5.0, title="Architectural Dilemma")
    tb_r = s4.shapes.add_textbox(Inches(7.1), Inches(2.5), Inches(5.1), Inches(4.0))
    tf_r = tb_r.text_frame; tf_r.word_wrap = True
    for h, b in [
        ("Rate-Matching (Condition E3-D)", "Downsample sEMG to match IMU rate (148.15 Hz) via cubic spline interpolation. Standardizes temporal sequence length to 148 samples, but introduces spectral aliasing risks."),
        ("Native Multirate (Condition E4)", "Preserve raw sEMG at 1259.26 Hz (238 samples) and IMU at 148.15 Hz (148 samples). Retains full MUAP bandwidth, but creates asymmetric temporal receptive fields."),
        ("Fundamental Research Question", "Does preserving native sEMG sampling frequency outweigh the synchronization benefits of uniform rate-matching in subject-independent fusion?")
    ]:
        p = tf_r.add_paragraph(); p.text = h; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = ACCENT_PURPLE
        p2 = tf_r.add_paragraph(); p2.text = b; p2.font.size = Pt(11); p2.font.color.rgb = TEXT_LIGHT; p2.space_after = Pt(10)

    # ==================== SLIDE 5: Research Gap ====================
    s5 = prs.slides.add_slide(blank_layout)
    set_background(s5)
    add_header(s5, "Addressing Critical Gaps in Prior Literature", "Research Gap")
    for i, (gt, gb, gs) in enumerate([
        ("Conflicting Prior Claims", "Previous studies report contradictory outcomes regarding downsampling sEMG, but confounded resampling method with model capacity differences (e.g. comparing differing kernel sizes and channel widths).", ACCENT_ROSE),
        ("Single-Seed Vulnerability", "Much of the wearable sensor literature reports single-seed results or random participant splits that inflate accuracy and mask seed-induced variance components.", ACCENT_AMBER),
        ("Uncontrolled Receptive Fields", "Prior works rarely analyze how multirate pooling alters the effective physical duration spanned by convolutional kernels across modalities.", ACCENT_BLUE)
    ]):
        add_card(s5, 0.8 + i*4.0, 1.8, 3.7, 4.9, title=gt)
        tb = s5.shapes.add_textbox(Inches(1.0 + i*4.0), Inches(2.6), Inches(3.3), Inches(3.8))
        tf = tb.text_frame; tf.word_wrap = True
        p = tf.paragraphs[0]; p.text = gb; p.font.size = Pt(12); p.font.color.rgb = TEXT_LIGHT; p.space_after = Pt(14)
        p2 = tf.add_paragraph(); p2.text = f"Study V2 Innovation:\nStrict parameter matching (330,052 params), 5-seed replication, and explicit temporal receptive field decomposition."; p2.font.size = Pt(10.5); p2.font.color.rgb = gs

    # ==================== SLIDE 6: Hypotheses & Objectives ====================
    s6 = prs.slides.add_slide(blank_layout)
    set_background(s6)
    add_header(s6, "Research Hypotheses & Experimental Objectives", "Methodology")
    add_card(s6, 0.8, 1.8, 5.6, 5.0, title="Core Research Hypotheses")
    tb = s6.shapes.add_textbox(Inches(1.1), Inches(2.5), Inches(5.0), Inches(4.0))
    tf = tb.text_frame; tf.word_wrap = True
    for h, b in [
        ("Hypothesis 1 (Primary)", "Rate-matched fusion (E3-D) provides superior locomotion mode classification over native-rate fusion (E4) under strictly matched parameter budgets due to synchronous cross-modal temporal alignment."),
        ("Hypothesis 2 (Spectral Aliasing)", "Downsampling sEMG to 148.15 Hz without an anti-aliasing pre-filter folds super-Nyquist power (> 74.07 Hz) into the baseband, creating a participant-dependent aliasing penalty."),
        ("Hypothesis 3 (Seed Stability)", "Between-participant anatomical heterogeneity accounts for the majority of variance, but random seed initialization contributes non-trivial variance that requires multi-seed modeling.")
    ]:
        p = tf.add_paragraph(); p.text = h; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = ACCENT_GREEN
        p2 = tf.add_paragraph(); p2.text = b; p2.font.size = Pt(11); p2.font.color.rgb = TEXT_LIGHT; p2.space_after = Pt(10)

    add_card(s6, 6.8, 1.8, 5.7, 5.0, title="Operational Objectives")
    tb_r = s6.shapes.add_textbox(Inches(7.1), Inches(2.5), Inches(5.1), Inches(4.0))
    tf_r = tb_r.text_frame; tf_r.word_wrap = True
    for h, b in [
        ("Objective 1: Controlled Ablation", "Design a dual-branch 1D CNN with exactly 330,052 parameters for both rate-matched and native-rate pipelines."),
        ("Objective 2: Exhaustive 90-Run LOSO", "Execute 9-fold LOSO cross-validation across 5 seeds (42, 123, 2024, 3407, 7777) totaling 90 trained models and 62,030 evaluation inferences."),
        ("Objective 3: Rigorous Inference", "Apply non-parametric exact Wilcoxon, exact sign-flip permutation, and two-stage hierarchical bootstrap confidence intervals."),
        ("Objective 4: Full Transparency", "Release all 90 prediction CSVs, training logs, verification scripts, and preprocessed arrays under open-science DOIs.")
    ]:
        p = tf_r.add_paragraph(); p.text = h; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = ACCENT_BLUE
        p2 = tf_r.add_paragraph(); p2.text = b; p2.font.size = Pt(11); p2.font.color.rgb = TEXT_LIGHT; p2.space_after = Pt(8)

    # ==================== SLIDE 7: Benchmark Dataset ====================
    s7 = prs.slides.add_slide(blank_layout)
    set_background(s7)
    add_header(s7, "The SDALLE Public Benchmark Dataset", "Experimental Data")
    
    cards_data = [
        ("9 Participants", "Healthy adult cohort (P1–P9) performing continuous locomotor transitions", ACCENT_BLUE, 0.8),
        ("4 Activities", "Walking, Jogging, Stairs Up, Stairs Down (balanced natural locomotion)", ACCENT_GREEN, 3.8),
        ("361 Trials", "Validated continuous multi-sensor recordings under identical lab protocols", ACCENT_PURPLE, 6.8),
        ("56 Sensor Ch", "8-ch surface EMG (bipolar electrodes) + 48-ch IMU (accelerometer/gyro)", ACCENT_AMBER, 9.8),
    ]
    for val, lbl, col, left in cards_data:
        add_card(s7, left, 1.6, 2.7, 1.8)
        tb = s7.shapes.add_textbox(Inches(left + 0.2), Inches(1.8), Inches(2.3), Inches(1.4))
        tf = tb.text_frame
        p = tf.paragraphs[0]; p.text = val; p.font.size = Pt(22); p.font.bold = True; p.font.color.rgb = col
        p2 = tf.add_paragraph(); p2.text = lbl; p2.font.size = Pt(10.5); p2.font.color.rgb = TEXT_LIGHT

    add_card(s7, 0.8, 3.8, 11.7, 3.1, title="Rigorous Participant Test Window Distribution (6,203 Windows / Seed)")
    tb_w = s7.shapes.add_textbox(Inches(1.1), Inches(4.4), Inches(11.1), Inches(2.3))
    tf_w = tb_w.text_frame; tf_w.word_wrap = True
    p = tf_w.paragraphs[0]
    p.text = "Each participant acts as a strictly isolated test fold in 9-fold Leave-One-Subject-Out evaluation:"
    p.font.size = Pt(11.5); p.font.color.rgb = TEXT_LIGHT; p.space_after = Pt(8)
    
    p2 = tf_w.add_paragraph()
    p2.text = "• P1: 647 windows  |  • P2: 568 windows  |  • P3: 729 windows  |  • P4: 696 windows  |  • P5: 746 windows\n• P6: 722 windows  |  • P7: 654 windows  |  • P8: 690 windows  |  • P9: 751 windows  |  TOTAL: 6,203 windows"
    p2.font.size = Pt(12); p2.font.bold = True; p2.font.color.rgb = ACCENT_BLUE; p2.space_after = Pt(8)
    
    p3 = tf_w.add_paragraph()
    p3.text = "Data Availability: Fully public under CC BY 4.0 at Zenodo (DOI: 10.5281/zenodo.14841611). No proprietary patient data or restricted medical records used."
    p3.font.size = Pt(10.5); p3.font.color.rgb = TEXT_MUTED

    # ==================== SLIDE 8: Multimodal Signal Characteristics ====================
    s8 = prs.slides.add_slide(blank_layout)
    set_background(s8)
    add_header(s8, "Multimodal Sensor Properties: sEMG vs. IMU", "Signal Physics")
    add_card(s8, 0.8, 1.8, 5.6, 5.0, title="Surface Electromyography (sEMG)")
    tb_emg = s8.shapes.add_textbox(Inches(1.1), Inches(2.5), Inches(5.0), Inches(4.0))
    tf_emg = tb_emg.text_frame; tf_emg.word_wrap = True
    for h, b in [
        ("Source Physics", "Summation of motor unit action potentials (MUAPs) generated during muscle fiber depolarization."),
        ("Bandwidth & Sampling", "Dominant frequency range: 20–450 Hz. Acquired at ~1259.26 Hz (Nyquist: 629.63 Hz)."),
        ("Signal Nature", "Stochastic, zero-mean, interference pattern representing neural drive and muscular activation onset prior to mechanical movement (~30-50 ms electromechanical delay).")
    ]:
        p = tf_emg.add_paragraph(); p.text = h; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = ACCENT_BLUE
        p2 = tf_emg.add_paragraph(); p2.text = b; p2.font.size = Pt(11); p2.font.color.rgb = TEXT_LIGHT; p2.space_after = Pt(10)

    add_card(s8, 6.8, 1.8, 5.7, 5.0, title="Inertial Measurement Units (IMU)")
    tb_imu = s8.shapes.add_textbox(Inches(7.1), Inches(2.5), Inches(5.1), Inches(4.0))
    tf_imu = tb_imu.text_frame; tf_imu.word_wrap = True
    for h, b in [
        ("Source Physics", "Direct kinematic recording of tri-axial linear acceleration and angular velocity at segmental limb nodes."),
        ("Bandwidth & Sampling", "Human locomotion movement bandwidth: 0.5–15 Hz. Acquired at ~148.15 Hz (Nyquist: 74.07 Hz)."),
        ("Signal Nature", "Deterministic, quasi-periodic waveform reflecting gross limb mechanics, heel strike, and swing phase kinematics. Highly subject-specific due to biomechanical geometry.")
    ]:
        p = tf_imu.add_paragraph(); p.text = h; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = ACCENT_PURPLE
        p2 = tf_imu.add_paragraph(); p2.text = b; p2.font.size = Pt(11); p2.font.color.rgb = TEXT_LIGHT; p2.space_after = Pt(10)

    # ==================== SLIDE 9: Research Architecture ====================
    s9 = prs.slides.add_slide(blank_layout)
    set_background(s9)
    add_header(s9, "Research Architecture: Controlled Evaluation Framework", "System Design")
    
    add_card(s9, 0.8, 1.8, 11.7, 5.0, title="End-to-End Experimental Execution Workflow")
    tb = s9.shapes.add_textbox(Inches(1.1), Inches(2.5), Inches(11.1), Inches(4.0))
    tf = tb.text_frame; tf.word_wrap = True
    
    steps = [
        ("Stage 1: Raw Data Ingestion", "361 trials from SDALLE public benchmark ingested and validated against SHA-256 digests. Timestamps aligned across 8 sEMG and 48 IMU channels."),
        ("Stage 2: Sliding-Window Segmentation", "200 ms windows segmented with 50% overlap (100 ms step). E3-D uses cubic-spline interpolation without anti-aliasing pre-filtering to yield 148 samples; E4 retains 238 sEMG and 148 IMU samples."),
        ("Stage 3: Normalization", "Z-score normalization computed strictly within training folds to prevent test set data leakage."),
        ("Stage 4: Deep Multi-Branch Modeling", "DualBranchCNN (330,052 parameters) trained with AdamW, Cosine Annealing, and Focal Loss (γ = 2.0) across 9 LOSO folds and 5 random seeds (90 runs)."),
        ("Stage 5: Independent Statistical Verification", "Frozen predictions subjected to exact Wilcoxon signed-rank tests, exact sign-flip permutation tests (2⁹ = 512), and two-stage hierarchical bootstrap resampling.")
    ]
    for h, b in steps:
        p = tf.add_paragraph(); p.text = h; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = ACCENT_GREEN
        p2 = tf.add_paragraph(); p2.text = b; p2.font.size = Pt(11); p2.font.color.rgb = TEXT_LIGHT; p2.space_after = Pt(8)

    # ==================== SLIDE 10: Preprocessing & Rate-Matching ====================
    s10 = prs.slides.add_slide(blank_layout)
    set_background(s10)
    add_header(s10, "Preprocessing & Cubic-Spline Interpolation", "Signal Processing")
    
    add_card(s10, 0.8, 1.8, 5.6, 5.0, title="Condition E3-D: Cubic Spline Rate-Matching")
    tb = s10.shapes.add_textbox(Inches(1.1), Inches(2.5), Inches(5.0), Inches(4.0))
    tf = tb.text_frame; tf.word_wrap = True
    for h, b in [
        ("Mathematical Formulation", "Evaluated via scipy.interpolate.interp1d(kind='cubic') directly at synchronized IMU sample times t_IMU."),
        ("Resampling Frequency", "Downsamples sEMG from ~1259.26 Hz to ~148.15 Hz. Target Nyquist frequency f_N = 74.07 Hz."),
        ("Absence of Anti-Aliasing Pre-Filter", "No low-pass Butterworth pre-filter was applied prior to spline evaluation. 19.0% of cohort sEMG power residing above 74.07 Hz is folded into the baseband as aliased energy."),
        ("Architectural Impact", "Uniform sequence length (148) permits identical receptive field sample strides across both encoders.")
    ]:
        p = tf.add_paragraph(); p.text = h; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = ACCENT_BLUE
        p2 = tf.add_paragraph(); p2.text = b; p2.font.size = Pt(11); p2.font.color.rgb = TEXT_LIGHT; p2.space_after = Pt(10)

    add_card(s10, 6.8, 1.8, 5.7, 5.0, title="Condition E4: Native-Rate Multirate")
    tb = s10.shapes.add_textbox(Inches(7.1), Inches(2.5), Inches(5.1), Inches(4.0))
    tf = tb.text_frame; tf.word_wrap = True
    for h, b in [
        ("Mathematical Formulation", "Raw sEMG samples preserved at 1259.26 Hz. No temporal resampling or interpolation applied."),
        ("Bandwidth Retention", "Full MUAP frequency spectrum (up to 629.63 Hz) available to convolutional filters. Zero spectral aliasing."),
        ("Dimensional Asymmetry", "Yields 238 sEMG samples and 148 IMU samples per 200 ms window."),
        ("Architectural Consequence", "Adaptive average pooling required prior to fusion concatenation; temporal kernel spans only 22.2 ms of physical time on sEMG.")
    ]:
        p = tf.add_paragraph(); p.text = h; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = ACCENT_PURPLE
        p2 = tf.add_paragraph(); p2.text = b; p2.font.size = Pt(11); p2.font.color.rgb = TEXT_LIGHT; p2.space_after = Pt(10)

    # ==================== SLIDE 11: DualBranchCNN Architecture ====================
    s11 = prs.slides.add_slide(blank_layout)
    set_background(s11)
    add_header(s11, "DualBranchCNN: Strictly Matched Capacity", "Deep Architecture")
    
    cols = [
        ("sEMG Encoder", "147,712 Parameters (44.8%)\n\n• Conv1D(8, 64, k=7, s=2)\n• BatchNorm1d(64)\n• ReLU + MaxPool1d(2)\n• Conv1D(64, 128, k=5, s=2)\n• BatchNorm1d(128)\n• AdaptiveAvgPool1d(1)\n• Output: 128-D embedding", ACCENT_BLUE, 0.8),
        ("IMU Encoder", "165,632 Parameters (50.2%)\n\n• Conv1D(48, 64, k=7, s=2)\n• BatchNorm1d(64)\n• ReLU + MaxPool1d(2)\n• Conv1D(64, 128, k=5, s=2)\n• BatchNorm1d(128)\n• AdaptiveAvgPool1d(1)\n• Output: 128-D embedding", ACCENT_PURPLE, 4.8),
        ("Fusion Head", "16,708 Parameters (5.0%)\n\n• Concat: [128, 128] -> 256-D\n• Dropout(p = 0.3)\n• Linear(256, 64)\n• ReLU activation\n• Linear(64, 4)\n• Output: 4 locomotion classes\n• Total: 330,052 params", ACCENT_GREEN, 8.8)
    ]
    for ct, cd, ca, left in cols:
        add_card(s11, left, 1.8, 3.7, 4.9, title=ct)
        tb = s11.shapes.add_textbox(Inches(left + 0.2), Inches(2.5), Inches(3.3), Inches(4.0))
        tf = tb.text_frame; tf.word_wrap = True
        p = tf.paragraphs[0]; p.text = cd; p.font.size = Pt(11.5); p.font.color.rgb = TEXT_LIGHT

    # ==================== SLIDE 12: Receptive Field Dynamics ====================
    s12 = prs.slides.add_slide(blank_layout)
    set_background(s12)
    add_header(s12, "Temporal Receptive Field Dynamics", "Ablation Mechanism")
    
    add_card(s12, 0.8, 1.8, 5.6, 5.0, title="Theoretical Receptive Field: 28 Samples")
    tb = s12.shapes.add_textbox(Inches(1.1), Inches(2.5), Inches(5.0), Inches(4.0))
    tf = tb.text_frame; tf.word_wrap = True
    for h, b in [
        ("Layer 1 Expansion", "Conv1D(k=7, s=2) spans 7 input samples. Stride = 2."),
        ("Layer 2 Expansion", "MaxPool1d(2) doubles effective stride to 4."),
        ("Layer 3 Expansion", "Conv1D(k=5, s=2) expands receptive field by (5-1) * 4 = 16 samples."),
        ("Total Receptive Field Formula", "RF = 1 + (7-1) + (2-1)*2 + (5-1)*4 = 28 samples.")
    ]:
        p = tf.add_paragraph(); p.text = h; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = ACCENT_BLUE
        p2 = tf.add_paragraph(); p2.text = b; p2.font.size = Pt(11); p2.font.color.rgb = TEXT_LIGHT; p2.space_after = Pt(8)

    add_card(s12, 6.8, 1.8, 5.7, 5.0, title="Physical Duration Divergence")
    tb_r = s12.shapes.add_textbox(Inches(7.1), Inches(2.5), Inches(5.1), Inches(4.0))
    tf_r = tb_r.text_frame; tf_r.word_wrap = True
    for h, b in [
        ("Rate-Matched E3-D (148.15 Hz)", "28 samples / 148.15 Hz = 189.0 milliseconds.\nThe convolutional kernels span nearly the entire 200 ms locomotion window, capturing full swing/stance sub-phases."),
        ("Native-Rate E4 (1259.26 Hz)", "28 samples / 1259.26 Hz = 22.2 milliseconds.\nThe sEMG kernels perceive only a tiny 22 ms micro-burst, failing to capture macroscopic muscle activation envelopes without deeper pooling."),
        ("The Decisive Insight", "The empirical superiority of E3-D stems primarily from temporal receptive field alignment (189 ms match) rather than spectral aliasing benefits.")
    ]:
        p = tf_r.add_paragraph(); p.text = h; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = ACCENT_PURPLE
        p2 = tf_r.add_paragraph(); p2.text = b; p2.font.size = Pt(11); p2.font.color.rgb = TEXT_LIGHT; p2.space_after = Pt(8)

    # ==================== SLIDE 13: LOSO Evaluation Strategy ====================
    s13 = prs.slides.add_slide(blank_layout)
    set_background(s13)
    add_header(s13, "Leave-One-Subject-Out (LOSO) 9-Fold Scheme", "Validation Rigor")
    
    add_card(s13, 0.8, 1.8, 11.7, 5.0, title="Strict Zero-Shot Subject-Independent Cross-Validation")
    tb = s13.shapes.add_textbox(Inches(1.1), Inches(2.5), Inches(11.1), Inches(4.0))
    tf = tb.text_frame; tf.word_wrap = True
    for h, b in [
        ("Fold Partitioning", "In each fold k ∈ {1..9}, all data from Participant k is withheld strictly for testing. Training uses data pooled from the remaining 8 participants."),
        ("Zero Leakage Guarantee", "Feature normalization parameters (mean, standard deviation) are computed exclusively on the 8 training participants and applied to the test participant."),
        ("Real-World Clinical Simulation", "Accurately models clinical deployment where a pre-trained exoskeleton or prosthesis encounters a new patient with no prior calibration."),
        ("Participant Heterogeneity Challenge", "Inter-subject anatomical variance (tissue thickness, electrode impedance, cadence) makes LOSO substantially more challenging than random train-test splitting.")
    ]:
        p = tf.add_paragraph(); p.text = h; p.font.size = Pt(12.5); p.font.bold = True; p.font.color.rgb = ACCENT_GREEN
        p2 = tf.add_paragraph(); p2.text = b; p2.font.size = Pt(11.5); p2.font.color.rgb = TEXT_LIGHT; p2.space_after = Pt(10)

    # ==================== SLIDE 14: Multi-Seed Protocol ====================
    s14 = prs.slides.add_slide(blank_layout)
    set_background(s14)
    add_header(s14, "Multi-Seed Replication Matrix: 90 Model Runs", "Experimental Rigor")
    
    add_card(s14, 0.8, 1.8, 11.7, 5.0, title="5 Random Seeds × 9 Folds × 2 Conditions = 90 Fully Trained Models")
    tb = s14.shapes.add_textbox(Inches(1.1), Inches(2.5), Inches(11.1), Inches(4.0))
    tf = tb.text_frame; tf.word_wrap = True
    for h, b in [
        ("Seeds Evaluated", "Seeds 42, 123, 2024, 3407, and 7777 initialized across PyTorch, NumPy, and Python standard libraries."),
        ("Seed-Level Mean Results", "Seed 42: E3-D 72.63% vs E4 69.53% (Δ = +3.09 pp)\nSeed 123: E3-D 73.14% vs E4 70.25% (Δ = +2.89 pp)\nSeed 2024: E3-D 72.48% vs E4 71.22% (Δ = +1.26 pp)\nSeed 3407: E3-D 73.54% vs E4 66.83% (Δ = +6.71 pp)\nSeed 7777: E3-D 72.83% vs E4 67.63% (Δ = +5.20 pp)"),
        ("Leave-One-Seed-Out Sensitivity", "Removing any single seed preserves statistical significance: W ∈ [2.0, 6.0], p ∈ [0.012, 0.055]. Rate-matching advantage is invariant to random initialization."),
        ("Complete Run Archive", "All 90 model run folders contain individual history.json, meta.json, and predictions.csv verified bit-identical.")
    ]:
        p = tf.add_paragraph(); p.text = h; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = ACCENT_PURPLE
        p2 = tf.add_paragraph(); p2.text = b; p2.font.size = Pt(11); p2.font.color.rgb = TEXT_LIGHT; p2.space_after = Pt(8)

    # ==================== SLIDE 15: Primary Findings (with Fig 1) ====================
    s15 = prs.slides.add_slide(blank_layout)
    set_background(s15)
    add_header(s15, "Primary Findings: Rate-Matched Fusion Outperforms Native-Rate", "Results")
    
    add_card(s15, 0.8, 1.8, 4.8, 5.0, title="Empirical Outcome Summary")
    tb = s15.shapes.add_textbox(Inches(1.0), Inches(2.5), Inches(4.4), Inches(4.0))
    tf = tb.text_frame; tf.word_wrap = True
    for h, b in [
        ("Condition E3-D Mean", "72.90% ± 9.24% test accuracy across 9 LOSO folds."),
        ("Condition E4 Mean", "69.07% ± 10.80% test accuracy across 9 LOSO folds."),
        ("Mean Paired Difference", "+3.83 percentage points (95% CI: [1.07, 6.65] pp)."),
        ("Statistical Significance", "Wilcoxon signed-rank p = 0.039.\nExact sign-flip permutation p = 0.031."),
        ("Cohort Consistency", "8 of 9 participants demonstrated superior accuracy under rate-matched fusion.")
    ]:
        p = tf.add_paragraph(); p.text = h; p.font.size = Pt(11.5); p.font.bold = True; p.font.color.rgb = ACCENT_BLUE
        p2 = tf.add_paragraph(); p2.text = b; p2.font.size = Pt(10.5); p2.font.color.rgb = TEXT_LIGHT; p2.space_after = Pt(8)

    fig1_path = FIG_DIR / "fig1_participant_paired_comparison.png"
    if fig1_path.exists():
        s15.shapes.add_picture(str(fig1_path), Inches(5.8), Inches(1.8), width=Inches(6.7))

    # ==================== SLIDE 16: Participant Breakdown (with Fig 2) ====================
    s16 = prs.slides.add_slide(blank_layout)
    set_background(s16)
    add_header(s16, "Participant-Level Performance Distribution", "Results Breakdown")
    
    fig2_path = FIG_DIR / "fig2_accuracy_distribution_boxplot.png"
    if fig2_path.exists():
        s16.shapes.add_picture(str(fig2_path), Inches(0.8), Inches(1.8), width=Inches(6.0))
        
    add_card(s16, 7.1, 1.8, 5.4, 5.0, title="5-Seed Mean Participant Accuracies")
    tb = s16.shapes.add_textbox(Inches(7.3), Inches(2.4), Inches(5.0), Inches(4.2))
    tf = tb.text_frame; tf.word_wrap = True
    
    rows = [
        ("P1", "77.77%", "80.93%", "-3.15 pp (Favors E4)", ACCENT_ROSE),
        ("P2", "81.37%", "80.70%", "+0.67 pp (Favors E3-D)", ACCENT_GREEN),
        ("P3", "50.86%", "45.29%", "+5.57 pp (Favors E3-D)", ACCENT_GREEN),
        ("P4", "70.32%", "69.20%", "+1.12 pp (Favors E3-D)", ACCENT_GREEN),
        ("P5", "72.71%", "70.24%", "+2.47 pp (Favors E3-D)", ACCENT_GREEN),
        ("P6", "78.64%", "72.27%", "+6.37 pp (Favors E3-D)", ACCENT_GREEN),
        ("P7", "79.20%", "69.27%", "+9.94 pp (Favors E3-D)", ACCENT_GREEN),
        ("P8", "69.25%", "60.90%", "+8.35 pp (Favors E3-D)", ACCENT_GREEN),
        ("P9", "75.98%", "72.84%", "+3.14 pp (Favors E3-D)", ACCENT_GREEN),
    ]
    for p_id, e3, e4, d, col in rows:
        p = tf.add_paragraph()
        p.text = f"{p_id}: E3-D={e3} | E4={e4} | Δ={d}"
        p.font.size = Pt(10.5); p.font.bold = True; p.font.color.rgb = col; p.space_after = Pt(2)

    # ==================== SLIDE 17: Statistical Significance (with Fig 4) ====================
    s17 = prs.slides.add_slide(blank_layout)
    set_background(s17)
    add_header(s17, "Rigorous Inferential Statistical Verification", "Statistical Analysis")
    
    add_card(s17, 0.8, 1.8, 5.0, 5.0, title="Inferential Test Battery")
    tb = s17.shapes.add_textbox(Inches(1.0), Inches(2.5), Inches(4.6), Inches(4.0))
    tf = tb.text_frame; tf.word_wrap = True
    for h, b in [
        ("Exact Wilcoxon Signed-Rank", "W = 5.0, W+ = 40.0, W- = 5.0\nExact two-sided p = 0.0390625\nRank-biserial correlation r = 0.778"),
        ("Exact Sign-Flip Permutation", "2⁹ = 512 exhaustive sign assignments\np = 0.03125 (16 / 512 permutations)\nCompletely distribution-free"),
        ("Two-Stage Hierarchical Bootstrap", "10,000 resamples accounting for participant and seed sampling\n95% CI: [1.07, 6.65] pp\nZero effect strictly excluded"),
        ("Paired T-Test (Reference)", "t(8) = 2.791, p = 0.024")
    ]:
        p = tf.add_paragraph(); p.text = h; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = ACCENT_GREEN
        p2 = tf.add_paragraph(); p2.text = b; p2.font.size = Pt(10.5); p2.font.color.rgb = TEXT_LIGHT; p2.space_after = Pt(8)

    fig4_path = FIG_DIR / "fig4_hierarchical_bootstrap_ci.png"
    if fig4_path.exists():
        s17.shapes.add_picture(str(fig4_path), Inches(6.0), Inches(1.8), width=Inches(6.5))

    # ==================== SLIDE 18: Spectral Analysis of Participant 1 (with Fig 3) ====================
    s18 = prs.slides.add_slide(blank_layout)
    set_background(s18)
    add_header(s18, "Spectral Analysis: Explaining the P1 Negative Delta", "Spectral Diagnostics")
    
    fig3_path = FIG_DIR / "fig3_spectral_density_aliasing.png"
    if fig3_path.exists():
        s18.shapes.add_picture(str(fig3_path), Inches(0.8), Inches(1.8), width=Inches(6.3))
        
    add_card(s18, 7.3, 1.8, 5.2, 5.0, title="The Causal Mechanism of P1")
    tb = s18.shapes.add_textbox(Inches(7.5), Inches(2.5), Inches(4.8), Inches(4.0))
    tf = tb.text_frame; tf.word_wrap = True
    for h, b in [
        ("The Outlier Phenomenon", "P1 is the sole participant where Native-Rate E4 (80.93%) outperformed Rate-Matched E3-D (77.77%), creating a negative delta of -3.15 pp."),
        ("Super-Nyquist Spectral Power", "Full-cohort spectral audit across all 361 trials revealed that P1 possesses only 13.51% super-Nyquist energy above 74.07 Hz (vs. 19.0% cohort average)."),
        ("Lower Aliasing Penalty in Native", "Because P1's sEMG contains unusually low high-frequency noise, native-rate processing retains clean signal dynamics without experiencing the aliasing folding that degraded other participants."),
        ("Scientific Integrity", "Demonstrates that rate-matching is not universally optimal: patient-specific spectral profiles dictate resampling benefits.")
    ]:
        p = tf.add_paragraph(); p.text = h; p.font.size = Pt(11.5); p.font.bold = True; p.font.color.rgb = ACCENT_AMBER
        p2 = tf.add_paragraph(); p2.text = b; p2.font.size = Pt(10.5); p2.font.color.rgb = TEXT_LIGHT; p2.space_after = Pt(8)

    # ==================== SLIDE 19: Variance Components (with Fig 5) ====================
    s19 = prs.slides.add_slide(blank_layout)
    set_background(s19)
    add_header(s19, "Variance Components & Random Seed Sensitivity", "Variance Analysis")
    
    fig5_path = FIG_DIR / "fig5_variance_components_decomposition.png"
    if fig5_path.exists():
        s19.shapes.add_picture(str(fig5_path), Inches(0.8), Inches(1.8), width=Inches(6.3))
        
    add_card(s19, 7.3, 1.8, 5.2, 5.0, title="Two-Way ANOVA Decomposition")
    tb = s19.shapes.add_textbox(Inches(7.5), Inches(2.5), Inches(4.8), Inches(4.0))
    tf = tb.text_frame; tf.word_wrap = True
    for h, b in [
        ("Participant Share: 51.3%", "Between-participant SD = 3.66 pp.\nConfirms anatomical heterogeneity is the dominant performance determinant."),
        ("Seed Noise Share: 12.4%", "Within-participant, between-seed SD = 4.23 pp.\nProves single-seed evaluations are unreliable."),
        ("Residual Variance: 36.3%", "Unexplained stochastic interaction between weights and gait cycles."),
        ("Intraclass Correlation (ICC)", "ICC = 0.427.\nIndicates moderate-to-strong participant stability."),
        ("Standard Error of Participant Mean", "SE = 1.89 pp from seed noise alone, validating 5-seed averaging.")
    ]:
        p = tf.add_paragraph(); p.text = h; p.font.size = Pt(11.5); p.font.bold = True; p.font.color.rgb = ACCENT_PURPLE
        p2 = tf.add_paragraph(); p2.text = b; p2.font.size = Pt(10.5); p2.font.color.rgb = TEXT_LIGHT; p2.space_after = Pt(6)

    # ==================== SLIDE 20: Activity Recall Gains (with Fig 6) ====================
    s20 = prs.slides.add_slide(blank_layout)
    set_background(s20)
    add_header(s20, "Activity-Specific Recall & Classification Gains", "Activity Analysis")
    
    fig6_path = FIG_DIR / "fig6_confusion_matrix_comparison.png"
    if fig6_path.exists():
        s20.shapes.add_picture(str(fig6_path), Inches(0.8), Inches(1.8), width=Inches(6.4))
        
    add_card(s20, 7.4, 1.8, 5.1, 5.0, title="Per-Activity Sensitivity Gains")
    tb = s20.shapes.add_textbox(Inches(7.6), Inches(2.5), Inches(4.7), Inches(4.0))
    tf = tb.text_frame; tf.word_wrap = True
    for h, b in [
        ("Stairs Down: +6.45 pp Gain", "E3-D 69.32% vs E4 62.87%.\nLargest single improvement observed. Downstairs locomotion features high impact forces and eccentric quadriceps contraction well-aligned by rate-matching."),
        ("Jogging: +4.13 pp Gain", "E3-D 77.79% vs E4 73.66%.\nHigh-cadence gait benefits from synchronized phase alignment."),
        ("Walking: +3.12 pp Gain", "E3-D 75.77% vs E4 72.65%.\nSteady-state walking gains stability across stance-to-swing transition."),
        ("Stairs Up: +2.59 pp Gain", "E3-D 63.56% vs E4 60.97%.\nConcentric muscle drive benefits across both modalities.")
    ]:
        p = tf.add_paragraph(); p.text = h; p.font.size = Pt(11.5); p.font.bold = True; p.font.color.rgb = ACCENT_GREEN
        p2 = tf.add_paragraph(); p2.text = b; p2.font.size = Pt(10.5); p2.font.color.rgb = TEXT_LIGHT; p2.space_after = Pt(6)

    # ==================== SLIDE 21: Scientific Limitations ====================
    s21 = prs.slides.add_slide(blank_layout)
    set_background(s21)
    add_header(s21, "Scientific Limitations & Boundary Conditions", "Critical Analysis")
    
    cards = [
        ("Absence of Anti-Aliasing", "Cubic-spline interpolation was conducted without an explicit Butterworth pre-filter. A portion of E3-D performance reflects aliased energy folding rather than pure decimation.", ACCENT_AMBER, 0.8),
        ("Controlled Laboratory Setting", "Evaluated on healthy young adults in structured laboratory sessions; real-world community ambulation introduces irregular obstacles, variable terrain, and muscle fatigue.", ACCENT_ROSE, 4.8),
        ("Sensor Dropout & Electrode Shift", "Fixed sensor placements assume consistent positioning; longitudinal clinical deployment must handle electrode impedance changes and sensor migration.", ACCENT_BLUE, 8.8)
    ]
    for ct, cd, ca, left in cards:
        add_card(s21, left, 1.8, 3.7, 4.9, title=ct)
        tb = s21.shapes.add_textbox(Inches(left + 0.2), Inches(2.5), Inches(3.3), Inches(4.0))
        tf = tb.text_frame; tf.word_wrap = True
        p = tf.paragraphs[0]; p.text = cd; p.font.size = Pt(12); p.font.color.rgb = TEXT_LIGHT; p.space_after = Pt(14)
        p2 = tf.add_paragraph(); p2.text = f"Research Transparency:\nThese limitations are recorded in the open Scientific Discrepancy Register and demarcate the exact boundary of validated claims."; p2.font.size = Pt(10.5); p2.font.color.rgb = TEXT_MUTED

    # ==================== SLIDE 22: Reproducibility Protocol ====================
    s22 = prs.slides.add_slide(blank_layout)
    set_background(s22)
    add_header(s22, "Two-Tier Scientific Reproducibility Protocol", "Open Science")
    
    add_card(s22, 0.8, 1.8, 5.6, 5.0, title="Tier 1: Statistical Verification (< 10 sec)")
    tb = s22.shapes.add_textbox(Inches(1.1), Inches(2.5), Inches(5.0), Inches(4.0))
    tf = tb.text_frame; tf.word_wrap = True
    for h, b in [
        ("Source Files", "All 90 prediction CSV files (6,203 rows per seed) tracked directly in Git repository."),
        ("Execution Tooling", "pytest tests/ -v\npython3 scripts/verify_release.py"),
        ("Verification Outcome", "Recomputes exact Wilcoxon p = 0.039, permutation p = 0.031, bootstrap CI [1.07, 6.65] pp, and parameter counts in seconds without heavy compute."),
        ("Accessibility", "Runs on any laptop with Python 3.10–3.13 in under 10 seconds.")
    ]:
        p = tf.add_paragraph(); p.text = h; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = ACCENT_BLUE
        p2 = tf.add_paragraph(); p2.text = b; p2.font.size = Pt(11); p2.font.color.rgb = TEXT_LIGHT; p2.space_after = Pt(8)

    add_card(s22, 6.8, 1.8, 5.7, 5.0, title="Tier 2: Model Retraining (~4-8 GPU hrs)")
    tb_r = s22.shapes.add_textbox(Inches(7.1), Inches(2.5), Inches(5.1), Inches(4.0))
    tf_r = tb_r.text_frame; tf_r.word_wrap = True
    for h, b in [
        ("Source Files", "18 preprocessed windowed arrays (v2_reproducibility_data_final.zip, 2.22 GB on Zenodo)."),
        ("Execution Tooling", "python3 robustness_train.py --seed 42..7777"),
        ("Verification Outcome", "Trains all 90 neural networks from scratch. Reproduces trained weights, loss curves, and prediction CSVs within seed noise bounds (4.23 pp)."),
        ("Reproducibility Tiering", "Separates quick statistical auditability from expensive neural network retraining.")
    ]:
        p = tf_r.add_paragraph(); p.text = h; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = ACCENT_PURPLE
        p2 = tf_r.add_paragraph(); p2.text = b; p2.font.size = Pt(11); p2.font.color.rgb = TEXT_LIGHT; p2.space_after = Pt(8)

    # ==================== SLIDE 23: Research Artifacts & DOIs ====================
    s23 = prs.slides.add_slide(blank_layout)
    set_background(s23)
    add_header(s23, "Public Research Artifacts & Zenodo DOIs", "Permanent Archival")
    
    cards_doi = [
        ("Concept DOI (All Versions)", "10.5281/zenodo.22649504", "Permanent umbrella identifier resolving to the latest public release", ACCENT_BLUE, 0.8),
        ("Version 2.0.0 Record", "10.5281/zenodo.24220130", "Frozen V2 release candidate, 2.22 GB arrays, and verification suite", ACCENT_GREEN, 4.8),
        ("Upstream SDALLE Dataset", "10.5281/zenodo.14841611", "Public benchmark dataset by Ibrahim et al. (CC BY 4.0)", ACCENT_PURPLE, 8.8)
    ]
    for t, doi, desc, col, left in cards_doi:
        add_card(s23, left, 1.8, 3.7, 2.5)
        tb = s23.shapes.add_textbox(Inches(left + 0.2), Inches(2.0), Inches(3.3), Inches(2.1))
        tf = tb.text_frame; tf.word_wrap = True
        p = tf.paragraphs[0]; p.text = t; p.font.size = Pt(12.5); p.font.bold = True; p.font.color.rgb = TEXT_WHITE; p.space_after = Pt(6)
        p2 = tf.add_paragraph(); p2.text = doi; p2.font.size = Pt(13); p2.font.bold = True; p2.font.color.rgb = col; p2.space_after = Pt(8)
        p3 = tf.add_paragraph(); p3.text = desc; p3.font.size = Pt(10.5); p3.font.color.rgb = TEXT_LIGHT

    add_card(s23, 0.8, 4.6, 11.7, 2.3, title="GitHub Repository & Verification Suite")
    tb = s23.shapes.add_textbox(Inches(1.1), Inches(5.1), Inches(11.1), Inches(1.6))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Repository: https://github.com/SaqibAhmadBhat/subject-independent-emg-imu-fusion\n• Branch: feature/research-platform-experience  |  Release Tag: v2.0.0\n• Continuous Integration: GitHub Actions matrix across Python 3.10, 3.11, 3.12, 3.13\n• Software License: MIT License  |  Documentation & Figures: Creative Commons Attribution 4.0 (CC BY 4.0)"
    p.font.size = Pt(12); p.font.color.rgb = TEXT_LIGHT

    # ==================== SLIDE 24: Conclusion & Citations ====================
    s24 = prs.slides.add_slide(blank_layout)
    set_background(s24)
    add_header(s24, "Conclusion & Academic Attribution", "Summary")
    
    add_card(s24, 0.8, 1.8, 5.6, 5.0, title="Conclusions & Future Work")
    tb = s24.shapes.add_textbox(Inches(1.1), Inches(2.5), Inches(5.0), Inches(4.0))
    tf = tb.text_frame; tf.word_wrap = True
    for h, b in [
        ("Core Takeaway", "Rate-matched sensor fusion via cubic spline achieves statistically significant superiority (+3.83 pp, p = 0.039) over native-rate fusion for subject-independent locomotion classification under matched model capacity."),
        ("Key Driver", "Temporal receptive field alignment (189 ms match) dominates over high-frequency MUAP spectral retention in macro-locomotor gait recognition."),
        ("Future Roadmap", "1. Anti-aliased decimation filters (Chebyshev/polyphase) to eliminate spectral folding.\n2. Cross-modal temporal cross-attention transformers.\n3. Hardware deployment on embedded edge-AI prosthetics.")
    ]:
        p = tf.add_paragraph(); p.text = h; p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = ACCENT_GREEN
        p2 = tf.add_paragraph(); p2.text = b; p2.font.size = Pt(11); p2.font.color.rgb = TEXT_LIGHT; p2.space_after = Pt(10)

    add_card(s24, 6.8, 1.8, 5.7, 5.0, title="Citation & Contact")
    tb_r = s24.shapes.add_textbox(Inches(7.1), Inches(2.5), Inches(5.1), Inches(4.0))
    tf_r = tb_r.text_frame; tf_r.word_wrap = True
    p = tf_r.paragraphs[0]
    p.text = "BibTeX Citation:"
    p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = ACCENT_BLUE; p.space_after = Pt(6)
    
    p2 = tf_r.add_paragraph()
    p2.text = """@software{bhat2026emgimuv2,
  author    = {Bhat, Saqib Ahmad and Sona, G. and Karuvelam, P. Subha},
  title     = {{Subject-Independent EMG-IMU Fusion for Human Activity Recognition: Code and Frozen Results}},
  month     = nov,
  year      = 2026,
  publisher = {Zenodo},
  version   = {2.0.0},
  doi       = {10.5281/zenodo.22649504},
  url       = {https://github.com/SaqibAhmadBhat/subject-independent-emg-imu-fusion}
}"""
    p2.font.size = Pt(9.5); p2.font.color.rgb = TEXT_LIGHT; p2.font.name = "Courier"; p2.space_after = Pt(12)
    
    p3 = tf_r.add_paragraph()
    p3.text = "Contact: Saqib Ahmad Bhat (bhatsaqibahmad@gmail.com)\nDepartment of Computer Science & Engineering, SRM Institute of Science and Technology"
    p3.font.size = Pt(10.5); p3.font.color.rgb = TEXT_MUTED

    OUT_PPTX.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUT_PPTX)
    print(f"Successfully generated 24-slide research presentation at: {OUT_PPTX}")
    return OUT_PPTX


if __name__ == "__main__":
    build_presentation()
