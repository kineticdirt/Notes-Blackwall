#!/usr/bin/env python3
"""
MvM Phase 5: Load both arms' JSONL, compute metrics (creation, speed, accuracy, token cost), output comparison table.
Usage: python3 experiments/mvm_compare_report.py [results/mvm] [--plots]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    if not path.exists():
        return rows
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def p50(vals: list[float]) -> float:
    if not vals:
        return 0.0
    s = sorted(vals)
    i = max(0, (len(s) * 50 // 100) - 1)
    return s[i]


def p95(vals: list[float]) -> float:
    if not vals:
        return 0.0
    s = sorted(vals)
    i = max(0, (len(s) * 95 // 100) - 1)
    return s[i]


def mean(vals: list[float]) -> float:
    if not vals:
        return 0.0
    return sum(vals) / len(vals)


def main() -> None:
    parser = argparse.ArgumentParser(description="MvM comparison report: MCP vs MicroSearch.")
    parser.add_argument("dir", nargs="?", type=Path, default=None, help="Directory with *arm_*.jsonl (default: results/mvm)")
    parser.add_argument("--plots", action="store_true", help="Write optional plots (requires matplotlib)")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    base = args.dir or root / "results" / "mvm"
    if not base.is_absolute():
        base = root / base

    mcp_ret = load_jsonl(base / "mcp_arm_retrieval.jsonl")
    micro_ret = load_jsonl(base / "microsearch_arm_retrieval.jsonl")
    mcp_api = load_jsonl(base / "mcp_arm_api.jsonl")
    micro_api = load_jsonl(base / "microsearch_arm_api.jsonl")

    lines = [
        "",
        "=== MvM Comparison Report ===",
        f"Directory: {base}",
        "",
    ]

    # ---- Retrieval track ----
    if mcp_ret or micro_ret:
        lines.append("--- Retrieval track ---")
        for label, rows in [("MCP", mcp_ret), ("MicroSearch", micro_ret)]:
            if not rows:
                lines.append(f"  {label}: no data")
                continue
            total_lat = [r["total_latency_ms"] for r in rows if r.get("total_latency_ms") is not None]
            ans_lat = [r["answer_latency_ms"] for r in rows if r.get("answer_latency_ms") is not None]
            hit = sum(1 for r in rows if r.get("hit_at_k"))
            correct = sum(1 for r in rows if r.get("answer_correct"))
            tokens = sum(r.get("total_tokens", 0) for r in rows)
            cost = sum(r.get("cost_usd", 0) for r in rows)
            n = len(rows)
            lines.append(f"  {label}: n={n}")
            lines.append(f"    hit@k: {hit}/{n} ({100*hit/n:.1f}%)" if n else "    hit@k: -")
            lines.append(f"    answer_correct: {correct}/{n} ({100*correct/n:.1f}%)" if n else "    answer_correct: -")
            lines.append(f"    total_latency_ms: p50={p50(total_lat):.0f} p95={p95(total_lat):.0f} mean={mean(total_lat):.0f}")
            lines.append(f"    answer_latency_ms: p50={p50(ans_lat):.0f} p95={p95(ans_lat):.0f} mean={mean(ans_lat):.0f}")
            lines.append(f"    total_tokens: {tokens}  cost_usd: ${cost:.4f}")
        lines.append("")

    # ---- API track ----
    if mcp_api or micro_api:
        lines.append("--- API track ---")
        for label, rows in [("MCP", mcp_api), ("MicroSearch", micro_api)]:
            if not rows:
                lines.append(f"  {label}: no data")
                continue
            total_lat = [r["total_latency_ms"] for r in rows if r.get("total_latency_ms") is not None]
            sel_lat = [r["tool_selection_latency_ms"] for r in rows if r.get("tool_selection_latency_ms") is not None]
            call_lat = [r["tool_call_latency_ms"] for r in rows if r.get("tool_call_latency_ms") is not None]
            tool_ok = sum(1 for r in rows if r.get("tool_correct"))
            resp_ok = sum(1 for r in rows if r.get("response_success"))
            args_ok = sum(1 for r in rows if r.get("args_valid"))
            cost = sum(r.get("cost_usd", 0) for r in rows)
            tot_in = sum(r.get("input_tokens", 0) for r in rows)
            tot_out = sum(r.get("output_tokens", 0) for r in rows)
            n = len(rows)
            lines.append(f"  {label}: n={n}")
            lines.append(f"    tool_correct: {tool_ok}/{n} ({100*tool_ok/n:.1f}%)" if n else "    tool_correct: -")
            lines.append(f"    args_valid: {args_ok}/{n} ({100*args_ok/n:.1f}%)" if n else "    args_valid: -")
            lines.append(f"    response_success: {resp_ok}/{n} ({100*resp_ok/n:.1f}%)" if n else "    response_success: -")
            lines.append(f"    total_latency_ms: p50={p50(total_lat):.0f} p95={p95(total_lat):.0f} mean={mean(total_lat):.0f}")
            lines.append(f"    tool_selection_latency_ms: p50={p50(sel_lat):.0f} mean={mean(sel_lat):.0f}")
            lines.append(f"    tool_call_latency_ms: p50={p50(call_lat):.0f} mean={mean(call_lat):.0f}")
            lines.append(f"    tokens (tool-selection / Claude): input={tot_in} output={tot_out} total={tot_in + tot_out}")
            lines.append(f"    cost_usd: ${cost:.4f}")
        lines.append("")

    # ---- Cost and time breakdown: by time and content (MCP vs MicroSearch) ----
    lines.append("--- Cost breakdown by time and content ---")
    # Content (tokens + cost) for both arms
    for arm_label, ret_rows, api_rows in [
        ("MCP", mcp_ret, mcp_api),
        ("MicroSearch", micro_ret, micro_api),
    ]:
        for track_name, rows in [("Retrieval", ret_rows), ("API", api_rows)]:
            if not rows:
                continue
            tot_in = sum(r.get("input_tokens", 0) for r in rows)
            tot_out = sum(r.get("output_tokens", 0) for r in rows)
            tot_cost = sum(r.get("cost_usd", 0) for r in rows)
            lines.append(f"  {arm_label} [{track_name}]: n={len(rows)}  input_tokens={tot_in}  output_tokens={tot_out}  cost_usd=${tot_cost:.4f}")
        if api_rows and arm_label == "MicroSearch":
            nano_types = {r.get("nano_type") for r in api_rows if r.get("nano_type")}
            if nano_types:
                lines.append(f"  MicroSearch nano_type(s): {', '.join(sorted(nano_types))}")
    lines.append("  (MicroSearch uses no frontier LLM for answer/tool-selection, so its tokens/cost are 0 unless nano path calls an API.)")
    lines.append("")
    # Time breakdown (per-phase latency) for both arms
    if mcp_ret or micro_ret:
        lines.append("  Retrieval track — time by phase:")
        for label, rows in [("MCP", mcp_ret), ("MicroSearch", micro_ret)]:
            if not rows:
                continue
            ret_lat = [r.get("retrieval_latency_ms") or 0 for r in rows]
            ans_lat = [r.get("answer_latency_ms") or 0 for r in rows]
            tot_lat = [r.get("total_latency_ms") or 0 for r in rows]
            mean_tot = mean(tot_lat)
            pct_ret = 100 * mean(ret_lat) / mean_tot if mean_tot else 0
            pct_ans = 100 * mean(ans_lat) / mean_tot if mean_tot else 0
            lines.append(f"    {label}: retrieval_ms p50={p50(ret_lat):.0f} mean={mean(ret_lat):.0f} ({pct_ret:.0f}%)  answer_ms p50={p50(ans_lat):.0f} mean={mean(ans_lat):.0f} ({pct_ans:.0f}%)  total_ms mean={mean_tot:.0f}")
    if mcp_api or micro_api:
        lines.append("  API track — time by phase:")
        for label, rows in [("MCP", mcp_api), ("MicroSearch", micro_api)]:
            if not rows:
                continue
            sel_lat = [r.get("tool_selection_latency_ms") or 0 for r in rows]
            call_lat = [r.get("tool_call_latency_ms") or 0 for r in rows]
            tot_lat = [r.get("total_latency_ms") or 0 for r in rows]
            mean_tot = mean(tot_lat)
            pct_sel = 100 * mean(sel_lat) / mean_tot if mean_tot else 0
            pct_call = 100 * mean(call_lat) / mean_tot if mean_tot else 0
            lines.append(f"    {label}: tool_selection_ms p50={p50(sel_lat):.0f} mean={mean(sel_lat):.0f} ({pct_sel:.0f}%)  tool_call_ms p50={p50(call_lat):.0f} mean={mean(call_lat):.0f} ({pct_call:.0f}%)  total_ms mean={mean_tot:.0f}")
    lines.append("")

    # ---- Speed comparison: MCP vs MicroSearch (is MicroSearch faster?) ----
    lines.append("--- Speed comparison: MCP vs MicroSearch ---")
    if mcp_ret and micro_ret:
        mcp_tot = [r.get("total_latency_ms") or 0 for r in mcp_ret]
        mic_tot = [r.get("total_latency_ms") or 0 for r in micro_ret]
        mcp_ans = [r.get("answer_latency_ms") or 0 for r in mcp_ret]
        mic_ans = [r.get("answer_latency_ms") or 0 for r in micro_ret]
        faster_tot = "MicroSearch" if mean(mic_tot) < mean(mcp_tot) else "MCP"
        faster_ans = "MicroSearch" if mean(mic_ans) < mean(mcp_ans) else "MCP"
        lines.append("  Retrieval track:")
        lines.append(f"    total_latency_ms  MCP: p50={p50(mcp_tot):.0f} mean={mean(mcp_tot):.0f}  MicroSearch: p50={p50(mic_tot):.0f} mean={mean(mic_tot):.0f}  -> faster: {faster_tot}")
        lines.append(f"    answer_latency_ms MCP: p50={p50(mcp_ans):.0f} mean={mean(mcp_ans):.0f}  MicroSearch: p50={p50(mic_ans):.0f} mean={mean(mic_ans):.0f}  -> faster: {faster_ans}")
        lines.append("    (MicroSearch avoids frontier LLM for the answer step, so answer latency is typically lower.)")
    if mcp_api and micro_api:
        mcp_tot = [r.get("total_latency_ms") or 0 for r in mcp_api]
        mic_tot = [r.get("total_latency_ms") or 0 for r in micro_api]
        mcp_sel = [r.get("tool_selection_latency_ms") or 0 for r in mcp_api]
        mic_sel = [r.get("tool_selection_latency_ms") or 0 for r in micro_api]
        faster_tot = "MicroSearch" if mean(mic_tot) < mean(mcp_tot) else "MCP"
        faster_sel = "MicroSearch" if mean(mic_sel) < mean(mcp_sel) else "MCP"
        lines.append("  API track:")
        lines.append(f"    total_latency_ms           MCP: p50={p50(mcp_tot):.0f} mean={mean(mcp_tot):.0f}  MicroSearch: p50={p50(mic_tot):.0f} mean={mean(mic_tot):.0f}  -> faster: {faster_tot}")
        lines.append(f"    tool_selection_latency_ms  MCP: p50={p50(mcp_sel):.0f} mean={mean(mcp_sel):.0f}  MicroSearch: p50={p50(mic_sel):.0f} mean={mean(mic_sel):.0f}  -> faster: {faster_sel}")
        lines.append("    (MicroSearch uses nano/keyword for tool selection instead of Claude, so selection latency is typically lower.)")
    if (mcp_ret or mcp_api) and not (micro_ret or micro_api):
        lines.append("  (Only MCP data present; run MicroSearch arm to compare speed.)")
    if not (mcp_ret or mcp_api):
        lines.append("  (No MCP data; run both arms to compare.)")
    lines.append("")

    # ---- Summary table ----
    lines.append("--- Summary (token cost as overall cost metric) ---")
    all_ret = mcp_ret + micro_ret
    all_api = mcp_api + micro_api
    if all_ret:
        cost_ret_mcp = sum(r.get("cost_usd", 0) for r in mcp_ret)
        cost_ret_micro = sum(r.get("cost_usd", 0) for r in micro_ret)
        lines.append(f"  Retrieval: MCP cost=${cost_ret_mcp:.4f}  MicroSearch cost=${cost_ret_micro:.4f}")
    if all_api:
        cost_api_mcp = sum(r.get("cost_usd", 0) for r in mcp_api)
        cost_api_micro = sum(r.get("cost_usd", 0) for r in micro_api)
        lines.append(f"  API:       MCP cost=${cost_api_mcp:.4f}  MicroSearch cost=${cost_api_micro:.4f}")

    text = "\n".join(lines)
    print(text)

    if args.plots:
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            if mcp_ret and micro_ret:
                fig, ax = plt.subplots(1, 1)
                lat_mcp = [r.get("total_latency_ms") or 0 for r in mcp_ret]
                lat_micro = [r.get("total_latency_ms") or 0 for r in micro_ret]
                ax.boxplot([lat_mcp, lat_micro], labels=["MCP", "MicroSearch"])
                ax.set_ylabel("total_latency_ms")
                ax.set_title("Retrieval track: total latency")
                fig.savefig(base / "mvm_retrieval_latency.png", dpi=100)
                plt.close()
                print(f"Wrote {base / 'mvm_retrieval_latency.png'}")
            if mcp_api and micro_api:
                fig, ax = plt.subplots(1, 1)
                lat_mcp = [r.get("total_latency_ms") or 0 for r in mcp_api]
                lat_micro = [r.get("total_latency_ms") or 0 for r in micro_api]
                ax.boxplot([lat_mcp, lat_micro], labels=["MCP", "MicroSearch"])
                ax.set_ylabel("total_latency_ms")
                ax.set_title("API track: total latency")
                fig.savefig(base / "mvm_api_latency.png", dpi=100)
                plt.close()
                print(f"Wrote {base / 'mvm_api_latency.png'}")
        except ImportError:
            print("--plots requires matplotlib. pip install matplotlib", file=sys.stderr)


if __name__ == "__main__":
    main()
