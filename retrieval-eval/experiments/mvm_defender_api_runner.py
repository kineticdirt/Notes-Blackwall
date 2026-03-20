#!/usr/bin/env python3
"""
MvM API track against Defender mitigator cache MCP (from def-cterm.txt).
Compare Claude (MCP) vs keyword nano. Same executor: Defender cache MCP server.

Prereqs:
  1. Start Defender cache MCP: uvicorn experiments.defender_cache_mcp.api:app --host 127.0.0.1 --port 8766
  2. Optional: Defender backend at DEFENDER_BASE_URL (default http://localhost:9999) for real cache responses

Run: python3 experiments/mvm_defender_api_runner.py [--limit N] [--nano-type keyword|qwen4b]
  qwen4b: set DEFENDER_QWEN4B_LORA to LoRA dir after train_defender_intent_qwen4b.py
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from experiments.defender_http_mcp import call_tool, initialize, list_tools
from experiments.defender_cache_intents import get_defender_cache_intents
from experiments.defender_cache_test_cases import DefenderTestCase
from experiments.token_cost import token_cost_usd


def _tools_to_text(tools: list[dict]) -> str:
    lines = []
    for t in tools[:20]:
        name = t.get("name", "")
        desc = (t.get("description") or "").strip()
        lines.append(f"- {name}: {desc[:200]}")
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
        nano_type = "keyword"
    intent_lower = intent.lower().strip()
    names = [t.get("name") for t in tools if t.get("name")]
    # cacheAll before cacheInfo-ish "all" in "policy" phrases
    if re.search(
        r"cache\s+all|all\s+cache|full\s+cache|dump\s+cache|all\s+cache\s+data|entire\s+mitigator|everything\s+in\s+__cq|"
        r"full\s+snapshot|complete\s+cache\s+state|export\s+entire|in\s+one\s+response|endpoints\s+combined|"
        r"ip-map.*policy-map.*templates|single\s+get\s+equivalent|all\s+__cq\s+cache",
        intent_lower,
    ) and "cacheAll" in names:
        return "cacheAll", {}
    if re.search(
        r"cache\s+info|mitigator\s+cache\s+info|cache\s+summary|high-level|cache\s+stats|how\s+many\s+entries|"
        r"cache-summary|defender\s+cache\s+overview|overview|counts\b",
        intent_lower,
    ) and "cacheInfo" in names:
        if "policy-map" in intent_lower or "ip-map" in intent_lower:
            if re.search(r"how\s+many|stats|summary|counts|high-level|overview", intent_lower) and "cacheInfo" in names:
                return "cacheInfo", {}
        else:
            return "cacheInfo", {}
    if re.search(
        r"ip-map|ip\s+map|ipv4|ipv6|blocked\s+ips|ip-addresses|ipv4-map|ip\s+policies\s+per|"
        r"which\s+ip\b|ip\s+addresses\b|addresses\s+(are\s+)?in\s+the\s+cache|list\s+of\s+ips|cached\s+ips\b|"
        r"what\s+ips\b|show\s+me\s+the\s+ips|ip-address\b|ip\s+address\s+entries|clients\s+.*\s+ip\s+cache|"
        r"in\s+the\s+ip\s+cache",
        intent_lower,
    ) and "cacheIpMap" in names:
        return "cacheIpMap", {}
    # Summary counts mentioning policy/ip/fpv2 slices → cacheInfo, not full policy-map
    if (
        re.search(r"policy-map|ip-map|fpv2", intent_lower)
        and re.search(r"\bcounts?\b|how\s+many|high-level|stats|summary", intent_lower)
        and "cacheInfo" in names
    ):
        return "cacheInfo", {}
    if re.search(
        r"policy-map|policy\s+map|policies\s+in\s+the\s+cache|expression\s+and\s+fingerprint|correlation-id|"
        r"policy-type|match-criteria|configured\s+in\s+the\s+mitigator|expression\s+policies|"
        r"\bwaf\b|rate-limit|challenge\s+policies",
        intent_lower,
    ) and "cachePolicyMap" in names:
        return "cachePolicyMap", {}
    if "cacheInfo" in names and "info" in intent_lower and "cache" in intent_lower:
        return "cacheInfo", {}
    return None, {}


def run_one(spec: DefenderTestCase, api_key: str, nano_type: str) -> tuple[dict, dict]:
    tools = list_tools()
    task_id = spec.intent[:50].replace(" ", "_")
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
    ap = argparse.ArgumentParser(description="MvM Defender cache API: Claude vs micro (keyword).")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--output-dir", type=Path, default=None)
    ap.add_argument("--nano-type", choices=["keyword", "qwen4b"], default="keyword")
    args = ap.parse_args()
    if not (_root / ".api-key").exists() and not (_root / ".api-key.example").exists():
        print("Claude API key needed for MCP arm. retrieval-eval/.api-key", file=sys.stderr)
        sys.exit(1)
    from config import load_api_key
    api_key = load_api_key()
    try:
        initialize()
    except Exception as e:
        print(f"Defender MCP not reachable. Start: uvicorn experiments.defender_cache_mcp.api:app --host 127.0.0.1 --port 8766. Error: {e}", file=sys.stderr)
        sys.exit(1)
    intents = get_defender_cache_intents()
    if args.limit:
        intents = intents[: args.limit]
    out_dir = args.output_dir or _root / "results" / "mvm_defender"
    out_dir.mkdir(parents=True, exist_ok=True)
    mcp_path = out_dir / "mcp_arm_api.jsonl"
    micro_path = out_dir / "microsearch_arm_api.jsonl"
    print(f"Defender cache MvM: {len(intents)} intents, nano_type={args.nano_type}. Writing to {out_dir}.", flush=True)
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
