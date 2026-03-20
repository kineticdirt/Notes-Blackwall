# MCP → Tool calls → Contents → Train nano (unsupervised)

Pipeline: connect to Atlassian MCP from `.mcp.json`, run tool calls, collect (tool, arguments, content) into a corpus, then **train the nano model** (SmolLM3-3B) on that text for unsupervised learning on tool-call context.

## Steps

1. **Collect** — MCP tool calls → `mcp_tool_calls.jsonl`  
   - Uses first server in `.mcp.json` with `url` + `Authorization`.  
   - Calls: `getAccessibleAtlassianResources`, then (with cloudId) `getConfluenceSpaces`, `searchJiraIssuesUsingJql`, `atlassianUserInfo`, `search` (Rovo).  
   - `--quick`: only resources + atlassianUserInfo (2 records, fast).

2. **Train** — Format corpus (Tool / Arguments / Response blocks) and run causal LM training on SmolLM3-3B.  
   - Unsupervised: model learns to predict response text from tool+args context.  
   - Optional `--lora` (needs `peft`) for parameter-efficient training.

3. **Continue** — Optionally run nano again after training (`--continue-after`).

## Commands

```bash
cd retrieval-eval
export NANO_POC_SSL_VERIFY=0   # if needed for SSL

# Full pipeline: collect → train (1 epoch)
python3 experiments/run_mcp_collect_and_train.py

# Quick POC: collect 2 tools only, then train
python3 experiments/run_mcp_collect_and_train.py --quick

# Only collect (no training)
python3 experiments/run_mcp_collect_and_train.py --no-train

# Only train (use existing mcp_tool_calls.jsonl)
python3 experiments/run_mcp_collect_and_train.py --no-collect

# Collect + train + run one nano query after
python3 experiments/run_mcp_collect_and_train.py --quick --continue-after
```

## Files

| File | Role |
|------|------|
| `mcp_collect_tool_calls.py` | Connect to MCP, run tool calls, write JSONL. |
| `train_nano_on_tool_calls.py` | Read JSONL, build corpus, train SmolLM3 (optional LoRA). |
| `run_mcp_collect_and_train.py` | Orchestrator: collect → train → optional continue. |
| `mcp_tool_calls.jsonl` | Collected (tool, arguments, content) records. |
| `nano_trained_on_tools/` | Output dir for trained model (after training). |

## Research note

- Unsupervised learning from tool-call contents: model sees “Tool + Arguments → Response” and learns next-token prediction on that format (no labels beyond the text).  
- For stronger tool-use behavior, you can add supervised fine-tuning later (intent → tool+args) using the same corpus or filtered subsets.
