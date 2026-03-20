# MCP vs MicroSearch Architecture — Comparative Test Frame

**Goal:** A novel test framework to determine whether **MCP** (frontier model + MCP server for tools/retrieval) is faster (compiling, creation, and accuracy) relative to **MicroSearch Architecture** (nano model as primary interface, retrieval/API in the middle, MCP fallback).

---

## 1. Test frame name and scope

- **Name:** MCP vs MicroSearch Comparative Eval (MvM).
- **Scope:** Same tasks run under two arms; compare on **creation/setup**, **speed (latency)**, and **accuracy**.
- **Tracks:** (A) **Retrieval** — needle-in-haystack style, aligned with existing retrieval-eval. (B) **API/tool-call** — intent → tool + arguments, execution, response.

---

## 2. Arms (what we compare)

| Arm | Description | Retrieval path | API/tool path |
|-----|-------------|----------------|---------------|
| **MCP** | Current baseline: frontier LLM + MCP server. Retrieval = MCP or same store; answer = frontier with context. Tool use = frontier decides tool + args, MCP executes. | Build haystack → retriever (vector/substring/hybrid) → top-k chunks → **Claude** with context → answer. | User intent → **Claude** (with tools/list in context) → tools/call via MCP → tool result back to Claude → final answer. |
| **MicroSearch** | Nano as primary: small model does retrieval expansion and/or tool selection; execution via same store or direct API; optional frontier only at the end. | Same haystack/store → **nano** (keyword or SmolLM) maps query to search/params → same retriever → top-k → **nano** (or no LLM) summarizes OR **one** Claude call on compressed result. | User intent → **nano** (keyword or SmolLM) → (tool, args) → executor (MCP or direct API) → result; optional Claude for polish. |

Controlled variables: same corpus, same queries, same tool list (when applicable), same success criteria.

**MicroSearch = predigestion.** MicroSearch is primarily about **organizing and refining context before** the model parses it—e.g. summarizing or structuring top-k retrieval, or mapping intent → tool+args so the executor gets clean input. A **slightly larger model** (e.g. 4B instruct) is acceptable for this predigestion step if it improves accuracy or robustness.

---

## 3. Dimensions and metrics

### 3.1 Creation / setup (“compiling, creation”)

- **Definition:** One-time or cold-start cost before the system can serve requests.
- **Metrics:**
  - **Time to first request (TTFR):** Wall-clock from “start run” until first task completes (includes model load, MCP connect, any compilation).
  - **Setup time (optional):** If we separate “load model + connect” from “first inference,” record setup separately.
- **Comparison:** Lower is better. Report TTFR (and setup if applicable) for each arm.

### 3.2 Speed (latency)

- **Definition:** Per-task wall-clock time from task start to task end.
- **Metrics:**
  - **Retrieval track:** End-to-end latency = (build/load store if needed) + retrieval + (nano or Claude) answer. Record **retrieval_latency_ms** and **answer_latency_ms** separately when possible.
  - **API track:** End-to-end latency = intent in → (tool selection + tools/call + optional summarization) → result. Record **tool_selection_latency_ms**, **tool_call_latency_ms**, **total_latency_ms**.
- **Comparison:** Lower is better. Report percentiles (p50, p95) and mean over the task set.

### 3.3 Accuracy

- **Retrieval track:**
  - **hit_at_k:** Needle-containing chunk in top-k (boolean).
  - **rank:** 1-based rank of needle chunk if hit; null if miss.
  - **answer_correct:** Final answer contains required marker(s) (same as existing retrieval-eval).
- **API track:**
  - **tool_correct:** Selected tool matches expected tool for the intent (exact or allow equivalent).
  - **args_valid:** Arguments pass server validation (no 400/invalid).
  - **response_success:** Tool returned non-error (is_error false or HTTP 2xx).
  - **answer_correct (if applicable):** When we ask a question that requires a tool call, does the final answer satisfy the success criterion?
- **Comparison:** Higher is better. Report rates (e.g. % hit@k, % answer_correct) per arm.

### 3.4 Token / dollar cost

- **Definition:** Cost of frontier model usage per task (input + output tokens × model pricing).
- **Metrics:** **cost_usd** per task; sum per arm. MicroSearch arm = 0 when no frontier is used for tool selection or answer.
- **Comparison:** Lower is better. Report total cost_usd per arm (see comparison report script).

### 3.5 Training time (MicroSearch arm)

- **Definition:** One-time or periodic cost to produce/refresh the micro model or routing dataset from the API surface (OpenAPI, endpoints).
- **Metrics:** Recorded in **`microsearch/`** (separate folder):
  - **training_duration_seconds:** Wall-clock time for the training job (fine-tune, LoRA, or dataset build).
  - **training_data_generation_seconds (optional):** Time for frontier model to generate JSONL from OpenAPI only.
  - **openapi_spec_paths**, **num_openapi_operations**, **num_training_examples**, **training_backend**, **frontier_model_training_data**.
- **Recording:** `microsearch/scripts/record_training_run.py` appends to `microsearch/results/training_runs.jsonl`.
- **Comparison:** Report alongside MvM so total cost of ownership can include amortized training (e.g. training_duration_seconds / expected_requests). Full definition: **`microsearch/docs/FRAMEWORK.md`**.

---

## 4. Retrieval track (needle-in-haystack, same as existing eval)

- **Reuse:** Same store, retriever, haystack builder, needle positions, chunk sizes, and eval types (needle, reasoning, explanation, assistance) and datasets (default, work, cequence_cs) as in `retrieval-eval`.
- **Tasks:** For a fixed subset of permutations (e.g. one gravity, one k, one position, one chunk_size per eval_type):
  - **MCP arm:** Run current `run_one` flow: retrieval → Claude with top-k context → answer. Record: setup/TTFR (if cold), retrieval_latency_ms, answer_latency_ms, hit_at_k, rank, answer_correct, input_tokens, output_tokens.
  - **MicroSearch arm:** Same haystack/query/needle. Nano (keyword or SmolLM) is not used for retrieval *selection* (we use the same retriever); optionally nano summarizes top-k instead of Claude, or we measure “retrieval only” (no LLM) and then “retrieval + nano answer” vs “retrieval + Claude answer.” So either:
    - **Variant A:** Same retrieval; compare “Claude answer” vs “nano answer” (speed + accuracy).
    - **Variant B:** Nano suggests query expansion or k; then same retriever runs; then nano or Claude answers. (More complex; can be phase 2.)
- **Canonical choice for v1:** Same retrieval for both arms; only the **answer** step differs (Claude vs nano). That isolates “who answers” and keeps retrieval identical. Record hit@k and rank from the single retrieval run; record answer_latency_ms and answer_correct for each arm.

---

## 5. API / tool-call track

- **Task format:** (intent, expected_tool, expected_args_subset, success_criterion).
- **Intent examples:** “What Atlassian resources can I access?”, “List Confluence spaces”, “Search Jira for recent issues”, “Get Jira issue PROJ-123”.
- **Execution:**
  - **MCP arm:** Send intent to Claude with MCP tools/list; Claude returns tool + args; run tools/call; optionally Claude sees result and produces final answer. Record tool_selection_latency_ms (Claude turn), tool_call_latency_ms, total_latency_ms, tool_correct, args_valid, response_success, answer_correct.
  - **MicroSearch arm:** Nano (keyword or SmolLM) maps intent → (tool, args); same executor (MCP) runs tools/call. Record tool_selection_latency_ms (nano), tool_call_latency_ms, total_latency_ms, tool_correct, args_valid, response_success; if we add a final answer step, answer_correct.
- **Ground truth:** For each intent, define expected_tool and minimal expected_args (e.g. cloudId when required). tool_correct = (selected tool == expected_tool). args_valid = server did not return validation error.

---

## 6. Artifacts and output format

- **Per run:** One JSONL per arm (e.g. `mcp_arm_retrieval.jsonl`, `microsearch_arm_retrieval.jsonl`, `mcp_arm_api.jsonl`, `microsearch_arm_api.jsonl`) with one line per task:
  - run_id, arm, track, task_id, creation_ttfr_ms (optional), retrieval_latency_ms, answer_latency_ms or tool_selection_latency_ms, tool_call_latency_ms, total_latency_ms, hit_at_k, rank, answer_correct, tool_correct, args_valid, response_success, input_tokens, output_tokens, **cost_usd**, error.
  - **Token cost:** `cost_usd` is computed from input/output tokens (e.g. Claude Sonnet ~$3/1M in, $15/1M out) and is the **overall cost metric** for comparison (training time excluded).
- **Summary report:** A small script or notebook that:
  - Reads both arms’ JSONL.
  - Computes per-dimension metrics (creation, speed, accuracy) by arm and track.
  - Outputs a comparison table: MCP vs MicroSearch on creation (TTFR), speed (p50/p95/total_latency), accuracy (hit@k %, answer_correct %, tool_correct %, etc.).
- **MicroSearch framework (separate folder):** **`microsearch/`** holds training-data generation (OpenAPI → tools, frontier prompt), training-run recording (training_duration_seconds, provenance), and templates for exposing an API as MCP. Comparison results use the same report as above; training runs are summarized with `microsearch/scripts/summarize_training_runs.py`.

---

## 7. Implementation plan (phased)

| Phase | Deliverable |
|-------|-------------|
| **1. Plan** | This document. |
| **2. Retrieval track — same retrieval, two answer paths** | (a) Extract “run retrieval + get top-k” from current run_sequential so it can be called once per task. (b) Add “answer path” abstraction: Claude vs nano (existing microsearch_probe or SmolLM summarizer). (c) Runner that, for a fixed permutation subset, runs retrieval once, then runs both answer paths, records metrics for each arm. (d) Output JSONL per arm. |
| **3. API track** | (a) Define a small intent suite (5–10 intents) with expected_tool and expected_args. (b) MCP arm: call Claude with tools/list + intent, parse tool call, run tools/call, record metrics. (c) MicroSearch arm: run existing nano path (keyword or SmolLM → tool + args), same tools/call, record metrics. (d) Output JSONL per arm. |
| **4. Creation / TTFR** | (a) Optionally run “cold start” once per arm (e.g. load model, connect MCP, then first task). Record TTFR. (b) Add creation_ttfr_ms to run metadata. |
| **5. Comparison report** | Script or notebook: load both arms’ JSONL, compute creation (mean/median), speed (p50, p95, mean latency), accuracy (%, counts), output comparison table and optional plots. |

---

## 8. Success criteria for the test frame

- **Reproducible:** Same tasks and seeds produce comparable results across runs.
- **Fair:** Same data, same tools, same success criteria for both arms; only the “who does retrieval expansion / tool selection / answer” differs.
- **Interpretable:** Clear metrics (creation, speed, accuracy) and a single comparison report answering: “Is MCP faster (creation + latency) and more accurate than MicroSearch on this suite?” with evidence (numbers and optional plots).

---

## 9. Open choices (to resolve in implementation)

- **Retrieval track v1:** Compare only “answer step” (Claude vs nano) with identical retrieval, or also vary “who drives retrieval” (e.g. nano suggests k/query)? **Recommendation:** v1 = same retrieval, two answer paths; add “nano-driven retrieval” in a later phase.
- **Nano model for MicroSearch arm:** SmolLM3-3B, Ollama (e.g. qwen2.5:1.5b), or keyword-only? **Recommendation:** Support both keyword and SmolLM in the runner; report results per nano type.
- **API track ground truth:** Manually curated intents + expected tool/args, or derived from MCP tools/list + synthetic intents? **Recommendation:** Start with 5–10 curated (intent, expected_tool, expected_args) for Atlassian MCP; expand later.
