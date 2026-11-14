# Research Workflow & Experiment Lifecycle

This document describes the end-to-end scientific methodology and experimental lifecycle implemented in the V2 study.

---

## 1. End-to-End Experiment Lifecycle

```mermaid
flowchart TD
    RAW["Raw SDALLE Benchmark Dataset<br/>(Abdellatif Hamed Ibrahim et al., 2025; Zenodo: 10.5281/zenodo.14841611)<br/>9 Male Participants | 4 Locomotor Activities | 361 Continuous Trials"]
    
    RAW --> LOAD["Data Loading & Quality Checks<br/>(Raw CSV Inspection, Header Check, Channel Alignment)"]
    
    LOAD --> SPLIT["Leave-One-Participant-Out (LOSO) Split Design<br/>9 Cross-Validation Folds<br/>Train: 8 Participants (~5,500 Windows) | Test: 1 Participant (568–751 Windows)"]
    
    SPLIT --> COND["Experimental Preprocessing Pathways"]
    
    subgraph Pathways ["Two Controlled Conditions"]
        COND -->|Cubic Spline Interpolation to 148.15 Hz<br/>scipy.interpolate.interp1d<br/>No Anti-Aliasing Filter| E3D["Condition E3-D: Rate-Matched Fusion<br/>sEMG: (N, 148, 8) | IMU: (N, 148, 48)"]
        COND -->|Preserve Native Sampling Rates<br/>Zero Downsampling / Filtering| E4["Condition E4: Native-Rate Fusion<br/>sEMG: (N, 1259, 8) | IMU: (N, 148, 48)"]
    end
    
    E3D --> TRAIN["Repeated Stochastic Training<br/>5 Fixed Random Seeds: 42, 123, 2024, 3407, 7777<br/>Architecture: Dual-Branch CNN (330,052 Parameters)<br/>Optimizer: Adam (lr=1e-3, weight_decay=1e-4) | Cosine LR Annealing<br/>9 Folds x 5 Seeds = 45 Runs per Condition (90 Runs Total)"]
    E4 --> TRAIN
    
    TRAIN --> PREDS["Frozen Run Records<br/>- predictions.csv (Per-window test true vs predicted label)<br/>- history.json (Per-epoch training loss & accuracy)<br/>- meta.json (Wall-clock time, hyperparameters, environment)"]
    
    PREDS --> AGG["Participant-Level Metric Aggregation<br/>Seed-Averaged Participant Accuracies (N = 9)<br/>Mean Paired Difference: +3.83 pp (RM 72.90% vs NR 69.07%)"]
    
    AGG --> STATS["Formal Hypothesis Testing & Sensitivity Suite"]
    
    subgraph StatisticalInference ["Inference & Verification"]
        STATS --> P1["Protocol-Specified Primary Analysis<br/>Two-sided Wilcoxon Signed-Rank Test: W=5, p=0.039, r=0.78<br/>Percentile Bootstrap 95% CI: 1.27 to 6.35 pp"]
        STATS --> P2["Post Hoc Sensitivity Checks<br/>Exact Sign-Flip Permutation Test: p=0.031<br/>Hierarchical Two-Stage Bootstrap CI: 1.07 to 6.65 pp<br/>Leave-One-Seed-Out: p = 0.012 to 0.055<br/>Leave-One-Participant-Out: p = 0.008 to 0.078"]
        STATS --> P3["Variance Components Analysis<br/>Seed SD: 4.23 pp | Between-Participant SD: 3.66 pp | ICC: 0.43"]
        STATS --> P4["Full-Cohort Spectral Audit (361 Trials)<br/>sEMG Power > 74.07 Hz: 19.0% | Power < 20 Hz: 33.1%"]
    end
    
    StatisticalInference --> CANON["Canonical Reporting Artifacts<br/>Tables 1–4, Figures 1–5, Manuscript v2.1 Evidence Base"]
```

---

## 2. Experimental Conditions: E3-D versus E4

| Feature / Dimension | Condition E3-D (Rate-Matched Fusion) | Condition E4 (Native-Rate Fusion) | Scientific Significance |
|---|---|---|---|
| **sEMG Sampling Frequency** | **148.15 Hz** (nominal downsampling) | **1259.26 Hz** (unaltered native rate) | Investigates whether sEMG downsampling impairs classification. |
| **IMU Sampling Frequency** | **148.15 Hz** (native rate) | **148.15 Hz** (native rate) | IMU kinematics are identical across conditions. |
| **Interpolation Method** | Cubic spline (`scipy.interpolate.interp1d(kind='cubic')`) evaluated at IMU timepoints | None (native time series) | Standard rate-matching practice without anti-aliasing pre-filtering. |
| **Input Sequence Length** | sEMG: **148** samples<br>IMU: **148** samples | sEMG: **1259** samples<br>IMU: **148** samples | Rate matching reduces sEMG sequence length by an 8.5× factor. |
| **Model Architecture** | `DualBranchCNN` (330,052 parameters) | `DualBranchCNN` (330,052 parameters) | **Identical capacity and structure** between conditions. |
| **EMG Branch Receptive Field** | 28 samples = **189.00 ms** | 28 samples = **22.24 ms** | Convolutions at native rate span a much narrower temporal interval. |
| **Global Pooling** | Spans full 148 samples (1.0 s) | Spans full 1259 samples (1.0 s) | Both models aggregate across the entire 1.0 s window via GAP. |
| **Median Training Time** | **1,525.5 s** per run | **6,621.2 s** per run (**4.34× longer**) | Native-rate convolution on 1259 samples incurs substantial overhead. |
| **Observed Accuracy (Mean)** | **72.90%** $\pm$ 9.24% | **69.07%** $\pm$ 10.80% | Paired difference: **+3.83 pp** favoring rate matching. |

---

## 3. Methodological Principles

### A. Non-Contaminated Normalization
All input normalizations (channel-wise z-score) are fitted **strictly on the training partition of each fold**:
$$\mu_{\text{train}} = \frac{1}{N_{\text{train}} L} \sum_{i, t} x_{i, t}, \quad \sigma_{\text{train}} = \sqrt{\frac{1}{N_{\text{train}} L} \sum_{i, t} (x_{i, t} - \mu_{\text{train}})^2}$$
Test data are standardized using $\mu_{\text{train}}$ and $\sigma_{\text{train}}$. No test fold information leaks into training data or normalization.

### B. Unit of Inferential Analysis
The participant ($N=9$) is the unit of statistical inference. Windows within a participant are correlated (overlapping by 50% across consecutive samples). Therefore, all hypothesis tests and confidence intervals are computed over participant-level summary metrics, not on pooled individual windows.

### C. Accounting for Stochastic Training Variability
Prior studies often evaluate a single seed, risking seed-dependent bias. In V2, 5 random seeds (42, 123, 2024, 3407, 7777) are executed across all 9 folds, yielding 45 runs per condition. Our variance decomposition reveals that seed-to-seed standard deviation within participants ($4.23$ pp) exceeds between-participant standard deviation ($3.66$ pp), demonstrating that multi-seed replication is essential for robust deep learning evaluation in wearable HAR.
