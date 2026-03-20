#!/usr/bin/env python3
"""
Nano-model path over a single MCP server: intent → (tool + args) → MCP call → result.
No frontier LLM in the loop. Tool registry = trained on one server (e.g. agent-context-vault).

Usage:
  export AGENT_CONTEXT_VAULT_ROOT=/path/to/agent-context-vault/vault
  python3 nano_mcp_runner.py "list vault sources"
  python3 nano_mcp_runner.py "read source wf-claude-obsidian-001" [--ollama]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# MCP stdio (Node SDK): newline-delimited JSON, one message per line
def encode_mcp_message(msg: dict) -> bytes:
    return (json.dumps(msg) + "\n").encode("utf-8")


def read_mcp_response(stream) -> dict | None:
    """Read one newline-terminated JSON message from stream (blocking)."""
    buf = b""
    while True:
        chunk = stream.read(1)
        if not chunk:
            return None
        buf += chunk
        if buf.endswith(b"\n"):
            line = buf[:-1].decode("utf-8").rstrip("\r")
            if line:
                return json.loads(line)
            buf = b""


def run_mcp_tool(
    server_cmd: list[str],
    server_env: dict,
    tool_name: str,
    arguments: dict,
    timeout_sec: float = 30.0,
) -> tuple[str, bool]:
    """
    Spawn MCP server, send initialize → initialized → tools/call, return (text, is_error).
    """
    proc = subprocess.Popen(
        server_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, **server_env},
        cwd=Path(__file__).resolve().parent.parent.parent,
    )
    try:
        # Initialize
        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "nano-mcp-runner", "version": "0.1.0"},
            },
        }
        proc.stdin.write(encode_mcp_message(init_req))
        proc.stdin.flush()
        init_resp = read_mcp_response(proc.stdout)
        if not init_resp or "result" not in init_resp:
            err = init_resp.get("error", {}) if init_resp else {}
            return f"Initialize failed: {err}", True

        # Notify initialized
        proc.stdin.write(
            encode_mcp_message({"jsonrpc": "2.0", "method": "notifications/initialized"})
        )
        proc.stdin.flush()

        # tools/call
        call_req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }
        proc.stdin.write(encode_mcp_message(call_req))
        proc.stdin.flush()
        call_resp = read_mcp_response(proc.stdout)
        if not call_resp:
            return "No response from tools/call", True
        if "error" in call_resp:
            return call_resp["error"].get("message", str(call_resp["error"])), True
        result = call_resp.get("result", {})
        content = result.get("content", [])
        is_err = result.get("isError", False)
        text = ""
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                text += part.get("text", "")
        return text or "(empty)", is_err
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
        stderr = proc.stderr.read().decode("utf-8", errors="replace")
        if stderr and os.environ.get("NANO_MCP_DEBUG"):
            sys.stderr.write(stderr)


def load_registry(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("tools", [])


def intent_to_tool_keyword(intent: str, tools: list[dict]) -> tuple[str, dict]:
    """
    Simple keyword mapping: no LLM. Good for testing and as fallback.
    """
    intent_lower = intent.lower().strip()
    # "list sources" / "list vault" -> vault_list_sources
    if re.search(r"list|sources|vault\s*(sources)?", intent_lower):
        for t in tools:
            if t["name"] == "vault_list_sources":
                return t["name"], {}
    # "read source X" / "get source id" -> vault_read_source
    read_match = re.search(r"read\s+source\s+([a-zA-Z0-9_-]+)|source\s+([a-zA-Z0-9_-]+)|source_id[=:\s]+([a-zA-Z0-9_-]+)", intent_lower)
    if read_match:
        source_id = (read_match.group(1) or read_match.group(2) or read_match.group(3) or "").strip()
        if source_id:
            for t in tools:
                if t["name"] == "vault_read_source":
                    return t["name"], {"source_id": source_id}
    # "reload manifest" -> vault_reload_manifest
    if re.search(r"reload|manifest", intent_lower):
        for t in tools:
            if t["name"] == "vault_reload_manifest":
                return t["name"], {}
    # Default: list sources
    for t in tools:
        if t["name"] == "vault_list_sources":
            return t["name"], {}
    return "", {}


def intent_to_tool_ollama(
    intent: str, tools: list[dict], model: str, host: str
) -> tuple[str, dict]:
    """Use Ollama to map intent → tool name + arguments (JSON)."""
    tools_desc = "\n".join(
        f"- {t['name']}: {t['description']}; args: {t.get('inputSchema', {}).get('properties', {})}"
        for t in tools
    )
    prompt = f"""You are a router. Given the user intent, output exactly one JSON object with "tool" (name) and "arguments" (object). Only use these tools:
{tools_desc}

User intent: {intent}

Output only valid JSON, no markdown. Example: {{"tool":"vault_list_sources","arguments":{{}}}}"""
    body = json.dumps(
        {"model": model, "prompt": prompt, "stream": False, "options": {"num_predict": 256}}
    ).encode("utf-8")
    req = urllib.request.Request(
        f"{host.rstrip('/')}/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            out = json.loads(resp.read().decode())
    except urllib.error.URLError:
        return "", {}
    raw = (out.get("response") or "").strip()
    # Extract JSON (may be wrapped in markdown)
    for start in ("{", "```json"):
        i = raw.find(start)
        if i != -1:
            raw = raw[i:]
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0]
            break
    try:
        obj = json.loads(raw)
        name = obj.get("tool") or obj.get("name")
        args = obj.get("arguments") or obj.get("args") or {}
        if name and any(t["name"] == name for t in tools):
            return name, args
    except json.JSONDecodeError:
        pass
    return "", {}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Nano path: intent → single MCP server tool call (no frontier LLM)."
    )
    parser.add_argument("intent", nargs="+", help="User intent, e.g. 'list vault sources'.")
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path(__file__).parent / "mcp_vault_tools.json",
        help="Tool registry JSON (trained on this server).",
    )
    parser.add_argument(
        "--ollama",
        action="store_true",
        help="Use Ollama to map intent→tool; else keyword rules.",
    )
    parser.add_argument(
        "--ollama-model",
        default=os.environ.get("OLLAMA_MODEL", "qwen2.5:1.5b"),
        help="Ollama model for intent→tool.",
    )
    parser.add_argument(
        "--ollama-host",
        default="http://127.0.0.1:11434",
        help="Ollama API base.",
    )
    parser.add_argument(
        "--vault-root",
        default=os.environ.get("AGENT_CONTEXT_VAULT_ROOT"),
        help="AGENT_CONTEXT_VAULT_ROOT (vault dir with manifest.json).",
    )
    args = parser.parse_args()
    intent = " ".join(args.intent).strip()
    if not intent:
        print("Provide intent, e.g. 'list vault sources' or 'read source wf-claude-obsidian-001'")
        sys.exit(1)

    repo_root = Path(__file__).resolve().parent.parent.parent
    vault_dir = args.vault_root or str(repo_root / "agent-context-vault" / "vault")
    if not (Path(vault_dir) / "manifest.json").exists():
        print(f"Vault not found: {vault_dir}/manifest.json. Set AGENT_CONTEXT_VAULT_ROOT.", file=sys.stderr)
        sys.exit(1)

    tools = load_registry(args.registry)
    if args.ollama:
        tool_name, arguments = intent_to_tool_ollama(
            intent, tools, args.ollama_model, args.ollama_host
        )
        if not tool_name:
            print("Ollama could not pick a tool; falling back to keyword.", file=sys.stderr)
            tool_name, arguments = intent_to_tool_keyword(intent, tools)
    else:
        tool_name, arguments = intent_to_tool_keyword(intent, tools)

    if not tool_name:
        print("Could not map intent to any tool.", file=sys.stderr)
        sys.exit(1)

    print(f"Nano → tool: {tool_name} {arguments}", flush=True)
    server_cmd = ["node", str(repo_root / "agent-context-vault" / "mcp" / "server.mjs")]
    server_env = {"AGENT_CONTEXT_VAULT_ROOT": vault_dir}

    t0 = time.perf_counter()
    text, is_error = run_mcp_tool(server_cmd, server_env, tool_name, arguments)
    elapsed_ms = int((time.perf_counter() - t0) * 1000)
    print(f"MCP result ({elapsed_ms} ms):", flush=True)
    if is_error:
        print(f"(error) {text}", flush=True)
    else:
        print(text[:4000] + ("..." if len(text) > 4000 else ""), flush=True)


if __name__ == "__main__":
    main()
