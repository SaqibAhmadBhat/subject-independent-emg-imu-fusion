# Software Architecture — Multimodal EMG–IMU Robustness Study (V2)

## 1. High-Level System Architecture

The V2 research software evaluates the impact of sampling rate harmonization versus native-rate processing in deep multimodal sensor fusion for subject-independent human activity recognition (HAR).

```mermaid
graph TD
    subgraph Data Layer ["Data & Preprocessing Layer"]
        RAW["Raw SDALLE Recordings<br/>(361 Trials, 9 Subjects)<br/>sEMG: 1259.26 Hz | IMU: 148.15 Hz"]
        PREPROC["Windowing & Preprocessing<br/>(1.0 s Windows, 50% Stride)<br/>Per-Fold Training-Set Normalization"]
        RAW --> PREPROC
        PREPROC -->|Cubic Spline Interp| FOLD_E3D["Rate-Matched Dataset (E3-D)<br/>sEMG: (N, 148, 8)<br/>IMU: (N, 148, 48)"]
        PREPROC -->|Native Acquisition| FOLD_E4["Native-Rate Dataset (E4)<br/>sEMG: (N, 1259, 8)<br/>IMU: (N, 148, 48)"]
    end

    subgraph Model Layer ["Dual-Branch CNN Architecture (330,052 Parameters)"]
        FOLD_E3D -->|EMG: 148 x 8| B_E3D["EMG Branch (C=8)<br/>147,712 Params<br/>RF = 28 samples (189.0 ms)"]
        FOLD_E3D -->|IMU: 148 x 48| B_IMU1["IMU Branch (C=48)<br/>165,632 Params<br/>RF = 28 samples (189.0 ms)"]
        
        FOLD_E4 -->|EMG: 1259 x 8| B_E4["EMG Branch (C=8)<br/>147,712 Params<br/>RF = 28 samples (22.2 ms)"]
        FOLD_E4 -->|IMU: 148 x 48| B_IMU2["IMU Branch (C=48)<br/>165,632 Params<br/>RF = 28 samples (189.0 ms)"]
        
        B_E3D --> GAP1["Global Avg Pooling (128-d)"]
        B_IMU1 --> GAP2["Global Avg Pooling (128-d)"]
        B_E4 --> GAP3["Global Avg Pooling (128-d)"]
        B_IMU2 --> GAP4["Global Avg Pooling (128-d)"]
        
        GAP1 & GAP2 --> CAT1["Late Feature Concatenation (256-d)"]
        GAP3 & GAP4 --> CAT2["Late Feature Concatenation (256-d)"]
        
        CAT1 --> HEAD1["Classification Head<br/>Dense(256→64) → GELU → Dense(64→4)<br/>16,708 Params"]
        CAT2 --> HEAD2["Classification Head<br/>Dense(256→64) → GELU → Dense(64→4)<br/>16,708 Params"]
    end

    subgraph Evaluation Layer ["Evaluation & Inference Layer"]
        HEAD1 --> P_E3D["E3-D Predictions<br/>(90 Runs: 9 Folds x 5 Seeds)"]
        HEAD2 --> P_E4["E4 Predictions<br/>(90 Runs: 9 Folds x 5 Seeds)"]
        P_E3D & P_E4 --> STATS["Statistical Analysis & Sensitivity Suite<br/>- Wilcoxon Signed-Rank Test<br/>- Exact Sign-Flip Permutation Test<br/>- Two-Stage Hierarchical Bootstrap<br/>- Variance Components Decomposition"]
    end
```

---

## 2. Neural Network Branch Specification

Both branches in the dual-branch convolutional neural network (`DualBranchCNN` in `src/models.py`) share an identical block structure:

```mermaid
graph LR
    IN["Input (B, L, C)"] --> TR["Transpose (B, C, L)"]
    TR --> C1["Conv1D (k=7, s=1, out=64)<br/>No Bias"]
    C1 --> BN1["BatchNorm1d(64)"]
    BN1 --> A1["GELU"]
    A1 --> C2["Conv1D (k=5, s=1, out=64)<br/>No Bias"]
    C2 --> BN2["BatchNorm1d(64)"]
    BN2 --> A2["GELU"]
    A2 --> MP["MaxPool1D (k=2, s=2)"]
    MP --> C3["Conv1D (k=5, s=1, out=128)<br/>No Bias"]
    C3 --> BN3["BatchNorm1d(128)"]
    BN3 --> A3["GELU"]
    A3 --> C4["Conv1D (k=5, s=1, out=128)<br/>No Bias"]
    C4 --> BN4["BatchNorm1d(128)"]
    BN4 --> A4["GELU"]
    A4 --> GAP["AdaptiveAvgPool1d(1)"]
    GAP --> FL["Flatten (128-d)"]
```

### Parameter Count Breakdown
Convolutions are computed without bias terms (`bias=False`), followed by batch normalization and GELU activations:

1. **EMG Branch ($C = 8$ channels):**
   - $\text{Conv1}: 7 \times 8 \times 64 = 3{,}584$
   - $\text{BatchNorm1}: 2 \times 64 = 128$
   - $\text{Conv2}: 5 \times 64 \times 64 = 20{,}480$
   - $\text{BatchNorm2}: 2 \times 64 = 128$
   - $\text{Conv3}: 5 \times 64 \times 128 = 40{,}960$
   - $\text{BatchNorm3}: 2 \times 128 = 256$
   - $\text{Conv4}: 5 \times 128 \times 128 = 81{,}920$
   - $\text{BatchNorm4}: 2 \times 128 = 256$
   - **Total EMG Branch Parameters:** $\mathbf{147{,}712}$

2. **IMU Branch ($C = 48$ channels):**
   - $\text{Conv1}: 7 \times 48 \times 64 = 21{,}504$
   - $\text{BatchNorm1}: 2 \times 64 = 128$
   - $\text{Conv2}: 5 \times 64 \times 64 = 20{,}480$
   - $\text{BatchNorm2}: 2 \times 64 = 128$
   - $\text{Conv3}: 5 \times 64 \times 128 = 40{,}960$
   - $\text{BatchNorm3}: 2 \times 128 = 256$
   - $\text{Conv4}: 5 \times 128 \times 128 = 81{,}920$
   - $\text{BatchNorm4}: 2 \times 128 = 256$
   - **Total IMU Branch Parameters:** $\mathbf{165{,}632}$

3. **Classification Head:**
   - $\text{Linear1}: 256 \times 64 + 64 = 16{,}448$
   - $\text{Linear2}: 64 \times 4 + 4 = 260$
   - **Total Classification Head Parameters:** $\mathbf{16{,}708}$

**Overall Network Capacity:** $147{,}712 + 165{,}632 + 16{,}708 = \mathbf{330{,}052 \text{ parameters}}$.

The exact parameter count is identical between the rate-matched (E3-D) and native-rate (E4) networks, ensuring that performance differences cannot be attributed to model capacity.

---

## 3. Receptive Field Derivation

The theoretical receptive field (RF) and stride (jump $j$) at each layer of the feature extractor:

| Layer | Kernel ($k$) | Stride ($s$) | Jump in ($j_{\text{in}}$) | Receptive Field ($RF$) | Temporal Span (Native Rate, $1259.26$ Hz) | Temporal Span (Rate-Matched, $148.15$ Hz) |
|---|---|---|---|---|---|---|
| **Input** | — | — | 1 | 1 sample | 0.79 ms | 6.75 ms |
| **Conv1** | 7 | 1 | 1 | $1 + (7-1)\times 1 = \mathbf{7}$ | 5.56 ms | 47.25 ms |
| **Conv2** | 5 | 1 | 1 | $7 + (5-1)\times 1 = \mathbf{11}$ | 8.74 ms | 74.25 ms |
| **MaxPool** | 2 | 2 | 1 | $11 + (2-1)\times 1 = \mathbf{12}$ | 9.53 ms | 81.00 ms |
| **Conv3** | 5 | 1 | 2 | $12 + (5-1)\times 2 = \mathbf{20}$ | 15.88 ms | 135.00 ms |
| **Conv4 (Final)** | 5 | 1 | 2 | $20 + (5-1)\times 2 = \mathbf{28}$ | $\mathbf{22.24 \text{ ms}}$ | $\mathbf{189.00 \text{ ms}}$ |

Following the final convolution, **Adaptive Average Pooling (`AdaptiveAvgPool1d(1)`)** spans the entire temporal sequence ($148$ samples for E3-D, $1259$ samples for E4), integrating features across the entire $1.0\text{ s}$ window before classification.
