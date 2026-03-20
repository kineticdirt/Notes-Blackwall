"""
MCP tool definitions for Defender mitigator cache API (from def-cterm.txt).
Tools call GET http://localhost:9999/__cq/cache/{info|ip-map|policy-map|all}.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

DEFENDER_BASE = os.environ.get("DEFENDER_BASE_URL", "http://localhost:9999").strip().rstrip("/")

TOOLS_SCHEMA = [
    {
        "name": "cacheInfo",
        "description": "Get mitigator cache summary (ip-map, policy-map, fp-map counts, etc.)",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "cacheIpMap",
        "description": "Get mitigator cache IPv4/IPv6 map and policies per IP",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "cachePolicyMap",
        "description": "Get mitigator cache policy map (policies, correlation-ids, match-criteria)",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "cacheAll",
        "description": "Get full mitigator cache dump (all cache data)",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
]

_PATH = {
    "cacheInfo": "/__cq/cache/info",
    "cacheIpMap": "/__cq/cache/ip-map",
    "cachePolicyMap": "/__cq/cache/policy-map",
    "cacheAll": "/__cq/cache/all",
}


def execute_tool(name: str, arguments: dict) -> tuple[str, bool]:
    """GET defender cache endpoint. Returns (text_content, is_error)."""
    path = _PATH.get(name)
    if not path:
        return json.dumps({"error": f"Unknown tool: {name}"}), True
    url = DEFENDER_BASE + path
    try:
        req = urllib.request.Request(url, method="GET", headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8")
            try:
                obj = json.loads(raw)
                return json.dumps(obj, indent=2), False
            except json.JSONDecodeError:
                return raw, False
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else str(e)
        return json.dumps({"error": f"HTTP {e.code}", "body": body[:2000]}), True
    except urllib.error.URLError as e:
        return json.dumps({"error": "Connection failed", "reason": str(e.reason)}), True
    except Exception as e:
        return json.dumps({"error": str(e)}), True
