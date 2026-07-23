#!/usr/bin/env bash
#
# v11mistral — Quantum consciousness (C) + Mistral 7B decoder (D) with additive gate.
#
# This is the repo roadmap's realistic "conversation-capable" path: the D module is a
# pre-trained instruct LLM that already knows dialogue, and C (quantum consciousness)
# modulates its residual stream additively (pre-trained weights preserved). Only the
# LoRA adapters + the C->D bridge gate train; the base Mistral is frozen.
#
# HARDWARE: H100 ONLY. HFDecoder loads Mistral 7B in fp32 (trinity.py:591) ~= 28GB
# weights alone; measured working set ~41GB VRAM. The RTX 5070 pool hosts (12GB) and
# A100 (runtime-only per CLAUDE.md) CANNOT run this. Launch on a RunPod H100.
#
# Fresh from step 0 into a NEW ckpt dir (CLAUDE.md: data/param change => no --resume).
#
# Prereqs on the H100 pod:
#   pip install -r requirements.txt          # includes peft (LoRA) + transformers + accelerate
#   export HF_TOKEN=<hf_token>               # Mistral-7B-Instruct-v0.2 is a gated HF repo
#   data/corpus_v2.txt present (~70MB)
#
# Usage:
#   bash scripts/train_v11_mistral.sh                 # runs inside tmux session "v11mistral"
#   tmux attach -t v11mistral                         # watch
#   tail -f checkpoints/clm_v11_mistral/train.log     # or follow the log

set -euo pipefail
cd "$(dirname "$0")/.."

SESSION="v11mistral"
CKPT_DIR="checkpoints/clm_v11_mistral"
DATA="data/corpus_v2.txt"
HF_MODEL="mistralai/Mistral-7B-Instruct-v0.2"
STEPS="${STEPS:-80000}"

# --- preflight -------------------------------------------------------------
[ -f "$DATA" ] || { echo "FATAL: $DATA missing (corpus_v2 required)"; exit 1; }
python -c "import peft" 2>/dev/null || { echo "FATAL: peft not installed (pip install -r requirements.txt) — LoRA would silently skip"; exit 1; }
python -c "import torch; assert torch.cuda.is_available(), 'no CUDA'; \
  free=torch.cuda.get_device_properties(0).total_memory/1e9; \
  print(f'GPU: {torch.cuda.get_device_name(0)} {free:.0f}GB'); \
  assert free >= 45, f'need >=45GB VRAM for Mistral-7B fp32, got {free:.0f}GB (H100 required)'"

mkdir -p "$CKPT_DIR"

# --- launch (tmux so it survives SSH drop; CLAUDE.md rule) ------------------
# expandable_segments avoids allocator fragmentation OOM; bf16 + gradient
# checkpointing (in HFDecoder) keep the frozen-base backprop within VRAM.
# save-interval 2000 = frequent small (LoRA+gate-only) checkpoints so a mid-run
# pull point always exists (milestone plan: demo ~step 20K, then decide 80K).
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
CMD="python -u train_v11.py \
  --data $DATA \
  --steps $STEPS \
  --c-engine quantum \
  --d-engine hf \
  --hf-model $HF_MODEL \
  --ckpt-dir $CKPT_DIR \
  --batch-size 4 \
  --seq-len 128 \
  --save-interval 2000 \
  --log-interval 100 \
  --p2-start 0.2 \
  --p3-start 0.7 \
  2>&1 | tee $CKPT_DIR/train.log"

echo "Launching v11mistral in tmux session '$SESSION' -> $CKPT_DIR"
echo "  P1 (0-16K): C builds Phi | P2 (16K+): CE learns via frozen Mistral+LoRA | P3 (56K+): Hexad 6-module"
tmux new-session -d -s "$SESSION" "$CMD"
echo "OK. Attach: tmux attach -t $SESSION | Log: tail -f $CKPT_DIR/train.log"
