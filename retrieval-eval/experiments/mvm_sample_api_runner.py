#!/usr/bin/env python3
"""
MvM API track against Sample API MCP: compare Claude (traditional MCP) vs text-only micro (qwen4b/keyword).
Uses real-world style API (list, get, search). No Atlassian credentials.

Prereqs: Start sample API + MCP first:
  cd retrieval-eval && pip install fastapi uvicorn
  uvicorn experiments.sample_api_mcp.api:app --host 127.0.0.1 --port 8765 &

Then: python3 experiments/mvm_sample_api_runner.py [--limit N] [--nano-type keyword|qwen4b]
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

from experiments.sample_http_mcp import call_tool, initialize, list_tools
from experiments.sample_api_intents import SampleIntent, get_sample_intents
from experiments.token_cost import token_cost_usd


def _tools_to_text(tools: list[dict]) -> str:
    lines = []
    for t in tools[:20]:
        name = t.get("name", "")
        desc = (t.get("description") or "").strip()
        schema = t.get("inputSchema", {})
        req = schema.get("required", [])
        props = schema.get("properties", {})
        args_desc = ", ".join(f"{k}" + (" (required)" if k in req else "") for k in list(props.keys())[:6])
        lines.append(f"- {name}: {desc[:200]}. Args: {args_desc}")
    return "\n".join(lines) if lines else "No tools."


def claude_tool_selection(api_key: str, intent: str, tools: list[dict]) -> tuple[str | None, dict, dict, int]:
    from anthropic import Anthropic
    tools_text = _tools_to_text(tools)
    user = (
        f"Tools available:\n{tools_text}\n\n"
        f"User intent: {intent}\n\n"
        'Output exactly one JSON object with keys "tool" (exact tool name) and "arguments" (object). '
        "Use only tools listed. No markdown.\nJSON:"
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
    if nano_type == "qwen4b":
        try:
            from experiments.qwen4b_router import intent_to_tool
            return intent_to_tool(intent, tools)
        except Exception:
            pass
    # Keyword for sample API
    intent_lower = intent.lower()
    names = [t.get("name") for t in tools if t.get("name")]
    if re.search(r"list\s+posts|all\s+posts|first\s+(\d+)\s+posts", intent_lower):
        if "listPosts" in names:
            m = re.search(r"first\s+(\d+)\s+posts", intent_lower)
            limit = int(m.group(1)) if m else 10
            return "listPosts", {"limit": limit}
        if "listPosts" in names:
            return "listPosts", {}
    if re.search(r"get\s+post\s+(\d+)|post\s+(\d+)|post\s+with\s+id\s+(\d+)", intent_lower):
        m = re.search(r"(\d+)", intent)
        if m and "getPost" in names:
            return "getPost", {"id": int(m.group(1))}
    if re.search(r"search\s+posts|find\s+posts|posts\s+containing|posts\s+for\s+the\s+word|posts\s+about", intent_lower):
        if "searchPosts" in names:
            for w in ("API", "REST", "pagination", "search", "filter"):
                if w.lower() in intent_lower:
                    return "searchPosts", {"q": w}
            m = re.search(r"about\s+(\w+)", intent_lower)
            if m:
                return "searchPosts", {"q": m.group(1)}
            return "searchPosts", {"q": "post"}
    if re.search(r"list\s+users|all\s+users", intent_lower) and "listUsers" in names:
        return "listUsers", {}
    if re.search(r"get\s+user\s+(\d+)|user\s+(\d+)|user\s+by\s+id\s+(\d+)", intent_lower):
        m = re.search(r"(\d+)", intent)
        if m and "getUser" in names:
            return "getUser", {"id": int(m.group(1))}
    if "listPosts" in names:
        return "listPosts", {}
    return None, {}


def run_one(spec: SampleIntent, api_key: str, nano_type: str) -> tuple[dict, dict]:
    tools = list_tools()
    task_id = spec.intent[:50].replace(" ", "_")
    # MCP arm (Claude)
    tool_mcp, args_mcp, usage, sel_ms_mcp = claude_tool_selection(api_key, spec.intent, tools)
    if not tool_mcp:
        mcp_row = {"run_id": task_id, "arm": "mcp", "track": "api", "task_id": task_id, "intent": spec.intent,
                   "tool_selection_latency_ms": sel_ms_mcp, "tool_call_latency_ms": None, "total_latency_ms": sel_ms_mcp,
                   "tool_correct": False, "args_valid": False, "response_success": False,
                   "expected_tool": spec.expected_tool, "selected_tool": None,
                   "input_tokens": usage.get("input_tokens", 0), "output_tokens": usage.get("output_tokens", 0),
                   "cost_usd": round(token_cost_usd(usage.get("input_tokens", 0), usage.get("output_tokens", 0)), 6), "error": "No tool"}
    else:
        t0 = time.perf_counter()
        text_mcp, err_mcp = call_tool(tool_mcp, args_mcp)
        call_ms_mcp = int((time.perf_counter() - t0) * 1000)
        mcp_row = {"run_id": task_id, "arm": "mcp", "track": "api", "task_id": task_id, "intent": spec.intent,
                   "tool_selection_latency_ms": sel_ms_mcp, "tool_call_latency_ms": call_ms_mcp,
                   "total_latency_ms": sel_ms_mcp + call_ms_mcp,
                   "tool_correct": tool_mcp == spec.expected_tool, "args_valid": not err_mcp, "response_success": not err_mcp,
                   "expected_tool": spec.expected_tool, "selected_tool": tool_mcp,
                   "input_tokens": usage.get("input_tokens", 0), "output_tokens": usage.get("output_tokens", 0),
                   "cost_usd": round(token_cost_usd(usage.get("input_tokens", 0), usage.get("output_tokens", 0)), 6)}
    # Micro arm
    t0 = time.perf_counter()
    tool_nano, args_nano = nano_tool_selection(spec.intent, tools, nano_type)
    sel_ms_nano = int((time.perf_counter() - t0) * 1000)
    if not tool_nano:
        micro_row = {"run_id": task_id, "arm": "microsearch", "track": "api", "task_id": task_id, "intent": spec.intent,
                     "tool_selection_latency_ms": sel_ms_nano, "tool_call_latency_ms": None, "total_latency_ms": sel_ms_nano,
                     "tool_correct": False, "args_valid": False, "response_success": False,
                     "expected_tool": spec.expected_tool, "selected_tool": None, "nano_type": nano_type, "error": "No tool"}
    else:
        t0 = time.perf_counter()
        text_nano, err_nano = call_tool(tool_nano, args_nano)
        call_ms_nano = int((time.perf_counter() - t0) * 1000)
        micro_row = {"run_id": task_id, "arm": "microsearch", "track": "api", "task_id": task_id, "intent": spec.intent,
                     "tool_selection_latency_ms": sel_ms_nano, "tool_call_latency_ms": call_ms_nano,
                     "total_latency_ms": sel_ms_nano + call_ms_nano,
                     "tool_correct": tool_nano == spec.expected_tool, "args_valid": not err_nano, "response_success": not err_nano,
                     "expected_tool": spec.expected_tool, "selected_tool": tool_nano, "nano_type": nano_type}
    return mcp_row, micro_row


def main():
    ap = argparse.ArgumentParser(description="MvM Sample API: Claude vs micro (text-only).")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--output-dir", type=Path, default=None)
    ap.add_argument("--nano-type", choices=["keyword", "qwen4b"], default="keyword")
    args = ap.parse_args()
    if not ( _root / ".api-key").exists() and not (_root / ".api-key.example").exists():
        print("Claude API key needed for MCP arm. retrieval-eval/.api-key", file=sys.stderr)
        sys.exit(1)
    from config import load_api_key
    api_key = load_api_key()
    try:
        initialize()
    except Exception as e:
        print(f"Sample MCP not reachable. Start server: uvicorn experiments.sample_api_mcp.api:app --host 127.0.0.1 --port 8765. Error: {e}", file=sys.stderr)
        sys.exit(1)
    intents = get_sample_intents()
    if args.limit:
        intents = intents[: args.limit]
    out_dir = args.output_dir or _root / "results" / "mvm_sample"
    out_dir.mkdir(parents=True, exist_ok=True)
    mcp_path = out_dir / "mcp_arm_api.jsonl"
    micro_path = out_dir / "microsearch_arm_api.jsonl"
    print(f"Sample API MvM: {len(intents)} intents, nano_type={args.nano_type}. Writing to {out_dir}.", flush=True)
    with open(mcp_path, "w") as fm, open(micro_path, "w") as fn:
        for i, spec in enumerate(intents):
            print(f"  [{i+1}/{len(intents)}] {spec.intent[:45]}...")
            try:
                mcp_row, micro_row = run_one(spec, api_key, args.nano_type)
                fm.write(json.dumps(mcp_row) + "\n")
                fn.write(json.dumps(micro_row) + "\n")
                fm.flush()
                fn.flush()
                print(f"    MCP: tool_ok={mcp_row['tool_correct']} cost=${mcp_row.get('cost_usd',0):.4f}  Micro: tool_ok={micro_row['tool_correct']}")
            except Exception as e:
                print(f"    error: {e}")
                for w, p in [(mcp_path, fm), (micro_path, fn)]:
                    p.write(json.dumps({"error": str(e), "intent": spec.intent[:40]}) + "\n")
                    p.flush()
    print(f"Done. Compare: python3 experiments/mvm_compare_report.py {out_dir}")

if __name__ == "__main__":
    main()
