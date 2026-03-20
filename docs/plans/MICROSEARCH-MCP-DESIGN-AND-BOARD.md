# MicroSearch × MCP — design notes & working board

**Where we are:** product lifecycle is **plan → code → test**, repeated until the flow feels **refined enough** to widen scope (e.g. large vendor MCPs). This file is the **single markdown anchor**: design intent + a lightweight **kanban-style board** you can edit in place.

**Preference:** Prefer a **small, owned HTTP MCP** (like the sample or defender-style servers) over **Atlassian-scale** surfaces until routing, eval, and training loops are stable.

---

## 1. Design goals (short)

| Goal | Meaning |
|------|--------|
| **Same executor, two brains** | **MCP arm:** frontier picks tool + args → `tools/call`. **MicroSearch arm:** keyword / small model picks tool + args → same `tools/call`. |
| **Ingest, don’t idolize one vendor** | Training inputs: **OpenAPI**, endpoint lists, or exported **`tools/list` JSON** — see `microsearch/docs/FRAMEWORK.md`. |
| **Prove with numbers** | **MvM:** latency, `tool_correct`, `cost_usd` — see `retrieval-eval/experiments/README-MVM.md` and `docs/plans/2026-03-18-MCP-VS-MICROSEARCH-TEST-FRAME.md`. |
| **Cannibalize local MCP shapes** | Reuse transport + tool registration patterns from repos below; don’t rewrite MCP from scratch. |

---

## 2. Repo map — MCP servers / clients to reuse (“cannibalize”)

| Asset | Path | Use when… |
|-------|------|-----------|
| **Sample REST + HTTP MCP** | `retrieval-eval/experiments/sample_api_mcp/` + `sample_http_mcp.py` | You want the **simplest** full loop: list/get/search, no auth — drives `mvm_sample_api_runner.py`. |
| **Defender cache MCP** | `retrieval-eval/experiments/defender_cache_mcp/` + `defender_http_mcp.py` | You want **few tools**, JSON-shaped reads, **Qwen4B / LoRA** story — see `experiments/README-DEFENDER-QWEN4B.md`. |
| **Atlassian HTTP client (reference)** | `retrieval-eval/experiments/atlassian_http_mcp.py` | Complex OAuth/cloudId patterns — **defer** until micro path is proven. |
| **Blackwall MCP framework** | `blackwall/mcp/server_framework.py`, `server_builder.py` | You want **dataclass tool defs**, `inputSchema`, resources — see `grainrad-poc/grainrad_mcp_server.py` as a consumer. |
| **Vault MCP (Node)** | `agent-context-vault/mcp/server.mjs` | You want a **minimal streamable/stdio** reference in JS. |
| **OpenAPI → tools** | `microsearch/scripts/openapi_to_mcp_tools.py`, `microsearch/templates/MCP_SERVER_FROM_OPENAPI.md` | You have a **spec**, not a server yet. |

When you add *your* MCP server, align with: **`initialize` → `tools/list` → `tools/call`** over HTTP (same JSON-RPC style as `sample_http_mcp.py`).

---

## 3. Working board (Plan · Code · Test)

Move lines between columns as work progresses. **Rule:** nothing sits in “Done” until a **test command** or **acceptance check** is named.

### Plan

- [ ] Lock **v1 tool surface** for the next MCP (names, schemas, 1–2 success paths per tool).
- [ ] Define **10–20 intents** + expected tool (+ minimal args) — mirror `sample_api_intents.py` / `defender_cache_test_cases.py`.
- [ ] Decide **training path**: keyword-only v1 vs `qwen4b` / LoRA v2; record runs via `microsearch/scripts/record_training_run.py` when training exists.
- [ ] Explicitly **defer** Atlassian (or any giant catalog) until sample + defender-style **MvM** is green.

### Code

- [ ] Implement or thin-wrap API as **HTTP MCP** (FastAPI pattern from sample/defender).
- [ ] Wire **env-based config** (base URL, bearer if needed) — no secrets in repo; see team secret rules.
- [ ] Optional: export **`tools/list` JSON** for prompts / dataset generation (`mcp_collect_tool_calls.py` patterns).

### Test

- [ ] **Smoke:** `initialize` + `tools/list` returns expected tools.
- [ ] **MvM sample path:** `mvm_sample_api_runner.py` (or your runner clone) + `mvm_compare_report.py` on `results/mvm_sample` (or your output dir).
- [ ] **Defender-style path (if applicable):** `mvm_defender_api_runner.py` + compare report.
- [ ] **Retrieval track (optional):** `mvm_retrieval_runner.py` when comparing **who answers** after same retrieval.

### Done (last few — edit as you ship)

- [ ] *(add dated entries, e.g. 2026-03-20 — sample MvM 2-intent pass + report)*

### Blocked / parking lot

- [ ] Atlassian MCP full catalog — **after** simpler MCP MvM is stable.
- [ ] OAuth / multi-tenant — only when v1 executor + eval are repeatable.

---

## 4. Quick commands (sanity)

```text
# Sample MCP server (terminal 1)
cd retrieval-eval
python3 -m uvicorn experiments.sample_api_mcp.api:app --host 127.0.0.1 --port 8765

# Sample MvM (terminal 2)
cd retrieval-eval
python3 experiments/mvm_sample_api_runner.py --limit 10 --nano-type keyword
python3 experiments/mvm_compare_report.py results/mvm_sample
```

---

## 5. Related docs

- `docs/plans/MICROSEARCH-ARCHITECTURE-PROBE.md` — nano-primary, MCP fallback narrative.
- `docs/plans/2026-03-18-MCP-VS-MICROSEARCH-TEST-FRAME.md` — full MvM metric definitions.
- `microsearch/docs/FRAMEWORK.md` — training provenance + inputs.
- `retrieval-eval/experiments/README-MVM.md` — operator runbook.

---

*Edit this file as the board of record; optionally mirror headings into `.mcp-ui/kanban/board.md` if you use that UI.*
