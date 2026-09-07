"""
dataset_loader.py
-----------------
Loads and parses SDALLE trial CSVs into structured Trial objects.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np

# ── Constants ────────────────────────────────────────────────────────────────

DATASET_DIR = Path("data/raw/SDALLE")

DATA_START_LINE = 8          # First row of numerical signal data

N_SENSORS  = 8
COLS_PER_SENSOR = 7
TOTAL_COLS = N_SENSORS * COLS_PER_SENSOR   # 56

EMG_COL_INDICES: List[int] = [k * COLS_PER_SENSOR for k in range(N_SENSORS)]
IMU_COL_INDICES: List[int] = [
    c for c in range(TOTAL_COLS) if c not in EMG_COL_INDICES
]

ACTIVITY_LABELS: Dict[str, int] = {
    "jogging":     0,
    "stairs_down": 1,
    "stairs_up":   2,
    "walking":     3,
}

EXPECTED_EMG_RATE = 1259.2593
EXPECTED_IMU_RATE = 148.1481


@dataclass
class Trial:
    subject_id:     int
    trial_id:       int
    activity_label: int
    activity_name:  str
    file_path:      Path
    emg: np.ndarray              # shape (N_emg, 8)
    imu: np.ndarray              # shape (N_imu, 48)


def _read_csv_rows(file_path: Path) -> list:
    with open(file_path, "r", encoding="utf-8-sig", errors="replace", newline="") as fh:
        return list(csv.reader(fh))


def _parse_raw_array(file_path: Path) -> np.ndarray:
    rows = _read_csv_rows(file_path)
    if len(rows) < DATA_START_LINE:
        raise ValueError(f"File contains fewer than {DATA_START_LINE} lines")
    
    # Assert rates from SAMPLING_RATE_LINE (Line 8 is index 7, but SAMPLING_RATE_LINE is 7 -> index 6)
    # The user noted SAMPLING_RATE_LINE = 7
    # Wait, my inspect_dataset.py logic says: SAMPLING_RATE_LINE = 7
    rates_row = rows[6]
    parsed_rates = []
    for val in rates_row:
        m = re.search(r"([0-9.]+)", val.strip())
        if m:
            parsed_rates.append(float(m.group(1)))
            
    if parsed_rates:
        emg_rates = parsed_rates[0::7]
        imu_rates = [r for i, r in enumerate(parsed_rates) if i % 7 != 0]
        # Allow small tolerance
        if emg_rates and abs(emg_rates[0] - EXPECTED_EMG_RATE) > 1.0:
            print(f"Warning: Unexpected EMG rate in {file_path}: {emg_rates[0]}")
        if imu_rates and abs(imu_rates[0] - EXPECTED_IMU_RATE) > 1.0:
            print(f"Warning: Unexpected IMU rate in {file_path}: {imu_rates[0]}")
            
    data_rows = rows[DATA_START_LINE - 1:]

    numeric = []
    for row in data_rows:
        if not any(cell.strip() for cell in row):
            continue
        try:
            values = [
                float(x.strip()) if x.strip() else float("nan")
                for x in row
            ]
            numeric.append(values)
        except ValueError:
            continue

    if not numeric:
        raise ValueError(f"No numeric data found in {file_path}")

    arr = np.array(numeric, dtype=np.float32)
    assert arr.shape[1] == TOTAL_COLS, f"Expected {TOTAL_COLS} columns, got {arr.shape[1]} in {file_path}"
    return arr


def _extract_emg_imu(arr: np.ndarray):
    emg_raw = arr[:, EMG_COL_INDICES]          # (N, 8)
    assert emg_raw.shape[1] == 8, "EMG must have 8 channels"

    imu_raw = arr[:, IMU_COL_INDICES]          # (N, 48)
    valid_mask = ~np.any(np.isnan(imu_raw), axis=1)
    imu_valid = imu_raw[valid_mask]            # (N_imu, 48)
    assert imu_valid.shape[1] == 48, "IMU must have 48 channels"

    return emg_raw, imu_valid


def _normalise_activity(raw_name: str) -> str:
    return raw_name.lower()


def load_all_trials(dataset_dir: Path = DATASET_DIR, limit: int = None) -> List[Trial]:
    if not dataset_dir.exists():
        raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")

    trials: List[Trial] = []
    errors: List[str] = []

    subject_dirs = sorted(
        p for p in dataset_dir.glob("Subject_*") if p.is_dir()
    )

    for subject_dir in subject_dirs:
        m_subj = re.search(r"(\d+)$", subject_dir.name)
        if not m_subj: continue
        subject_id = int(m_subj.group(1))

        for activity_dir in sorted(p for p in subject_dir.iterdir() if p.is_dir()):
            activity_name = _normalise_activity(activity_dir.name)
            if activity_name not in ACTIVITY_LABELS:
                continue

            label = ACTIVITY_LABELS[activity_name]

            for csv_file in sorted(activity_dir.glob("*.csv")):
                if limit and len(trials) >= limit:
                    break
                m_trial = re.search(r"(\d+)", csv_file.name)
                trial_id = int(m_trial.group(1)) if m_trial else 0
                
                try:
                    raw = _parse_raw_array(csv_file)
                    emg, imu = _extract_emg_imu(raw)

                    trials.append(Trial(
                        subject_id=subject_id,
                        trial_id=trial_id,
                        activity_label=label,
                        activity_name=activity_name,
                        file_path=csv_file,
                        emg=emg,
                        imu=imu,
                    ))
                except Exception as exc:
                    errors.append(f"ERROR {csv_file.name}: {exc}")
                    
            if limit and len(trials) >= limit:
                break
        if limit and len(trials) >= limit:
            break

    for err in errors:
        print(err)

    return trials
