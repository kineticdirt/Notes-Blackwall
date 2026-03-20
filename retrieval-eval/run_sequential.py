"""
Run all retrieval-eval permutations sequentially.
Uses API key from retrieval-eval/.api-key or ANTHROPIC_API_KEY.
Supports --all-questions (every question index × design perm) and --corpus (prebuilt chunks).
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

from config import load_api_key
from permutations import all_permutations, Permutation
from needle import run_needle_eval, build_haystack, chunk_text, get_sentences
from evals import get_test_config, is_answer_correct, get_question_count
from store import Store
from retrievers import get_retriever
from llm import answer_with_context, check_api_connectivity, write_failure_report

try:
    from external_datasets import (
        EXTERNAL_DATASET_SOURCES,
        get_external_example,
        get_external_example_count,
    )
except ImportError:
    EXTERNAL_DATASET_SOURCES = ()
    def get_external_example(*args, **kwargs):
        return None
    def get_external_example_count(*args, **kwargs):
        return 0


def run_id(p: Permutation, question_index: int) -> str:
    """Unique id for this (permutation, question_index) so we can resume by skipping done runs."""
    return (
        f"{p.search_type}|{p.thinking}|{p.gravity}|{p.eval_type}|{getattr(p, 'k', 5)}|"
        f"{getattr(p, 'needle_position', 'middle')}|{getattr(p, 'chunk_size', 200)}|"
        f"{getattr(p, 'dataset_source', 'default')}|{question_index}"
    )


def run_id_from_row(row: dict) -> str | None:
    """Build run_id from an existing result row (for resume)."""
    try:
        return (
            f"{row.get('search_type', '?')}|{row.get('thinking')}|{row.get('gravity', '?')}|"
            f"{row.get('eval_type', '?')}|{row.get('k', 5)}|"
            f"{row.get('needle_position', 'middle')}|{row.get('chunk_size', 200)}|"
            f"{row.get('dataset_source', row.get('dataset', '?'))}|{row.get('question_index', 0)}"
        )
    except Exception:
        return None


def load_done_run_ids(path: Path) -> set[str]:
    """Load run_ids from existing JSONL so we can skip them on resume."""
    done: set[str] = set()
    if not path.exists():
        return done
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
                rid = run_id_from_row(row)
                if rid:
                    done.add(rid)
            except json.JSONDecodeError:
                continue
    return done


def run_one(
    p: Permutation,
    api_key: str,
    dataset: str = "default",
    question_index: int = 0,
    corpus_path: Path | None = None,
    doc_id: str | None = None,
) -> dict:
    """Run one full permutation: retrieval + LLM answer (thinking on/off).
    dataset comes from p.dataset_source when using permutation axis; external sources use loaded examples."""
    dataset_source = getattr(p, "dataset_source", dataset)
    store = Store()
    retriever = get_retriever(p.search_type)
    k = getattr(p, "k", 5)
    chunk_size = getattr(p, "chunk_size", 200)

    if dataset_source in EXTERNAL_DATASET_SOURCES:
        ex = get_external_example(dataset_source, question_index)
        if ex is None:
            return {
                "error": f"no external example {question_index} for {dataset_source}",
                "dataset_source": dataset_source,
                "question_index": question_index,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "answer_correct": False,
            }
        query, context, success_markers = ex
        chunks = chunk_text(context, chunk_size=chunk_size)
        store.ingest_chunks(chunks, doc_id="external")
        top = retriever.search(store, query, node_type="chunk", limit=k)
        hit_at_k = False
        rank = None
        for i, n in enumerate(top):
            text = (n.content.get("text") or "").lower()
            if any(m and m.lower() in text for m in success_markers if m):
                hit_at_k = True
                rank = i + 1
                break
        metrics = {
            "search_type": p.search_type,
            "gravity": "n/a",
            "dataset": dataset_source,
            "dataset_source": dataset_source,
            "hit_at_k": hit_at_k,
            "rank": rank,
            "k": k,
            "num_chunks": len(chunks),
        }
    else:
        needle_sent, query, _primary, success_markers = get_test_config(dataset_source, p.eval_type, question_index)
        if corpus_path is not None and doc_id is not None and corpus_path.exists():
            from dataset_builder import ingest_corpus_doc_to_store
            from needle import retrieval_metrics_on_store
            ingest_corpus_doc_to_store(store, corpus_path, doc_id)
            metrics = retrieval_metrics_on_store(
                store, retriever, query, needle_sent, k=k,
                search_type=p.search_type, gravity=p.gravity, dataset=dataset_source,
            )
            top = retriever.search(store, query, node_type="chunk", limit=k)
        else:
            position = getattr(p, "needle_position", "middle")
            metrics = run_needle_eval(
                p.search_type, p.gravity, k=k, dataset=dataset_source,
                needle=needle_sent, query=query, position=position, chunk_size=chunk_size,
            )
            haystack, _ = build_haystack(p.gravity, needle=needle_sent, position=position, sentences=get_sentences(dataset_source))
            chunks = chunk_text(haystack, chunk_size=chunk_size)
            store.ingest_chunks(chunks, doc_id="haystack")
            top = retriever.search(store, query, node_type="chunk", limit=k)
        metrics["dataset_source"] = dataset_source
        metrics["answer_marker"] = _primary

    metrics["thinking"] = p.thinking
    metrics["eval_type"] = p.eval_type
    metrics["question_index"] = question_index
    metrics["needle_position"] = getattr(p, "needle_position", "middle")
    metrics["chunk_size"] = getattr(p, "chunk_size", 200)
    answer, usage = answer_with_context(api_key, query, top, p.thinking)
    metrics["answer"] = answer
    metrics["answer_correct"] = is_answer_correct(answer, success_markers)
    metrics["flag_for_investigation"] = answer.strip().startswith("(error:") or answer.strip().startswith("(no answer)")
    metrics["input_tokens"] = usage.get("input_tokens", 0)
    metrics["output_tokens"] = usage.get("output_tokens", 0)
    metrics["total_tokens"] = usage.get("total_tokens", 0)
    total = metrics["total_tokens"] or 1
    metrics["correct_per_1k_tokens"] = (1.0 if metrics["answer_correct"] else 0.0) * 1000.0 / total
    return metrics

def main() -> None:
    parser = argparse.ArgumentParser(description="Run retrieval-eval permutations sequentially.")
    parser.add_argument(
        "--dataset",
        default="default",
        choices=["default", "cequence_cs", "work"],
        help="Dataset: default | cequence_cs (legacy) | work (Jira + Confluence only).",
    )
    parser.add_argument(
        "--question-index",
        type=int,
        default=0,
        help="Which question index to run per eval type (0-based).",
    )
    parser.add_argument(
        "--all-questions",
        action="store_true",
        help="Run every question index for each eval type (work dataset: 7+5+4+2 = 18 per perm).",
    )
    parser.add_argument(
        "--corpus",
        type=Path,
        default=None,
        help="Path to prebuilt corpus_work.jsonl; use with --dataset work and optional --all-questions.",
    )
    parser.add_argument(
        "--max-external",
        type=int,
        default=20,
        help="Max examples per external dataset source per permutation (default 20).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Max number of runs (for quick testing). Truncates (permutation, question_index) list.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSONL path (default: results/sequential_run_<dataset>.jsonl). Use for separate runs (e.g. test_run1.jsonl).",
    )
    args = parser.parse_args()
    dataset = args.dataset
    root = Path(__file__).resolve().parent
    corpus_path = args.corpus
    if corpus_path is not None and not corpus_path.is_absolute():
        corpus_path = root / corpus_path

    if not (root / ".api-key").exists() and not (root / ".api-key.example").exists():
        print("Paste your Claude API key in: retrieval-eval/.api-key or .api-key.example", file=sys.stderr)
        print("See retrieval-eval/README.md.", file=sys.stderr)
        sys.exit(1)

    try:
        api_key = load_api_key()
    except RuntimeError as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    print("Checking API connectivity (one short request)...")
    try:
        check_api_connectivity(api_key)
    except Exception as e:
        print(f"API check failed: {e}", file=sys.stderr)
        sys.exit(1)
    print("API OK. Starting eval.")

    perms = all_permutations()
    results_dir = root / "results"
    results_dir.mkdir(exist_ok=True)
    out_path = args.output if args.output is not None else results_dir / f"sequential_run_{dataset}.jsonl"
    if not out_path.is_absolute():
        out_path = root / out_path

    # Build (permutation, question_index) list: respect dataset_source from permutation
    run_list = []
    for p in perms:
        ds = getattr(p, "dataset_source", dataset)
        if ds in EXTERNAL_DATASET_SOURCES:
            nq = get_external_example_count(ds, max_examples=args.max_external)
            for qi in range(nq):
                run_list.append((p, qi))
        elif args.all_questions and ds == "work":
            nq = get_question_count(ds, p.eval_type)
            for qi in range(nq):
                run_list.append((p, qi))
        else:
            run_list.append((p, args.question_index))

    if args.limit is not None and args.limit > 0:
        run_list = run_list[: args.limit]
        print(f"Limited to first {args.limit} runs (--limit).")

    # Resume: skip (p, qi) that already have a result in the output file
    done_ids = load_done_run_ids(out_path)
    if done_ids:
        run_list = [(p, qi) for p, qi in run_list if run_id(p, qi) not in done_ids]
        print(f"Resume: {len(done_ids)} already in {out_path.name}, {len(run_list)} runs remaining.")
    total = len(run_list)
    print(f"Runs: {total} (permutations × questions). Dataset filter: {dataset}.")
    if total == 0:
        print("Nothing to run (all done). Summarize: python3 summarize_results.py", out_path)
        return
    if corpus_path:
        print(f"Using prebuilt corpus: {corpus_path}")
    with open(out_path, "a") as f:
        for idx, (p, question_index) in enumerate(run_list):
            doc_id = None
            ds = getattr(p, "dataset_source", dataset)
            if corpus_path and corpus_path.exists() and ds == "work":
                pos = getattr(p, "needle_position", "middle")
                doc_id = f"doc_work_{p.eval_type}_{question_index}_{p.gravity}_{pos}"
            print(f"[{idx+1}/{total}] {p.search_type} {ds} {p.eval_type} q{question_index}")
            try:
                m = run_one(
                    p, api_key, dataset=ds, question_index=question_index,
                    corpus_path=corpus_path, doc_id=doc_id,
                )
                if m.get("flag_for_investigation"):
                    query_for_ctx = m.get("query") or (get_test_config(ds, p.eval_type, question_index)[1] if ds not in EXTERNAL_DATASET_SOURCES else "")
                    ctx = {
                        "dataset": ds,
                        "dataset_source": ds,
                        "eval_type": p.eval_type,
                        "question_index": question_index,
                        "permutation": f"{p.search_type}/{p.thinking}/{p.gravity}/k{getattr(p, 'k', 5)}",
                        "query": query_for_ctx,
                        "error_or_answer": m.get("answer", ""),
                    }
                    report = write_failure_report(api_key, m.get("answer", "(no answer)"), ctx)
                    m.update(report)
                f.write(json.dumps(m) + "\n")
                f.flush()
                tok = m.get("total_tokens", 0)
                print(f"  hit={m.get('hit_at_k')} rank={m.get('rank')} ok={m.get('answer_correct')} tokens={tok}")
            except Exception as e:
                print(f"  error: {e}")
                ds = getattr(p, "dataset_source", dataset)
                error_record = {
                    "error": str(e),
                    "permutation": f"{p.search_type}/{p.thinking}/{p.gravity}/k{getattr(p, 'k', 5)}",
                    "eval_type": p.eval_type,
                    "question_index": question_index,
                    "dataset": ds,
                    "dataset_source": ds,
                    "k": getattr(p, "k", 5),
                }
                ctx = {
                    "dataset": ds,
                    "eval_type": p.eval_type,
                    "question_index": question_index,
                    "permutation": error_record["permutation"],
                }
                report = write_failure_report(api_key, str(e), ctx)
                error_record.update(report)
                f.write(json.dumps(error_record) + "\n")
                f.flush()
    print(f"Done. Results appended to {out_path}. Summarize: python3 summarize_results.py {out_path}")

if __name__ == "__main__":
    main()
