# Atlassian nano router: SFT + hallucination control + H-Neurons

## Goal

Train the **nano** (SmolLM3-3B) **only** on Atlassian MCP routing: user intent → `{"tool","arguments"}` JSON. That reduces **prose hallucination** (model is trained to emit **JSON only**) and improves **efficient API calls** (right tool, valid args).

## 1. Supervised Atlassian-only training (primary path)

```bash
cd retrieval-eval

# Build supervised JSONL (~25+ intent variants → golden tool+args)
python3 experiments/atlassian_intent_router_dataset.py
# Optional: align tool list with live MCP
python3 experiments/atlassian_intent_router_dataset.py --refresh-tools

# LoRA SFT (GPU recommended)
pip install peft accelerate  # if needed
python3 experiments/train_atlassian_intent_nano.py --epochs 3 --batch-size 2

# Use trained adapter for routing
export ATLASSIAN_NANO_ADAPTER="$(pwd)/experiments/atlassian_intent_nano_lora"
export ATLASSIAN_CLOUD_ID="<uuid>"   # when tools need cloudId
python3 experiments/nano_atlassian_runner.py "List Confluence spaces" --smol
```

**Guard before MCP:** `atlassian_tool_guard.py` — unknown tool name or missing required args → do not call MCP (avoids bad API traffic).

## 2. H-Neurons ([thunlp/H-Neurons](https://github.com/thunlp/H-Neurons))

Paper: *H-Neurons: On the Existence, Impact, and Origin of Hallucination-Associated Neurons in LLMs* ([arXiv:2512.01797](https://arxiv.org/abs/2512.01797)).

**What it does:** After sampling model outputs, extract activations, train a **sparse linear classifier** to predict hallucination; identified neurons can be **intervened** (e.g. scale `down_proj` inputs) to reduce hallucination.

**Fit for the nano router**

| Use | Role |
|-----|------|
| **Research / audit** | Run H-Neurons pipeline on **SmolLM3** with prompts = your router prompts and labels = JSON parse OK + tool in allowlist vs failure. Tests whether failures correlate with specific neurons. |
| **Production** | **SFT + JSON-only target + `atlassian_tool_guard`** is simpler and deterministic. H-Neurons-style intervention is heavier (vLLM, activation hooks, per-model tuning). |

**Suggested order:** (1) SFT + guard until `tool_correct` / `args_valid` are high on your intent suite; (2) if residual hallucinations remain, use H-Neurons to **analyze** the same base or LoRA adapter; (3) only then consider intervention experiments.

## 3. Expand training data

Edit `GOLDEN` in `atlassian_intent_router_dataset.py` or append rows to `atlassian_intent_router.jsonl` from **logged Claude tool calls** (`mcp_tool_calls.jsonl` is response-focused; prefer intent→tool pairs from `mvm_api_runner` logs or internal analytics).

## 4. Metrics

Re-run **`experiments/mvm_api_runner.py --nano-type smol`** after training and compare `tool_correct`, `response_success`, and **sum `cost_usd`** on the MCP arm vs nano arm.
