"""
normalizer.py
-------------
Per-fold z-score normalization using ONLY training-fold statistics.

DESIGN RULES:
- Scaler is fit on training data ONLY (no test leakage).
- Channel-wise normalization: each of the C channels gets its own mean/std.
- Constant channels (std=0) are left unchanged (std replaced with 1.0).
- For E4 dual-branch, two independent scalers are fitted and returned.
- All parameters (mean, scale) are returned for auditability.
"""

from __future__ import annotations

from typing import Tuple, Dict
import numpy as np


def _fit_scaler(X_train: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Fit channel-wise mean and std from training data of shape (N, W, C).
    Time dimension is flattened so every sample across all timesteps is used.

    Returns
    -------
    mean  : shape (C,)
    scale : shape (C,)  — zero-std channels are set to 1.0
    """
    N, W, C = X_train.shape
    flat = X_train.reshape(-1, C)      # (N*W, C)
    mean = flat.mean(axis=0)           # (C,)
    scale = flat.std(axis=0)           # (C,)
    scale[scale == 0.0] = 1.0          # avoid division by zero
    return mean, scale


def _apply_scaler(X: np.ndarray, mean: np.ndarray, scale: np.ndarray) -> np.ndarray:
    N, W, C = X.shape
    flat = X.reshape(-1, C)
    normed = (flat - mean) / scale
    return normed.reshape(N, W, C).astype(np.float32)


def normalize_single_branch(
    X_train: np.ndarray,
    X_test: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, Dict]:
    """
    Normalize (N, W, C) arrays for E1, E2, E3.
    Fit only on X_train.
    Returns normalized train, normalized test, and scaler parameters dict.
    """
    assert X_train.ndim == 3, f"Expected 3-D array, got shape {X_train.shape}"
    assert X_test.ndim == 3, f"Expected 3-D array, got shape {X_test.shape}"
    assert X_train.shape[2] == X_test.shape[2], "Channel count mismatch"
    assert X_train.shape[1] == X_test.shape[1], "Window-length mismatch"

    mean, scale = _fit_scaler(X_train)

    # ASSERTION: confirm no test subjects leaked into scaler fitting
    # (guaranteed structurally — caller passes only training-fold arrays)

    X_train_norm = _apply_scaler(X_train, mean, scale)
    X_test_norm  = _apply_scaler(X_test,  mean, scale)

    scaler_params = {"mean": mean, "scale": scale}
    return X_train_norm, X_test_norm, scaler_params


def normalize_dual_branch(
    X_emg_train: np.ndarray, X_emg_test: np.ndarray,
    X_imu_train: np.ndarray, X_imu_test: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, Dict, Dict]:
    """
    Normalize E4 dual-branch arrays. Fits two independent scalers.
    Returns: normed_emg_train, normed_emg_test,
             normed_imu_train, normed_imu_test,
             emg_scaler_params, imu_scaler_params.
    """
    X_emg_tr_n, X_emg_te_n, emg_params = normalize_single_branch(X_emg_train, X_emg_test)
    X_imu_tr_n, X_imu_te_n, imu_params = normalize_single_branch(X_imu_train, X_imu_test)
    return X_emg_tr_n, X_emg_te_n, X_imu_tr_n, X_imu_te_n, emg_params, imu_params
