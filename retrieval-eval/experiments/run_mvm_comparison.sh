#!/usr/bin/env bash
# Run MvM comparison: retrieval track + API track (if Atlassian MCP env set), then comparison report.
# Token cost is included as the overall cost metric (no training time).
#
# Prereqs:
#   - retrieval-eval/.api-key (or ANTHROPIC_API_KEY) for Claude
#   - For API track: ATLASSIAN_MCP_URL, ATLASSIAN_MCP_BEARER (optional ATLASSIAN_CLOUD_ID)
#
# Usage: from retrieval-eval/ run:
#   bash experiments/run_mvm_comparison.sh
# Or with limits:
#   LIMIT_RET=2 LIMIT_API=3 bash experiments/run_mvm_comparison.sh

set -e
cd "$(dirname "$0")/.."
OUT="${OUT:-results/mvm}"
LIMIT_RET="${LIMIT_RET:-4}"
LIMIT_API="${LIMIT_API:-5}"

echo "=== MvM comparison: standard model + same tools (no training time); token cost = cost metric ==="
mkdir -p "$OUT"

# Optional: clear previous run for a clean comparison (comment out to append)
# : > "$OUT/mcp_arm_retrieval.jsonl"
# : > "$OUT/microsearch_arm_retrieval.jsonl"
# : > "$OUT/mcp_arm_api.jsonl"
# : > "$OUT/microsearch_arm_api.jsonl"

echo "[1/3] Retrieval track (same retrieval, Claude vs nano answer)..."
python3 experiments/mvm_retrieval_runner.py --dataset work --limit "$LIMIT_RET" --output-dir "$OUT" --nano-type heuristic

echo "[2/3] API track (Claude vs nano tool selection; same Atlassian MCP executor)..."
if [ -n "${ATLASSIAN_MCP_URL:-}" ] && [ -n "${ATLASSIAN_MCP_BEARER:-}" ]; then
  python3 experiments/mvm_api_runner.py --limit "$LIMIT_API" --output-dir "$OUT" --nano-type keyword
else
  echo "  Skipping API track (set ATLASSIAN_MCP_URL and ATLASSIAN_MCP_BEARER to run)."
fi

echo "[3/3] Comparison report (speed, accuracy, token cost)..."
python3 experiments/mvm_compare_report.py "$OUT"

echo "Done. Artifacts in $OUT. View report above; token cost is the cost metric (MCP uses Claude tokens)."
