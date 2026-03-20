#!/usr/bin/env python3
"""
POC: Read MCP server URL and Bearer from .mcp.json, set env, run nano primary + MCP fallback.
Uses first mcpServer entry that has both "url" and "headers.Authorization".
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MCP_JSON = REPO_ROOT / ".mcp.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))


def load_mcp_config(path: Path) -> tuple[str, str]:
    """Return (url, bearer) from first server with url and Authorization header."""
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    servers = data.get("mcpServers") or {}
    for name, cfg in servers.items():
        url = (cfg.get("url") or "").strip()
        if not url:
            continue
        headers = cfg.get("headers") or {}
        auth = (headers.get("Authorization") or headers.get("authorization") or "").strip()
        if not auth:
            continue
        if auth.lower().startswith("bearer "):
            bearer = auth[7:].strip()
        else:
            bearer = auth
        if bearer:
            return url.rstrip("/"), bearer
    raise RuntimeError(f"No MCP server with url + Authorization in {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run nano POC using .mcp.json for URL and Bearer.")
    parser.add_argument("intent", nargs="*", help="User intent, e.g. 'what resources can I access?'")
    parser.add_argument("--smol", action="store_true", help="Use SmolLM3-3B when keyword has no match.")
    parser.add_argument("--list-tools-only", action="store_true", help="Only list tools and exit.")
    parser.add_argument("--mcp-json", type=Path, default=MCP_JSON, help="Path to .mcp.json")
    args = parser.parse_args()

    if not args.mcp_json.exists():
        print(f"Missing {args.mcp_json}", file=sys.stderr)
        sys.exit(1)

    url, bearer = load_mcp_config(args.mcp_json)
    os.environ["ATLASSIAN_MCP_URL"] = url
    os.environ["ATLASSIAN_MCP_BEARER"] = bearer
    print(f"Using MCP URL from config (Bearer set)", flush=True)

    # Run nano primary + MCP fallback (same as nano_primary_mcp_fallback.main)
    from atlassian_http_mcp import call_tool, initialize, list_tools

    FALLBACK_TOOL = "getAccessibleAtlassianResources"
    FALLBACK_ARGS: dict = {}

    def _keyword_tool(intent: str, tools: list[dict]) -> tuple[str | None, dict]:
        intent_lower = intent.lower().strip()
        names = [t.get("name") for t in tools if t.get("name")]
        if re.search(r"resource|accessible|cloud\s*id|what can i", intent_lower) and "getAccessibleAtlassianResources" in names:
            return "getAccessibleAtlassianResources", {}
        if re.search(r"jira\s+issue|get\s+issue", intent_lower):
            m = re.search(r"([A-Za-z]+-[0-9]+)", intent)
            if m and "getJiraIssue" in names:
                return "getJiraIssue", {"cloudId": "<need cloudId>", "issueIdOrKey": m.group(1)}
        if re.search(r"search\s+jira|jql", intent_lower) and "searchJiraIssuesUsingJql" in names:
            return "searchJiraIssuesUsingJql", {"cloudId": "<need cloudId>", "jql": "order by created DESC"}
        if re.search(r"confluence\s+space|list\s+spaces", intent_lower) and "getConfluenceSpaces" in names:
            return "getConfluenceSpaces", {}
        if "getAccessibleAtlassianResources" in names:
            return "getAccessibleAtlassianResources", {}
        return None, {}

    def _fallback_via_mcp(tools: list[dict], session_id: str | None) -> tuple[str, bool]:
        names = [t.get("name") for t in tools if t.get("name")]
        if FALLBACK_TOOL in names:
            return call_tool(FALLBACK_TOOL, FALLBACK_ARGS, session_id)
        return "No fallback tool.", True

    try:
        _result, session_id = initialize()
        tools = list_tools(session_id)
    except Exception as e:
        print(f"MCP init failed: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Nano primary / MCP fallback — {len(tools)} tools", flush=True)

    if args.list_tools_only:
        for t in tools[:25]:
            print(f"  - {t.get('name')}: {(t.get('description') or '')[:70]}...")
        return

    intent = " ".join(args.intent).strip()
    if not intent:
        print("Provide intent, e.g. 'what resources can I access?'", file=sys.stderr)
        sys.exit(1)

    tool_name, arguments = _keyword_tool(intent, tools)
    if tool_name is None and args.smol:
        try:
            from smol_nano import intent_to_tool as smol_intent_to_tool
            tool_name, arguments = smol_intent_to_tool(intent, tools)
        except RuntimeError as e:
            print(f"SmolLM3: {e}", file=sys.stderr)

    used_fallback = False
    if tool_name is None:
        print("Nano could not map intent; using MCP fallback.", flush=True)
        used_fallback = True
        t0 = time.perf_counter()
        text, is_error = _fallback_via_mcp(tools, session_id)
        print(f"Fallback result ({int((time.perf_counter()-t0)*1000)} ms)", flush=True)
    else:
        cloud_id = os.environ.get("ATLASSIAN_CLOUD_ID", "").strip()
        if cloud_id and arguments.get("cloudId") == "<need cloudId>":
            arguments["cloudId"] = cloud_id
        print(f"Nano → primary (MCP): {tool_name} {arguments}", flush=True)
        t0 = time.perf_counter()
        try:
            text, is_error = call_tool(tool_name, arguments, session_id)
        except Exception as e:
            print(f"Primary failed: {e}; fallback.", flush=True)
            used_fallback = True
            text, is_error = _fallback_via_mcp(tools, session_id)
        print(f"Primary result ({int((time.perf_counter()-t0)*1000)} ms)", flush=True)

    if used_fallback:
        print("(fallback: MCP)", flush=True)
    print(text[:6000] + ("..." if len(text) > 6000 else ""), flush=True)


if __name__ == "__main__":
    main()
