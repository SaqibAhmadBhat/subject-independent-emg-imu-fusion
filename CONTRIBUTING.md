# Contributing to Subject-Independent EMG–IMU Fusion

Thank you for your interest in contributing to this research repository.

## Scientific Integrity & Open Science Principles

This repository contains frozen, peer-reviewed scientific research artifacts across Version 1.0.0 and Version 2.0.0. To protect scientific reproducibility:

1. **Frozen Result Invariance:** Numerical results, prediction files (`predictions.csv`), and training histories (`history.json`) for completed studies (V1 and V2) are immutable historical artifacts and cannot be modified.
2. **New Analyses & Methodological Extensions:** We welcome contributions that introduce new architectures, improved fusion mechanisms, novel preprocessing techniques, or broader benchmark evaluations on new datasets. Such contributions should be proposed as new experimental conditions or standalone modules.
3. **Reproducibility First:** Any pull request modifying code or adding models must include automated tests and clear instructions for running and verifying results.

## Workflow

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/novel-fusion-branch`).
3. Ensure all automated tests pass (`pytest tests/ -v`).
4. Commit your changes with descriptive messages adhering to [Conventional Commits](https://www.conventionalcommits.org/).
5. Open a Pull Request detailing the scientific objective, methodology, and verification steps.

## Code Style & Standards

- Python code should conform to PEP 8 standards.
- Type annotations are encouraged for public functions.
- Convolutions and mathematical transforms should explicitly document layer-wise tensor dimensions and receptive fields.
