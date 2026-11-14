"""
models_v2.py
------------
V2 model module alias.
"""

from models import build_model_v2, build_model, DualBranchCNN, SingleBranchCNN, count_parameters

__all__ = [
    "build_model_v2",
    "build_model",
    "DualBranchCNN",
    "SingleBranchCNN",
    "count_parameters",
]
