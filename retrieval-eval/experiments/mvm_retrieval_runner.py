#!/usr/bin/env python3
"""
MvM Phase 2: Retrieval track — same retrieval, two answer paths (Claude vs nano).
Outputs mcp_arm_retrieval.jsonl and microsearch_arm_retrieval.jsonl with latency, accuracy, tokens, cost_usd.

Run from retrieval-eval/: python3 experiments/mvm_retrieval_runner.py [--dataset work] [--limit N] [--nano-type heuristic|ollama]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

# Run from retrieval-eval/ so parent is on path
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from config import load_api_key
from evals import get_test_config, is_answer_correct
from needle import (
    build_haystack,
    chunk_text,
    get_sentences,
    retrieval_metrics_on_store,
    run_needle_eval,
)
from store import Store
from retrievers import get_retriever
from llm import answer_with_context, check_api_connectivity

try:
    from dataset_builder import ingest_corpus_doc_to_store
except ImportError:
    ingest_corpus_doc_to_store = None

from experiments.token_cost import token_cost_usd


def _run_retrieval_once(
    store: Store,
    retriever,
    query: str,
    k: int,
) -> tuple[list, dict, int]:
    """Run retrieval once. Returns (top_nodes, metrics, retrieval_latency_ms)."""
    t0 = time.perf_counter()
    top = retriever.search(store, query, node_type="chunk", limit=k)
    retrieval_latency_ms = int((time.perf_counter() - t0) * 1000)
    # metrics (hit_at_k, rank) computed by caller from top + needle
    return top, {}, retrieval_latency_ms


def _hit_at_k_rank(top_nodes, needle: str) -> tuple[bool, int | None]:
    hit = False
    rank = None
    for i, n in enumerate(top_nodes):
        text = (n.content.get("text") or "").lower()
        if needle.lower() in text:
            hit = True
            rank = i + 1
            break
    return hit, rank


def _nano_answer_heuristic(query: str, top_nodes: list) -> str:
    from experiments.microsearch_probe import heuristic_answer
    chunks = [n.content.get("text", str(n.content)) for n in top_nodes]
    return heuristic_answer(query, chunks)


def _nano_answer_ollama(query: str, top_nodes: list, host: str = "http://127.0.0.1:11434", model: str | None = None) -> tuple[str, int]:
    from experiments.microsearch_probe import ollama_summarize
    import os
    context = "\n\n".join(n.content.get("text", str(n.content)) for n in top_nodes[:5])
    model = model or os.environ.get("OLLAMA_MODEL", "qwen2.5:1.5b")
    return ollama_summarize(model, query, context, host)


def _nano_answer_qwen4b(query: str, top_nodes: list) -> tuple[str, int]:
    """Text-only micro model: answer from retrieved context."""
    from experiments.qwen4b_router import answer_from_context
    context = "\n\n".join(n.content.get("text", str(n.content)) for n in top_nodes[:5])
    t0 = time.perf_counter()
    ans = answer_from_context(context, query)
    return ans, int((time.perf_counter() - t0) * 1000)


def run_one_task_retrieval(
    p,
    api_key: str,
    dataset: str,
    question_index: int,
    corpus_path: Path | None,
    doc_id: str | None,
    nano_type: str,  # "heuristic" | "ollama"
    ollama_host: str,
) -> tuple[dict, dict]:
    """
    Run one task: retrieval once, then MCP arm (Claude) and MicroSearch arm (nano).
    Returns (mcp_row, microsearch_row) for JSONL.
    """
    store = Store()
    retriever = get_retriever(p.search_type)
    k = getattr(p, "k", 5)
    chunk_size = getattr(p, "chunk_size", 200)
    needle_sent, query, _primary, success_markers = get_test_config(dataset, p.eval_type, question_index)

    # ---- Retrieval (same for both arms) ----
    if corpus_path and doc_id and corpus_path.exists() and ingest_corpus_doc_to_store:
        ingest_corpus_doc_to_store(store, corpus_path, doc_id)
        t0_ret = time.perf_counter()
        top = retriever.search(store, query, node_type="chunk", limit=k)
        retrieval_latency_ms = int((time.perf_counter() - t0_ret) * 1000)
        metrics = {
            "hit_at_k": any(needle_sent in (n.content.get("text") or "") for n in top),
            "rank": next((i + 1 for i, n in enumerate(top) if needle_sent in (n.content.get("text") or "")), None),
        }
    else:
        position = getattr(p, "needle_position", "middle")
        haystack, _ = build_haystack(
            p.gravity, needle=needle_sent, position=position,
            sentences=get_sentences(dataset),
        )
        chunks = chunk_text(haystack, chunk_size=chunk_size)
        store.ingest_chunks(chunks, doc_id="haystack")
        t0 = time.perf_counter()
        top = retriever.search(store, query, node_type="chunk", limit=k)
        retrieval_latency_ms = int((time.perf_counter() - t0) * 1000)
        metrics = {
            "hit_at_k": any(needle_sent in (n.content.get("text") or "") for n in top),
            "rank": next((i + 1 for i, n in enumerate(top) if needle_sent in (n.content.get("text") or "")), None),
        }

    hit_at_k = metrics.get("hit_at_k", False)
    rank = metrics.get("rank")

    task_id = f"{p.search_type}|{p.gravity}|{p.eval_type}|{question_index}|{getattr(p, 'needle_position', 'middle')}"

    # ---- MCP arm: Claude answer ----
    t0 = time.perf_counter()
    answer_mcp, usage = answer_with_context(api_key, query, top, p.thinking)
    answer_latency_mcp_ms = int((time.perf_counter() - t0) * 1000)
    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)
    total_tokens = usage.get("total_tokens", 0) or (input_tokens + output_tokens)
    cost_usd_mcp = token_cost_usd(input_tokens, output_tokens)

    mcp_row = {
        "run_id": task_id,
        "arm": "mcp",
        "track": "retrieval",
        "task_id": task_id,
        "retrieval_latency_ms": retrieval_latency_ms,
        "answer_latency_ms": answer_latency_mcp_ms,
        "total_latency_ms": retrieval_latency_ms + answer_latency_mcp_ms,
        "hit_at_k": hit_at_k,
        "rank": rank,
        "answer_correct": is_answer_correct(answer_mcp, success_markers),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "cost_usd": round(cost_usd_mcp, 6),
        "search_type": p.search_type,
        "gravity": p.gravity,
        "eval_type": p.eval_type,
        "question_index": question_index,
    }
    if answer_mcp.startswith("(error:") or answer_mcp.startswith("(no answer)"):
        mcp_row["error"] = answer_mcp[:500]

    # ---- MicroSearch arm: nano answer (text-only micro for retrieval) ----
    if nano_type == "qwen4b":
        try:
            ans_nano, answer_latency_nano_ms = _nano_answer_qwen4b(query, top)
        except Exception as e:
            ans_nano = f"(error: {e})"
            answer_latency_nano_ms = 0
    elif nano_type == "ollama":
        try:
            ans_nano, answer_latency_nano_ms = _nano_answer_ollama(query, top, ollama_host)
        except Exception as e:
            ans_nano = f"(error: {e})"
            answer_latency_nano_ms = 0
    else:
        ans_nano = _nano_answer_heuristic(query, top)
        answer_latency_nano_ms = 0  # heuristic is instant

    microsearch_row = {
        "run_id": task_id,
        "arm": "microsearch",
        "track": "retrieval",
        "task_id": task_id,
        "retrieval_latency_ms": retrieval_latency_ms,
        "answer_latency_ms": answer_latency_nano_ms,
        "total_latency_ms": retrieval_latency_ms + answer_latency_nano_ms,
        "hit_at_k": hit_at_k,
        "rank": rank,
        "answer_correct": is_answer_correct(ans_nano, success_markers),
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "cost_usd": 0.0,
        "nano_type": nano_type,
        "search_type": p.search_type,
        "gravity": p.gravity,
        "eval_type": p.eval_type,
        "question_index": question_index,
    }

    return mcp_row, microsearch_row


def main() -> None:
    parser = argparse.ArgumentParser(description="MvM Phase 2: Retrieval track (Claude vs nano answer).")
    parser.add_argument("--dataset", default="work", choices=["default", "cequence_cs", "work"])
    parser.add_argument("--question-index", type=int, default=0)
    parser.add_argument("--limit", type=int, default=None, help="Max tasks to run")
    parser.add_argument("--corpus", type=Path, default=None, help="Prebuilt corpus_work.jsonl path")
    parser.add_argument("--output-dir", type=Path, default=None, help="Default: retrieval-eval/results/mvm")
    parser.add_argument("--nano-type", choices=["heuristic", "ollama", "qwen4b"], default="heuristic",
                        help="qwen4b = text-only 4B instruct for retrieval answer.")
    parser.add_argument("--ollama-host", default="http://127.0.0.1:11434")
    parser.add_argument("--search-type", default="substring", choices=["substring", "vector", "hybrid", "graph"])
    parser.add_argument("--gravity", default="medium")
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--eval-types", nargs="+", default=["needle", "reasoning", "explanation", "assistance"])
    args = parser.parse_args()

    from permutations import Permutation

    root = _root
    if args.corpus and not args.corpus.is_absolute():
        args.corpus = root / args.corpus
    out_dir = args.output_dir or root / "results" / "mvm"
    out_dir.mkdir(parents=True, exist_ok=True)
    mcp_path = out_dir / "mcp_arm_retrieval.jsonl"
    micro_path = out_dir / "microsearch_arm_retrieval.jsonl"

    if not (root / ".api-key").exists() and not (root / ".api-key.example").exists():
        print("Paste your Claude API key in retrieval-eval/.api-key (see README).", file=sys.stderr)
        sys.exit(1)
    api_key = load_api_key()
    print("Checking API connectivity...")
    try:
        check_api_connectivity(api_key)
    except Exception as e:
        print(f"API check failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Build task list: one perm per eval_type (and optionally question indices)
    tasks = []
    for eval_type in args.eval_types:
        p = Permutation(
            search_type=args.search_type,
            thinking=False,
            eval_type=eval_type,
            gravity=args.gravity,
            k=args.k,
            needle_position="middle",
            chunk_size=200,
            dataset_source=args.dataset,
        )
        tasks.append((p, args.question_index))
    if args.limit:
        tasks = tasks[: args.limit]

    print(f"MvM retrieval track: {len(tasks)} tasks, nano_type={args.nano_type}. Writing to {out_dir}.")
    with open(mcp_path, "a") as fm, open(micro_path, "a") as fn:
        for i, (p, qi) in enumerate(tasks):
            doc_id = None
            if args.corpus and args.corpus.exists() and args.dataset == "work":
                doc_id = f"doc_work_{p.eval_type}_{qi}_{p.gravity}_middle"
            print(f"  [{i+1}/{len(tasks)}] {p.eval_type} q{qi}")
            try:
                mcp_row, micro_row = run_one_task_retrieval(
                    p, api_key, args.dataset, qi, args.corpus, doc_id,
                    args.nano_type, args.ollama_host,
                )
                fm.write(json.dumps(mcp_row) + "\n")
                fm.flush()
                fn.write(json.dumps(micro_row) + "\n")
                fn.flush()
                print(f"    MCP: ok={mcp_row['answer_correct']} lat={mcp_row['answer_latency_ms']}ms tokens={mcp_row['total_tokens']} cost=${mcp_row['cost_usd']:.4f}")
                print(f"    Micro: ok={micro_row['answer_correct']} lat={micro_row['answer_latency_ms']}ms")
            except Exception as e:
                print(f"    error: {e}")
                err_row = {"error": str(e), "task_id": f"{p.search_type}|{p.gravity}|{p.eval_type}|{qi}", "arm": "mcp", "track": "retrieval"}
                fm.write(json.dumps(err_row) + "\n")
                fm.flush()
                err_row["arm"] = "microsearch"
                fn.write(json.dumps(err_row) + "\n")
                fn.flush()

    print(f"Done. MCP: {mcp_path}, MicroSearch: {micro_path}")
    print("Compare: python3 experiments/mvm_compare_report.py", out_dir)


if __name__ == "__main__":
    main()
