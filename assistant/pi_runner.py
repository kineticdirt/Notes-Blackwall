"""
General-purpose assistant: gate -> LLM with built-in tools, preferences, and dynamic MCP.
Runs continuously (REPL or daemon with optional HTTP). Saves preferences over its lifetime.
Run: python -m assistant.pi_runner [--daemon]
Config: PI_LLM_API_BASE, PI_LLM_MODEL, PI_LLM_API_KEY or PI_LLM_API_KEY_FILE or CEQUENCE_SECRETS_FILE (external file),
        PI_LLM_PROVIDER (anthropic|openai), PI_GATE_REMEDY, PI_PROJECT_ROOT, PI_PREFERENCES_PATH, PI_MCP_CONFIG, PI_HTTP_PORT.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Project root: assistant/ is inside repo
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Load secrets from CEQUENCE_SECRETS_FILE (and optional project .env) before any key access
try:
    from assistant.load_secrets import load_secrets
    load_secrets()
except Exception:
    pass

# Built-in tools (manifest-aligned)
ALLOWED_TOOL_NAMES: List[str] = [
    "read_file",
    "write_file",
    "codebase_search",
    "grep",
    "run_terminal_cmd",
    "read_lints",
    "list_dir",
    "glob_file_search",
    "read_preferences",
    "save_preference",
]


def _project_root() -> Path:
    return Path(os.environ.get("PI_PROJECT_ROOT", os.getcwd())).resolve()


def _get_api_key() -> Optional[str]:
    """Read API key from PI_LLM_API_KEY or from file PI_LLM_API_KEY_FILE (one key per file, trimmed)."""
    key = os.environ.get("PI_LLM_API_KEY", "").strip()
    if key:
        return key
    path = os.environ.get("PI_LLM_API_KEY_FILE", "").strip()
    if path:
        p = Path(path)
        if p.is_absolute() or not p.exists():
            p = _project_root() / path
        if p.exists():
            try:
                return p.read_text(encoding="utf-8").strip()
            except OSError:
                pass
    return None


def _tool_definitions() -> List[Dict[str, Any]]:
    """OpenAI-compatible tool definitions for allowed tools."""
    root = str(_project_root())
    return [
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read contents of a file. Use path relative to project root or absolute.",
                "parameters": {
                    "type": "object",
                    "properties": {"path": {"type": "string", "description": "File path"}},
                    "required": ["path"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write content to a file. Overwrites if exists.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path"},
                        "contents": {"type": "string", "description": "Content to write"},
                    },
                    "required": ["path", "contents"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "codebase_search",
                "description": "Search for text in codebase (grep-based). Optional path to limit scope.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search string or pattern"},
                        "path": {"type": "string", "description": "Optional directory path (relative to project)"},
                    },
                    "required": ["query"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "grep",
                "description": "Search for a pattern in files under a path.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string"},
                        "path": {"type": "string", "description": "Directory or file path (default project root)"},
                    },
                    "required": ["pattern"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "run_terminal_cmd",
                "description": "Run a terminal command. Use for read-only or small edits. Prefer short commands.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string"},
                        "is_background": {"type": "boolean", "description": "If true, run in background", "default": False},
                    },
                    "required": ["command"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_lints",
                "description": "Read linter diagnostics for given paths (e.g. file or directory).",
                "parameters": {
                    "type": "object",
                    "properties": {"paths": {"type": "array", "items": {"type": "string"}, "description": "Paths to check"}},
                    "required": ["paths"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_dir",
                "description": "List directory contents. Path relative to project or absolute.",
                "parameters": {
                    "type": "object",
                    "properties": {"path": {"type": "string", "description": "Directory path (default project root)"}},
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "glob_file_search",
                "description": "Glob search for files (e.g. '**/*.py'). Path is optional base directory.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string"},
                        "path": {"type": "string", "description": "Optional base directory"},
                    },
                    "required": ["pattern"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_preferences",
                "description": "Read all saved user preferences (persisted over the assistant's lifetime). Use to respect user choices.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "save_preference",
                "description": "Save a user preference. Call when the user states a preference (e.g. theme, language, style). Key can be dotted, e.g. theme.dark.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "description": "Preference key (e.g. theme, editor.font_size)"},
                        "value": {"type": "string", "description": "Value to store"},
                    },
                    "required": ["key", "value"],
                },
            },
        },
    ]


def _resolve_path(path: str) -> Path:
    p = Path(path)
    if not p.is_absolute():
        p = _project_root() / path
    return p.resolve()


def _path_under_root(p: Path) -> bool:
    """True if p is under project root (or equals root)."""
    root = _project_root()
    try:
        p.resolve().relative_to(root)
        return True
    except ValueError:
        return p.resolve() == root


def _run_tool(name: str, arguments: Dict[str, Any]) -> str:
    """Execute a single tool and return a string result. Paths are relative to PI_PROJECT_ROOT."""
    root = _project_root()
    try:
        if name == "read_file":
            p = _resolve_path(arguments["path"])
            if not _path_under_root(p):
                return "Error: path must be under project root"
            return p.read_text(encoding="utf-8", errors="replace")

        if name == "write_file":
            p = _resolve_path(arguments["path"])
            if not _path_under_root(p):
                return "Error: path must be under project root"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(arguments["contents"], encoding="utf-8")
            return f"Wrote {p.relative_to(root)}"

        if name == "codebase_search":
            query = arguments["query"]
            base = arguments.get("path") or "."
            dir_p = _resolve_path(base)
            if not dir_p.is_dir():
                return f"Error: not a directory: {base}"
            if not _path_under_root(dir_p):
                return "Error: path must be under project root"
            out = subprocess.run(
                ["grep", "-r", "-n", "-l", "--include=*", query, str(dir_p)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(root),
            )
            if out.returncode not in (0, 1):
                return out.stderr or "grep failed"
            return out.stdout or f"No matches for '{query}'"

        if name == "grep":
            pattern = arguments["pattern"]
            path = arguments.get("path") or "."
            p = _resolve_path(path)
            if not p.exists():
                return f"Error: path does not exist: {path}"
            if not _path_under_root(p):
                return "Error: path must be under project root"
            out = subprocess.run(
                ["grep", "-r", "-n", "--include=*", pattern, str(p)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(root),
            )
            if out.returncode not in (0, 1):
                return out.stderr or "grep failed"
            return out.stdout or f"No matches for '{pattern}'"

        if name == "run_terminal_cmd":
            cmd = arguments["command"]
            bg = arguments.get("is_background", False)
            if bg:
                subprocess.Popen(
                    cmd,
                    shell=True,
                    cwd=str(root),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return f"Started in background: {cmd}"
            r = subprocess.run(
                cmd,
                shell=True,
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=60,
            )
            out = (r.stdout or "").strip() or "(no stdout)"
            err = (r.stderr or "").strip()
            if err:
                out += "\nstderr: " + err
            return f"exit {r.returncode}\n{out}"

        if name == "read_lints":
            # No IDE linter in CLI; return placeholder
            paths = arguments.get("paths") or []
            return f"Lints requested for: {paths}. (Runner has no IDE linter; run linters manually or via tools.)"

        if name == "list_dir":
            path = arguments.get("path") or "."
            p = _resolve_path(path)
            if not p.is_dir():
                return f"Error: not a directory: {path}"
            if not _path_under_root(p):
                return "Error: path must be under project root"
            parts = [f"{x.name}/" if x.is_dir() else x.name for x in sorted(p.iterdir())]
            return "\n".join(parts)

        if name == "glob_file_search":
            pattern = arguments["pattern"]
            base = arguments.get("path") or "."
            dir_p = _resolve_path(base)
            if not dir_p.is_dir():
                return f"Error: not a directory: {base}"
            if not _path_under_root(dir_p):
                return "Error: path must be under project root"
            found = list(dir_p.rglob(pattern))
            return "\n".join(str(f.relative_to(dir_p)) for f in sorted(found)) or f"No files matching {pattern}"

        if name == "read_preferences":
            from assistant.preferences_store import read_preferences, format_preferences_for_prompt
            prefs = read_preferences()
            return format_preferences_for_prompt(prefs)

        if name == "save_preference":
            from assistant.preferences_store import save_preference
            key = arguments.get("key", "")
            value = arguments.get("value", "")
            if not key:
                return "Error: key required"
            return save_preference(key, value)

        return f"Unknown tool: {name}"
    except subprocess.TimeoutExpired:
        return "Error: command timed out"
    except Exception as e:
        return f"Error: {e}"


def _all_tool_definitions_static() -> List[Dict[str, Any]]:
    """Built-in + preference tools only (no MCP)."""
    return _tool_definitions()


def _gate_process(user_input: str) -> tuple[str, bool, str]:
    """Run prompt_injection_gate. Returns (passed_text, blocked, block_message)."""
    try:
        from blackwall.prompt_injection import SacrificialGate
    except ImportError:
        return user_input, False, ""
    remedy = os.environ.get("PI_GATE_REMEDY", "sanitize")
    gate = SacrificialGate(remedy_mode=remedy)
    passed_text, result = gate.process(user_input)
    return passed_text, result.blocked, result.block_message or ""


def _openai_tools_to_anthropic(tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert OpenAI-format tools to Anthropic (name, description, input_schema)."""
    out = []
    for t in tools:
        fn = (t or {}).get("function") or t
        name = fn.get("name", "")
        desc = fn.get("description", "")
        params = fn.get("parameters") or {}
        out.append({
            "name": name,
            "description": desc or name,
            "input_schema": params if isinstance(params, dict) else {"type": "object", "properties": {}},
        })
    return out


def _llm_chat_anthropic(
    model: str,
    api_key: Optional[str],
    system: str,
    messages_anthropic: List[Dict[str, Any]],
    tools_anthropic: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """One round of Anthropic Messages API. Returns dict with content_blocks (text + tool_use)."""
    import urllib.request
    url = "https://api.anthropic.com/v1/messages"
    body: Dict[str, Any] = {
        "model": model,
        "max_tokens": 4096,
        "system": system,
        "messages": messages_anthropic,
    }
    if tools_anthropic:
        body["tools"] = tools_anthropic
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key or "",
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
    content_blocks = raw.get("content") or []
    return {"content_blocks": content_blocks, "raw": raw}


def _openai_messages_to_anthropic(messages: List[Dict[str, Any]]) -> tuple[str, List[Dict[str, Any]]]:
    """Convert OpenAI-format messages to (system, anthropic_messages)."""
    system_parts = []
    anthropic_messages: List[Dict[str, Any]] = []
    for m in messages:
        role = (m.get("role") or "").strip()
        content = m.get("content")
        if role == "system":
            system_parts.append(content if isinstance(content, str) else json.dumps(content))
            continue
        if role == "user":
            anthropic_messages.append({"role": "user", "content": content if isinstance(content, str) else [{"type": "text", "text": json.dumps(content)}]})
            continue
        if role == "assistant":
            text_content = (content or "").strip() if isinstance(content, str) else ""
            tool_calls = m.get("tool_calls") or []
            blocks = []
            if text_content:
                blocks.append({"type": "text", "text": text_content})
            for tc in tool_calls:
                fn = tc.get("function") or {}
                blocks.append({
                    "type": "tool_use",
                    "id": tc.get("id") or "",
                    "name": fn.get("name") or "",
                    "input": json.loads(fn.get("arguments") or "{}"),
                })
            anthropic_messages.append({"role": "assistant", "content": blocks if blocks else [{"type": "text", "text": ""}]})
            continue
        if role == "tool":
            tid = m.get("tool_call_id") or ""
            anthropic_messages.append({
                "role": "user",
                "content": [{"type": "tool_result", "tool_use_id": tid, "content": (m.get("content") or "")}],
            })
    return "\n\n".join(system_parts) or "", anthropic_messages


def _llm_chat(
    api_base: str,
    model: str,
    api_key: Optional[str],
    messages: List[Dict[str, Any]],
    tools: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """One round of chat (OpenAI-compatible). Uses urllib to avoid extra deps."""
    import urllib.request

    url = api_base.rstrip("/") + "/chat/completions"
    body: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "max_tokens": 4096,
        "temperature": 0.3,
    }
    if tools:
        body["tools"] = tools
        body["tool_choice"] = "auto"
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}" if api_key else "",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


async def _run_assistant_turn_async(user_text: str) -> str:
    """One user turn: gate -> LLM loop with tool execution. Uses one MCP pool per turn."""
    passed_text, blocked, block_message = _gate_process(user_text)
    if blocked:
        return block_message

    provider = (os.environ.get("PI_LLM_PROVIDER") or "").strip().lower() or "openai"
    api_base = os.environ.get("PI_LLM_API_BASE", "").strip()
    model = os.environ.get("PI_LLM_MODEL", "llama3.2").strip()
    api_key = _get_api_key()
    if provider == "anthropic":
        if not model:
            model = "claude-sonnet-4-5"
        if not api_key:
            return "Set PI_LLM_API_KEY or PI_LLM_API_KEY_FILE for Claude (Anthropic), or use key-holder: PI_LLM_API_BASE=http://127.0.0.1:8766/v1 and PI_LLM_PROVIDER=openai."
    else:
        if not api_base:
            return "Set PI_LLM_API_BASE (e.g. http://localhost:11434/v1 for Ollama, or http://127.0.0.1:8766/v1 for key-holder) and PI_LLM_MODEL."
    # When using key-holder, api_key may be empty; key-holder injects it

    from assistant.mcp_dynamic import MCPDynamicPool
    pool = MCPDynamicPool()
    await pool.connect_all()
    tools = _all_tool_definitions_static() + pool.get_openai_tools()
    all_tool_names: Set[str] = set(ALLOWED_TOOL_NAMES) | set(pool.get_all_tool_names())

    try:
        from assistant.preferences_store import read_preferences, format_preferences_for_prompt
        prefs_str = format_preferences_for_prompt(read_preferences())
    except Exception:
        prefs_str = "No preferences loaded."
    system_content = (
        "You are a general-purpose assistant (Pi-style): concise, friendly, and tool-capable. "
        "Use the provided tools to read/write files, search code, run commands, gather information from connected MCP services, and remember user preferences. "
        "When the user states a preference (e.g. theme, language, style), call save_preference to persist it. "
        "Current saved preferences (use them to personalize): " + prefs_str + " "
        "Answer briefly; use multiple tool calls if needed, then summarize for the user."
    )
    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": passed_text},
    ]

    tools_anthropic = _openai_tools_to_anthropic(tools) if provider == "anthropic" else None

    try:
        max_rounds = 15
        for _ in range(max_rounds):
            if provider == "anthropic":
                system_str, anthropic_messages = _openai_messages_to_anthropic(messages)
                try:
                    resp = _llm_chat_anthropic(model, api_key, system_str, anthropic_messages, tools_anthropic)
                except Exception as e:
                    return f"LLM request failed: {e}"
                blocks = resp.get("content_blocks") or []
                text_parts = []
                tool_uses = []
                for b in blocks:
                    if b.get("type") == "text":
                        text_parts.append((b.get("text") or "").strip())
                    elif b.get("type") == "tool_use":
                        tool_uses.append(b)
                if not tool_uses:
                    await pool.close_all()
                    return " ".join(text_parts).strip() or "(No text in response)"
                msg = {
                    "role": "assistant",
                    "content": " ".join(text_parts).strip(),
                    "tool_calls": [
                        {"id": u.get("id"), "function": {"name": u.get("name"), "arguments": json.dumps(u.get("input") or {})}}
                        for u in tool_uses
                    ],
                }
            else:
                try:
                    resp = _llm_chat(api_base, model, api_key, messages, tools=tools)
                except Exception as e:
                    return f"LLM request failed: {e}"
                choices = resp.get("choices") or []
                if not choices:
                    return "No response from model."
                msg = choices[0].get("message") or {}
                content = (msg.get("content") or "").strip()
                tool_calls = msg.get("tool_calls")
                if not tool_calls:
                    return content or "(No text in response)"

            messages.append(msg)
            tool_calls = msg.get("tool_calls") or []
            for tc in tool_calls:
                tid = tc.get("id") or ""
                name = (tc.get("function") or {}).get("name") or ""
                args_raw = (tc.get("function") or {}).get("arguments")
                if isinstance(args_raw, dict):
                    args = args_raw
                else:
                    try:
                        args = json.loads(args_raw or "{}")
                    except json.JSONDecodeError:
                        args = {}
                if name not in all_tool_names:
                    result = f"Tool not allowed: {name}"
                elif name in pool.get_all_tool_names():
                    try:
                        result = await pool.call_tool(name, args)
                    except Exception as e:
                        result = f"Error: {e}"
                else:
                    result = _run_tool(name, args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tid,
                    "content": result,
                })
        return "(Max tool rounds reached; try a simpler request.)"
    finally:
        await pool.close_all()


def _run_assistant_turn(user_text: str) -> str:
    """Sync entry: run one turn in a dedicated event loop (so MCP connections stay valid for the turn)."""
    return asyncio.run(_run_assistant_turn_async(user_text))


def _run_http_server(port: int) -> None:
    """Run a simple HTTP server that accepts POST /message with JSON { \"message\": \"...\" } and returns { \"reply\": \"...\" }."""

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            if self.path != "/message" and self.path != "/message/":
                self.send_response(404)
                self.end_headers()
                return
            length = int(self.headers.get("Content-Length", 0))
            try:
                body = self.rfile.read(length).decode("utf-8")
                data = json.loads(body)
                msg = data.get("message", "").strip()
            except (ValueError, json.JSONDecodeError):
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid JSON or missing message"}).encode("utf-8"))
                return
            reply = _run_assistant_turn(msg)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"reply": reply}).encode("utf-8"))

        def log_message(self, format, *args):
            pass

    server = HTTPServer(("", port), Handler)
    server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description="General-purpose assistant (gate + LLM + tools + MCP + preferences)")
    parser.add_argument("--daemon", action="store_true", help="Run continuously with HTTP endpoint for messages")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PI_HTTP_PORT", "8765")), help="HTTP port when --daemon")
    args = parser.parse_args()

    print("General-purpose assistant. Config: PI_LLM_*, PI_PREFERENCES_PATH, PI_MCP_CONFIG, PI_HTTP_PORT")
    print("Project root:", _project_root())
    if args.daemon:
        port = args.port
        print(f"HTTP server listening on port {port} (POST /message with JSON {{\"message\": \"...\"}})")
        _run_http_server(port)
        return
    print("Type a message and press Enter. Ctrl+D or 'exit' to quit.")
    while True:
        try:
            line = input("\n> ").strip()
        except EOFError:
            break
        if not line:
            continue
        if line.lower() in ("exit", "quit"):
            break
        reply = _run_assistant_turn(line)
        print(reply)
    print("Bye.")


if __name__ == "__main__":
    main()
