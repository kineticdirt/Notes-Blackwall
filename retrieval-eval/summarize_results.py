"""
Summarize retrieval-eval sequential run results (JSONL) into a general breakdown.
Usage: python3 summarize_results.py [results/sequential_run_work.jsonl] [results/sequential_run_cequence_cs.jsonl ...]
       If no file given, uses results/sequential_run_*.jsonl in retrieval-eval/results.
"""
from __future__ import annotations
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

try:
    from permutations import GRAVITIES
except ImportError:
    GRAVITIES = ("tiny", "short", "medium", "long", "xlong")


def load_results(path: Path) -> list[dict]:
    out = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def _is_error(r: dict) -> bool:
    return "error" in r or (r.get("answer") or "").strip().startswith("(error:")


def summarize(rows: list[dict], label: str = "", high_error_note: bool = True) -> None:
    if not rows:
        print("No results to summarize.")
        return
    n = len(rows)
    errors = sum(1 for r in rows if _is_error(r))
    error_pct = 100 * errors / n
    hits = sum(1 for r in rows if r.get("hit_at_k"))
    correct = sum(1 for r in rows if r.get("answer_correct"))
    ranks = [r["rank"] for r in rows if r.get("rank") is not None]
    mrr = (sum(1 / r for r in ranks) / len(ranks)) if ranks else 0.0
    mostly_errors = error_pct >= 80.0

    print("=" * 60)
    if label:
        print(label)
    print("=" * 60)
    print(f"Total runs:     {n}")
    # When most runs errored, lead with retrieval (still valid); then LLM/errors
    if mostly_errors and high_error_note:
        print()
        print("Retrieval (all runs):")
        print(f"  Hit@k:          {hits}  ({100 * hits / n:.1f}%)")
        if ranks:
            print(f"  MRR (when hit): {mrr:.3f}")
        print()
        print("LLM step:")
        print(f"  Errors:         {errors}  ({error_pct:.1f}%)  <- API/connection or timeout")
        print(f"  Answer correct: {correct}  ({100 * correct / n:.1f}%)  (N/A when LLM errored)")
        print()
        print("  Note: Retrieval metrics above are valid. Re-run with a working API key/network")
        print("  to get answer_correct for this dataset, or rely on work dataset summary.")
    else:
        print(f"Errors:         {errors}  ({error_pct:.1f}%)")
        print(f"Hit@k:          {hits}  ({100 * hits / n:.1f}%)")
        print(f"Answer correct: {correct}  ({100 * correct / n:.1f}%)")
        if ranks:
            print(f"MRR (when hit): {mrr:.3f}")
    flagged = sum(1 for r in rows if r.get("flag_for_investigation"))
    if flagged:
        print(f"Flagged for investigation: {flagged}  (failure_report / failure_meta_analysis in JSONL)")

    # Token expenditure and success vs token usage
    token_rows = [r for r in rows if r.get("total_tokens") is not None and r.get("total_tokens", 0) > 0]
    if token_rows:
        total_tokens = sum(r["total_tokens"] for r in token_rows)
        input_tok = sum(r.get("input_tokens", 0) for r in token_rows)
        output_tok = sum(r.get("output_tokens", 0) for r in token_rows)
        correct_with_tokens = sum(1 for r in token_rows if r.get("answer_correct"))
        mean_tokens = total_tokens / len(token_rows)
        correct_per_1k = (correct_with_tokens * 1000.0 / total_tokens) if total_tokens else 0.0
        print()
        print("Token expenditure & success vs tokens:")
        print(f"  Total tokens:     {total_tokens}  (input: {input_tok}  output: {output_tok})")
        print(f"  Mean tokens/run:   {mean_tokens:.0f}")
        print(f"  Correct (w/ tokens): {correct_with_tokens}  ({100 * correct_with_tokens / len(token_rows):1f}%)")
        print(f"  Correct per 1k tokens: {correct_per_1k:.3f}  (success efficiency)")
    print()

    # By search_type
    by_search: dict[str, list] = defaultdict(list)
    for r in rows:
        by_search[r.get("search_type", "?")].append(r)
    print("By search_type:")
    for st in sorted(by_search.keys()):
        rs = by_search[st]
        h = sum(1 for r in rs if r.get("hit_at_k"))
        c = sum(1 for r in rs if r.get("answer_correct"))
        print(f"  {st:10}  n={len(rs):4}  hit@k={100*h/len(rs):5.1f}%  answer_ok={100*c/len(rs):5.1f}%")
    print()

    # By gravity
    by_gravity: dict[str, list] = defaultdict(list)
    for r in rows:
        by_gravity[r.get("gravity", "?")].append(r)
    print("By gravity:")
    for g in GRAVITIES:
        if g not in by_gravity:
            continue
        rs = by_gravity[g]
        h = sum(1 for r in rs if r.get("hit_at_k"))
        c = sum(1 for r in rs if r.get("answer_correct"))
        print(f"  {g:8}  n={len(rs):4}  hit@k={100*h/len(rs):5.1f}%  answer_ok={100*c/len(rs):5.1f}%")
    print()

    # By thinking
    by_thinking: dict[str, list] = defaultdict(list)
    for r in rows:
        key = "thinking" if r.get("thinking") else "direct"
        by_thinking[key].append(r)
    print("By thinking:")
    for key in ("direct", "thinking"):
        if key not in by_thinking:
            continue
        rs = by_thinking[key]
        h = sum(1 for r in rs if r.get("hit_at_k"))
        c = sum(1 for r in rs if r.get("answer_correct"))
        print(f"  {key:10}  n={len(rs):4}  hit@k={100*h/len(rs):5.1f}%  answer_ok={100*c/len(rs):5.1f}%")
    print()

    # By k (retrieval depth, if present)
    by_k: dict[int, list] = defaultdict(list)
    for r in rows:
        k_val = r.get("k")
        if k_val is not None:
            by_k[k_val].append(r)
    if by_k:
        print("By k (retrieval depth):")
        for k_val in sorted(by_k.keys()):
            rs = by_k[k_val]
            h = sum(1 for r in rs if r.get("hit_at_k"))
            c = sum(1 for r in rs if r.get("answer_correct"))
            print(f"  k={k_val}     n={len(rs):4}  hit@k={100*h/len(rs):5.1f}%  answer_ok={100*c/len(rs):5.1f}%")
        print()

    # By eval_type (if present and varied)
    by_eval: dict[str, list] = defaultdict(list)
    for r in rows:
        by_eval[r.get("eval_type", "?")].append(r)
    if len(by_eval) > 1:
        print("By eval_type:")
        for et in sorted(by_eval.keys()):
            rs = by_eval[et]
            h = sum(1 for r in rs if r.get("hit_at_k"))
            c = sum(1 for r in rs if r.get("answer_correct"))
            print(f"  {et:12}  n={len(rs):4}  hit@k={100*h/len(rs):5.1f}%  answer_ok={100*c/len(rs):5.1f}%")
        print()

    # By dataset_source (if present and varied)
    by_ds: dict[str, list] = defaultdict(list)
    for r in rows:
        by_ds[r.get("dataset_source", r.get("dataset", "?"))].append(r)
    if len(by_ds) > 1:
        print("By dataset_source:")
        for ds in sorted(by_ds.keys()):
            rs = by_ds[ds]
            h = sum(1 for r in rs if r.get("hit_at_k"))
            c = sum(1 for r in rs if r.get("answer_correct"))
            tot = sum(r.get("total_tokens", 0) for r in rs)
            eff = (c * 1000.0 / tot) if tot else 0.0
            print(f"  {ds:14}  n={len(rs):4}  hit@k={100*h/len(rs):5.1f}%  answer_ok={100*c/len(rs):5.1f}%  tokens={tot}  correct/1k={eff:.3f}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize retrieval-eval JSONL results.")
    parser.add_argument("files", nargs="*", type=Path, help="JSONL result files (default: results/sequential_run_*.jsonl).")
    parser.add_argument("--results-dir", type=Path, default=None, help="Directory containing sequential_run_*.jsonl.")
    parser.add_argument(
        "--include-all",
        action="store_true",
        help="Include high-error runs in Combined summary (default: exclude files with >=90%% errors).",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    results_dir = args.results_dir or (root / "results")

    if args.files:
        paths = [p if p.is_absolute() else root / p for p in args.files]
    else:
        paths = sorted(results_dir.glob("sequential_run_*.jsonl"))

    if not paths:
        print("No result files found. Run: python3 run_sequential.py --dataset work", file=sys.stderr)
        sys.exit(1)

    all_rows = []
    for path in paths:
        if not path.exists():
            print(f"Skip (not found): {path}", file=sys.stderr)
            continue
        rows = load_results(path)
        label = path.name
        if rows:
            summarize(rows, label=label)
            err_count = sum(1 for r in rows if _is_error(r))
            error_pct = 100 * err_count / len(rows)
            if args.include_all or error_pct < 90.0:
                all_rows.extend(rows)
            elif error_pct >= 90.0:
                print(f"(Excluded from Combined: {label} has {error_pct:.0f}% errors. Use --include-all to include.)")
                print()

    if len(paths) > 1 and all_rows:
        summarize(all_rows, label="Combined (all files)")


if __name__ == "__main__":
    main()
