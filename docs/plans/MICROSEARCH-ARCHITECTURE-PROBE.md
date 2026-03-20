# Microsearch / nano-model architecture — probe (parallel to main eval)

Maps the sketch (context cloud → data sources → quest/ans → final ask) to a **minimal pipeline** you can run while `run_sequential.py` is using Claude.

## Nano replaces MCP: primary interface, MCP fallback

**Goal:** The smaller model **replaces the MCP server in its entirety** as the primary interface. It feeds and interfaces with **your API** (Jira, Confluence, etc.); the nano is the **AI in the middle** between user intent and backend. Focus on **logic and repeatability** first; use **MCP only as fallback** when the nano can’t handle the request.

| Role | Meaning |
|------|--------|
| **Nano = primary** | Single place that understands intent → tool/action. Same contract as MCP (tool name + args) but executed by nano-driven logic or direct API, not by calling MCP first. |
| **Logic + repeatability** | Deterministic rules (keywords, patterns) first; small model for fuzzy intent. Same intent → same (tool, args) where possible; trainable on your API surface. |
| **MCP fallback** | When nano returns no tool, execution fails, or intent is out of scope, hand off to the real MCP server so the system still works. |

Flow: **User intent → Nano (logic / small model) → structured (tool, args) → primary executor (direct API or thin backend) → result**. If primary fails or nano says “unknown”: **→ MCP** (full tools/list + tools/call). No frontier LLM in the loop for the primary path.

## Why this cuts large-model token burn

| Today (typical MCP / tool loop) | Nano path |
|----------------------------------|-----------|
| Frontier model reads long system + history + tool schemas + prior tool outputs each turn | Frontier gets a **short intent** (or nothing until the end) |
| Every tool call is another **assistant + tool_result** exchange on the big model | **Nano model** (local, cheap or fixed hardware cost) expands intent → structured steps → runs retrieval/CLI/fs **without** billing frontier tokens for those hops |
| Context grows with each MCP round-trip | Big model only sees a **compressed artifact** (summary, citations, diff) when you choose “final ask / approve” |

So the savings are not “MCP vs no MCP” alone—they’re **who pays tokens for orchestration**. If the small model owns *expand intent → execute → summarize*, the large model’s burn drops to occasional high-judgment passes on small payloads.

**Nano models (“if you will”):** sub–few-B params, runnable on-device or a small sidecar; acceptable to fine-tune or distill on (a) your **specific corpus** (org docs, APIs, CLI conventions) or (b) a **broad once** “everything else” dataset, then **refresh on a schedule** (retrain / LoRA / or **recache** embeddings + routing tables) instead of stuffing the frontier context every session.

## Flow (target production shape)

1. **User / app** → thin **intent** to nano (keywords, task class, or one short line).
2. **Nano** → **expands** into concrete retrieval queries, file paths, CLI patterns, or API shapes it was trained/cached for.
3. **Execute locally** (grep, index search, subprocess with guardrails)—no frontier turn per step.
4. **Nano** → **packages** result (bullet summary + pointers).
5. **Optional frontier** → single call: “approve / refine / answer user” on **that package only**—minimal input tokens.

## Intent (from sketch)

| Piece | Probe implementation |
|-------|----------------------|
| Data source | In-memory chunks or a small text file |
| Quest / Ans | CLI args: `--query` → ranked chunks → short answer |
| Logical micro model | **Optional** Ollama (1B–4B class); else heuristic extract (no LLM) |
| Final ask + approve | Script prints candidates + answer; human or later “big model” step |

## Why this doesn’t fight the main test

Main eval uses **Anthropic**. The probe uses **no Anthropic** by default; optional **Ollama** on localhost only.

## Run

```bash
cd retrieval-eval
python3 experiments/microsearch_probe.py --query "your question"
```

With local micro-model summarization (if Ollama is running):

```bash
export OLLAMA_MODEL=qwen2.5:1.5b
python3 experiments/microsearch_probe.py --query "..." --ollama
```

Custom corpus (first lines = chunks separated by blank line, or whole file as one doc split by paragraphs):

```bash
python3 experiments/microsearch_probe.py --query "..." --corpus path/to.txt
```

## Nano over a single MCP server (trained on one server’s tools)

To **run the nano path using a simple MCP server** (no frontier LLM in the loop):

1. **Tool registry** = one server’s tools only. Example: `retrieval-eval/experiments/mcp_vault_tools.json` — trained on **agent-context-vault** (3 tools: `vault_list_sources`, `vault_read_source`, `vault_reload_manifest`).
2. **Intent → tool + args**: keyword rules (default) or `--ollama` with a small local model.
3. **Execute**: Python MCP stdio client spawns the vault server, sends `initialize` → `tools/call`, returns result.

```bash
cd retrieval-eval
# Optional: set if vault is elsewhere
export AGENT_CONTEXT_VAULT_ROOT=/path/to/agent-context-vault/vault

python3 experiments/nano_mcp_runner.py "list vault sources"
python3 experiments/nano_mcp_runner.py "read source wf-claude-obsidian-001"
# With Ollama (intent→tool by small model):
python3 experiments/nano_mcp_runner.py "show me the obsidian workflow doc" --ollama
```

The **large model never sees** tool schemas or MCP round-trips; the nano layer (keyword or 1B–4B local) does intent → single tool call. To train on another server: replace `mcp_vault_tools.json` with that server’s tool list (from `tools/list`) and point the runner at that server’s command + env.

## Comparative test frame: MCP vs MicroSearch

A **novel test frame** compares MCP (frontier + MCP server) vs MicroSearch (nano as primary) on **retrieval** (needle-in-haystack, same as existing eval) and **API/tool-call** tasks, on three dimensions: **creation/setup**, **speed (latency)**, and **accuracy**. Plan: **`docs/plans/2026-03-18-MCP-VS-MICROSEARCH-TEST-FRAME.md`**.

## Next steps (not in probe)

- Wire **intent → JSON plan → allowlisted executors** from nano output (same role MCP fills for the big model, but **off** the frontier bill).
- Log **frontier input tokens** with vs without nano path on identical tasks (A/B).
- Define **recache policy**: e.g. weekly index rebuild + quarterly LoRA refresh on new internal docs.
- Add more servers: one registry (or one nano) per server, or a single nano trained on multiple servers’ tool sets.

## Nano over Atlassian: primary interface, MCP fallback

The **nano replaces MCP** as the primary interface: it feeds and interfaces with your API (e.g. Atlassian); MCP is used only when the nano can’t map intent or execution fails.

- **Logic and repeatability:** Deterministic keyword rules first; optional SmolLM3-3B for fuzzy intent. Same intent → same (tool, args) where possible.
- **Runner:** `retrieval-eval/experiments/nano_primary_mcp_fallback.py` — nano (keyword or `--smol`) → primary executor (MCP today); on no-tool or failure → MCP fallback (safe default).
- **Env:** `ATLASSIAN_MCP_URL`, `ATLASSIAN_MCP_BEARER` (no secrets in code).
- **Deps:** `experiments/requirements-nano.txt` for `--smol`.
- **Details:** `retrieval-eval/experiments/README-NANO-ATLASSIAN.md`.
