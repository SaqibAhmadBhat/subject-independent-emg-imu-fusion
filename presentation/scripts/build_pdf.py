#!/usr/bin/env python3
"""
presentation/scripts/build_pdf.py
---------------------------------
Renders a 24-page publication-quality vector presentation PDF matching
EMG_IMU_Research_Presentation.pptx in 16:9 widescreen format (960 x 540 pt)
using reportlab.
Output: presentation/EMG_IMU_Research_Presentation.pdf
"""
from pathlib import Path
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.pdfgen import canvas

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
OUT_PDF = REPO_ROOT / "presentation" / "EMG_IMU_Research_Presentation.pdf"
FIG_DIR = REPO_ROOT / "presentation" / "figures"

# 16:9 Widescreen dimensions in points
WIDTH = 960.0
HEIGHT = 540.0

# Palette
BG_COLOR = HexColor("#0F172A")
CARD_BG = HexColor("#1E293B")
CARD_BORDER = HexColor("#334155")
ACCENT_BLUE = HexColor("#0EA5E9")
ACCENT_GREEN = HexColor("#10B981")
ACCENT_PURPLE = HexColor("#8B5CF6")
ACCENT_AMBER = HexColor("#F59E0B")
ACCENT_ROSE = HexColor("#F43F5E")
TEXT_WHITE = HexColor("#F8FAFC")
TEXT_LIGHT = HexColor("#E2E8F0")
TEXT_MUTED = HexColor("#94A3B8")


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        # Footer
        self.setFont("Helvetica", 8.5)
        self.setFillColor(TEXT_MUTED)
        self.drawString(45, 20, "Subject-Independent sEMG–IMU Fusion Study V2.0.0 | DOI: 10.5281/zenodo.22649504")
        self.drawRightString(WIDTH - 45, 20, f"Slide {self._pageNumber} of {page_count}")
        self.restoreState()


def draw_background_and_header(canvas_obj, doc, title_text, category=""):
    canvas_obj.saveState()
    # Dark background
    canvas_obj.setFillColor(BG_COLOR)
    canvas_obj.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
    
    if doc.page > 1:
        # Category label
        if category:
            canvas_obj.setFont("Helvetica-Bold", 9)
            canvas_obj.setFillColor(ACCENT_BLUE)
            canvas_obj.drawString(50, HEIGHT - 35, category.upper())
            
        # Title
        canvas_obj.setFont("Helvetica-Bold", 18)
        canvas_obj.setFillColor(TEXT_WHITE)
        canvas_obj.drawString(50, HEIGHT - 58, title_text)
        
        # Subtle dividing line
        canvas_obj.setStrokeColor(HexColor("#1E293B"))
        canvas_obj.setLineWidth(1)
        canvas_obj.line(50, HEIGHT - 68, WIDTH - 50, HEIGHT - 68)
        
    canvas_obj.restoreState()


def build_pdf():
    doc = SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=(WIDTH, HEIGHT),
        leftMargin=45,
        rightMargin=45,
        topMargin=80,
        bottomMargin=35
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        "CoverTitle",
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=30,
        textColor=TEXT_WHITE,
        spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        fontName="Helvetica",
        fontSize=13,
        leading=18,
        textColor=TEXT_MUTED,
        spaceAfter=15
    )
    cat_style = ParagraphStyle(
        "CoverCategory",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=ACCENT_BLUE,
        spaceAfter=12
    )
    h2_style = ParagraphStyle(
        "CardTitle",
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=TEXT_WHITE,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        "CardBody",
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=TEXT_LIGHT,
        spaceAfter=6
    )
    stat_val_style = ParagraphStyle(
        "StatVal",
        fontName="Helvetica-Bold",
        fontSize=26,
        leading=30,
        textColor=ACCENT_BLUE
    )
    stat_lbl_style = ParagraphStyle(
        "StatLbl",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=TEXT_LIGHT
    )
    stat_sub_style = ParagraphStyle(
        "StatSub",
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=TEXT_MUTED
    )

    story = []

    def make_card(content_list, width, bg=CARD_BG, border=CARD_BORDER):
        t = Table([[c] for c in content_list], colWidths=[width])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg),
            ('BOX', (0,0), (-1,-1), 1.2, border),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ]))
        return t

    # ----------------- SLIDE 1: Cover -----------------
    story.append(Spacer(1, 40))
    story.append(Paragraph("BIOMEDICAL ENGINEERING & REHABILITATION ROBOTICS", cat_style))
    story.append(Paragraph("Subject-Independent sEMG–IMU Sensor Fusion<br/>for Human Activity Recognition", title_style))
    story.append(Paragraph("A Controlled Empirical Robustness Study of Rate-Matching vs. Native-Rate Deep Fusion", subtitle_style))
    story.append(Spacer(1, 25))
    
    meta_box = [
        Paragraph("<b>Research Software Release: Version 2.0.0</b> (Concept DOI: 10.5281/zenodo.22649504)", ParagraphStyle('Meta1', parent=body_style, fontName='Helvetica-Bold', textColor=ACCENT_GREEN)),
        Paragraph("Authors: Saqib Ahmad Bhat (0009-0003-9248-6174), Sona G (0000-0002-1786-4193), P. Subha Karuvelam (0000-0002-9958-6106)", body_style),
        Paragraph("Benchmark: SDALLE Dataset (Zenodo 10.5281/zenodo.14841611) | GitHub: SaqibAhmadBhat/subject-independent-emg-imu-fusion", ParagraphStyle('Meta3', parent=body_style, textColor=TEXT_MUTED)),
    ]
    story.append(make_card(meta_box, 860))
    story.append(PageBreak())

    # ----------------- SLIDE 2: Executive Summary -----------------
    stat1 = [Paragraph("+3.83 pp", stat_val_style), Paragraph("Mean Paired Gap", stat_lbl_style), Paragraph("E3-D (72.90%) outperforms E4 (69.07%) across 5 seeds", stat_sub_style)]
    stat2 = [Paragraph("p = 0.039", ParagraphStyle('S2', parent=stat_val_style, textColor=ACCENT_GREEN)), Paragraph("Wilcoxon Test", stat_lbl_style), Paragraph("Exact W = 5.0 (8 of 9 participants favored Rate-Matching)", stat_sub_style)]
    stat3 = [Paragraph("330,052", ParagraphStyle('S3', parent=stat_val_style, textColor=ACCENT_PURPLE)), Paragraph("Matched Parameters", stat_lbl_style), Paragraph("DualBranchCNN capacity strictly invariant across conditions", stat_sub_style)]
    
    t_stats = Table([[make_card(stat1, 270), make_card(stat2, 270), make_card(stat3, 270)]], colWidths=[290, 290, 290])
    t_stats.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t_stats)
    story.append(Spacer(1, 15))
    
    summary_bullets = [
        Paragraph("Key Scientific Takeaways", h2_style),
        Paragraph("• <b>Rigorous Experimental Protocol:</b> 9-fold LOSO cross-validation evaluated across 5 random seeds (90 runs, 31,015 test windows per condition).", body_style),
        Paragraph("• <b>Statistical Verification:</b> Exact sign-flip permutation p = 0.031; two-stage hierarchical bootstrap 95% CI is [1.07, 6.65] pp.", body_style),
        Paragraph("• <b>Ablation Discovery:</b> Rate-matching sEMG via cubic spline expands the temporal receptive field (189 ms vs 22 ms), improving macro-locomotion coordination despite 19.0% super-Nyquist energy.", body_style),
        Paragraph("• <b>Transparent Science:</b> Negative participant outcome (P1 favors native-rate by -3.15 pp) disclosed and causally linked to reduced super-Nyquist energy (13.51%).", body_style),
    ]
    story.append(make_card(summary_bullets, 860))
    story.append(PageBreak())

    # ----------------- SLIDE 3: Clinical Relevance -----------------
    col1 = [
        Paragraph("Wearable Exoskeletons", h2_style),
        Paragraph("Active robotic orthoses require reliable, subject-independent locomotion mode classification to deliver seamless phase-dependent torque assistance without calibration delays.", body_style),
        Paragraph("<i>Challenge:</i> Calibration-free patient donning.", ParagraphStyle('I1', parent=body_style, textColor=ACCENT_BLUE))
    ]
    col2 = [
        Paragraph("Intelligent Prosthetics", h2_style),
        Paragraph("Myoelectric lower-limb prostheses must combine neural intent (sEMG) with kinematic limb state (IMU) to prevent catastrophic stumble and fall events.", body_style),
        Paragraph("<i>Challenge:</i> Zero-shot cross-user generalization.", ParagraphStyle('I2', parent=body_style, textColor=ACCENT_GREEN))
    ]
    col3 = [
        Paragraph("Gait Biomarkers", h2_style),
        Paragraph("Longitudinal neuromotor monitoring in Parkinson's disease and post-stroke recovery demands models that generalize to unseen patient anatomies.", body_style),
        Paragraph("<i>Challenge:</i> Real-world anatomical variance.", ParagraphStyle('I3', parent=body_style, textColor=ACCENT_PURPLE))
    ]
    t_clin = Table([[make_card(col1, 270), make_card(col2, 270), make_card(col3, 270)]], colWidths=[290, 290, 290])
    story.append(t_clin)
    story.append(PageBreak())

    # ----------------- SLIDE 4: Research Problem -----------------
    p_left = [
        Paragraph("Asynchronous Sensor Rates", h2_style),
        Paragraph("<b>sEMG Acquisition (~1259.26 Hz):</b> Captures fast motor unit action potentials (MUAPs) in 20-450 Hz bandwidth. 238 samples per 200 ms.", body_style),
        Paragraph("<b>IMU Acquisition (~148.15 Hz):</b> Captures limb kinematics in 0.5-15 Hz range. 28 samples per 200 ms.", body_style),
        Paragraph("<b>Dimensional Asymmetry:</b> Convolutions cannot directly concatenate feature maps across differing sequence lengths without resampling.", body_style),
    ]
    p_right = [
        Paragraph("Architectural Dilemma", h2_style),
        Paragraph("<b>Approach A (Rate-Matched, E3-D):</b> Interpolate sEMG to 148 Hz using cubic spline. Standardizes sequence length to 148 samples, but introduces aliasing risk.", body_style),
        Paragraph("<b>Approach B (Native-Rate, E4):</b> Preserve sEMG at 1259 Hz (238 samples) and IMU at 148 Hz. Retains MUAP bandwidth, but creates asymmetric receptive fields.", body_style),
        Paragraph("<b>The Central Question:</b> Does preserving native sEMG bandwidth outweigh uniform temporal receptive field alignment?", ParagraphStyle('CQ', parent=body_style, fontName='Helvetica-Bold', textColor=ACCENT_PURPLE)),
    ]
    story.append(Table([[make_card(p_left, 415), make_card(p_right, 415)]], colWidths=[435, 435]))
    story.append(PageBreak())

    # ----------------- SLIDE 5: Research Gap -----------------
    g1 = [Paragraph("Conflicting Prior Claims", h2_style), Paragraph("Previous literature reported contradictory results on sEMG decimation, but confounded resampling method with model capacity (different kernels and filter counts).", body_style)]
    g2 = [Paragraph("Single-Seed Fragility", h2_style), Paragraph("Wearable sensor studies commonly evaluate single random seeds, hiding seed-level variance and producing non-reproducible baseline comparisons.", body_style)]
    g3 = [Paragraph("Receptive Field Blindness", h2_style), Paragraph("Prior works rarely analyze how multirate pooling alters the effective physical duration spanned by convolutional kernels across modalities.", body_style)]
    story.append(Table([[make_card(g1, 270), make_card(g2, 270), make_card(g3, 270)]], colWidths=[290, 290, 290]))
    story.append(PageBreak())

    # ----------------- SLIDE 6: Hypotheses & Objectives -----------------
    h_box = [
        Paragraph("Core Hypotheses", h2_style),
        Paragraph("<b>H1:</b> Rate-matched fusion (E3-D) provides superior classification over native-rate fusion (E4) under strictly matched capacity due to synchronous cross-modal temporal alignment.", body_style),
        Paragraph("<b>H2:</b> Downsampling sEMG to 148 Hz without anti-aliasing folds super-Nyquist energy (> 74 Hz) into baseband, creating participant-dependent aliasing penalties.", body_style),
        Paragraph("<b>H3:</b> Participant anatomical heterogeneity accounts for the majority of variance, but random seeds contribute non-trivial noise requiring multi-seed averaging.", body_style)
    ]
    o_box = [
        Paragraph("Operational Objectives", h2_style),
        Paragraph("• Design DualBranchCNN with exactly 330,052 parameters for both conditions.", body_style),
        Paragraph("• Conduct 9-fold LOSO cross-validation across 5 seeds (90 runs, 62,030 inferences).", body_style),
        Paragraph("• Perform exact Wilcoxon, exact sign-flip permutation, and two-stage bootstrap inference.", body_style),
        Paragraph("• Release all prediction CSVs, models, and arrays under permanent open DOIs.", body_style)
    ]
    story.append(Table([[make_card(h_box, 415), make_card(o_box, 415)]], colWidths=[435, 435]))
    story.append(PageBreak())

    # ----------------- SLIDE 7: SDALLE Benchmark Dataset -----------------
    d1 = [Paragraph("9 Participants", stat_val_style), Paragraph("Adult cohort (P1–P9)", stat_sub_style)]
    d2 = [Paragraph("4 Locomotion Modes", ParagraphStyle('D2', parent=stat_val_style, textColor=ACCENT_GREEN)), Paragraph("Walking, Jogging, Stairs Up, Stairs Down", stat_sub_style)]
    d3 = [Paragraph("361 Trials", ParagraphStyle('D3', parent=stat_val_style, textColor=ACCENT_PURPLE)), Paragraph("Continuous synchronized recordings", stat_sub_style)]
    d4 = [Paragraph("56 Channels", ParagraphStyle('D4', parent=stat_val_style, textColor=ACCENT_AMBER)), Paragraph("8 sEMG + 48 IMU channels", stat_sub_style)]
    story.append(Table([[make_card(d1, 200), make_card(d2, 200), make_card(d3, 200), make_card(d4, 200)]], colWidths=[215, 215, 215, 215]))
    story.append(Spacer(1, 15))
    
    fold_dist = [
        Paragraph("Participant Test Window Counts (6,203 Total Windows / Seed)", h2_style),
        Paragraph("• P1: 647 windows | • P2: 568 windows | • P3: 729 windows | • P4: 696 windows | • P5: 746 windows<br/>• P6: 722 windows | • P7: 654 windows | • P8: 690 windows | • P9: 751 windows", ParagraphStyle('FD', parent=body_style, fontName='Helvetica-Bold', textColor=ACCENT_BLUE)),
        Paragraph("Publicly accessible via Zenodo (DOI: 10.5281/zenodo.14841611). CC BY 4.0 license.", stat_sub_style)
    ]
    story.append(make_card(fold_dist, 860))
    story.append(PageBreak())

    # ----------------- SLIDE 8: Multimodal Signal Physics -----------------
    emg_p = [
        Paragraph("Surface Electromyography (sEMG)", h2_style),
        Paragraph("<b>Bandwidth:</b> 20–450 Hz (Nyquist: 629.63 Hz at 1259.26 Hz sampling).", body_style),
        Paragraph("<b>Physics:</b> Muscle action potentials preceding mechanical force by 30-50 ms electromechanical delay.", body_style),
        Paragraph("<b>Property:</b> Stochastic interference pattern capturing neural activation.", body_style)
    ]
    imu_p = [
        Paragraph("Inertial Measurement Units (IMU)", h2_style),
        Paragraph("<b>Bandwidth:</b> 0.5–15 Hz (Nyquist: 74.07 Hz at 148.15 Hz sampling).", body_style),
        Paragraph("<b>Physics:</b> Multi-axis accelerations and rotational rates reflecting segmental limb kinematics.", body_style),
        Paragraph("<b>Property:</b> Quasi-periodic mechanical waveform capturing gait phases.", body_style)
    ]
    story.append(Table([[make_card(emg_p, 415), make_card(imu_p, 415)]], colWidths=[435, 435]))
    story.append(PageBreak())

    # ----------------- SLIDE 9: Research Architecture -----------------
    arch_steps = [
        Paragraph("5-Stage Experimental Execution Framework", h2_style),
        Paragraph("<b>1. Raw Ingestion:</b> 361 trials ingested and verified against SHA-256 manifests.", body_style),
        Paragraph("<b>2. Segmentation:</b> 200 ms windows with 50% overlap. E3-D uses cubic spline (148 samples); E4 retains 238 sEMG samples.", body_style),
        Paragraph("<b>3. Normalization:</b> Z-score standardisation computed strictly on training folds to prevent data leakage.", body_style),
        Paragraph("<b>4. Deep Fusion:</b> DualBranchCNN (330,052 parameters) trained across 9 folds × 5 seeds = 90 runs.", body_style),
        Paragraph("<b>5. Statistical Verification:</b> Exact Wilcoxon, exact permutation, and bootstrap CI validation.", body_style)
    ]
    story.append(make_card(arch_steps, 860))
    story.append(PageBreak())

    # ----------------- SLIDE 10: Preprocessing & Rate-Matching -----------------
    e3d_prep = [
        Paragraph("Condition E3-D: Cubic Spline Rate-Matching", h2_style),
        Paragraph("• Evaluated via <code>scipy.interpolate.interp1d(kind='cubic')</code> directly at IMU sample times.", body_style),
        Paragraph("• Downsamples sEMG from 1259.26 Hz to 148.15 Hz (148 samples).", body_style),
        Paragraph("• <b>Warning:</b> No anti-aliasing pre-filter applied; 19.0% super-Nyquist energy folded into baseband.", ParagraphStyle('W1', parent=body_style, textColor=ACCENT_AMBER)),
    ]
    e4_prep = [
        Paragraph("Condition E4: Native-Rate Multirate", h2_style),
        Paragraph("• Raw sEMG preserved at 1259.26 Hz (238 samples per 200 ms).", body_style),
        Paragraph("• Full MUAP bandwidth preserved; zero spectral folding.", body_style),
        Paragraph("• Produces asymmetric temporal sequences requiring adaptive pooling.", body_style)
    ]
    story.append(Table([[make_card(e3d_prep, 415), make_card(e4_prep, 415)]], colWidths=[435, 435]))
    story.append(PageBreak())

    # ----------------- SLIDE 11: DualBranchCNN Architecture -----------------
    b1 = [Paragraph("sEMG Encoder", h2_style), Paragraph("147,712 Params (44.8%)<br/>• Conv1D(8, 64, k=7, s=2)<br/>• BatchNorm + MaxPool1d(2)<br/>• Conv1D(64, 128, k=5, s=2)<br/>• AdaptiveAvgPool1d(1)", body_style)]
    b2 = [Paragraph("IMU Encoder", h2_style), Paragraph("165,632 Params (50.2%)<br/>• Conv1D(48, 64, k=7, s=2)<br/>• BatchNorm + MaxPool1d(2)<br/>• Conv1D(64, 128, k=5, s=2)<br/>• AdaptiveAvgPool1d(1)", body_style)]
    b3 = [Paragraph("Fusion Head", h2_style), Paragraph("16,708 Params (5.0%)<br/>• Concat: [128, 128] -> 256-D<br/>• Dropout(0.3) + Linear(256, 64)<br/>• Linear(64, 4) -> Softmax<br/>• <b>Total: 330,052 params</b>", body_style)]
    story.append(Table([[make_card(b1, 270), make_card(b2, 270), make_card(b3, 270)]], colWidths=[290, 290, 290]))
    story.append(PageBreak())

    # ----------------- SLIDE 12: Receptive Field Dynamics -----------------
    rf_card = [
        Paragraph("Theoretical Receptive Field: 28 Samples", h2_style),
        Paragraph("<b>Formula:</b> RF = 1 + (7-1) + (2-1)*2 + (5-1)*4 = 28 samples across both encoders.", body_style),
        Paragraph("<b>Rate-Matched E3-D (148.15 Hz):</b> 28 samples / 148.15 Hz = <b>189.0 milliseconds</b>. Spans 95% of the 200 ms locomotion window, capturing full sub-phase transitions.", ParagraphStyle('RF1', parent=body_style, textColor=ACCENT_BLUE)),
        Paragraph("<b>Native-Rate E4 (1259.26 Hz):</b> 28 samples / 1259.26 Hz = <b>22.2 milliseconds</b>. Spans only 11% of the window, perceiving only micro-bursts without macroscopic phase context.", ParagraphStyle('RF2', parent=body_style, textColor=ACCENT_PURPLE)),
        Paragraph("<b>Key Finding:</b> Receptive field temporal alignment is the primary driver of E3-D superiority.", ParagraphStyle('RF3', parent=body_style, fontName='Helvetica-Bold', textColor=ACCENT_GREEN))
    ]
    story.append(make_card(rf_card, 860))
    story.append(PageBreak())

    # ----------------- SLIDE 13: LOSO Scheme -----------------
    loso_card = [
        Paragraph("9-Fold Leave-One-Subject-Out Cross-Validation", h2_style),
        Paragraph("• In each fold k, Participant k is held out strictly for testing; remaining 8 participants form training set.", body_style),
        Paragraph("• Zero data leakage: Normalization statistics (μ, σ) computed exclusively on training folds.", body_style),
        Paragraph("• Clinical fidelity: Models zero-shot generalization to unseen patient physiologies.", body_style),
        Paragraph("• Evaluated across 31,015 test windows per condition.", body_style)
    ]
    story.append(make_card(loso_card, 860))
    story.append(PageBreak())

    # ----------------- SLIDE 14: Multi-Seed Protocol -----------------
    seed_card = [
        Paragraph("Multi-Seed Experimental Protocol: 90 Model Runs", h2_style),
        Paragraph("5 Random Seeds (42, 123, 2024, 3407, 7777) × 9 LOSO Folds × 2 Conditions = <b>90 Models</b>.", body_style),
        Paragraph("• Seed 42: E3-D 72.63% vs E4 69.53% (Δ = +3.09 pp)", body_style),
        Paragraph("• Seed 123: E3-D 73.14% vs E4 70.25% (Δ = +2.89 pp)", body_style),
        Paragraph("• Seed 2024: E3-D 72.48% vs E4 71.22% (Δ = +1.26 pp)", body_style),
        Paragraph("• Seed 3407: E3-D 73.54% vs E4 66.83% (Δ = +6.71 pp)", body_style),
        Paragraph("• Seed 7777: E3-D 72.83% vs E4 67.63% (Δ = +5.20 pp)", body_style),
        Paragraph("Leave-One-Seed-Out sensitivity proves significance across all sub-cohorts (p ∈ [0.012, 0.055]).", ParagraphStyle('SS', parent=body_style, textColor=ACCENT_GREEN))
    ]
    story.append(make_card(seed_card, 860))
    story.append(PageBreak())

    # ----------------- SLIDE 15: Primary Findings (with Fig 1) -----------------
    f1_desc = [
        Paragraph("Primary Statistical Findings", h2_style),
        Paragraph("<b>Rate-Matched E3-D:</b> 72.90% ± 9.24%", body_style),
        Paragraph("<b>Native-Rate E4:</b> 69.07% ± 10.80%", body_style),
        Paragraph("<b>Paired Difference:</b> +3.83 pp (p = 0.039)", ParagraphStyle('P1D', parent=body_style, fontName='Helvetica-Bold', textColor=ACCENT_BLUE)),
        Paragraph("<b>Permutation Test:</b> p = 0.031", body_style),
        Paragraph("8 of 9 participants demonstrated superior performance with rate-matching.", body_style)
    ]
    fig1_path = FIG_DIR / "fig1_participant_paired_comparison.png"
    if fig1_path.exists():
        im1 = Image(str(fig1_path), width=480, height=336)
        story.append(Table([[make_card(f1_desc, 350), im1]], colWidths=[370, 490]))
    else:
        story.append(make_card(f1_desc, 860))
    story.append(PageBreak())

    # ----------------- SLIDE 16: Participant Distribution (with Fig 2) -----------------
    fig2_path = FIG_DIR / "fig2_accuracy_distribution_boxplot.png"
    part_table_rows = [
        Paragraph("Participant Accuracies (5-Seed Means)", h2_style),
        Paragraph("• P1: E3-D 77.77% vs E4 80.93% (<b>Δ = -3.15 pp, Favors E4</b>)", ParagraphStyle('PP1', parent=body_style, textColor=ACCENT_ROSE)),
        Paragraph("• P2: E3-D 81.37% vs E4 80.70% (Δ = +0.67 pp, Favors E3-D)", body_style),
        Paragraph("• P3: E3-D 50.86% vs E4 45.29% (Δ = +5.57 pp, Favors E3-D)", body_style),
        Paragraph("• P4: E3-D 70.32% vs E4 69.20% (Δ = +1.12 pp, Favors E3-D)", body_style),
        Paragraph("• P5: E3-D 72.71% vs E4 70.24% (Δ = +2.47 pp, Favors E3-D)", body_style),
        Paragraph("• P6: E3-D 78.64% vs E4 72.27% (Δ = +6.37 pp, Favors E3-D)", body_style),
        Paragraph("• P7: E3-D 79.20% vs E4 69.27% (Δ = +9.94 pp, Favors E3-D)", body_style),
        Paragraph("• P8: E3-D 69.25% vs E4 60.90% (Δ = +8.35 pp, Favors E3-D)", body_style),
        Paragraph("• P9: E3-D 75.98% vs E4 72.84% (Δ = +3.14 pp, Favors E3-D)", body_style)
    ]
    if fig2_path.exists():
        im2 = Image(str(fig2_path), width=440, height=300)
        story.append(Table([[im2, make_card(part_table_rows, 390)]], colWidths=[460, 400]))
    else:
        story.append(make_card(part_table_rows, 860))
    story.append(PageBreak())

    # ----------------- SLIDE 17: Statistical Verification (with Fig 4) -----------------
    fig4_path = FIG_DIR / "fig4_hierarchical_bootstrap_ci.png"
    stat_card = [
        Paragraph("Inferential Test Battery", h2_style),
        Paragraph("<b>Exact Wilcoxon:</b> W = 5.0, p = 0.0390625, r_rb = 0.778", body_style),
        Paragraph("<b>Sign-Flip Permutation:</b> 2⁹ = 512 permutations, p = 0.03125", body_style),
        Paragraph("<b>Hierarchical Bootstrap:</b> 95% CI is [1.07, 6.65] pp", body_style),
        Paragraph("<b>Paired t-test:</b> t(8) = 2.791, p = 0.024", body_style),
        Paragraph("All inferential tests reject the null hypothesis of no difference.", ParagraphStyle('ST', parent=body_style, textColor=ACCENT_GREEN))
    ]
    if fig4_path.exists():
        im4 = Image(str(fig4_path), width=480, height=300)
        story.append(Table([[make_card(stat_card, 350), im4]], colWidths=[370, 490]))
    else:
        story.append(make_card(stat_card, 860))
    story.append(PageBreak())

    # ----------------- SLIDE 18: Spectral Diagnostics (with Fig 3) -----------------
    fig3_path = FIG_DIR / "fig3_spectral_density_aliasing.png"
    spec_card = [
        Paragraph("Spectral Analysis & Participant 1", h2_style),
        Paragraph("<b>Cohort Super-Nyquist Power:</b> 19.0% of cohort sEMG resides above 74.07 Hz and is folded into baseband.", body_style),
        Paragraph("<b>Participant 1 Profile:</b> P1 has only 13.51% super-Nyquist energy.", body_style),
        Paragraph("<b>Mechanism:</b> With minimal high-frequency noise, P1 experiences less aliasing distortion in native-rate mode, explaining the negative delta (-3.15 pp).", body_style),
        Paragraph("Demonstrates that spectral characteristics dictate resampling outcomes.", ParagraphStyle('SPO', parent=body_style, textColor=ACCENT_AMBER))
    ]
    if fig3_path.exists():
        im3 = Image(str(fig3_path), width=460, height=270)
        story.append(Table([[im3, make_card(spec_card, 370)]], colWidths=[480, 380]))
    else:
        story.append(make_card(spec_card, 860))
    story.append(PageBreak())

    # ----------------- SLIDE 19: Variance Analysis (with Fig 5) -----------------
    fig5_path = FIG_DIR / "fig5_variance_components_decomposition.png"
    var_card = [
        Paragraph("Two-Way ANOVA Decomposition", h2_style),
        Paragraph("• <b>Participant Share (51.3%):</b> Between-participant SD = 3.66 pp.", body_style),
        Paragraph("• <b>Seed Noise Share (12.4%):</b> Within-participant SD = 4.23 pp.", body_style),
        Paragraph("• <b>Residual Share (36.3%):</b> Stochastic model interactions.", body_style),
        Paragraph("• <b>Intraclass Correlation (ICC):</b> 0.427 (moderate participant stability).", body_style),
        Paragraph("• <b>Standard Error:</b> SE = 1.89 pp from seed noise alone.", body_style)
    ]
    if fig5_path.exists():
        im5 = Image(str(fig5_path), width=480, height=250)
        story.append(Table([[make_card(var_card, 350), im5]], colWidths=[370, 490]))
    else:
        story.append(make_card(var_card, 860))
    story.append(PageBreak())

    # ----------------- SLIDE 20: Activity Analysis (with Fig 6) -----------------
    fig6_path = FIG_DIR / "fig6_confusion_matrix_comparison.png"
    act_card = [
        Paragraph("Activity-Specific Recall Gains", h2_style),
        Paragraph("• <b>Stairs Down:</b> +6.45 pp gain (E3-D 69.32% vs E4 62.87%)", body_style),
        Paragraph("• <b>Jogging:</b> +4.13 pp gain (E3-D 77.79% vs E4 73.66%)", body_style),
        Paragraph("• <b>Walking:</b> +3.12 pp gain (E3-D 75.77% vs E4 72.65%)", body_style),
        Paragraph("• <b>Stairs Up:</b> +2.59 pp gain (E3-D 63.56% vs E4 60.97%)", body_style),
        Paragraph("Stairs down features high impact forces and eccentric contractions that benefit most from synchronized cross-modal alignment.", ParagraphStyle('AG', parent=body_style, textColor=ACCENT_GREEN))
    ]
    if fig6_path.exists():
        im6 = Image(str(fig6_path), width=480, height=240)
        story.append(Table([[make_card(act_card, 350), im6]], colWidths=[370, 490]))
    else:
        story.append(make_card(act_card, 860))
    story.append(PageBreak())

    # ----------------- SLIDE 21: Limitations -----------------
    lim_boxes = [
        Paragraph("Scientific Limitations & Boundary Conditions", h2_style),
        Paragraph("<b>1. Absence of Anti-Aliasing Pre-Filter:</b> Cubic spline was applied without an anti-aliasing pre-filter. Performance reflects aliased decimation.", body_style),
        Paragraph("<b>2. Laboratory Setting:</b> Healthy adult cohort in controlled indoor environment; community ambulation introduces irregular obstacles.", body_style),
        Paragraph("<b>3. Static Electrode Placements:</b> Assumes fixed electrode arrays; real-world usage encounters sweat impedance shifts and electrode migration.", body_style)
    ]
    story.append(make_card(lim_boxes, 860))
    story.append(PageBreak())

    # ----------------- SLIDE 22: Reproducibility Protocol -----------------
    tier_l = [
        Paragraph("Tier 1: Statistical Verification (< 10 sec)", h2_style),
        Paragraph("• Uses 90 frozen prediction CSVs in Git.", body_style),
        Paragraph("• Runs <code>pytest tests/</code> and <code>verify_release.py</code>.", body_style),
        Paragraph("• Recomputes exact Wilcoxon p=0.039, permutation p=0.031, bootstrap CI [1.07, 6.65] pp.", body_style)
    ]
    tier_r = [
        Paragraph("Tier 2: Model Retraining (~4-8 GPU hrs)", h2_style),
        Paragraph("• Uses 18 preprocessed .npz arrays (2.22 GB on Zenodo).", body_style),
        Paragraph("• Trains all 90 neural networks from scratch across 5 seeds.", body_style),
        Paragraph("• Reproduces trained weights and accuracy gap within seed noise (4.23 pp).", body_style)
    ]
    story.append(Table([[make_card(tier_l, 415), make_card(tier_r, 415)]], colWidths=[435, 435]))
    story.append(PageBreak())

    # ----------------- SLIDE 23: Research Artifacts -----------------
    doi_boxes = [
        Paragraph("Permanent Open-Science Archival", h2_style),
        Paragraph("• <b>Concept DOI (All Versions):</b> 10.5281/zenodo.22649504", body_style),
        Paragraph("• <b>Version 2.0.0 Record:</b> 10.5281/zenodo.24220130 (Frozen code, 2.22 GB arrays, verification audit)", body_style),
        Paragraph("• <b>SDALLE Benchmark Dataset:</b> 10.5281/zenodo.14841611 (CC BY 4.0)", body_style),
        Paragraph("• <b>GitHub Repository:</b> SaqibAhmadBhat/subject-independent-emg-imu-fusion (MIT License)", body_style)
    ]
    story.append(make_card(doi_boxes, 860))
    story.append(PageBreak())

    # ----------------- SLIDE 24: Conclusion & Citations -----------------
    conc_l = [
        Paragraph("Conclusions & Future Work", h2_style),
        Paragraph("<b>Core Conclusion:</b> Rate-matched sensor fusion via cubic spline achieves statistically significant superiority (+3.83 pp, p = 0.039) over native-rate fusion under matched capacity.", body_style),
        Paragraph("<b>Primary Mechanism:</b> Temporal receptive field alignment (189 ms match) dominates over high-frequency MUAP spectral retention.", body_style),
        Paragraph("<b>Future Roadmap:</b> Anti-aliased polyphase decimation filters, cross-attention transformers, and embedded edge-AI inference.", body_style)
    ]
    conc_r = [
        Paragraph("Academic Attribution", h2_style),
        Paragraph("<b>BibTeX:</b><br/><code>@software{bhat2026emgimuv2,<br/>&nbsp;&nbsp;author = {Bhat, S. A. and Sona, G. and Karuvelam, P. S.},<br/>&nbsp;&nbsp;title = {{Subject-Independent EMG-IMU Fusion: V2}},<br/>&nbsp;&nbsp;year = {2026},<br/>&nbsp;&nbsp;doi = {10.5281/zenodo.22649504}<br/>}</code>", ParagraphStyle('Bib', parent=body_style, fontSize=8.5, leading=11, fontName='Courier')),
        Paragraph("<b>Contact:</b> Saqib Ahmad Bhat (bhatsaqibahmad@gmail.com)<br/>SRM Institute of Science and Technology", stat_sub_style)
    ]
    story.append(Table([[make_card(conc_l, 415), make_card(conc_r, 415)]], colWidths=[435, 435]))

    # Build with NumberedCanvas and custom background callback
    def on_page(canvas_obj, document):
        titles = [
            "",
            "Executive Summary: The Core Research Findings",
            "Clinical & Engineering Relevance",
            "The Multirate Multimodal Sensor Challenge",
            "Addressing Critical Gaps in Prior Literature",
            "Research Hypotheses & Experimental Objectives",
            "The SDALLE Public Benchmark Dataset",
            "Multimodal Sensor Properties: sEMG vs. IMU",
            "Research Architecture: Controlled Evaluation Framework",
            "Preprocessing & Cubic-Spline Interpolation",
            "DualBranchCNN: Strictly Matched Capacity",
            "Temporal Receptive Field Dynamics",
            "Leave-One-Subject-Out (LOSO) 9-Fold Scheme",
            "Multi-Seed Replication Matrix: 90 Model Runs",
            "Primary Findings: Rate-Matched Fusion Outperforms Native-Rate",
            "Participant-Level Performance Distribution",
            "Rigorous Inferential Statistical Verification",
            "Spectral Analysis: Explaining the P1 Negative Delta",
            "Variance Components & Random Seed Sensitivity",
            "Activity-Specific Recall & Classification Gains",
            "Scientific Limitations & Boundary Conditions",
            "Two-Tier Scientific Reproducibility Protocol",
            "Public Research Artifacts & Zenodo DOIs",
            "Conclusion & Academic Attribution"
        ]
        cats = [
            "",
            "Study Overview",
            "Domain Motivation",
            "Research Problem",
            "Research Gap",
            "Methodology",
            "Experimental Data",
            "Signal Physics",
            "System Design",
            "Signal Processing",
            "Deep Architecture",
            "Ablation Mechanism",
            "Validation Rigor",
            "Experimental Rigor",
            "Results",
            "Results Breakdown",
            "Statistical Analysis",
            "Spectral Diagnostics",
            "Variance Analysis",
            "Activity Analysis",
            "Critical Analysis",
            "Open Science",
            "Permanent Archival",
            "Summary"
        ]
        p_num = document.page
        t_text = titles[p_num - 1] if p_num <= len(titles) else ""
        c_text = cats[p_num - 1] if p_num <= len(cats) else ""
        draw_background_and_header(canvas_obj, document, t_text, c_text)

    doc.build(story, canvasmaker=NumberedCanvas, onFirstPage=on_page, onLaterPages=on_page)
    print(f"Successfully generated 24-page research presentation PDF at: {OUT_PDF}")


if __name__ == "__main__":
    build_pdf()
