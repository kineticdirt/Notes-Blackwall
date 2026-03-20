#!/usr/bin/env python3
"""
Build supervised JSONL for Atlassian-only intent → tool + arguments (pure API routing).
Use for training the nano to be non-hallucinatory: target is **only JSON**, no prose.

Optional: --refresh-tools pulls live tool names from MCP (.mcp.json) to keep schema aligned.
Output: experiments/atlassian_intent_router.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_DEFAULT = ROOT / "atlassian_intent_router.jsonl"

# Fixed training pairs: (intent variants..., tool, arguments). Arguments use placeholder cloudId where needed.
GOLDEN: list[tuple[list[str], str, dict]] = [
    (
        [
            "What Atlassian resources can I access?",
            "List my Atlassian sites and cloud IDs.",
            "Which Jira or Confluence instances do I have?",
            "Show accessible Atlassian resources.",
        ],
        "getAccessibleAtlassianResources",
        {},
    ),
    (
        [
            "List Confluence spaces.",
            "Get all spaces in Confluence.",
            "Show Confluence spaces I can see.",
            "What spaces exist in Confluence?",
        ],
        "getConfluenceSpaces",
        {"cloudId": "<cloudId>"},
    ),
    (
        [
            "Search Jira for recent issues.",
            "Find latest Jira issues.",
            "JQL search for issues ordered by created.",
            "Show me recent tickets in Jira.",
        ],
        "searchJiraIssuesUsingJql",
        {"cloudId": "<cloudId>", "jql": "order by created DESC"},
    ),
    (
        [
            "Get Jira issue PROJ-123.",
            "Fetch ticket PROJ-123 from Jira.",
            "Show me issue PROJ-123.",
        ],
        "getJiraIssue",
        {"cloudId": "<cloudId>", "issueIdOrKey": "PROJ-123"},
    ),
    (
        [
            "Get Jira issue AF-42.",
            "Open AF-42 in Jira.",
        ],
        "getJiraIssue",
        {"cloudId": "<cloudId>", "issueIdOrKey": "AF-42"},
    ),
    (
        [
            "Who am I in Atlassian?",
            "Show my Atlassian user profile.",
        ],
        "atlassianUserInfo",
        {},
    ),
    (
        [
            "Search Atlassian for docs about OAuth.",
            "Find pages mentioning OAuth across Atlassian.",
        ],
        "search",
        {"query": "OAuth", "limit": 10},
    ),
]


def completion_json(tool: str, arguments: dict) -> str:
    return json.dumps({"tool": tool, "arguments": arguments}, separators=(",", ":"))


def tools_header(names: list[str]) -> str:
    """Compact tool list for prompt (reduces tokens; router learns names)."""
    return "Available tools: " + ", ".join(sorted(names)) + "."


def build_prompt(intent: str, tool_names: list[str]) -> str:
    sys_p = (
        "You are an Atlassian MCP router. Reply with ONLY a JSON object with keys "
        '"tool" (exact tool name) and "arguments" (object). No markdown, no explanation.\n'
    )
    return sys_p + tools_header(tool_names) + f'\nUser request: {intent}\nJSON:'


def default_tool_names() -> list[str]:
    return [
        "getAccessibleAtlassianResources",
        "getConfluenceSpaces",
        "searchJiraIssuesUsingJql",
        "getJiraIssue",
        "atlassianUserInfo",
        "search",
    ]


def fetch_tool_names_from_mcp() -> list[str]:
    REPO_ROOT = ROOT.parent.parent
    mcp_json = REPO_ROOT / ".mcp.json"
    if not mcp_json.exists():
        return default_tool_names()
    raw = mcp_json.read_text(encoding="utf-8")
    cfg = json.loads(raw)
    for _, c in (cfg.get("mcpServers") or {}).items():
        url = (c.get("url") or "").strip()
        auth = (c.get("headers") or {}).get("Authorization", "")
        if url and auth:
            os.environ["ATLASSIAN_MCP_URL"] = url.rstrip("/")
            os.environ["ATLASSIAN_MCP_BEARER"] = (
                auth[7:].strip() if auth.lower().startswith("bearer ") else auth.strip()
            )
            break
    else:
        return default_tool_names()
    from atlassian_http_mcp import initialize, list_tools

    _, sid = initialize()
    tools = list_tools(sid)
    return [t["name"] for t in tools if t.get("name")]


def main() -> None:
    ap = argparse.ArgumentParser(description="Build Atlassian intent→tool supervised JSONL.")
    ap.add_argument("--out", type=Path, default=OUT_DEFAULT)
    ap.add_argument("--refresh-tools", action="store_true", help="Fetch tool names from live MCP")
    opts = ap.parse_args()

    names = fetch_tool_names_from_mcp() if opts.refresh_tools else default_tool_names()
    rows = []
    for intents, tool, tool_args in GOLDEN:
        if opts.refresh_tools and tool not in names:
            continue
        comp = completion_json(tool, tool_args)
        for intent in intents:
            rows.append(
                {
                    "instruction": build_prompt(intent, names),
                    "completion": comp,
                    "tool": tool,
                }
            )

    opts.out.parent.mkdir(parents=True, exist_ok=True)
    with open(opts.out, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Wrote {len(rows)} supervised rows to {opts.out}", flush=True)


if __name__ == "__main__":
    main()
