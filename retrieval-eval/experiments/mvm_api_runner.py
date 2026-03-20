#!/usr/bin/env python3
"""
MvM Phase 3: API/tool-call track — MCP arm (Claude selects tool) vs MicroSearch arm (nano selects tool).
Same Atlassian MCP executor; compare tool_selection_latency_ms, tool_call_latency_ms, tool_correct, args_valid, response_success, cost_usd.

Requires: ATLASSIAN_MCP_URL, ATLASSIAN_MCP_BEARER. Optional: ATLASSIAN_CLOUD_ID for tools that need cloudId.
Run from retrieval-eval/: python3 experiments/mvm_api_runner.py [--limit N] [--nano-type keyword|smol]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from experiments.atlassian_http_mcp import call_tool, initialize, list_tools
from experiments.mvm_api_intents import ApiIntent, get_intents
from experiments.token_cost import token_cost_usd


def _tools_to_text(tools: list[dict]) -> str:
    lines = []
    for t in tools[:40]:
        name = t.get("name", "")
        desc = (t.get("description") or "").strip()
        schema = t.get("inputSchema", t.get("arguments", {}))
        req = schema.get("required", []) if isinstance(schema, dict) else []
        props = schema.get("properties", {}) if isinstance(schema, dict) else {}
        args_desc = ", ".join(f"{k}" + (" (required)" if k in req else "") for k in (list(props.keys())[:10]))
        lines.append(f"- {name}: {desc[:250]}. Args: {args_desc}")
    return "\n".join(lines) if lines else "No tools."


def claude_tool_selection(api_key: str, intent: str, tools: list[dict]) -> tuple[str | None, dict, dict, int]:
    """
    Ask Claude to pick one tool + arguments for the intent. Returns (tool_name, arguments, usage, latency_ms).
    """
    from anthropic import Anthropic

    tools_text = _tools_to_text(tools)
    user = (
        f"Tools available:\n{tools_text}\n\n"
        f"User intent: {intent}\n\n"
        "Output exactly one JSON object with keys \"tool\" (exact tool name from the list) and \"arguments\" (object). "
        "Use only tools listed. For cloudId use a placeholder if you don't know it. No markdown, no explanation.\n"
        "JSON:"
    )
    t0 = time.perf_counter()
    try:
        client = Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=256,
            messages=[{"role": "user", "content": user}],
        )
    except Exception as e:
        return None, {}, {"input_tokens": 0, "output_tokens": 0}, int((time.perf_counter() - t0) * 1000)

    latency_ms = int((time.perf_counter() - t0) * 1000)
    text = (msg.content[0].text if msg.content else "").strip()
    usage = {"input_tokens": 0, "output_tokens": 0}
    if getattr(msg, "usage", None):
        usage["input_tokens"] = getattr(msg.usage, "input_tokens", 0) or 0
        usage["output_tokens"] = getattr(msg.usage, "output_tokens", 0) or 0

    # Parse JSON from response
    for start in ("{", "```json"):
        i = text.find(start)
        if i != -1:
            text = text[i:]
            if text.startswith("```"):
                text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
            break
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text)
        obj = json.loads(m.group(0)) if m else {}
    name = obj.get("tool") or obj.get("name")
    args = obj.get("arguments") or obj.get("args") or {}
    if not name or not isinstance(args, dict):
        return None, {}, usage, latency_ms
    return str(name), args, usage, latency_ms


def nano_tool_selection(intent: str, tools: list[dict], nano_type: str) -> tuple[str | None, dict]:
    """Keyword, SmolLM, or Qwen 4B (text-only) intent → tool + args. nano_type: keyword | smol | qwen4b."""
    if nano_type == "qwen4b":
        try:
            from experiments.qwen4b_router import intent_to_tool
            return intent_to_tool(intent, tools)
        except Exception:
            pass
        nano_type = "keyword"
    if nano_type == "smol":
        try:
            from experiments.smol_nano import intent_to_tool
            return intent_to_tool(intent, tools)
        except Exception:
            pass
    # Keyword fallback
    intent_lower = intent.lower().strip()
    names = [t.get("name") for t in tools if t.get("name")]
    if re.search(r"resource|accessible|cloud\s*id|what can i|list.*atlassian|project", intent_lower):
        if "getAccessibleAtlassianResources" in names:
            return "getAccessibleAtlassianResources", {}
    if re.search(r"jira\s+issue|get\s+issue|fetch\s+issue|issue\s+([A-Za-z]+-[0-9]+)", intent_lower):
        m = re.search(r"([A-Za-z]+-[0-9]+)", intent)
        key = m.group(1) if m else None
        if "getJiraIssue" in names and key:
            return "getJiraIssue", {"cloudId": "<need cloudId>", "issueIdOrKey": key}
    if re.search(r"search\s+jira|jql|jira\s+search|recent\s+issue", intent_lower):
        if "searchJiraIssuesUsingJql" in names:
            return "searchJiraIssuesUsingJql", {"cloudId": "<need cloudId>", "jql": "order by created DESC"}
    if re.search(r"confluence\s+space|list\s+space|space", intent_lower):
        if "getConfluenceSpaces" in names:
            return "getConfluenceSpaces", {}
    if "getAccessibleAtlassianResources" in names:
        return "getAccessibleAtlassianResources", {}
    return None, {}


def run_one_intent_api(
    api_key: str,
    session_id: str | None,
    intent_spec: ApiIntent,
    nano_type: str,  # keyword | smol | qwen4b
) -> tuple[dict, dict]:
    """Run one intent: MCP arm (Claude) and MicroSearch arm (text-only micro commits to tool+args). Same executor. Returns (mcp_row, micro_row)."""
    tools = list_tools(session_id)
    task_id = intent_spec.intent[:60].replace(" ", "_")

    # ---- MCP arm: Claude selects tool ----
    tool_mcp, args_mcp, usage, tool_selection_latency_mcp_ms = claude_tool_selection(
        api_key, intent_spec.intent, tools
    )
    if not tool_mcp:
        mcp_row = {
            "run_id": task_id,
            "arm": "mcp",
            "track": "api",
            "task_id": task_id,
            "intent": intent_spec.intent,
            "tool_selection_latency_ms": tool_selection_latency_mcp_ms,
            "tool_call_latency_ms": None,
            "total_latency_ms": tool_selection_latency_mcp_ms,
            "tool_correct": False,
            "args_valid": False,
            "response_success": False,
            "expected_tool": intent_spec.expected_tool,
            "selected_tool": None,
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
            "cost_usd": round(token_cost_usd(usage.get("input_tokens", 0), usage.get("output_tokens", 0)), 6),
            "error": "Claude did not return a valid tool",
        }
    else:
        cloud_id = os.environ.get("ATLASSIAN_CLOUD_ID", "").strip()
        if cloud_id and args_mcp.get("cloudId") == "<need cloudId>":
            args_mcp["cloudId"] = cloud_id
        t0 = time.perf_counter()
        try:
            text_mcp, is_error_mcp = call_tool(tool_mcp, args_mcp, session_id)
        except Exception as e:
            text_mcp, is_error_mcp = str(e), True
        tool_call_latency_mcp_ms = int((time.perf_counter() - t0) * 1000)
        args_valid_mcp = not (is_error_mcp and ("validation" in text_mcp.lower() or "400" in text_mcp or "invalid" in text_mcp.lower()))
        mcp_row = {
            "run_id": task_id,
            "arm": "mcp",
            "track": "api",
            "task_id": task_id,
            "intent": intent_spec.intent,
            "tool_selection_latency_ms": tool_selection_latency_mcp_ms,
            "tool_call_latency_ms": tool_call_latency_mcp_ms,
            "total_latency_ms": tool_selection_latency_mcp_ms + tool_call_latency_mcp_ms,
            "tool_correct": tool_mcp == intent_spec.expected_tool,
            "args_valid": args_valid_mcp,
            "response_success": not is_error_mcp,
            "expected_tool": intent_spec.expected_tool,
            "selected_tool": tool_mcp,
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
            "cost_usd": round(token_cost_usd(usage.get("input_tokens", 0), usage.get("output_tokens", 0)), 6),
        }

    # ---- MicroSearch arm: text-only micro commits to tool + args (MCP alternative) ----
    t0_nano = time.perf_counter()
    tool_nano, args_nano = nano_tool_selection(intent_spec.intent, tools, nano_type)
    tool_selection_latency_nano_ms = int((time.perf_counter() - t0_nano) * 1000)
    if not tool_nano:
        micro_row = {
            "run_id": task_id,
            "arm": "microsearch",
            "track": "api",
            "task_id": task_id,
            "intent": intent_spec.intent,
            "tool_selection_latency_ms": tool_selection_latency_nano_ms,
            "tool_call_latency_ms": None,
            "total_latency_ms": tool_selection_latency_nano_ms,
            "tool_correct": False,
            "args_valid": False,
            "response_success": False,
            "expected_tool": intent_spec.expected_tool,
            "selected_tool": None,
            "input_tokens": 0,
            "output_tokens": 0,
            "cost_usd": 0.0,
            "nano_type": nano_type,
            "error": "Nano did not map to a tool",
        }
    else:
        if cloud_id := os.environ.get("ATLASSIAN_CLOUD_ID", "").strip():
            if args_nano.get("cloudId") == "<need cloudId>":
                args_nano["cloudId"] = cloud_id
        t0_call = time.perf_counter()
        try:
            text_nano, is_error_nano = call_tool(tool_nano, args_nano, session_id)
        except Exception as e:
            text_nano, is_error_nano = str(e), True
        tool_call_latency_nano_ms = int((time.perf_counter() - t0_call) * 1000)
        args_valid_nano = not (is_error_nano and ("validation" in text_nano.lower() or "400" in text_nano or "invalid" in text_nano.lower()))
        micro_row = {
            "run_id": task_id,
            "arm": "microsearch",
            "track": "api",
            "task_id": task_id,
            "intent": intent_spec.intent,
            "tool_selection_latency_ms": tool_selection_latency_nano_ms,
            "tool_call_latency_ms": tool_call_latency_nano_ms,
            "total_latency_ms": tool_selection_latency_nano_ms + tool_call_latency_nano_ms,
            "tool_correct": tool_nano == intent_spec.expected_tool,
            "args_valid": args_valid_nano,
            "response_success": not is_error_nano,
            "expected_tool": intent_spec.expected_tool,
            "selected_tool": tool_nano,
            "input_tokens": 0,
            "output_tokens": 0,
            "cost_usd": 0.0,
            "nano_type": nano_type,
        }

    return mcp_row, micro_row


def main() -> None:
    parser = argparse.ArgumentParser(description="MvM Phase 3: API track (Claude vs nano tool selection).")
    parser.add_argument("--limit", type=int, default=None, help="Max intents to run")
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--nano-type", choices=["keyword", "smol", "qwen4b"], default="keyword",
                        help="qwen4b = text-only 4B instruct for API command commitment (MCP alternative).")
    args = parser.parse_args()

    if not os.environ.get("ATLASSIAN_MCP_URL") or not os.environ.get("ATLASSIAN_MCP_BEARER"):
        print("Set ATLASSIAN_MCP_URL and ATLASSIAN_MCP_BEARER.", file=sys.stderr)
        sys.exit(1)

    root = _root
    if not (root / ".api-key").exists() and not (root / ".api-key.example").exists():
        print("Claude API key required for MCP arm. Paste in retrieval-eval/.api-key", file=sys.stderr)
        sys.exit(1)
    from config import load_api_key
    api_key = load_api_key()

    try:
        _, session_id = initialize()
    except Exception as e:
        print(f"MCP initialize failed: {e}", file=sys.stderr)
        sys.exit(1)

    intents = get_intents()
    if args.limit:
        intents = intents[: args.limit]

    out_dir = args.output_dir or root / "results" / "mvm"
    out_dir.mkdir(parents=True, exist_ok=True)
    mcp_path = out_dir / "mcp_arm_api.jsonl"
    micro_path = out_dir / "microsearch_arm_api.jsonl"

    print(f"MvM API track: {len(intents)} intents, nano_type={args.nano_type}. Writing to {out_dir}.")
    with open(mcp_path, "a") as fm, open(micro_path, "a") as fn:
        for i, intent_spec in enumerate(intents):
            print(f"  [{i+1}/{len(intents)}] {intent_spec.intent[:50]}...")
            try:
                mcp_row, micro_row = run_one_intent_api(
                    api_key, session_id, intent_spec, args.nano_type,
                )
                fm.write(json.dumps(mcp_row) + "\n")
                fm.flush()
                fn.write(json.dumps(micro_row) + "\n")
                fn.flush()
                print(f"    MCP: tool_ok={mcp_row.get('tool_correct')} resp_ok={mcp_row.get('response_success')} cost=${mcp_row.get('cost_usd', 0):.4f}")
                print(f"    Micro: tool_ok={micro_row.get('tool_correct')} resp_ok={micro_row.get('response_success')}")
            except Exception as e:
                print(f"    error: {e}")
                for arm, p in [("mcp", fm), ("microsearch", fn)]:
                    err_row = {"error": str(e), "task_id": intent_spec.intent[:40], "arm": arm, "track": "api"}
                    p.write(json.dumps(err_row) + "\n")
                    p.flush()

    print(f"Done. MCP: {mcp_path}, MicroSearch: {micro_path}")
    print("Compare: python3 experiments/mvm_compare_report.py", out_dir)


if __name__ == "__main__":
    main()
