"""
HTTP MCP client for a single remote server (e.g. Atlassian MCP).
Uses POST with JSON-RPC body. Auth via env: ATLASSIAN_MCP_URL, ATLASSIAN_MCP_BEARER.
No secrets in code.
"""
from __future__ import annotations

import json
import os
import ssl
import urllib.error
import urllib.request
from typing import Any


def _ssl_context():
    if os.environ.get("NANO_POC_SSL_VERIFY", "1").strip().lower() in ("0", "false", "no"):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx
    return None


def _env_url() -> str:
    v = os.environ.get("ATLASSIAN_MCP_URL", "").strip()
    if not v:
        raise RuntimeError("Set ATLASSIAN_MCP_URL (e.g. https://.../mcp)")
    return v.rstrip("/")


def _env_bearer() -> str:
    v = os.environ.get("ATLASSIAN_MCP_BEARER", "").strip()
    if not v:
        raise RuntimeError("Set ATLASSIAN_MCP_BEARER for Authorization header")
    return v


def _post(msg: dict, session_id: str | None = None) -> dict:
    url = _env_url()
    # Some servers use /mcp as base; others expect path for messages. Try base URL first.
    req = urllib.request.Request(
        url,
        data=json.dumps(msg).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Authorization": f"Bearer {_env_bearer()}",
        },
        method="POST",
    )
    if session_id:
        req.add_header("mcp-session-id", session_id)
    ctx = _ssl_context()
    kwargs = {"timeout": 60}
    if ctx is not None:
        kwargs["context"] = ctx
    with urllib.request.urlopen(req, **kwargs) as resp:
        out = resp.read().decode("utf-8")
    # Handle SSE-style response (data: {...}\n\n or multiple data: lines)
    for line in out.split("\n"):
        line = line.strip()
        if line.startswith("data:"):
            payload = line[5:].strip()
            if payload and payload != "[DONE]":
                return json.loads(payload)
    # Fallback: try parse whole body as JSON
    out = out.strip()
    if out:
        return json.loads(out)
    raise ValueError("Empty or non-JSON response")


def initialize() -> tuple[dict, str | None]:
    """Send initialize; return (result, session_id if present)."""
    msg = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "nano-atlassian-mcp", "version": "0.1.0"},
        },
    }
    resp = _post(msg)
    session_id = None
    if "result" in resp:
        session_id = resp["result"].get("sessionId") or resp["result"].get("serverInfo", {}).get("sessionId")
    return resp.get("result", {}), session_id


def list_tools(session_id: str | None = None) -> list[dict]:
    """Return tools from tools/list."""
    msg = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    resp = _post(msg, session_id)
    if "error" in resp:
        raise RuntimeError(resp["error"].get("message", str(resp["error"])))
    result = resp.get("result", {})
    tools = result.get("tools", [])
    return tools


def call_tool(name: str, arguments: dict, session_id: str | None = None) -> tuple[str, bool]:
    """Call tools/call; return (text_content, is_error)."""
    msg = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": name, "arguments": arguments},
    }
    resp = _post(msg, session_id)
    if "error" in resp:
        return resp["error"].get("message", str(resp["error"])), True
    result = resp.get("result", {})
    content = result.get("content", [])
    is_error = result.get("isError", False)
    text_parts = []
    for part in content:
        if isinstance(part, dict) and part.get("type") == "text":
            text_parts.append(part.get("text", ""))
    return "\n".join(text_parts) or "(empty)", is_error


def get_tools_and_call(intent_tool_name: str, arguments: dict) -> tuple[str, bool]:
    """
    One-shot: initialize (with optional session), then call tool.
    Use when you already know tool name + args (e.g. from nano model).
    """
    result, session_id = initialize()
    return call_tool(intent_tool_name, arguments, session_id)
