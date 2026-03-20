#!/usr/bin/env python3
"""
Build supervised JSONL for Defender cache intent → JSON(tool, arguments).
Same completion format as qwen4b_router / Claude MCP arm.

Usage (from retrieval-eval/):
  python3 experiments/defender_intent_router_dataset.py
Writes: experiments/defender_intent_router.jsonl
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
_ROOT = ROOT.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

OUT = ROOT / "defender_intent_router.jsonl"

from experiments.defender_cache_test_cases import DEFENDER_TEST_CASES

# Must match defender_cache_mcp/mcp_tools.py tool names
TOOLS = ["cacheAll", "cacheInfo", "cacheIpMap", "cachePolicyMap"]


def tools_line() -> str:
    return "Available tools: " + ", ".join(sorted(TOOLS)) + "."


def instruction_for(intent: str) -> str:
    sys_p = (
        'You are an MCP router. Reply with ONLY a JSON object with keys '
        '"tool" (exact tool name) and "arguments" (object). No markdown, no explanation.\n'
    )
    return sys_p + tools_line() + f"\nUser request: {intent}\nJSON:"


def main() -> None:
    lines_out = []
    for tc in DEFENDER_TEST_CASES:
        intent, tool, args = tc.intent, tc.expected_tool, tc.expected_args_subset
        comp = json.dumps({"tool": tool, "arguments": args}, separators=(",", ":"))
        row = {"instruction": instruction_for(intent), "completion": comp, "intent": intent, "expected_tool": tool}
        lines_out.append(json.dumps(row, ensure_ascii=False))
    OUT.write_text("\n".join(lines_out) + "\n", encoding="utf-8")
    print(f"Wrote {len(lines_out)} rows to {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
