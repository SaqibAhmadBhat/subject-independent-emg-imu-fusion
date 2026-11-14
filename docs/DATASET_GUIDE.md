# SDALLE Dataset Guide & Modality Specification

## 1. Dataset Overview

This study utilizes the **SDALLE** (Surface-electrode Dataset for Activity recognition of the Lower Limb Extremities) benchmark:

- **Source:** [Zenodo Record 14841611](https://doi.org/10.5281/zenodo.14841611)
- **Creators:** Abdellatif Hamed Ibrahim, Mohamed Ali, Reham Mohsen, Ahmed El-Khoreby, Hossam Farouk (2025).
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0).
- **Associated Journal Publications:**
  - El-Khoreby et al., *Applied System Innovation*, 2026, 9(1): 13. [doi:10.3390/asi9010013](https://doi.org/10.3390/asi9010013)
  - Farouk et al., *Scientific Reports*, 2026, 16: 26180.
- **Redistribution Notice:** The original raw continuous SDALLE recordings are **not redistributed** in this repository. Users can obtain them directly from Zenodo.

---

## 2. Participant & Acquisition Protocol

- **Participants:** 9 healthy male subjects (Subject 1 through Subject 9).
  - Age: 12 to 39 years (Participant 9 is 12 years old; Participants 1–8 are 21–39 years).
  - Height: 152 to 182 cm.
  - Weight: 47 to 88 kg.
- **Acquisition Hardware:** Delsys Trigno Discover system (software v1.7.0) with Avanti wireless sensors.
- **Sensor Placement:** 8 sensors mounted bilaterally on the following lower-limb muscle bellies:
  1. Left Rectus femoris
  2. Right Rectus femoris
  3. Left Vastus medialis
  4. Right Vastus medialis
  5. Left Vastus lateralis
  6. Right Vastus lateralis
  7. Left Semitendinosus
  8. Right Semitendinosus

---

## 3. Sensor Modalities & Signal Specifications

Each of the 8 sensors records simultaneous sEMG and 6-axis inertial data:

| Modality | Number of Channels | Sampling Rate | Measurement Units / Range |
|---|---|---|---|
| **Surface EMG (sEMG)** | 8 channels (1 per sensor) | **1259.2593 Hz** (nominal 1260 Hz) | $\mu\text{V}$, differential surface bipolar electrodes |
| **Triaxial Accelerometer** | 24 channels (3 per sensor: $X, Y, Z$) | **148.1481 Hz** (nominal 148 Hz) | $\pm 16g$ ($g \approx 9.81 \text{ m/s}^2$) |
| **Triaxial Gyroscope** | 24 channels (3 per sensor: $X, Y, Z$) | **148.1481 Hz** (nominal 148 Hz) | $\pm 2000^\circ/\text{s}$ angular velocity |
| **Total Sensor Channels** | **56 channels** | — | 8 sEMG + 48 IMU |

---

## 4. Hardware Synchronization Disclosure

- **Upstream Literature:** Farouk et al. (2026, *Sci. Rep.*) report that sEMG and IMU data were "inherently synchronised ... common timestamp reference within the Trigno system".
- **Empirical CSV Column Audit:** Direct inspection of the raw CSV files distributed on Zenodo reveals that the columns contain only sensor values (floating-point amplitudes). No hardware timestamp channel, sample clock counter, or TTL trigger signal is provided in the public distribution.
- **Scientific Caveat:** Temporal alignment between modalities relies on the manufacturer's acquisition software and cannot be independently audited from the released CSV files alone.

---

## 5. Locomotor Tasks & Class Distribution

The dataset records four ambulation activities across level ground and stairs:

| Class Index | Activity Name | Description | Test Windows per Seed | Class Balance (%) |
|:---:|---|---|:---:|:---:|
| **0** | Jogging | Continuous level-ground jogging | 1,528 | 24.63% |
| **1** | Stairs Down | Stairway descent | 1,204 | 19.41% |
| **2** | Stairs Up | Stairway ascent | 1,237 | 19.94% |
| **3** | Walking | Continuous level-ground walking | 2,234 | 36.01% |
| **Total** | — | — | **6,203** | **100.00%** |

Walking represents the majority class ($36.01\%$). A majority-class baseline classifier would achieve $36.01\%$ accuracy. Both tested models (RM: $72.90\%$, NR: $69.07\%$) comfortably surpass this threshold.
