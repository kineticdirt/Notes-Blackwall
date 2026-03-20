#!/usr/bin/env bash
# Full Defender cache pipeline (run from retrieval-eval/). One command per line.
set -e
cd "$(dirname "$0")/.."

echo "[1/5] Build intent router dataset..."
python3 experiments/defender_intent_router_dataset.py

echo "[2/5] Train Qwen4B LoRA (requires GPU recommended; HF download first time)..."
python3 experiments/train_defender_intent_qwen4b.py --epochs 2 --batch-size 1 --lora

echo "[3/5] Start Defender MCP in another terminal:"
echo "  python3 -m uvicorn experiments.defender_cache_mcp.api:app --host 127.0.0.1 --port 8766"
echo "Press Enter when MCP is up..."
read -r _

export DEFENDER_QWEN4B_LORA="$(pwd)/experiments/defender_qwen4b_lora"

echo "[4/5] MvM: Claude vs Qwen4B..."
python3 experiments/mvm_defender_api_runner.py --nano-type qwen4b

echo "[5/5] Report..."
python3 experiments/mvm_compare_report.py results/mvm_defender
