"""
Key-holder service: holds the API key and proxies LLM requests.
The key never leaves this process; the assistant sends requests without a key and gets only the model response.
Bind to localhost by default (KEYHOLDER_HOST, KEYHOLDER_PORT). Do not expose to the internet.

Run: python -m assistant.key_holder.server
"""

from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add repo root for load_secrets
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Load secrets at startup (key only in this process)
try:
    from assistant.load_secrets import load_secrets
    load_secrets()
except Exception:
    pass

# Keys: never log or return these
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("PI_LLM_API_KEY") or ""
OPENAI_KEY = os.environ.get("OPENAI_API_KEY") or ""


def _openai_tools_to_anthropic(tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for t in tools or []:
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


def _openai_messages_to_anthropic(messages: List[Dict[str, Any]]) -> tuple[str, List[Dict[str, Any]]]:
    system_parts = []
    anthropic_messages: List[Dict[str, Any]] = []
    for m in messages or []:
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
            anthropic_messages.append({
                "role": "user",
                "content": [{"type": "tool_result", "tool_use_id": m.get("tool_call_id") or "", "content": (m.get("content") or "")}],
            })
    return "\n\n".join(system_parts) or "", anthropic_messages


def _anthropic_blocks_to_openai_message(blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
    text_parts = []
    tool_calls = []
    for b in blocks or []:
        if b.get("type") == "text":
            text_parts.append((b.get("text") or "").strip())
        elif b.get("type") == "tool_use":
            tool_calls.append({
                "id": b.get("id") or "",
                "function": {"name": b.get("name") or "", "arguments": json.dumps(b.get("input") or {})},
            })
    return {
        "role": "assistant",
        "content": " ".join(text_parts).strip(),
        "tool_calls": tool_calls if tool_calls else None,
    }


def _call_anthropic(model: str, system: str, messages_anthropic: List[Dict], tools_anthropic: List[Dict]) -> Dict[str, Any]:
    import urllib.request
    if not ANTHROPIC_KEY:
        return {"error": "Key-holder has no ANTHROPIC_API_KEY"}
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
        "https://api.anthropic.com/v1/messages",
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
    blocks = raw.get("content") or []
    msg = _anthropic_blocks_to_openai_message(blocks)
    return {"choices": [{"message": msg, "index": 0}]}


def _call_openai(model: str, messages: List[Dict], tools: Optional[List[Dict]]) -> Dict[str, Any]:
    import urllib.request
    if not OPENAI_KEY:
        return {"error": "Key-holder has no OPENAI_API_KEY"}
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
        "https://api.openai.com/v1/chat/completions",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_KEY}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _handle_chat_completions(body: Dict[str, Any]) -> Dict[str, Any]:
    model = (body.get("model") or "").strip()
    messages = body.get("messages") or []
    tools = body.get("tools")

    if model.lower().startswith("claude-"):
        system_str, anthropic_messages = _openai_messages_to_anthropic(messages)
        tools_anthropic = _openai_tools_to_anthropic(tools) if tools else []
        return _call_anthropic(model, system_str, anthropic_messages, tools_anthropic)
    else:
        return _call_openai(model, messages, tools)


class KeyHolderHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/v1/chat/completions" and not self.path.rstrip("/").endswith("/chat/completions"):
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            raw = self.rfile.read(length).decode("utf-8")
            body = json.loads(raw)
        except (ValueError, json.JSONDecodeError):
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON body"}).encode("utf-8"))
            return
        result = _handle_chat_completions(body)
        if "error" in result:
            self.send_response(502)
        else:
            self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode("utf-8"))

    def log_message(self, format, *args):
        # Do not log request bodies (could contain sensitive data)
        pass


def main():
    host = os.environ.get("KEYHOLDER_HOST", "127.0.0.1")
    port = int(os.environ.get("KEYHOLDER_PORT", "8766"))
    server = HTTPServer((host, port), KeyHolderHandler)
    print(f"Key-holder listening on {host}:{port} (do not expose to internet)", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
