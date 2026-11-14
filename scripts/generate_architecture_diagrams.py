#!/usr/bin/env python3
"""
scripts/generate_architecture_diagrams.py
-----------------------------------------
Generates clean, modern, publication-ready SVG architecture diagrams for the EMG-IMU platform.
Outputs:
- research_workflow.svg
- signal_processing_pipeline.svg
- dual_branch_cnn_architecture.svg
- loso_evaluation_matrix.svg
- reproducibility_architecture.svg
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "docs" / "assets" / "diagrams"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def create_dual_branch_cnn_svg():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 600" width="100%" height="100%" style="background:#0F172A; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
  <defs>
    <linearGradient id="emgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0284C7"/>
      <stop offset="100%" stop-color="#0369A1"/>
    </linearGradient>
    <linearGradient id="imuGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38BDF8"/>
      <stop offset="100%" stop-color="#0284C7"/>
    </linearGradient>
    <linearGradient id="headGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#8B5CF6"/>
      <stop offset="100%" stop-color="#6D28D9"/>
    </linearGradient>
    <linearGradient id="outGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#10B981"/>
      <stop offset="100%" stop-color="#059669"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.4"/>
    </filter>
  </defs>

  <!-- Title -->
  <text x="500" y="45" fill="#F8FAFC" font-size="22" font-weight="bold" text-anchor="middle">DualBranchCNN Neural Network Architecture</text>
  <text x="500" y="70" fill="#94A3B8" font-size="13" text-anchor="middle">Strictly Capacity-Matched Multimodal Fusion (330,052 Trainable Parameters)</text>

  <!-- EMG Branch Box -->
  <rect x="50" y="105" width="410" height="230" rx="12" fill="#1E293B" stroke="#0284C7" stroke-width="2" filter="url(#glow)"/>
  <rect x="50" y="105" width="410" height="35" rx="12" fill="url(#emgGrad)"/>
  <text x="255" y="128" fill="#FFFFFF" font-size="14" font-weight="bold" text-anchor="middle">sEMG Encoder Branch (147,712 Parameters)</text>

  <!-- EMG Inputs -->
  <rect x="75" y="155" width="105" height="50" rx="8" fill="#0F172A" stroke="#38BDF8" stroke-width="1.5"/>
  <text x="127" y="177" fill="#F8FAFC" font-size="12" font-weight="bold" text-anchor="middle">Input Tensor</text>
  <text x="127" y="194" fill="#94A3B8" font-size="10.5" text-anchor="middle">8 x 148 / 238</text>

  <!-- Arrow -->
  <path d="M 180 180 L 205 180" stroke="#38BDF8" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- EMG Conv Layers -->
  <rect x="205" y="155" width="115" height="50" rx="8" fill="#0F172A" stroke="#38BDF8" stroke-width="1.5"/>
  <text x="262" y="175" fill="#F8FAFC" font-size="11.5" font-weight="bold" text-anchor="middle">Conv1D + BN</text>
  <text x="262" y="192" fill="#94A3B8" font-size="10" text-anchor="middle">k=7, s=2, ch=64</text>

  <!-- Arrow -->
  <path d="M 320 180 L 345 180" stroke="#38BDF8" stroke-width="2"/>

  <!-- EMG Conv2 + Pool -->
  <rect x="345" y="155" width="95" height="50" rx="8" fill="#0F172A" stroke="#38BDF8" stroke-width="1.5"/>
  <text x="392" y="175" fill="#F8FAFC" font-size="11.5" font-weight="bold" text-anchor="middle">Conv2 + Pool</text>
  <text x="392" y="192" fill="#94A3B8" font-size="10" text-anchor="middle">ch=128, pool=4</text>

  <!-- EMG Features -->
  <rect x="180" y="235" width="150" height="40" rx="8" fill="#0369A1" stroke="#38BDF8" stroke-width="1.5"/>
  <text x="255" y="260" fill="#FFFFFF" font-size="12" font-weight="bold" text-anchor="middle">128-D EMG Vector</text>

  <!-- Connect Conv to Vector -->
  <path d="M 392 205 L 392 255 L 330 255" fill="none" stroke="#38BDF8" stroke-width="2"/>

  <!-- IMU Branch Box -->
  <rect x="540" y="105" width="410" height="230" rx="12" fill="#1E293B" stroke="#0284C7" stroke-width="2" filter="url(#glow)"/>
  <rect x="540" y="105" width="410" height="35" rx="12" fill="url(#imuGrad)"/>
  <text x="745" y="128" fill="#FFFFFF" font-size="14" font-weight="bold" text-anchor="middle">IMU Encoder Branch (165,632 Parameters)</text>

  <!-- IMU Inputs -->
  <rect x="565" y="155" width="105" height="50" rx="8" fill="#0F172A" stroke="#38BDF8" stroke-width="1.5"/>
  <text x="617" y="177" fill="#F8FAFC" font-size="12" font-weight="bold" text-anchor="middle">Input Tensor</text>
  <text x="617" y="194" fill="#94A3B8" font-size="10.5" text-anchor="middle">48 x 148</text>

  <!-- Arrow -->
  <path d="M 670 180 L 695 180" stroke="#38BDF8" stroke-width="2"/>

  <!-- IMU Conv Layers -->
  <rect x="695" y="155" width="115" height="50" rx="8" fill="#0F172A" stroke="#38BDF8" stroke-width="1.5"/>
  <text x="752" y="175" fill="#F8FAFC" font-size="11.5" font-weight="bold" text-anchor="middle">Conv1D + BN</text>
  <text x="752" y="192" fill="#94A3B8" font-size="10" text-anchor="middle">k=7, s=2, ch=64</text>

  <!-- Arrow -->
  <path d="M 810 180 L 835 180" stroke="#38BDF8" stroke-width="2"/>

  <!-- IMU Conv2 + Pool -->
  <rect x="835" y="155" width="95" height="50" rx="8" fill="#0F172A" stroke="#38BDF8" stroke-width="1.5"/>
  <text x="882" y="175" fill="#F8FAFC" font-size="11.5" font-weight="bold" text-anchor="middle">Conv2 + Pool</text>
  <text x="882" y="192" fill="#94A3B8" font-size="10" text-anchor="middle">ch=128, pool=4</text>

  <!-- IMU Features -->
  <rect x="670" y="235" width="150" height="40" rx="8" fill="#0369A1" stroke="#38BDF8" stroke-width="1.5"/>
  <text x="745" y="260" fill="#FFFFFF" font-size="12" font-weight="bold" text-anchor="middle">128-D IMU Vector</text>

  <!-- Connect Conv to Vector -->
  <path d="M 882 205 L 882 255 L 820 255" fill="none" stroke="#38BDF8" stroke-width="2"/>

  <!-- Concat Node -->
  <path d="M 255 275 L 255 385 L 430 385" fill="none" stroke="#38BDF8" stroke-width="2.5"/>
  <path d="M 745 275 L 745 385 L 570 385" fill="none" stroke="#38BDF8" stroke-width="2.5"/>

  <rect x="430" y="365" width="140" height="40" rx="8" fill="#475569" stroke="#94A3B8" stroke-width="1.5"/>
  <text x="500" y="390" fill="#FFFFFF" font-size="12.5" font-weight="bold" text-anchor="middle">Concat (256-D)</text>

  <!-- Fusion Classifier Head Box -->
  <rect x="250" y="435" width="500" height="135" rx="12" fill="#1E293B" stroke="#8B5CF6" stroke-width="2" filter="url(#glow)"/>
  <rect x="250" y="435" width="500" height="32" rx="12" fill="url(#headGrad)"/>
  <text x="500" y="456" fill="#FFFFFF" font-size="13.5" font-weight="bold" text-anchor="middle">Fusion Classifier Head (16,708 Parameters)</text>

  <!-- Connect Concat to Head -->
  <path d="M 500 405 L 500 435" stroke="#8B5CF6" stroke-width="2.5"/>

  <!-- Dense Layers -->
  <rect x="280" y="485" width="120" height="45" rx="8" fill="#0F172A" stroke="#8B5CF6" stroke-width="1.5"/>
  <text x="340" y="505" fill="#F8FAFC" font-size="11.5" font-weight="bold" text-anchor="middle">Dense (64 units)</text>
  <text x="340" y="521" fill="#94A3B8" font-size="10" text-anchor="middle">Dropout = 0.3</text>

  <!-- Arrow -->
  <path d="M 400 507 L 440 507" stroke="#8B5CF6" stroke-width="2"/>

  <!-- Softmax Output -->
  <rect x="440" y="485" width="130" height="45" rx="8" fill="#0F172A" stroke="#8B5CF6" stroke-width="1.5"/>
  <text x="505" y="505" fill="#F8FAFC" font-size="11.5" font-weight="bold" text-anchor="middle">Dense (4 classes)</text>
  <text x="505" y="521" fill="#94A3B8" font-size="10" text-anchor="middle">Logits / Softmax</text>

  <!-- Arrow to Output Classes -->
  <path d="M 570 507 L 610 507" stroke="#10B981" stroke-width="2"/>

  <!-- Output Box -->
  <rect x="610" y="480" width="120" height="55" rx="8" fill="url(#outGrad)"/>
  <text x="670" y="503" fill="#FFFFFF" font-size="11" font-weight="bold" text-anchor="middle">Predicted Mode</text>
  <text x="670" y="520" fill="#E2E8F0" font-size="9" text-anchor="middle">Walk / Jog / Stairs</text>
</svg>"""
    (OUTPUT_DIR / "dual_branch_cnn_architecture.svg").write_text(svg, encoding="utf-8")
    print("  Created dual_branch_cnn_architecture.svg")


def create_signal_processing_pipeline_svg():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 520" width="100%" height="100%" style="background:#0F172A; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
  <defs>
    <linearGradient id="emgRaw" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38BDF8"/>
      <stop offset="100%" stop-color="#0284C7"/>
    </linearGradient>
    <linearGradient id="imuRaw" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#F59E0B"/>
      <stop offset="100%" stop-color="#D97706"/>
    </linearGradient>
    <linearGradient id="splineGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#8B5CF6"/>
      <stop offset="100%" stop-color="#6D28D9"/>
    </linearGradient>
  </defs>

  <!-- Title -->
  <text x="500" y="40" fill="#F8FAFC" font-size="20" font-weight="bold" text-anchor="middle">Multimodal Signal Preprocessing & Rate-Matching Pipeline</text>
  <text x="500" y="65" fill="#94A3B8" font-size="13" text-anchor="middle">Controlled Ablation: Rate-Matched (E3-D) vs Native-Rate (E4)</text>

  <!-- Raw Sensors Section -->
  <rect x="40" y="95" width="220" height="380" rx="10" fill="#1E293B" stroke="#334155" stroke-width="1.5"/>
  <text x="150" y="125" fill="#F8FAFC" font-size="14" font-weight="bold" text-anchor="middle">Raw SDALLE Acquisition</text>

  <!-- EMG Node -->
  <rect x="60" y="150" width="180" height="70" rx="8" fill="url(#emgRaw)"/>
  <text x="150" y="178" fill="#FFFFFF" font-size="13" font-weight="bold" text-anchor="middle">sEMG Sensors (8 Ch)</text>
  <text x="150" y="200" fill="#F0F9FF" font-size="11" text-anchor="middle">fs ≈ 1259.26 Hz</text>

  <!-- IMU Node -->
  <rect x="60" y="270" width="180" height="70" rx="8" fill="url(#imuRaw)"/>
  <text x="150" y="298" fill="#FFFFFF" font-size="13" font-weight="bold" text-anchor="middle">IMU Sensors (48 Ch)</text>
  <text x="150" y="320" fill="#FFFBEB" font-size="11" text-anchor="middle">fs ≈ 148.15 Hz</text>

  <!-- Sync Timestamp Note -->
  <rect x="60" y="380" width="180" height="75" rx="8" fill="#0F172A" stroke="#475569" stroke-width="1"/>
  <text x="150" y="405" fill="#94A3B8" font-size="10.5" font-weight="bold" text-anchor="middle">Temporal Alignment</text>
  <text x="150" y="423" fill="#CBD5E1" font-size="9.5" text-anchor="middle">Synchronized Sample Times</text>
  <text x="150" y="439" fill="#CBD5E1" font-size="9.5" text-anchor="middle">361 Validated Trials</text>

  <!-- Rate Transformation Stage -->
  <rect x="310" y="95" width="340" height="380" rx="10" fill="#1E293B" stroke="#334155" stroke-width="1.5"/>
  <text x="480" y="125" fill="#F8FAFC" font-size="14" font-weight="bold" text-anchor="middle">Rate-Matching & Conditioning</text>

  <!-- Path E3-D: Spline Interpolation -->
  <rect x="330" y="150" width="300" height="110" rx="8" fill="#0F172A" stroke="#8B5CF6" stroke-width="1.5"/>
  <rect x="330" y="150" width="300" height="28" rx="8" fill="url(#splineGrad)"/>
  <text x="480" y="169" fill="#FFFFFF" font-size="12" font-weight="bold" text-anchor="middle">Condition E3-D: Cubic Spline Interpolation</text>
  <text x="480" y="196" fill="#F8FAFC" font-size="11" text-anchor="middle">scipy.interpolate.interp1d(kind='cubic')</text>
  <text x="480" y="215" fill="#FCD34D" font-size="10.5" text-anchor="middle">Evaluated at IMU sample times (148.15 Hz)</text>
  <text x="480" y="235" fill="#F87171" font-size="10" font-weight="bold" text-anchor="middle">⚠ No Anti-Aliasing Pre-Filter Applied</text>

  <!-- Path E4: Native-Rate -->
  <rect x="330" y="280" width="300" height="90" rx="8" fill="#0F172A" stroke="#64748B" stroke-width="1.5"/>
  <rect x="330" y="280" width="300" height="28" rx="8" fill="#475569"/>
  <text x="480" y="299" fill="#FFFFFF" font-size="12" font-weight="bold" text-anchor="middle">Condition E4: Native-Rate Multirate</text>
  <text x="480" y="325" fill="#F8FAFC" font-size="11" text-anchor="middle">sEMG remains at 1259.26 Hz (8 ch)</text>
  <text x="480" y="345" fill="#94A3B8" font-size="10.5" text-anchor="middle">IMU remains at 148.15 Hz (48 ch)</text>

  <!-- Windowing Stage -->
  <rect x="690" y="95" width="270" height="380" rx="10" fill="#1E293B" stroke="#334155" stroke-width="1.5"/>
  <text x="825" y="125" fill="#F8FAFC" font-size="14" font-weight="bold" text-anchor="middle">Sliding Window Segmentation</text>

  <!-- 200 ms Windowing E3-D -->
  <rect x="710" y="150" width="230" height="110" rx="8" fill="#0F172A" stroke="#0284C7" stroke-width="1.5"/>
  <text x="825" y="175" fill="#38BDF8" font-size="12" font-weight="bold" text-anchor="middle">E3-D Window Tensors</text>
  <text x="825" y="198" fill="#F8FAFC" font-size="11" text-anchor="middle">sEMG: 8 ch × 148 samples</text>
  <text x="825" y="218" fill="#F8FAFC" font-size="11" text-anchor="middle">IMU: 48 ch × 148 samples</text>
  <text x="825" y="240" fill="#10B981" font-size="10" font-weight="bold" text-anchor="middle">Identical Sequence Length (148)</text>

  <!-- 200 ms Windowing E4 -->
  <rect x="710" y="280" width="230" height="110" rx="8" fill="#0F172A" stroke="#64748B" stroke-width="1.5"/>
  <text x="825" y="305" fill="#94A3B8" font-size="12" font-weight="bold" text-anchor="middle">E4 Window Tensors</text>
  <text x="825" y="328" fill="#F8FAFC" font-size="11" text-anchor="middle">sEMG: 8 ch × 238 samples</text>
  <text x="825" y="348" fill="#F8FAFC" font-size="11" text-anchor="middle">IMU: 48 ch × 148 samples</text>
  <text x="825" y="370" fill="#F59E0B" font-size="10" font-weight="bold" text-anchor="middle">Multirate Dual Sampling</text>

  <!-- Connectors -->
  <path d="M 240 185 L 330 185" stroke="#38BDF8" stroke-width="2"/>
  <path d="M 240 185 L 285 185 L 285 320 L 330 320" stroke="#38BDF8" stroke-width="2" fill="none"/>
  <path d="M 630 185 L 710 185" stroke="#8B5CF6" stroke-width="2"/>
  <path d="M 630 320 L 710 320" stroke="#64748B" stroke-width="2"/>
</svg>"""
    (OUTPUT_DIR / "signal_processing_pipeline.svg").write_text(svg, encoding="utf-8")
    print("  Created signal_processing_pipeline.svg")


def create_research_workflow_svg():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 480" width="100%" height="100%" style="background:#0F172A; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
  <text x="500" y="40" fill="#F8FAFC" font-size="20" font-weight="bold" text-anchor="middle">End-to-End Experimental & Validation Architecture</text>
  <text x="500" y="65" fill="#94A3B8" font-size="13" text-anchor="middle">Rigorous Multi-Seed Leave-One-Subject-Out Cross-Validation Matrix</text>

  <!-- Stage 1 -->
  <rect x="40" y="100" width="160" height="280" rx="10" fill="#1E293B" stroke="#0284C7" stroke-width="1.5"/>
  <rect x="40" y="100" width="160" height="30" rx="10" fill="#0284C7"/>
  <text x="120" y="120" fill="#FFFFFF" font-size="12" font-weight="bold" text-anchor="middle">1. Data Ingestion</text>
  <text x="120" y="155" fill="#F8FAFC" font-size="11" font-weight="bold" text-anchor="middle">SDALLE Dataset</text>
  <text x="120" y="180" fill="#94A3B8" font-size="10" text-anchor="middle">9 Participants</text>
  <text x="120" y="200" fill="#94A3B8" font-size="10" text-anchor="middle">4 Activity Classes</text>
  <text x="120" y="220" fill="#94A3B8" font-size="10" text-anchor="middle">361 Raw Trials</text>
  <text x="120" y="250" fill="#38BDF8" font-size="10" font-weight="bold" text-anchor="middle">Zenodo Verified</text>
  <text x="120" y="270" fill="#94A3B8" font-size="9.5" text-anchor="middle">10.5281/zenodo.14841611</text>

  <!-- Arrow -->
  <path d="M 200 240 L 230 240" stroke="#38BDF8" stroke-width="2"/>

  <!-- Stage 2 -->
  <rect x="230" y="100" width="160" height="280" rx="10" fill="#1E293B" stroke="#38BDF8" stroke-width="1.5"/>
  <rect x="230" y="100" width="160" height="30" rx="10" fill="#0369A1"/>
  <text x="310" y="120" fill="#FFFFFF" font-size="12" font-weight="bold" text-anchor="middle">2. Windowing</text>
  <text x="310" y="155" fill="#F8FAFC" font-size="11" font-weight="bold" text-anchor="middle">200 ms Windows</text>
  <text x="310" y="180" fill="#94A3B8" font-size="10" text-anchor="middle">50% Overlap (100 ms)</text>
  <text x="310" y="200" fill="#94A3B8" font-size="10" text-anchor="middle">Cubic Spline (E3-D)</text>
  <text x="310" y="220" fill="#94A3B8" font-size="10" text-anchor="middle">Native Multirate (E4)</text>
  <text x="310" y="250" fill="#38BDF8" font-size="10" font-weight="bold" text-anchor="middle">Total Windows</text>
  <text x="310" y="270" fill="#94A3B8" font-size="9.5" text-anchor="middle">6,203 test / seed</text>

  <!-- Arrow -->
  <path d="M 390 240 L 420 240" stroke="#38BDF8" stroke-width="2"/>

  <!-- Stage 3 -->
  <rect x="420" y="100" width="170" height="280" rx="10" fill="#1E293B" stroke="#8B5CF6" stroke-width="1.5"/>
  <rect x="420" y="100" width="170" height="30" rx="10" fill="#8B5CF6"/>
  <text x="505" y="120" fill="#FFFFFF" font-size="12" font-weight="bold" text-anchor="middle">3. 90-Run LOSO</text>
  <text x="505" y="155" fill="#F8FAFC" font-size="11" font-weight="bold" text-anchor="middle">5 Random Seeds</text>
  <text x="505" y="175" fill="#CBD5E1" font-size="9.5" text-anchor="middle">42, 123, 2024, 3407, 7777</text>
  <text x="505" y="205" fill="#F8FAFC" font-size="11" font-weight="bold" text-anchor="middle">9 LOSO Folds</text>
  <text x="505" y="225" fill="#CBD5E1" font-size="9.5" text-anchor="middle">Leave-One-Participant-Out</text>
  <text x="505" y="255" fill="#C084FC" font-size="10.5" font-weight="bold" text-anchor="middle">2 Conditions</text>
  <text x="505" y="275" fill="#CBD5E1" font-size="9.5" text-anchor="middle">9 × 5 × 2 = 90 Models</text>

  <!-- Arrow -->
  <path d="M 590 240 L 620 240" stroke="#8B5CF6" stroke-width="2"/>

  <!-- Stage 4 -->
  <rect x="620" y="100" width="160" height="280" rx="10" fill="#1E293B" stroke="#10B981" stroke-width="1.5"/>
  <rect x="620" y="100" width="160" height="30" rx="10" fill="#10B981"/>
  <text x="700" y="120" fill="#FFFFFF" font-size="12" font-weight="bold" text-anchor="middle">4. Results</text>
  <text x="700" y="155" fill="#F8FAFC" font-size="11" font-weight="bold" text-anchor="middle">E3-D: 72.90%</text>
  <text x="700" y="175" fill="#94A3B8" font-size="10" text-anchor="middle">± 9.24% SD</text>
  <text x="700" y="205" fill="#F8FAFC" font-size="11" font-weight="bold" text-anchor="middle">E4: 69.07%</text>
  <text x="700" y="225" fill="#94A3B8" font-size="10" text-anchor="middle">± 10.80% SD</text>
  <text x="700" y="255" fill="#10B981" font-size="11" font-weight="bold" text-anchor="middle">Gap: +3.83 pp</text>
  <text x="700" y="275" fill="#94A3B8" font-size="9.5" text-anchor="middle">8 of 9 participants +</text>

  <!-- Arrow -->
  <path d="M 780 240 L 810 240" stroke="#10B981" stroke-width="2"/>

  <!-- Stage 5 -->
  <rect x="810" y="100" width="150" height="280" rx="10" fill="#1E293B" stroke="#F59E0B" stroke-width="1.5"/>
  <rect x="810" y="100" width="150" height="30" rx="10" fill="#D97706"/>
  <text x="885" y="120" fill="#FFFFFF" font-size="12" font-weight="bold" text-anchor="middle">5. Inference</text>
  <text x="885" y="155" fill="#F8FAFC" font-size="10.5" font-weight="bold" text-anchor="middle">Wilcoxon W = 5</text>
  <text x="885" y="175" fill="#FCD34D" font-size="10" text-anchor="middle">p = 0.039</text>
  <text x="885" y="205" fill="#F8FAFC" font-size="10.5" font-weight="bold" text-anchor="middle">Sign-Flip Perm</text>
  <text x="885" y="225" fill="#FCD34D" font-size="10" text-anchor="middle">p = 0.031</text>
  <text x="885" y="255" fill="#F8FAFC" font-size="10.5" font-weight="bold" text-anchor="middle">Bootstrap 95% CI</text>
  <text x="885" y="275" fill="#FCD34D" font-size="10" text-anchor="middle">[1.07, 6.65] pp</text>
</svg>"""
    (OUTPUT_DIR / "research_workflow.svg").write_text(svg, encoding="utf-8")
    print("  Created research_workflow.svg")


def create_reproducibility_architecture_svg():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 950 420" width="100%" height="100%" style="background:#0F172A; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
  <text x="475" y="40" fill="#F8FAFC" font-size="20" font-weight="bold" text-anchor="middle">Two-Tier Scientific Reproducibility Protocol</text>
  <text x="475" y="65" fill="#94A3B8" font-size="13" text-anchor="middle">Transparent, Multi-Level Verification Designed for Independent Researchers</text>

  <!-- Tier 1 -->
  <rect x="50" y="100" width="400" height="280" rx="12" fill="#1E293B" stroke="#0284C7" stroke-width="2"/>
  <rect x="50" y="100" width="400" height="35" rx="12" fill="#0284C7"/>
  <text x="250" y="123" fill="#FFFFFF" font-size="13" font-weight="bold" text-anchor="middle">Tier 1: Statistical Verification (&lt; 10 seconds)</text>

  <rect x="75" y="155" width="350" height="50" rx="8" fill="#0F172A" stroke="#38BDF8" stroke-width="1"/>
  <text x="250" y="177" fill="#F8FAFC" font-size="11.5" font-weight="bold" text-anchor="middle">Input: 90 Frozen Prediction CSVs</text>
  <text x="250" y="195" fill="#94A3B8" font-size="10" text-anchor="middle">Tracked in Git repository (6,203 test rows / seed)</text>

  <rect x="75" y="220" width="350" height="50" rx="8" fill="#0F172A" stroke="#38BDF8" stroke-width="1"/>
  <text x="250" y="242" fill="#F8FAFC" font-size="11.5" font-weight="bold" text-anchor="middle">Execution: Verification Test Suite</text>
  <text x="250" y="260" fill="#38BDF8" font-size="10" text-anchor="middle">pytest tests/ &amp; verify_v2_statistics.py</text>

  <rect x="75" y="285" width="350" height="75" rx="8" fill="#0369A1" stroke="#38BDF8" stroke-width="1"/>
  <text x="250" y="307" fill="#FFFFFF" font-size="11" font-weight="bold" text-anchor="middle">Output: Bit-Identical Scientific Recomputation</text>
  <text x="250" y="325" fill="#E0F2FE" font-size="10" text-anchor="middle">Wilcoxon p=0.039, Sign-Flip p=0.031</text>
  <text x="250" y="343" fill="#E0F2FE" font-size="10" text-anchor="middle">Bootstrap CI [1.07, 6.65], SD breakdown</text>

  <!-- Tier 2 -->
  <rect x="500" y="100" width="400" height="280" rx="12" fill="#1E293B" stroke="#8B5CF6" stroke-width="2"/>
  <rect x="500" y="100" width="400" height="35" rx="12" fill="#8B5CF6"/>
  <text x="700" y="123" fill="#FFFFFF" font-size="13" font-weight="bold" text-anchor="middle">Tier 2: Full Model Retraining (~4-8 GPU hrs)</text>

  <rect x="525" y="155" width="350" height="50" rx="8" fill="#0F172A" stroke="#C084FC" stroke-width="1"/>
  <text x="700" y="177" fill="#F8FAFC" font-size="11.5" font-weight="bold" text-anchor="middle">Input: 18 Preprocessed .npz Arrays</text>
  <text x="700" y="195" fill="#94A3B8" font-size="10" text-anchor="middle">v2_reproducibility_data_final.zip (2.22 GB on Zenodo)</text>

  <rect x="525" y="220" width="350" height="50" rx="8" fill="#0F172A" stroke="#C084FC" stroke-width="1"/>
  <text x="700" y="242" fill="#F8FAFC" font-size="11.5" font-weight="bold" text-anchor="middle">Execution: Multi-Seed Training Harness</text>
  <text x="700" y="260" fill="#C084FC" font-size="10" text-anchor="middle">python3 robustness_train.py --seed 42..7777</text>

  <rect x="525" y="285" width="350" height="75" rx="8" fill="#6D28D9" stroke="#C084FC" stroke-width="1"/>
  <text x="700" y="307" fill="#FFFFFF" font-size="11" font-weight="bold" text-anchor="middle">Output: Complete Model Checkpoint Regeneration</text>
  <text x="700" y="325" fill="#EDE9FE" font-size="10" text-anchor="middle">90 freshly trained weights, logs &amp; predictions</text>
  <text x="700" y="343" fill="#EDE9FE" font-size="10" text-anchor="middle">Replicates accuracy gap within seed noise (4.23 pp)</text>
</svg>"""
    (OUTPUT_DIR / "reproducibility_architecture.svg").write_text(svg, encoding="utf-8")
    print("  Created reproducibility_architecture.svg")


def main():
    print("Generating SVG architecture diagrams...")
    create_dual_branch_cnn_svg()
    create_signal_processing_pipeline_svg()
    create_research_workflow_svg()
    create_reproducibility_architecture_svg()
    print("All architecture diagrams created successfully.")


if __name__ == "__main__":
    main()
