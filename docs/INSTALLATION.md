# Installation & Setup Guide

This guide walks through setting up the Python environment required to run, verify, or retrain the V2 research software.

---

## 1. System Requirements

- **Operating System:** macOS (macOS 12+ on Apple Silicon or Intel), Linux (Ubuntu 20.04+, Debian 11+, RHEL 8+), or Windows 10/11 with WSL2.
- **Python:** Python 3.10, 3.11, 3.12, or 3.13.
- **Hardware:**
  - *For statistical verification (Tier 1):* Any standard computer (runs in seconds, < 500 MB RAM).
  - *For retraining (Tier 2):* Multi-core CPU (8+ threads) or modern GPU (NVIDIA GPU with CUDA 11.8+ or Apple Silicon with MPS). Retraining all 90 runs sequentially on CPU takes approximately 36 hours.

---

## 2. Step-by-Step Setup

### Step 1: Clone the Repository
```bash
git clone https://github.com/SaqibAhmadBhat/subject-independent-emg-imu-fusion.git
cd subject-independent-emg-imu-fusion
```

### Step 2: Create a Virtual Environment
```bash
# Create virtual environment named .venv
python3 -m venv .venv

# Activate on macOS / Linux:
source .venv/bin/activate

# Or on Windows (PowerShell):
# .\.venv\Scripts\Activate.ps1
```

### Step 3: Upgrade Pip and Install Dependencies
```bash
pip install --upgrade pip setuptools wheel

# Install core study dependencies
pip install -r v2_rate_matching_study/V2_ROBUSTNESS_STUDY/requirements.txt

# Install testing and development dependencies
pip install pytest pytest-cov
```

### Step 4: Verify Installation
Verify that PyTorch, SciPy, and NumPy load correctly:
```bash
python3 -c "
import torch, scipy, numpy, pandas
print('PyTorch Version :', torch.__version__)
print('CUDA Available  :', torch.cuda.is_available())
print('MPS Available   :', torch.backends.mps.is_available())
print('NumPy Version   :', numpy.__version__)
print('SciPy Version   :', scipy.__version__)
print('Status          : Environment ready')
"
```

---

## 3. GPU Acceleration Notes

- **Apple Silicon (Mac M1/M2/M3/M4):**
  PyTorch automatically detects the Metal Performance Shaders (MPS) backend:
  ```python
  device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
  ```
- **NVIDIA GPU (Linux / Windows WSL2):**
  Install the appropriate CUDA-enabled PyTorch build from [pytorch.org](https://pytorch.org):
  ```bash
  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
  ```
- **CPU Only:**
  Standard PyTorch runs efficiently on multi-core CPUs using OpenMP / MKL. Training condition E3-D takes ~25 minutes per run on an Apple M4 CPU.
