# General-Purpose Assistant (Pi-Style)

A **general-purpose assistant** that connects to different MCP services on the fly, saves personal preferences over its lifetime, and runs continuously (REPL or daemon with HTTP). Open-source, manifest-aligned.

## Goals

- **General-purpose**: Coding, info gathering, and personalization via tools and MCP.
- **Dynamic MCP**: Connect to MCP servers from config (e.g. `.mcp.json`) on the fly; tools from those servers are available to the LLM each turn.
- **Persistent preferences**: Save user preferences (theme, language, style, etc.) over the assistant’s lifetime; loaded into context each turn.
- **Runs continuously**: REPL until exit, or `--daemon` with an HTTP endpoint for remote messages.

## Pipeline

1. **prompt_injection_gate** — User input is scanned; if injection detected, block or sanitize. Only `passed_text` goes downstream.
2. **MCP (on the fly)** — Load server config; connect to stdio (and optionally HTTP) MCP servers; merge their tools with built-in tools. Tool names are prefixed by server id (e.g. `notes_read_notes`).
3. **Built-in tools** — `read_file`, `write_file`, `codebase_search`, `grep`, `run_terminal_cmd`, `read_lints`, `list_dir`, `glob_file_search`, `read_preferences`, `save_preference`.
4. **LLM loop** — Model receives passed text and current preferences; can call any of the above tools; runner executes and returns results until the model responds.

## Components

| Component             | Role |
|-----------------------|------|
| `pi_runner.py`        | REPL or daemon: gate → LLM with tool loop; built-in + preference + MCP tools. |
| `preferences_store.py`| Persistent JSON store for user preferences; `read_preferences` / `save_preference`. |
| `mcp_dynamic.py`      | Load MCP config; connect to servers (stdio); list/call tools; one pool per turn. |
| `manifest.yaml`       | Source of allowed built-in tools and pipeline order. |
| Gate                  | `blackwall.prompt_injection.SacrificialGate`. |

## Configuration (env)

- `PI_LLM_API_BASE` — e.g. `http://localhost:11434/v1` (Ollama) or OpenAI base URL (not used for Anthropic).
- `PI_LLM_MODEL` — e.g. `llama3.2`, `gpt-4`, or `claude-sonnet-4-5` for Claude.
- `PI_LLM_API_KEY` — API key (optional for some providers). Prefer file for K8s: see `PI_LLM_API_KEY_FILE`.
- `PI_LLM_API_KEY_FILE` — Path to file containing the API key (e.g. `assistant/llm_keys/ANTHROPIC_API_KEY` or `/run/secrets/anthropic_api_key` in K8s).
- `PI_LLM_PROVIDER` — `anthropic` (Claude) or `openai` (Ollama/OpenAI/LiteLLM). Default `openai`.
- `PI_GATE_REMEDY` — `block` or `sanitize` (default: `sanitize`).
- `PI_PROJECT_ROOT` — Workspace path for file/tool operations (default: cwd).
- `PI_PREFERENCES_PATH` — Path to preferences JSON (default: `assistant/data/preferences.json`).
- `PI_MCP_CONFIG` — Path to MCP servers config; if unset, uses `.mcp.json` in project root.
- `PI_HTTP_PORT` — Port for HTTP server when running with `--daemon` (default: 8765).

## Usage

```bash
# REPL (run until you type exit or Ctrl+D)
export PI_LLM_API_BASE="http://localhost:11434/v1"
export PI_LLM_MODEL="llama3.2"
python3 -m assistant.pi_runner

# Continuous run with HTTP endpoint (same REPL + POST /message)
python3 -m assistant.pi_runner --daemon
# POST http://localhost:8765/message with JSON: {"message": "Hello"}
```

Preferences are stored under `PI_PREFERENCES_PATH` and loaded each turn. The LLM can call `save_preference` when the user states a preference.

MCP servers are read from `PI_MCP_CONFIG` or `.mcp.json` (key `mcpServers`). Stdio servers (command/args) are connected each turn; their tools are exposed with a `serverId_toolName` prefix.

## Optional: MCP SDK

For dynamic MCP connections, install the MCP Python SDK:

```bash
pip install mcp
```

If `mcp` is not installed, the assistant still runs with built-in and preference tools only.

## Out of scope (for now)

- workflow_canvas and subagents are not invoked by the runner.
- Streamable-HTTP MCP servers: only stdio is implemented in `mcp_dynamic.py`.
- Overseer contract: not used by the runner.
