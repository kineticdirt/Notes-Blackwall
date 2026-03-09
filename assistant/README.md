# Personal Assistant — Manifest-Driven Composition

The **personal assistant** is defined by **frankensteining multiple orchestrators** together under a single, secure definition. No new Python orchestration runtime; composition is declarative (YAML manifest) and enforced by boundaries and consistency rules.

## Intent

- **Secure**: Boundaries per orchestrator; no secrets in manifest; pipeline order (input filter first).
- **Consistent**: Single source of truth (`manifest.yaml`); validation script; audit sink.
- **Non-Python**: Definition and validation are YAML + shell; execution is existing systems (MCP, workflow-canvas, subagents, prompt-injection gate, overseer contract).

## Files

| File | Purpose |
|------|--------|
| `manifest.yaml` | Orchestrators, pipeline order, boundaries, consistency rules. **No secrets.** |
| `SECURITY-BOUNDARIES.md` | Human-readable per-orchestrator boundaries. |
| `validate.sh` | Shell script to validate manifest (required keys, no secret values, pipeline consistency). No Python. |
| `.cursor/rules/personal-assistant-manifest.mdc` | Cursor rule: assistant is defined by manifest; follow pipeline and boundaries. |

## Validation

```bash
./assistant/validate.sh
# or
./assistant/validate.sh /path/to/manifest.yaml
```

Exit 0 = valid; non-zero = invalid (errors to stderr).

## Pipeline (from manifest)

1. **prompt_injection_gate** — User input → scan → block or pass. Downstream only sees passed text.
2. **mcp** — Allowed tools only; no secrets in config.
3. **workflow_canvas** — Allowed blocks only; no raw secrets in workflow.
4. **subagents** — Allowed agents (cleanup, test, doc); ledger path fixed.
5. **overseer_contract** — Append-only to `.overseer`; goal from env.

## Running as part of the system

To run the assistant as a first-class system component (key-holder + assistant in one command): see **`docs/runbooks/RUN_ASSISTANT_SYSTEM.md`**. From repo root: `./scripts/run-assistant-system.sh` or `docker compose -f docker-compose.assistant.yaml up --build`.

## One place for keys and MCP

Put your **Anthropic key** and **MCP servers** in a single file: **`assistant/config/user_config.yaml`** (copy from `user_config.example.yaml`). The assistant loads it at startup; the HTTP API never returns your key. See **`assistant/config/README.md`** and **`assistant/API.md`** (key-free response format).

## General-Purpose Assistant (Pi-style runner)

A general-purpose assistant that connects to MCP services on the fly, saves preferences over its lifetime, and runs continuously. See **PI-ASSISTANT.md**.

```bash
export PI_LLM_API_BASE="http://localhost:11434/v1"
export PI_LLM_MODEL="llama3.2"
python3 -m assistant.pi_runner          # REPL
python3 -m assistant.pi_runner --daemon # REPL + HTTP POST /message
```

Optional: `pip install mcp` for dynamic MCP server connections. Preferences: `PI_PREFERENCES_PATH`; MCP config: `PI_MCP_CONFIG` or `.mcp.json`.

## Changing the Assistant

1. Edit `assistant/manifest.yaml` (orchestrators, pipeline_order, boundaries).
2. Run `./assistant/validate.sh`.
3. Keep MCP config, `.claude/agents`, workflow JSON consistent with the manifest by convention or tooling.
4. Do not put secrets in the manifest; use env or vault references.
