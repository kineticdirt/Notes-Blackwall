"""
Build the work dataset and corpus for retrieval eval.
Writes:
  - results/dataset_work.json   (case manifest for runner and ES metadata)
  - results/corpus_work.jsonl   (one line per chunk for ES bulk index and RAG ingest)
Run from retrieval-eval: python3 build_corpus.py [--combos [N]] [--no-combos]
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

from dataset_builder import (
    all_single_cases,
    all_combination_cases,
    write_dataset_json,
    write_corpus_jsonl,
)

def main() -> None:
    parser = argparse.ArgumentParser(description="Build work dataset and corpus (ES + RAG).")
    parser.add_argument(
        "--combos",
        type=int,
        default=None,
        metavar="N",
        help="Add up to N combination (multi-needle) cases. Default: 0. Use a number to limit.",
    )
    parser.add_argument(
        "--no-combos",
        action="store_true",
        help="Do not add any combination cases (default if --combos not set).",
    )
    parser.add_argument(
        "--same-type-only",
        action="store_true",
        help="Only pair needles from same eval_type (for combination cases).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: retrieval-eval/results).",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    out_dir = args.output_dir or (root / "results")
    out_dir.mkdir(parents=True, exist_ok=True)
    dataset_path = out_dir / "dataset_work.json"
    corpus_path = out_dir / "corpus_work.jsonl"

    single = all_single_cases()
    if args.no_combos or (args.combos is not None and args.combos == 0):
        combos = []
    elif args.combos is not None:
        combos = all_combination_cases(max_pairs=args.combos, same_type_only=args.same_type_only)
    else:
        combos = []

    print(f"Single cases: {len(single)}")
    print(f"Combination cases: {len(combos)}")

    write_dataset_json(dataset_path, single_cases=single, combination_cases=combos)
    print(f"Wrote {dataset_path}")

    total_chunks = write_corpus_jsonl(corpus_path, single_cases=single, combination_cases=combos)
    print(f"Wrote {corpus_path} ({total_chunks} chunks)")
    print("Use corpus_work.jsonl for Elasticsearch bulk index and for RAG Store ingest by doc_id.")

if __name__ == "__main__":
    main()
