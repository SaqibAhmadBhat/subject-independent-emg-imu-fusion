"""Tests for DualBranchCNN neural network architecture, parameter budget, and receptive field."""
import sys
from pathlib import Path
import pytest
import torch

# Add v2_rate_matching_study/V2_ROBUSTNESS_STUDY/src to path
src_dir = Path(__file__).resolve().parent.parent / "v2_rate_matching_study" / "V2_ROBUSTNESS_STUDY" / "src"
sys.path.insert(0, str(src_dir))

from models import DualBranchCNN


def test_dual_branch_cnn_parameter_count():
    """Verify that DualBranchCNN has exactly 330,052 parameters."""
    model = DualBranchCNN(n_classes=4, dropout=0.3)
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    assert total_params == 330052, f"Expected 330,052 parameters, got {total_params}"
    assert trainable_params == 330052, f"Expected 330,052 trainable parameters, got {trainable_params}"


def test_dual_branch_cnn_branch_breakdown():
    """Verify individual parameter budgets for EMG encoder, IMU encoder, and head."""
    model = DualBranchCNN(n_classes=4, dropout=0.3)
    
    emg_params = sum(p.numel() for p in model.emg_encoder.parameters())
    imu_params = sum(p.numel() for p in model.imu_encoder.parameters())
    head_params = sum(p.numel() for p in model.head.parameters())
    
    assert emg_params == 147712, f"Expected EMG encoder 147,712 params, got {emg_params}"
    assert imu_params == 165632, f"Expected IMU encoder 165,632 params, got {imu_params}"
    assert head_params == 16708, f"Expected classifier head 16,708 params, got {head_params}"


def test_forward_pass_rate_matched():
    """Verify forward pass on rate-matched inputs (8x148 EMG, 48x148 IMU)."""
    model = DualBranchCNN(n_classes=4, dropout=0.3)
    model.eval()
    
    batch_size = 4
    emg_input = torch.randn(batch_size, 8, 148)
    imu_input = torch.randn(batch_size, 48, 148)
    
    with torch.no_grad():
        output = model(emg_input, imu_input)
    
    assert output.shape == (batch_size, 4), f"Expected shape ({batch_size}, 4), got {output.shape}"


def test_forward_pass_native_rate():
    """Verify forward pass on native-rate inputs (8x1259 EMG, 48x148 IMU)."""
    model = DualBranchCNN(n_classes=4, dropout=0.3)
    model.eval()
    
    batch_size = 4
    emg_input = torch.randn(batch_size, 8, 1259)
    imu_input = torch.randn(batch_size, 48, 148)
    
    with torch.no_grad():
        output = model(emg_input, imu_input)
    
    assert output.shape == (batch_size, 4), f"Expected shape ({batch_size}, 4), got {output.shape}"


def test_theoretical_receptive_field():
    """Verify theoretical receptive field calculation for 4-layer conv block."""
    # Conv1: k=7, s=1 -> RF = 7
    # Conv2: k=5, s=1 -> RF = 7 + (5-1)*1 = 11
    # MaxPool: k=2, s=2 -> RF = 11 + (2-1)*1 = 12, jump = 2
    # Conv3: k=5, s=1 -> RF = 12 + (5-1)*2 = 20, jump = 2
    # Conv4: k=5, s=1 -> RF = 20 + (5-1)*2 = 28, jump = 2
    rf = 1
    jump = 1
    layers = [
        (7, 1), # conv1
        (5, 1), # conv2
        (2, 2), # maxpool
        (5, 1), # conv3
        (5, 1), # conv4
    ]
    for k, s in layers:
        rf = rf + (k - 1) * jump
        jump = jump * s
        
    assert rf == 28, f"Expected final receptive field of 28 samples, got {rf}"
