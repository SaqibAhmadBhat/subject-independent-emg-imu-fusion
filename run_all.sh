#!/usr/bin/env bash
# =============================================================================
# run_all.sh — RP4 Final Training Orchestration (Resumable)
# =============================================================================
#
# Runs all 36 experiment/fold combinations (E1–E4 × folds 1–9).
#
# RULES:
#   - Skips a fold ONLY if results/<EXP>/fold_<N>/model.pt exists AND
#     results/<EXP>/fold_<N>/history.json exists and is valid JSON.
#   - Empty or partial directories are NOT treated as completed.
#   - If a fold fails, logs the failure and continues to the next fold.
#   - No experimental settings are altered — purely orchestration.
#
# Usage:
#   cd <project_root>
#   source .venv/bin/activate
#   bash run_all.sh
# =============================================================================

set -o pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT" || { echo "FATAL: cannot cd to $PROJECT_ROOT"; exit 1; }

DEVICE="mps"
EPOCHS=50
LOGFILE="results/final_training.log"
MANIFEST="results/experiment_manifest.csv"

EXPERIMENTS=("E1" "E2" "E3" "E4")
FOLDS=(1 2 3 4 5 6 7 8 9)

TOTAL=0
COMPLETED=0
SKIPPED=0
FAILED=0
FAILED_LIST=""

# Ensure results directory exists
mkdir -p results

# Start/append log
echo "" >> "$LOGFILE"
echo "=================================================================" >> "$LOGFILE"
echo "  FINAL TRAINING RUN — $(date '+%Y-%m-%d %H:%M:%S %Z')" >> "$LOGFILE"
echo "  Device: $DEVICE  |  Epochs: $EPOCHS" >> "$LOGFILE"
echo "  Python: $(python --version 2>&1)" >> "$LOGFILE"
echo "  PyTorch: $(python -c 'import torch; print(torch.__version__)' 2>&1)" >> "$LOGFILE"
echo "=================================================================" >> "$LOGFILE"
echo "" >> "$LOGFILE"

GLOBAL_START=$(date +%s)

for EXP in "${EXPERIMENTS[@]}"; do
    for FOLD in "${FOLDS[@]}"; do
        TOTAL=$((TOTAL + 1))
        FOLD_DIR="results/${EXP}/fold_${FOLD}"
        MODEL_PATH="${FOLD_DIR}/model.pt"
        HISTORY_PATH="${FOLD_DIR}/history.json"

        echo "--- ${EXP} Fold ${FOLD} ---"

        # Check if this fold is already completed (valid model.pt + valid history.json)
        if [ -f "$MODEL_PATH" ] && [ -s "$MODEL_PATH" ] && [ -f "$HISTORY_PATH" ] && [ -s "$HISTORY_PATH" ]; then
            # Validate that history.json is valid JSON with expected keys
            VALID=$(python -c "
import json, sys
try:
    with open('${HISTORY_PATH}') as f:
        h = json.load(f)
    if 'train_loss' in h and 'train_acc' in h and len(h['train_loss']) == ${EPOCHS}:
        print('VALID')
    else:
        print('INVALID')
except Exception:
    print('INVALID')
" 2>/dev/null)

            if [ "$VALID" = "VALID" ]; then
                echo "  SKIP: already completed (valid model.pt + history.json with ${EPOCHS} epochs)"
                echo "[SKIP] ${EXP} fold_${FOLD} — already completed" >> "$LOGFILE"
                SKIPPED=$((SKIPPED + 1))
                COMPLETED=$((COMPLETED + 1))
                continue
            else
                echo "  Partial/invalid output detected — re-running"
                echo "[RERUN] ${EXP} fold_${FOLD} — partial/invalid output, re-running" >> "$LOGFILE"
                rm -rf "$FOLD_DIR"
            fi
        fi

        # Run training
        FOLD_START=$(date +%s)
        echo "[START] ${EXP} fold_${FOLD} — $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOGFILE"

        python src/train.py --exp "$EXP" --fold "$FOLD" --epochs "$EPOCHS" --device "$DEVICE" 2>&1 | tee -a "$LOGFILE"
        EXIT_CODE=${PIPESTATUS[0]}

        FOLD_END=$(date +%s)
        FOLD_ELAPSED=$((FOLD_END - FOLD_START))

        # Validate output
        if [ $EXIT_CODE -eq 0 ] && [ -f "$MODEL_PATH" ] && [ -s "$MODEL_PATH" ] && [ -f "$HISTORY_PATH" ] && [ -s "$HISTORY_PATH" ]; then
            # Double-check history.json validity
            VALID=$(python -c "
import json, sys
try:
    with open('${HISTORY_PATH}') as f:
        h = json.load(f)
    keys = set(h.keys())
    has_test = any(k for k in keys if 'test' in k or 'val' in k)
    if 'train_loss' in h and 'train_acc' in h and len(h['train_loss']) == ${EPOCHS} and not has_test:
        print('VALID')
    else:
        print('INVALID')
except Exception:
    print('INVALID')
" 2>/dev/null)

            if [ "$VALID" = "VALID" ]; then
                echo "[DONE] ${EXP} fold_${FOLD} — ${FOLD_ELAPSED}s — PASS" >> "$LOGFILE"
                COMPLETED=$((COMPLETED + 1))
            else
                echo "[FAIL] ${EXP} fold_${FOLD} — ${FOLD_ELAPSED}s — output validation failed" >> "$LOGFILE"
                FAILED=$((FAILED + 1))
                FAILED_LIST="${FAILED_LIST}  ${EXP}/fold_${FOLD}\n"
            fi
        else
            echo "[FAIL] ${EXP} fold_${FOLD} — ${FOLD_ELAPSED}s — exit code ${EXIT_CODE}" >> "$LOGFILE"
            FAILED=$((FAILED + 1))
            FAILED_LIST="${FAILED_LIST}  ${EXP}/fold_${FOLD}\n"
        fi

        echo "" >> "$LOGFILE"
    done
done

GLOBAL_END=$(date +%s)
GLOBAL_ELAPSED=$((GLOBAL_END - GLOBAL_START))

# ── Generate experiment manifest ──────────────────────────────────────────────

echo "experiment,fold,status,model_pt_exists,model_pt_bytes,history_json_exists,history_epochs" > "$MANIFEST"

for EXP in "${EXPERIMENTS[@]}"; do
    for FOLD in "${FOLDS[@]}"; do
        FOLD_DIR="results/${EXP}/fold_${FOLD}"
        MODEL_PATH="${FOLD_DIR}/model.pt"
        HISTORY_PATH="${FOLD_DIR}/history.json"

        MODEL_EXISTS="no"
        MODEL_BYTES=0
        HISTORY_EXISTS="no"
        HISTORY_EPOCHS=0
        STATUS="MISSING"

        if [ -f "$MODEL_PATH" ] && [ -s "$MODEL_PATH" ]; then
            MODEL_EXISTS="yes"
            MODEL_BYTES=$(stat -f%z "$MODEL_PATH" 2>/dev/null || stat --printf="%s" "$MODEL_PATH" 2>/dev/null)
        fi

        if [ -f "$HISTORY_PATH" ] && [ -s "$HISTORY_PATH" ]; then
            HISTORY_EXISTS="yes"
            HISTORY_EPOCHS=$(python -c "
import json
try:
    with open('${HISTORY_PATH}') as f:
        h = json.load(f)
    print(len(h.get('train_loss', [])))
except Exception:
    print(0)
" 2>/dev/null)
        fi

        if [ "$MODEL_EXISTS" = "yes" ] && [ "$HISTORY_EXISTS" = "yes" ] && [ "$HISTORY_EPOCHS" = "$EPOCHS" ]; then
            STATUS="COMPLETE"
        elif [ "$MODEL_EXISTS" = "yes" ] || [ "$HISTORY_EXISTS" = "yes" ]; then
            STATUS="PARTIAL"
        fi

        echo "${EXP},${FOLD},${STATUS},${MODEL_EXISTS},${MODEL_BYTES},${HISTORY_EXISTS},${HISTORY_EPOCHS}" >> "$MANIFEST"
    done
done

# ── Final summary ─────────────────────────────────────────────────────────────

echo "" >> "$LOGFILE"
echo "=================================================================" >> "$LOGFILE"
echo "  TRAINING COMPLETE — $(date '+%Y-%m-%d %H:%M:%S %Z')" >> "$LOGFILE"
echo "=================================================================" >> "$LOGFILE"
echo "  Total:     ${TOTAL}" >> "$LOGFILE"
echo "  Completed: ${COMPLETED}" >> "$LOGFILE"
echo "  Skipped:   ${SKIPPED} (already completed from prior run)" >> "$LOGFILE"
echo "  Failed:    ${FAILED}" >> "$LOGFILE"
echo "  Total time: ${GLOBAL_ELAPSED}s ($(( GLOBAL_ELAPSED / 3600 ))h $(( (GLOBAL_ELAPSED % 3600) / 60 ))m $(( GLOBAL_ELAPSED % 60 ))s)" >> "$LOGFILE"
if [ -n "$FAILED_LIST" ]; then
    echo "" >> "$LOGFILE"
    echo "  Failed folds:" >> "$LOGFILE"
    echo -e "$FAILED_LIST" >> "$LOGFILE"
fi
echo "" >> "$LOGFILE"
echo "  Manifest: ${MANIFEST}" >> "$LOGFILE"
echo "  Log:      ${LOGFILE}" >> "$LOGFILE"
echo "=================================================================" >> "$LOGFILE"

# Print summary to stdout
echo ""
echo "================================================================="
echo "  TRAINING COMPLETE"
echo "================================================================="
echo "  Total:     ${TOTAL}"
echo "  Completed: ${COMPLETED}"
echo "  Skipped:   ${SKIPPED}"
echo "  Failed:    ${FAILED}"
echo "  Total time: ${GLOBAL_ELAPSED}s ($(( GLOBAL_ELAPSED / 3600 ))h $(( (GLOBAL_ELAPSED % 3600) / 60 ))m $(( GLOBAL_ELAPSED % 60 ))s)"
if [ -n "$FAILED_LIST" ]; then
    echo ""
    echo "  Failed folds:"
    echo -e "$FAILED_LIST"
fi
echo ""
echo "  Manifest: ${MANIFEST}"
echo "  Log:      ${LOGFILE}"
echo "================================================================="
