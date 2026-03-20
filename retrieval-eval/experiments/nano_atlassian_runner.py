#!/usr/bin/env python3
"""
Nano path over Atlassian MCP (HTTP): intent → SmolLM3 or keyword → MCP tools/call.
Context is delivered by the MCP server; no frontier LLM in the loop.

Set in env (no secrets in code):
  ATLASSIAN_MCP_URL     e.g. https://ztaib-qj3ty3na-e4l2dawa5a-uc.a.run.app/mcp
  ATLASSIAN_MCP_BEARER  Bearer token for Authorization header

Usage:
  export ATLASSIAN_MCP_URL=... ATLASSIAN_MCP_BEARER=...
  python3 nano_atlassian_runner.py "what Atlassian resources can I access?"
  python3 nano_atlassian_runner.py "get Jira issue PROJ-123" --smol
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path

# Add parent so we can import experiments
sys.path.insert(0, str(Path(__file__).resolve().parent))

from atlassian_http_mcp import call_tool, initialize, list_tools


def _keyword_tool(intent: str, tools: list[dict]) -> tuple[str | None, dict]:
    """Simple keyword → tool for a few common Atlassian actions."""
    intent_lower = intent.lower().strip()
    names = [t.get("name") for t in tools if t.get("name")]

    if re.search(r"resource|accessible|cloud\s*id|what can i", intent_lower):
        if "getAccessibleAtlassianResources" in names:
            return "getAccessibleAtlassianResources", {}

    if re.search(r"jira\s+issue|get\s+issue|issue\s+([A-Za-z]+-[0-9]+)", intent_lower):
        m = re.search(r"([A-Za-z]+-[0-9]+)", intent)
        key = m.group(1) if m else None
        if "getJiraIssue" in names and key:
            return "getJiraIssue", {"cloudId": "<need cloudId>", "issueIdOrKey": key}

    if re.search(r"search\s+jira|jql|jira\s+search", intent_lower):
        if "searchJiraIssuesUsingJql" in names:
            return "searchJiraIssuesUsingJql", {"cloudId": "<need cloudId>", "jql": "order by created DESC"}

    if re.search(r"confluence\s+space|list\s+spaces", intent_lower):
        if "getConfluenceSpaces" in names:
            return "getConfluenceSpaces", {}

    # Default: list accessible resources (safe, no project-specific args)
    if "getAccessibleAtlassianResources" in names:
        return "getAccessibleAtlassianResources", {}
    return None, {}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Nano over Atlassian MCP: intent → tool call (HTTP, Bearer auth)."
    )
    parser.add_argument("intent", nargs="+", help="User intent, e.g. 'what resources can I access?'")
    parser.add_argument(
        "--smol",
        action="store_true",
        help="Use SmolLM3-3B for intent→tool (requires transformers, torch).",
    )
    parser.add_argument(
        "--qwen4b",
        action="store_true",
        help="Use Qwen 4B instruct (JIULANG/unsloth-Qwen3.5-4B-Instruct-CitationMarker-LM) for intent→tool.",
    )
    parser.add_argument("--list-tools-only", action="store_true", help="Only fetch and print tools/list, then exit.")
    args = parser.parse_args()
    intent = " ".join(args.intent).strip()

    if not os.environ.get("ATLASSIAN_MCP_URL") or not os.environ.get("ATLASSIAN_MCP_BEARER"):
        print("Set ATLASSIAN_MCP_URL and ATLASSIAN_MCP_BEARER (no secrets in code).", file=sys.stderr)
        sys.exit(1)

    try:
        result, session_id = initialize()
    except Exception as e:
        print(f"Initialize failed: {e}", file=sys.stderr)
        sys.exit(1)

    tools = list_tools(session_id)
    print(f"Atlassian MCP: {len(tools)} tools", flush=True)

    if args.list_tools_only:
        for t in tools[:20]:
            print(f"  - {t.get('name')}: { (t.get('description') or '')[:80]}...")
        return

    if not intent:
        print("Provide intent, e.g. 'what Atlassian resources can I access?'", file=sys.stderr)
        sys.exit(1)

    if args.qwen4b:
        try:
            from qwen4b_router import intent_to_tool as qwen4b_intent_to_tool
            tool_name, arguments = qwen4b_intent_to_tool(intent, tools)
        except RuntimeError as e:
            print(f"Qwen 4B not available: {e}", file=sys.stderr)
            tool_name, arguments = _keyword_tool(intent, tools)
    elif args.smol:
        try:
            from smol_nano import intent_to_tool as smol_intent_to_tool
            tool_name, arguments = smol_intent_to_tool(intent, tools)
        except RuntimeError as e:
            print(f"SmolLM3 not available: {e}", file=sys.stderr)
            tool_name, arguments = _keyword_tool(intent, tools)
    else:
        tool_name, arguments = _keyword_tool(intent, tools)

    if not tool_name:
        print("Could not map intent to a tool. Try --smol or phrases like 'what resources can I access?'", file=sys.stderr)
        sys.exit(1)

    # Replace placeholders if we have a cached cloudId (e.g. from prior run)
    cloud_id = os.environ.get("ATLASSIAN_CLOUD_ID", "").strip()
    if cloud_id and arguments.get("cloudId") == "<need cloudId>":
        arguments["cloudId"] = cloud_id

    print(f"Nano → tool: {tool_name} {arguments}", flush=True)
    t0 = time.perf_counter()
    try:
        text, is_error = call_tool(tool_name, arguments, session_id)
    except Exception as e:
        print(f"MCP call failed: {e}", flush=True)
        sys.exit(1)
    elapsed_ms = int((time.perf_counter() - t0) * 1000)
    print(f"MCP result ({elapsed_ms} ms):", flush=True)
    if is_error:
        print(f"(error) {text}", flush=True)
    else:
        print(text[:6000] + ("..." if len(text) > 6000 else ""), flush=True)


if __name__ == "__main__":
    main()
