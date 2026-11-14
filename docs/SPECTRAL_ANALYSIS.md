# Spectral Analysis & Downsampling Aliasing Investigation

This document details the frequency-domain investigation into the cubic-spline downsampling operation used to rate-match surface electromyography (sEMG) to inertial measurement unit (IMU) rates in the V2 study.

---

## 1. Physical Nyquist Limits & Sampling Frequencies

In the SDALLE dataset:
- Surface EMG is acquired at $f_{\text{s, EMG}} = 1259.2593\text{ Hz}$ ($f_{\text{Nyquist, EMG}} \approx 629.6\text{ Hz}$).
- IMU data is acquired at $f_{\text{s, IMU}} = 148.1481\text{ Hz}$ ($f_{\text{Nyquist, IMU}} \approx 74.07\text{ Hz}$).

Human surface EMG signals exhibit physiological power spectra spanning **$20\text{ to } 450\text{ Hz}$**, with dominant firing and recruitment frequencies concentrated between **$50\text{ and } 150\text{ Hz}$**.

When downsampling continuous 1259.26 Hz signals to 148.15 Hz, any spectral energy above the new Nyquist limit ($74.07\text{ Hz}$) must be eliminated by a low-pass anti-aliasing filter. In the rate-matched condition (E3-D), downsampling was performed via `scipy.interpolate.interp1d(kind="cubic")` without a pre-filter. Consequently, high-frequency motor unit action potential energy folds back into the baseband:

$$f_{\text{alias}} = |f - k \cdot f_{\text{s, IMU}}| \le 74.07\text{ Hz}$$

---

## 2. Empirical Spectral Density & Foldover

We computed the Power Spectral Density (PSD) across all 361 trials using Welch's method (Hanning window, 512 points, 50% overlap):

<figure class="scientific-figure">
  <img src="../assets/figures/fig3_spectral_density_aliasing.svg" alt="Spectral Density & Aliasing" />
  <figcaption><strong>Figure 1:</strong> Power Spectral Density (PSD) analysis of surface EMG. Top: Raw 1259 Hz spectrum (blue) versus cubic-spline downsampled 148 Hz spectrum (red dashed), highlighting the Nyquist folding frequency at 74.07 Hz. Bottom: Participant-by-participant super-Nyquist energy fraction (&gt;74 Hz), showing Participant 1 with the lowest high-frequency energy fraction (13.51%).</figcaption>
</figure>

---

## 3. Super-Nyquist Energy by Participant

The proportion of total spectral power residing above the $74.07\text{ Hz}$ threshold was evaluated for every trial and averaged per subject:

$$\text{Fraction}_{>74\text{ Hz}} = \frac{\int_{74.07}^{629.63} P_{xx}(f) \, df}{\int_{0}^{629.63} P_{xx}(f) \, df}$$

| Participant | Age (yr) | Super-Nyquist Energy Fraction (%) | E3-D Gain ($\Delta$ pp) | Condition Favored |
|---|---|---|---|---|
| **P1** | 21 | **13.51%** | **-3.15 pp** | **E4 (Native Rate)** |
| **P2** | 24 | 17.84% | +0.67 pp | E3-D (Rate-Matched) |
| **P3** | 27 | 20.12% | +5.57 pp | E3-D (Rate-Matched) |
| **P4** | 22 | 16.95% | +1.12 pp | E3-D (Rate-Matched) |
| **P5** | 39 | 18.42% | +2.47 pp | E3-D (Rate-Matched) |
| **P6** | 25 | 21.05% | +6.37 pp | E3-D (Rate-Matched) |
| **P7** | 23 | **22.38%** | **+9.94 pp** | E3-D (Rate-Matched) |
| **P8** | 28 | 19.87% | +8.35 pp | E3-D (Rate-Matched) |
| **P9** | 12 | 20.89% | +3.14 pp | E3-D (Rate-Matched) |
| **Cohort Average** | 24.6 | **19.00%** | **+3.83 pp** | **E3-D (Rate-Matched)** |

---

## 4. Why Does Participant 1 Differ?

Participant 1 is the sole participant out of 9 who achieves higher accuracy under the native-rate condition (E4, $70.39\%$ vs E3-D, $67.24\%$).

1. **Minimal High-Frequency Content:** Participant 1 exhibits only **13.51%** super-Nyquist energy (cohort average: $19.00\%$, standard deviation: $2.49\%$). 
2. **Receptive Field Trade-off:** For participants with high super-Nyquist energy (e.g., P7 at $22.38\%$), cubic-spline downsampling effectively folds burst intensity into lower frequencies where the 189 ms receptive field easily detects it. For Participant 1, the high-frequency burst energy is already weak; downsampling distorts the subtle amplitude transitions without providing commensurate envelope benefits.
3. **Biological Determinants:** Participant 1's lower super-Nyquist energy is consistent with higher skin impedance, differences in subcutaneous adipose layer thickness, or motor unit firing recruitment patterns during locomotion.
