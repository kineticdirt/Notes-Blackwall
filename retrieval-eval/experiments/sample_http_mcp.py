"""
HTTP MCP client for sample API server (no auth).
Set SAMPLE_MCP_URL e.g. http://localhost:8765/mcp
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


def _url() -> str:
    return os.environ.get("SAMPLE_MCP_URL", "http://127.0.0.1:8765/mcp").strip().rstrip("/")


def _post(msg: dict) -> dict:
    req = urllib.request.Request(
        _url(),
        data=json.dumps(msg).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def initialize() -> tuple[dict, str | None]:
    msg = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "sample-mcp-client", "version": "0.1.0"}},
    }
    resp = _post(msg)
    return resp.get("result", {}), None


def list_tools() -> list[dict]:
    msg = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    resp = _post(msg)
    if "error" in resp:
        raise RuntimeError(resp["error"].get("message", str(resp["error"])))
    return resp.get("result", {}).get("tools", [])


def call_tool(name: str, arguments: dict, session_id: str | None = None) -> tuple[str, bool]:
    msg = {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": name, "arguments": arguments}}
    resp = _post(msg)
    if "error" in resp:
        return resp["error"].get("message", str(resp["error"])), True
    result = resp.get("result", {})
    content = result.get("content", [])
    is_error = result.get("isError", False)
    text_parts = [p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text"]
    return "\n".join(text_parts) or "(empty)", is_error
