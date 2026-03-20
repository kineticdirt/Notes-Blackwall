# Text-only micro model: retrieval and API commitment

We test a **text-only** small/micro model for two things:

1. **Better retrieval of information** — the micro model either **answers** from retrieved context or **refines** (predigests) context before the main model.
2. **Committing to specific API commands** — the micro model maps user intent → tool + arguments as an **MCP alternative** (same executor; the micro decides *what* to call).

All paths are **text-to-text only** (no images). The default micro is the 4B Qwen instruct (`qwen4b`); alternatives are heuristic, Ollama, or SmolLM.

---

## 1. Retrieval: better information retrieval

**Same retrieval** (haystack, retriever, top-k). Only the **answer** step varies:

| Arm | Who answers |
|-----|-------------|
| MCP | Claude (frontier) with top-k context |
| Micro | **Text-only micro**: heuristic, Ollama, or **Qwen 4B** (`answer_from_context`) |

**Run retrieval track with 4B (text-only):**

```bash
cd retrieval-eval
python3 experiments/mvm_retrieval_runner.py --dataset work --limit 4 --nano-type qwen4b
```

- **`--nano-type heuristic`** — no LLM; first chunk snippet (baseline).
- **`--nano-type ollama`** — local Ollama model (e.g. qwen2.5:1.5b).
- **`--nano-type qwen4b`** — 4B Qwen instruct answers from context (text-only).

**Predigestion (optional):** Use `refine_context(context, query)` in `qwen4b_router.py` to summarize/organize context before passing to another model. Not wired in the runner by default; you can call it in a custom pipeline.

---

## 2. API: commit to specific commands (MCP alternative)

The **micro model** decides **which tool and arguments** to call; the **same MCP** executes. So the micro is an MCP alternative for *routing*, not for execution.

| Arm | Who selects tool + args |
|-----|--------------------------|
| MCP | Claude (frontier) with tools/list |
| Micro | **Text-only micro**: keyword rules, SmolLM, or **Qwen 4B** (`intent_to_tool`) |

**Run API track with 4B (text-only):**

```bash
export ATLASSIAN_MCP_URL=... ATLASSIAN_MCP_BEARER=...
cd retrieval-eval
python3 experiments/mvm_api_runner.py --limit 5 --nano-type qwen4b
```

- **`--nano-type keyword`** — regex/keyword → tool (no LLM).
- **`--nano-type smol`** — SmolLM3-3B base.
- **`--nano-type qwen4b`** — 4B Qwen instruct → JSON tool + args (text-only).

---

## 3. Model and env

- **4B router/answer:** `experiments/qwen4b_router.py`. Model ID from env **`QWEN4B_MODEL_ID`** (default: JIULANG/unsloth-Qwen3.5-4B-Instruct-CitationMarker-LM). Text-to-text only.
- **Single run:** `nano_atlassian_runner.py "List Confluence spaces" --qwen4b`.

---

## 4. Metrics

- **Retrieval:** `answer_correct`, `answer_latency_ms`, `hit_at_k`, `cost_usd` (MCP only).
- **API:** `tool_correct`, `args_valid`, `response_success`, `tool_selection_latency_ms`, `cost_usd`.

Report: `python3 experiments/mvm_compare_report.py results/mvm`.
