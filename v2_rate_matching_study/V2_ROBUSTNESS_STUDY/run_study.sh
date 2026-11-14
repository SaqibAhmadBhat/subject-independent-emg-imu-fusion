#!/usr/bin/env bash
# V2_ROBUSTNESS_STUDY/run_study.sh
# ─────────────────────────────────────────────────────────────────────────────
# Orchestrates the full robustness study in order:
#   1. Training (Phase 1)
#   2. Analysis (Phases 2-12)
#   3. Report generation (Phase 13)
#
# SAFETY GUARANTEES:
#   - Never writes to V2/results/raw/
#   - Never deletes or overwrites existing V2 files
#   - All output goes to V2_ROBUSTNESS_STUDY/
#
# Usage:
#   cd "RP4 imu emg"
#   bash V2_ROBUSTNESS_STUDY/run_study.sh
#
# Options (edit below):
#   DEVICE   : cpu | mps | cuda
#   SEEDS    : space-separated seed values
#   EXP      : E3-D | E4 | all
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

DEVICE="${DEVICE:-cpu}"
EXP="${EXP:-all}"
SEEDS="${SEEDS:-42 123 2024 3407 7777}"
RESUME="${RESUME:-0}"
DRY_RUN="${DRY_RUN:-0}"

# Parse optional arguments
for arg in "$@"; do
    case "$arg" in
        --resume|-r)
            RESUME=1
            ;;
        --dry-run)
            DRY_RUN=1
            ;;
        *)
            ;;
    esac
done

STUDY_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="$(dirname "$STUDY_DIR")"

echo "======================================================"
echo "  V2 Robustness Study"
echo "======================================================"
echo "  Workspace : $WORKSPACE"
echo "  Study dir : $STUDY_DIR"
echo "  Device    : $DEVICE"
echo "  Exp       : $EXP"
echo "  Seeds     : $SEEDS"
echo "  Resume    : $RESUME"
if [ "$DRY_RUN" = "1" ] || [ "$DRY_RUN" = "true" ]; then
    echo "  Dry run   : YES"
fi
echo "======================================================"

# ── Safety check: V2/results must not be in the output path ──────────────────
V2_RESULTS="$WORKSPACE/V2/results/raw"
if [ -d "$V2_RESULTS" ]; then
    echo "  [CHECK] V2/results/raw exists — will NOT be modified"
fi

# ── Phase 1: Training ─────────────────────────────────────────────────────────
echo ""
echo "── Phase 1: Training (90 runs: 5 seeds × 9 folds × 2 conditions) ──"
echo ""

EXTRA_FLAGS=""
if [ "$RESUME" = "1" ] || [ "$RESUME" = "true" ]; then
    EXTRA_FLAGS="$EXTRA_FLAGS --resume"
fi
if [ "$DRY_RUN" = "1" ] || [ "$DRY_RUN" = "true" ]; then
    EXTRA_FLAGS="$EXTRA_FLAGS --dry-run"
fi

cd "$WORKSPACE"
python3 V2_ROBUSTNESS_STUDY/robustness_train.py \
    --exp "$EXP" \
    --seeds $SEEDS \
    --folds all \
    --device "$DEVICE" \
    $EXTRA_FLAGS

echo ""
echo "── Phase 1 complete ──"

if [ "$DRY_RUN" = "1" ] || [ "$DRY_RUN" = "true" ]; then
    echo "  [DRY RUN] Dry run finished. Skipping analysis and report."
    exit 0
fi

# ── Phases 2-12: Statistical Analysis ────────────────────────────────────────
echo ""
echo "── Phases 2-12: Statistical Analysis ──"
echo ""

python3 V2_ROBUSTNESS_STUDY/robustness_analyze.py

echo ""
echo "── Analysis complete ──"

# ── Phase 13: Report ──────────────────────────────────────────────────────────
echo ""
echo "── Phase 13: Generating final_report.md ──"
echo ""

python3 V2_ROBUSTNESS_STUDY/robustness_report.py

echo ""
echo "======================================================"
echo "  Study complete."
echo "  Results: $STUDY_DIR"
echo "  Report : $STUDY_DIR/final_report.md"
echo "======================================================"
