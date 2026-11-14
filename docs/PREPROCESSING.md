# Signal Processing & Preprocessing Pipeline

This document describes the signal conditioning, temporal windowing, rate harmonization, and normalization protocols applied to the multimodal SDALLE dataset in the V2 study.

---

## 1. End-to-End Preprocessing Flow

The preprocessing workflow transforms continuous, multi-rate biosignal recordings into synchronized, windowed tensors ready for deep learning ingestion:

<figure class="scientific-figure">
  <img src="../assets/diagrams/signal_processing_pipeline.svg" alt="Signal Processing Pipeline" />
  <figcaption><strong>Figure 1:</strong> Preprocessing pipeline from continuous raw recordings to model tensors. Surface EMG (1259.26 Hz) and IMU (148.15 Hz) are segmented into 1.0-second sliding windows with 50% overlap. In the rate-matched condition (E3-D), cubic spline interpolation matches sEMG to IMU temporal sampling grid without anti-aliasing pre-filtering.</figcaption>
</figure>

---

## 2. Sliding Window Segmentation

Continuous recordings from all 9 participants are sliced into uniform time windows:
- **Window Length ($T$):** $1.0\text{ second}$.
- **Stride ($S$):** $0.5\text{ seconds}$ (50% temporal overlap).
- **Temporal Sample Counts:**
  - Surface EMG ($f_{\text{s, EMG}} = 1259.2593\text{ Hz}$): $L_{\text{EMG}} = 1259\text{ samples}$ per window.
  - IMU ($f_{\text{s, IMU}} = 148.1481\text{ Hz}$): $L_{\text{IMU}} = 148\text{ samples}$ per window.

---

## 3. Rate Harmonization (E3-D vs E4)

### A. Rate-Matched Condition (E3-D)
In the E3-D condition, the 8 surface EMG channels are downsampled to match the IMU sampling grid ($L = 148$ samples per window):
- **Interpolation Scheme:** Cubic-spline interpolation via `scipy.interpolate.interp1d(kind="cubic")`.
- **Anti-Aliasing Pre-filter:** None. No low-pass anti-aliasing filter was applied prior to evaluation at IMU sample timestamps.
- **Resulting Tensor Dimensions:**
  - $\mathbf{X}_{\text{EMG}} \in \mathbb{R}^{N \times 148 \times 8}$
  - $\mathbf{X}_{\text{IMU}} \in \mathbb{R}^{N \times 148 \times 48}$

### B. Native-Rate Condition (E4)
In the E4 condition, both modalities are retained at their respective hardware digitization frequencies:
- Surface EMG is preserved in its native resolution without downsampling.
- **Resulting Tensor Dimensions:**
  - $\mathbf{X}_{\text{EMG}} \in \mathbb{R}^{N \times 1259 \times 8}$
  - $\mathbf{X}_{\text{IMU}} \in \mathbb{R}^{N \times 148 \times 48}$

---

## 4. Normalization & Leakage Prevention Protocol

To ensure strict compliance with clinical machine learning standards and prevent cross-participant data contamination:
1. **Per-Fold Normalization:** Normalization parameters (mean $\mu_{\text{train}}$ and standard deviation $\sigma_{\text{train}}$) are computed exclusively on the 8 training participants within each Leave-One-Subject-Out fold.
2. **Channel-Wise Standard Scaling:**
   $$x_{\text{norm}}^{(c)} = \frac{x^{(c)} - \mu_{\text{train}}^{(c)}}{\sigma_{\text{train}}^{(c)} + \epsilon}$$
   where $\epsilon = 10^{-8}$ prevents division by zero.
3. **Test Participant Isolation:** The unseen test participant's data is standardized using the frozen training set statistics, ensuring zero leakage of test subject distribution into the training pipeline.
