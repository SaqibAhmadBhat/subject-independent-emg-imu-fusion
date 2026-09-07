"""
models.py
---------
Lightweight 1D CNN architectures for E1–E4.

Design philosophy (identical across all experiments for fairness):
  - Two conv blocks: [Conv1d → BN → ReLU] × 2 per block, with MaxPool between
  - AdaptiveAvgPool collapses time to a fixed-length feature vector
  - Shared classifier head: Linear(128, 64) → ReLU → Dropout(0.3) → Linear(64, 4)

E4 uses two independent branches (one EMG, one IMU), each producing 128-dim
features, concatenated → Linear(256, 64) → ...

Input convention (PyTorch): (batch, channels, timesteps)
  - Callers must transpose (N, W, C) → (N, C, W) before passing to the model.

Predetermined hyperparameters (NOT tuned on any test fold):
  - Conv filters:  [64, 128]
  - Kernel sizes:  7 (first conv), 5 (subsequent convs)
  - Dropout:       0.3
  - Latent dim:    128 per branch
"""

from __future__ import annotations

import torch
import torch.nn as nn


# ── Shared building block ─────────────────────────────────────────────────────

class _ConvBlock(nn.Module):
    """Two successive Conv1d → BN → GELU layers, no pooling."""
    def __init__(self, in_ch: int, out_ch: int, k1: int = 7, k2: int = 5):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(in_ch, out_ch, kernel_size=k1, padding=k1 // 2, bias=False),
            nn.BatchNorm1d(out_ch),
            nn.GELU(),
            nn.Conv1d(out_ch, out_ch, kernel_size=k2, padding=k2 // 2, bias=False),
            nn.BatchNorm1d(out_ch),
            nn.GELU(),
        )

    def forward(self, x):
        return self.net(x)


class _Encoder(nn.Module):
    """
    Generic 1-D CNN encoder: two conv blocks with max-pooling in between,
    then adaptive average pooling to produce a 128-d feature vector.
    """
    def __init__(self, in_channels: int):
        super().__init__()
        self.block1 = _ConvBlock(in_channels, 64, k1=7, k2=5)
        self.pool   = nn.MaxPool1d(kernel_size=2, stride=2)
        self.block2 = _ConvBlock(64, 128, k1=5, k2=5)
        self.gap    = nn.AdaptiveAvgPool1d(1)   # → (batch, 128, 1)

    def forward(self, x):
        x = self.block1(x)
        x = self.pool(x)
        x = self.block2(x)
        x = self.gap(x)
        return x.squeeze(-1)                     # (batch, 128)


# ── Classifier head (shared design) ──────────────────────────────────────────

class _Head(nn.Module):
    def __init__(self, latent_dim: int, n_classes: int = 4, dropout: float = 0.3):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(latent_dim, 64),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(64, n_classes),
        )

    def forward(self, x):
        return self.net(x)


# ── E1 / E2 / E3 — Single-branch ─────────────────────────────────────────────

class SingleBranchCNN(nn.Module):
    """
    Shared model for E1 (EMG-only), E2 (IMU-only), E3 (rate-matched fusion).

    Input shape: (batch, in_channels, timesteps)
    Output:      (batch, 4)  — raw logits
    """
    def __init__(self, in_channels: int, n_classes: int = 4, dropout: float = 0.3):
        super().__init__()
        self.encoder = _Encoder(in_channels)
        self.head    = _Head(128, n_classes, dropout)

    def forward(self, x):
        z = self.encoder(x)     # (batch, 128)
        return self.head(z)     # (batch, 4)


# ── E4 — Dual-branch ─────────────────────────────────────────────────────────

class DualBranchCNN(nn.Module):
    """
    Two independent encoders (EMG branch + IMU branch) followed by
    feature concatenation and a shared classifier head.

    EMG input: (batch, 8,  1259)
    IMU input: (batch, 48,  148)
    Output:    (batch, 4)  — raw logits
    """
    def __init__(self, n_classes: int = 4, dropout: float = 0.3):
        super().__init__()
        self.emg_encoder = _Encoder(in_channels=8)
        self.imu_encoder = _Encoder(in_channels=48)
        self.head        = _Head(128 + 128, n_classes, dropout)

    def forward(self, x_emg, x_imu):
        z_emg = self.emg_encoder(x_emg)          # (batch, 128)
        z_imu = self.imu_encoder(x_imu)          # (batch, 128)
        z     = torch.cat([z_emg, z_imu], dim=1) # (batch, 256)
        return self.head(z)                       # (batch, 4)


# ── Factory ───────────────────────────────────────────────────────────────────

def build_model(experiment: str) -> nn.Module:
    """
    Return a freshly initialised model for the given experiment code.

    Parameters
    ----------
    experiment : one of {"E1", "E2", "E3", "E4"}
    """
    exp = experiment.upper()
    if exp == "E1":
        return SingleBranchCNN(in_channels=8)
    elif exp == "E2":
        return SingleBranchCNN(in_channels=48)
    elif exp == "E3":
        return SingleBranchCNN(in_channels=56)
    elif exp == "E4":
        return DualBranchCNN()
    else:
        raise ValueError(f"Unknown experiment: {experiment!r}. Use E1-E4.")


def count_parameters(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)
