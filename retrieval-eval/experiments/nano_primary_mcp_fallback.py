"""
Nano as primary interface; MCP as fallback.

- Primary: Nano (logic + repeatability, optional SmolLM) → (tool, args) → executor.
  Executor today = MCP (same as before), but conceptually the nano *replaces* MCP
  as the interface; we focus on logic and repeatability.
- Fallback: When nano returns no tool or execution fails → run via MCP with a safe
  default or report so the system still works.

No frontier LLM in the loop. Set ATLASSIAN_MCP_URL, ATLASSIAN_MCP_BEARER in env.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from atlassian_http_mcp import call_tool, initialize, list_tools

# Safe default for fallback (no required args): list accessible resources
FALLBACK_TOOL = "getAccessibleAtlassianResources"
FALLBACK_ARGS: dict = {}


def _keyword_tool(intent: str, tools: list[dict]) -> tuple[str | None, dict]:
    """Deterministic logic first: repeatable intent → (tool, args)."""
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

    if "getAccessibleAtlassianResources" in names:
        return "getAccessibleAtlassianResources", {}
    return None, {}


def _nano_primary(intent: str, tools: list[dict], use_smol: bool) -> tuple[str | None, dict]:
    """Nano as primary: logic (keyword) first, then optional small model. Repeatable where possible."""
    tool_name, arguments = _keyword_tool(intent, tools)
    if tool_name is not None:
        return tool_name, arguments
    if use_smol:
        try:
            from smol_nano import intent_to_tool as smol_intent_to_tool
            tool_name, arguments = smol_intent_to_tool(intent, tools)
            if tool_name:
                return tool_name, arguments
        except RuntimeError:
            pass
    return None, {}


def _executor_mcp(tool_name: str, arguments: dict, session_id: str | None) -> tuple[str, bool]:
    """Primary executor: run (tool, args) via MCP. (Future: direct API adapter as alternative.)"""
    return call_tool(tool_name, arguments, session_id)


def _fallback_via_mcp(tools: list[dict], session_id: str | None) -> tuple[str, bool]:
    """Fallback: use MCP with a safe default when nano could not handle intent or execution failed."""
    names = [t.get("name") for t in tools if t.get("name")]
    if FALLBACK_TOOL in names:
        return call_tool(FALLBACK_TOOL, FALLBACK_ARGS, session_id)
    return "No fallback tool available (MCP list empty or missing getAccessibleAtlassianResources).", True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Nano as primary interface to API; MCP fallback when needed."
    )
    parser.add_argument("intent", nargs="+", help="User intent.")
    parser.add_argument("--smol", action="store_true", help="Use SmolLM3-3B when keyword logic has no match.")
    parser.add_argument("--list-tools-only", action="store_true", help="Print tools and exit.")
    args = parser.parse_args()
    intent = " ".join(args.intent).strip()

    if not os.environ.get("ATLASSIAN_MCP_URL") or not os.environ.get("ATLASSIAN_MCP_BEARER"):
        print("Set ATLASSIAN_MCP_URL and ATLASSIAN_MCP_BEARER.", file=sys.stderr)
        sys.exit(1)

    try:
        _result, session_id = initialize()
        tools = list_tools(session_id)
    except Exception as e:
        print(f"MCP init failed (fallback unavailable): {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Nano primary / MCP fallback — {len(tools)} tools from server", flush=True)

    if args.list_tools_only:
        for t in tools[:20]:
            print(f"  - {t.get('name')}: {(t.get('description') or '')[:80]}...")
        return

    if not intent:
        print("Provide intent.", file=sys.stderr)
        sys.exit(1)

    # Primary: nano (logic + optional smol) → (tool, args)
    tool_name, arguments = _nano_primary(intent, tools, args.smol)
    used_fallback = False

    if tool_name is None:
        print("Nano could not map intent → tool; using MCP fallback (safe default).", flush=True)
        used_fallback = True
        t0 = time.perf_counter()
        text, is_error = _fallback_via_mcp(tools, session_id)
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        print(f"Fallback result ({elapsed_ms} ms)", flush=True)
    else:
        cloud_id = os.environ.get("ATLASSIAN_CLOUD_ID", "").strip()
        if cloud_id and arguments.get("cloudId") == "<need cloudId>":
            arguments["cloudId"] = cloud_id
        print(f"Nano → primary executor (MCP): {tool_name} {arguments}", flush=True)
        t0 = time.perf_counter()
        try:
            text, is_error = _executor_mcp(tool_name, arguments, session_id)
        except Exception as e:
            print(f"Primary execution failed: {e}; using MCP fallback.", flush=True)
            used_fallback = True
            text, is_error = _fallback_via_mcp(tools, session_id)
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        print(f"Primary result ({elapsed_ms} ms)" + (" [then fallback]" if used_fallback else ""), flush=True)

    if used_fallback:
        print("(fallback: MCP)", flush=True)
    if is_error:
        print(f"(error) {text}", flush=True)
    else:
        print(text[:6000] + ("..." if len(text) > 6000 else ""), flush=True)


if __name__ == "__main__":
    main()
