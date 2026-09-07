"""
windower.py
-----------
Slices Trial objects into fixed-size windows for each experiment, attaching metadata.
"""

from __future__ import annotations

from typing import Dict, Any, List, Tuple

import numpy as np
from scipy.interpolate import interp1d

from dataset_loader import Trial, EXPECTED_EMG_RATE, EXPECTED_IMU_RATE

# ── Constants ─────────────────────────────────────────────────────────────────

WINDOW_SEC   = 1.0
STRIDE_SEC   = 0.5

EMG_WIN  = int(WINDOW_SEC * EXPECTED_EMG_RATE)   # 1259
IMU_WIN  = int(WINDOW_SEC * EXPECTED_IMU_RATE)   #  148

EMG_STRIDE = int(STRIDE_SEC * EXPECTED_EMG_RATE)  # 629
IMU_STRIDE = int(STRIDE_SEC * EXPECTED_IMU_RATE)  #  74


def _create_metadata(t: Trial, start_idx: int, rate: float, duration: float) -> Dict[str, Any]:
    return {
        "subject_id": t.subject_id,
        "trial_id": t.trial_id,
        "activity_label": t.activity_label,
        "start_time": start_idx / rate,
        "end_time": (start_idx / rate) + duration,
    }


def _slide_with_meta(arr: np.ndarray, win: int, stride: int, trial: Trial, rate: float) -> Tuple[List[np.ndarray], List[Dict[str, Any]]]:
    windows = []
    metadata = []
    n = arr.shape[0]
    start = 0
    while start + win <= n:
        windows.append(arr[start:start + win])
        metadata.append(_create_metadata(trial, start, rate, win / rate))
        start += stride
    return windows, metadata


def window_e1(trials: List[Trial]) -> Tuple[np.ndarray, np.ndarray, List[Dict]]:
    X, y, meta = [], [], []
    for t in trials:
        wins, m = _slide_with_meta(t.emg, EMG_WIN, EMG_STRIDE, t, EXPECTED_EMG_RATE)
        X.extend(wins)
        y.extend([t.activity_label]*len(wins))
        meta.extend(m)
    return np.stack(X).astype(np.float32) if X else np.array([]), np.array(y, dtype=np.int64), meta


def window_e2(trials: List[Trial]) -> Tuple[np.ndarray, np.ndarray, List[Dict]]:
    X, y, meta = [], [], []
    for t in trials:
        wins, m = _slide_with_meta(t.imu, IMU_WIN, IMU_STRIDE, t, EXPECTED_IMU_RATE)
        X.extend(wins)
        y.extend([t.activity_label]*len(wins))
        meta.extend(m)
    return np.stack(X).astype(np.float32) if X else np.array([]), np.array(y, dtype=np.int64), meta


def window_e3(trials: List[Trial]) -> Tuple[np.ndarray, np.ndarray, List[Dict]]:
    """
    E3: Rate-matched fusion.
    GLOBAL PER-TRIAL resampling: Resample the entire EMG trial to IMU sampling rate,
    then slice synchronized IMU-rate windows.
    """
    X, y, meta = [], [], []
    for t in trials:
        n_emg = t.emg.shape[0]
        t_emg = np.arange(n_emg) / EXPECTED_EMG_RATE
        
        n_imu = t.imu.shape[0]
        t_imu = np.arange(n_imu) / EXPECTED_IMU_RATE
        
        # We can only resample where time domains overlap. The CSV implies they start together.
        # Max time is bounded by the shorter duration
        max_time = min(t_emg[-1], t_imu[-1])
        valid_imu_idx = t_imu <= max_time
        t_imu_valid = t_imu[valid_imu_idx]
        
        # Cubic interpolation over the entire trial
        f_interp = interp1d(t_emg, t.emg, kind='cubic', axis=0, bounds_error=False, fill_value="extrapolate")
        emg_resampled_global = f_interp(t_imu_valid)  # Shape: (len(t_imu_valid), 8)
        
        imu_valid = t.imu[valid_imu_idx]              # Shape: (len(t_imu_valid), 48)
        
        # Concatenate channels
        fused = np.concatenate([emg_resampled_global, imu_valid], axis=1) # Shape: (len(t_imu_valid), 56)
        
        wins, m = _slide_with_meta(fused, IMU_WIN, IMU_STRIDE, t, EXPECTED_IMU_RATE)
        X.extend(wins)
        y.extend([t.activity_label]*len(wins))
        meta.extend(m)
        
    return np.stack(X).astype(np.float32) if X else np.array([]), np.array(y, dtype=np.int64), meta


def window_e4(trials: List[Trial]) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[Dict]]:
    """
    E4: Native-rate multirate fusion.
    Slice independently but ensure paired windows represent the same physical time.
    """
    X_emg, X_imu, y, meta = [], [], [], []
    for t in trials:
        n_emg = t.emg.shape[0]
        n_imu = t.imu.shape[0]
        
        # Calculate max valid pairs to prevent out-of-bounds
        n_pairs = min(
            (n_emg - EMG_WIN) // EMG_STRIDE + 1,
            (n_imu - IMU_WIN) // IMU_STRIDE + 1
        )
        if n_pairs <= 0:
            continue
            
        for i in range(n_pairs):
            emg_start = i * EMG_STRIDE
            imu_start = i * IMU_STRIDE
            
            X_emg.append(t.emg[emg_start:emg_start+EMG_WIN])
            X_imu.append(t.imu[imu_start:imu_start+IMU_WIN])
            
            y.append(t.activity_label)
            # Create metadata anchored to IMU time (both start at same physical time 0)
            meta.append(_create_metadata(t, imu_start, EXPECTED_IMU_RATE, WINDOW_SEC))
            
    return (
        np.stack(X_emg).astype(np.float32) if X_emg else np.array([]),
        np.stack(X_imu).astype(np.float32) if X_imu else np.array([]),
        np.array(y, dtype=np.int64),
        meta
    )
