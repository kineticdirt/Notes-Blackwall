#!/usr/bin/env python3
"""
MCP → Tool calls → Contents: connect to Atlassian MCP from .mcp.json, run a discovery
sequence of tool calls, save (tool, arguments, content) to JSONL for unsupervised
training of the nano model.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MCP_JSON = REPO_ROOT / ".mcp.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))


def load_mcp_config(path: Path) -> tuple[str, str]:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    for name, cfg in (data.get("mcpServers") or {}).items():
        url = (cfg.get("url") or "").strip()
        if not url:
            continue
        auth = (cfg.get("headers") or {}).get("Authorization") or (cfg.get("headers") or {}).get("authorization") or ""
        auth = auth.strip()
        if auth.lower().startswith("bearer "):
            bearer = auth[7:].strip()
        else:
            bearer = auth
        if bearer:
            return url.rstrip("/"), bearer
    raise RuntimeError(f"No MCP server with url + Authorization in {path}")


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Collect MCP tool-call contents for training.")
    parser.add_argument("--out", type=Path, default=Path(__file__).parent / "mcp_tool_calls.jsonl", help="Output JSONL")
    parser.add_argument("--mcp-json", type=Path, default=MCP_JSON, help="Path to .mcp.json")
    parser.add_argument("--max-content-chars", type=int, default=50_000, help="Truncate each response to this many chars")
    parser.add_argument("--quick", action="store_true", help="Only getAccessibleAtlassianResources + atlassianUserInfo (no cloudId calls)")
    args = parser.parse_args()

    if not args.mcp_json.exists():
        print(f"Missing {args.mcp_json}", file=sys.stderr)
        sys.exit(1)

    url, bearer = load_mcp_config(args.mcp_json)
    os.environ["ATLASSIAN_MCP_URL"] = url
    os.environ["ATLASSIAN_MCP_BEARER"] = bearer

    from atlassian_http_mcp import call_tool, initialize, list_tools

    print("Connecting to MCP...", flush=True)
    _result, session_id = initialize()
    tools = list_tools(session_id)
    print(f"Tools: {len(tools)}", flush=True)

    collected = []
    cloud_id = None

    # 1) getAccessibleAtlassianResources (no args) → get cloudId
    text, is_error = call_tool("getAccessibleAtlassianResources", {}, session_id)
    content = text[: args.max_content_chars] if text else ""
    collected.append({"tool": "getAccessibleAtlassianResources", "arguments": {}, "content": content, "is_error": is_error})
    if not is_error and text:
        try:
            arr = json.loads(text)
            if isinstance(arr, list) and len(arr) > 0 and isinstance(arr[0], dict) and arr[0].get("id"):
                cloud_id = arr[0]["id"]
                print(f"cloudId: {cloud_id}", flush=True)
        except json.JSONDecodeError:
            pass

    if not args.quick:
        # 2) getConfluenceSpaces(cloudId) if we have cloudId
        if cloud_id:
            text, is_error = call_tool("getConfluenceSpaces", {"cloudId": cloud_id}, session_id)
            content = text[: args.max_content_chars] if text else ""
            collected.append({"tool": "getConfluenceSpaces", "arguments": {"cloudId": cloud_id}, "content": content, "is_error": is_error})

        # 3) searchJiraIssuesUsingJql(cloudId, jql) — simple query
        if cloud_id:
            text, is_error = call_tool(
                "searchJiraIssuesUsingJql",
                {"cloudId": cloud_id, "jql": "order by created DESC", "maxResults": 10},
                session_id,
            )
            content = text[: args.max_content_chars] if text else ""
            collected.append({
                "tool": "searchJiraIssuesUsingJql",
                "arguments": {"cloudId": cloud_id, "jql": "order by created DESC", "maxResults": 10},
                "content": content,
                "is_error": is_error,
            })

    # 4) atlassianUserInfo (no args) if available
    names = [t.get("name") for t in tools if t.get("name")]
    if "atlassianUserInfo" in names:
        text, is_error = call_tool("atlassianUserInfo", {}, session_id)
        content = text[: args.max_content_chars] if text else ""
        collected.append({"tool": "atlassianUserInfo", "arguments": {}, "content": content, "is_error": is_error})

    if not args.quick:
        # 5) search (Rovo) with simple query if available
        if "search" in names and cloud_id:
            text, is_error = call_tool("search", {"query": "recent", "limit": 5}, session_id)
            content = text[: args.max_content_chars] if text else ""
            collected.append({"tool": "search", "arguments": {"query": "recent", "limit": 5}, "content": content, "is_error": is_error})

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        for row in collected:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"Wrote {len(collected)} tool-call records to {args.out}", flush=True)


if __name__ == "__main__":
    main()
