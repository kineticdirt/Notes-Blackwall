# MvM — MCP vs MicroSearch comparative test frame

Same tasks run under **MCP** (frontier LLM + MCP server) vs **MicroSearch** (nano as primary, same executor). Compare **speed**, **accuracy**, and **token cost** (cost metric; training time excluded). Plan: `docs/plans/2026-03-18-MCP-VS-MICROSEARCH-TEST-FRAME.md`.

## Tracks

- **Retrieval:** Same needle-in-haystack retrieval; only the **answer** step differs (Claude vs nano heuristic/Ollama). Outputs: `mcp_arm_retrieval.jsonl`, `microsearch_arm_retrieval.jsonl`.
- **API:** Same intents; MCP arm = Claude selects tool + args, MicroSearch arm = nano (keyword or SmolLM) selects tool + args; **same Atlassian MCP** runs `tools/call`. Outputs: `mcp_arm_api.jsonl`, `microsearch_arm_api.jsonl`.

## Prerequisites

- **Claude API key:** `retrieval-eval/.api-key` or `ANTHROPIC_API_KEY` (for MCP arm).
- **API track only:** `ATLASSIAN_MCP_URL`, `ATLASSIAN_MCP_BEARER`. Optional: `ATLASSIAN_CLOUD_ID` for Jira/Confluence calls.

## Run comparison (standard model, same tools, token cost as metric)

From `retrieval-eval/`:

```bash
# Full comparison (retrieval + API if env set)
bash experiments/run_mvm_comparison.sh

# With limits (e.g. 4 retrieval tasks, 5 API intents)
LIMIT_RET=4 LIMIT_API=5 bash experiments/run_mvm_comparison.sh
```

Then view the printed comparison report (speed p50/p95, accuracy %, **cost_usd** per arm).

## Run tracks separately

```bash
cd retrieval-eval

# Retrieval track only (Claude vs nano answer, same retrieval)
python3 experiments/mvm_retrieval_runner.py --dataset work --limit 4 --nano-type heuristic
# Or with Ollama for nano answer: --nano-type ollama

# API track only (requires ATLASSIAN_MCP_URL + ATLASSIAN_MCP_BEARER)
python3 experiments/mvm_api_runner.py --limit 5 --nano-type keyword
# Or: --nano-type smol (SmolLM for tool selection)

# Comparison report (table + optional plots)
python3 experiments/mvm_compare_report.py results/mvm
python3 experiments/mvm_compare_report.py results/mvm --plots
```

## Artifacts

- **JSONL** (one line per task): `run_id`, `arm`, `track`, latencies, `hit_at_k` / `tool_correct`, `answer_correct` / `response_success`, `input_tokens`, `output_tokens`, **`cost_usd`**, `error`.
- **Report:** Printed table; optional PNGs if `--plots` and matplotlib.

Token cost uses approximate Claude Sonnet pricing ($3/1M input, $15/1M output); MicroSearch arm is $0 when using heuristic/keyword (no API calls for answer/tool selection).

---

## Sample API (real-world style, no Atlassian)

A **sample REST API + MCP** provides list/get/search (real-world patterns) so you can run MvM **without** Atlassian credentials.

**1. Start the server** (from `retrieval-eval/`):

```bash
pip install -r experiments/requirements-sample.txt
python3 -m uvicorn experiments.sample_api_mcp.api:app --host 127.0.0.1 --port 8765
```

**2. Run MvM** (in another terminal):

```bash
cd retrieval-eval
python3 experiments/mvm_sample_api_runner.py --limit 10 --nano-type keyword
# Or --nano-type qwen4b for text-only 4B micro
python3 experiments/mvm_compare_report.py results/mvm_sample
```

**Tools:** `listPosts`, `getPost`, `searchPosts`, `listUsers`, `getUser`. Intents are in `experiments/sample_api_intents.py`. MCP URL default: `http://127.0.0.1:8765/mcp` (override with `SAMPLE_MCP_URL`).
