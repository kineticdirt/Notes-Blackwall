#!/usr/bin/env python3
"""
Load retrieval-eval sequential JSONL into Pandas, export tidy tables, and write plots.

Usage (from retrieval-eval/):
  conda activate retrieval-eval-ds
  python analysis/analyze_results.py
  python analysis/analyze_results.py results/sequential_run_work.jsonl
  python analysis/analyze_results.py results/sequential_run_work.jsonl results/sequential_run_cequence_cs.jsonl --export-csv results/analysis/runs.csv

Default input: all results/sequential_run_*.jsonl under retrieval-eval.
Default output dir: results/analysis/ (created if missing).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from analysis.load_results import load_jsonl


def load_jsonl_files(paths: list[Path]) -> pd.DataFrame:
    """Load JSONL; paths are under ROOT if not absolute."""
    return load_jsonl(ROOT, paths)


def export_tables(df: pd.DataFrame, out_dir: Path, stem: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    # Wide answer text makes CSV huge; drop for tabular export
    slim = df.drop(columns=["answer"], errors="ignore")
    parquet_path = out_dir / f"{stem}.parquet"
    csv_path = out_dir / f"{stem}.csv"
    try:
        slim.to_parquet(parquet_path, index=False)
        print(f"Wrote {parquet_path}")
    except Exception as e:
        print(f"Parquet skip: {e}", file=sys.stderr)
    slim.to_csv(csv_path, index=False)
    print(f"Wrote {csv_path}")


def _agg_success(df: pd.DataFrame, group_cols: list[str], label: str, out_dir: Path) -> None:
    sub = df[~df["is_error"]].copy() if "is_error" in df.columns else df.copy()
    if sub.empty:
        return
    g = sub.groupby(group_cols, dropna=False).agg(
        n=("answer_correct", "count"),
        hit_at_k_rate=("hit_at_k", "mean"),
        answer_correct_rate=("answer_correct", "mean"),
    ).reset_index()
    g.to_csv(out_dir / f"summary_by_{label}.csv", index=False)
    print(f"Wrote {out_dir / f'summary_by_{label}.csv'}")


def plot_heatmap_search_gravity(df: pd.DataFrame, out_dir: Path) -> None:
    sub = df[(~df["is_error"]) & (df["gravity"].notna()) & (df["gravity"] != "n/a")]
    if sub.empty or "search_type" not in sub.columns:
        return
    pivot = sub.pivot_table(
        index="gravity",
        columns="search_type",
        values="answer_correct",
        aggfunc="mean",
    )
    if pivot.empty:
        return
    fig, ax = plt.subplots(figsize=(max(8, pivot.shape[1] * 1.2), max(4, pivot.shape[0] * 0.6)))
    sns.heatmap(pivot, annot=True, fmt=".2f", cmap="RdYlGn", vmin=0, vmax=1, ax=ax)
    ax.set_title("Answer correct rate (non-error runs): gravity × search_type")
    fig.tight_layout()
    path = out_dir / "heatmap_gravity_search_type.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Wrote {path}")


def plot_bars_by_eval_type(df: pd.DataFrame, out_dir: Path) -> None:
    sub = df[~df["is_error"]]
    if sub.empty or "eval_type" not in sub.columns:
        return
    g = sub.groupby("eval_type", dropna=False).agg(
        hit_at_k=("hit_at_k", "mean"),
        answer_correct=("answer_correct", "mean"),
    ).reset_index()
    fig, ax = plt.subplots(figsize=(10, 5))
    x = range(len(g))
    w = 0.35
    ax.bar([i - w / 2 for i in x], g["hit_at_k"], width=w, label="hit@k")
    ax.bar([i + w / 2 for i in x], g["answer_correct"], width=w, label="answer_correct")
    ax.set_xticks(list(x))
    ax.set_xticklabels(g["eval_type"], rotation=25, ha="right")
    ax.set_ylim(0, 1.05)
    ax.legend()
    ax.set_title("Retrieval vs answer accuracy by eval_type")
    fig.tight_layout()
    path = out_dir / "bars_by_eval_type.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Wrote {path}")


def plot_thinking_compare(df: pd.DataFrame, out_dir: Path) -> None:
    sub = df[~df["is_error"]]
    if sub.empty or "thinking" not in sub.columns:
        return
    sub = sub.copy()
    sub["thinking_label"] = sub["thinking"].map({True: "thinking", False: "direct"})
    g = sub.groupby("thinking_label", dropna=False).agg(
        hit_at_k=("hit_at_k", "mean"),
        answer_correct=("answer_correct", "mean"),
    ).reset_index()
    fig, ax = plt.subplots(figsize=(6, 4))
    x = range(len(g))
    w = 0.35
    ax.bar([i - w / 2 for i in x], g["hit_at_k"], width=w, label="hit@k")
    ax.bar([i + w / 2 for i in x], g["answer_correct"], width=w, label="answer_correct")
    ax.set_xticks(list(x))
    ax.set_xticklabels(g["thinking_label"])
    ax.set_ylim(0, 1.05)
    ax.legend()
    ax.set_title("Thinking vs direct")
    fig.tight_layout()
    path = out_dir / "bars_thinking.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Wrote {path}")


def plot_question_index(df: pd.DataFrame, out_dir: Path) -> None:
    sub = df[~df["is_error"]]
    if sub.empty or "question_index" not in sub.columns:
        return
    g = sub.groupby(["eval_type", "question_index"], dropna=False).agg(
        answer_correct=("answer_correct", "mean"),
        n=("answer_correct", "count"),
    ).reset_index()
    if g.empty:
        return
    fig, ax = plt.subplots(figsize=(10, 5))
    for et in g["eval_type"].dropna().unique():
        part = g[g["eval_type"] == et]
        ax.plot(part["question_index"], part["answer_correct"], marker="o", label=str(et))
    ax.set_xlabel("question_index")
    ax.set_ylabel("answer_correct rate")
    ax.set_ylim(-0.05, 1.05)
    ax.legend(title="eval_type", bbox_to_anchor=(1.02, 1), loc="upper left")
    ax.set_title("Per-question difficulty (mean answer_correct)")
    fig.tight_layout()
    path = out_dir / "line_question_index_by_eval_type.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {path}")


def plot_tokens_vs_correct(df: pd.DataFrame, out_dir: Path) -> None:
    sub = df[(~df["is_error"]) & (df["total_tokens"].notna()) & (df["total_tokens"] > 0)]
    if len(sub) < 5:
        return
    fig, ax = plt.subplots(figsize=(8, 5))
    ok = sub[sub["answer_correct"] == True]  # noqa: E712
    bad = sub[sub["answer_correct"] == False]  # noqa: E712
    ax.scatter(ok["total_tokens"], [1] * len(ok), alpha=0.4, label="correct", s=20)
    ax.scatter(bad["total_tokens"], [0] * len(bad), alpha=0.4, label="incorrect", s=20)
    ax.set_xlabel("total_tokens")
    ax.set_ylabel("answer_correct (jittered 0/1)")
    ax.set_title("Token use vs correctness")
    ax.legend()
    fig.tight_layout()
    path = out_dir / "scatter_tokens_vs_correct.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Wrote {path}")


def plot_by_source_file(df: pd.DataFrame, out_dir: Path) -> None:
    if "source_file" not in df.columns or df["source_file"].nunique() < 2:
        return
    sub = df[~df["is_error"]]
    g = sub.groupby("source_file").agg(
        answer_correct=("answer_correct", "mean"),
        n=("answer_correct", "count"),
    ).reset_index()
    fig, ax = plt.subplots(figsize=(max(8, len(g) * 0.8), 4))
    sns.barplot(data=g, x="source_file", y="answer_correct", ax=ax)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_title("answer_correct rate by result file (compare runs)")
    fig.tight_layout()
    path = out_dir / "bars_by_source_file.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze retrieval-eval JSONL with Pandas + plots.")
    parser.add_argument(
        "jsonl",
        nargs="*",
        type=Path,
        help="JSONL files (default: results/sequential_run_*.jsonl).",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory for plots and summaries (default: results/analysis).",
    )
    parser.add_argument(
        "--export-csv",
        type=Path,
        default=None,
        help="Also write slim DataFrame to this CSV path.",
    )
    parser.add_argument(
        "--export-parquet",
        type=Path,
        default=None,
        help="Also write slim DataFrame to this Parquet path.",
    )
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Only load/export aggregates, skip figures.",
    )
    args = parser.parse_args()

    if args.jsonl:
        paths = [p if p.is_absolute() else ROOT / p for p in args.jsonl]
    else:
        paths = sorted((ROOT / "results").glob("sequential_run_*.jsonl"))

    if not paths:
        print("No JSONL files found. Run run_sequential.py first or pass paths.", file=sys.stderr)
        sys.exit(1)

    df = load_jsonl_files(paths)
    if df.empty:
        print("No rows loaded.", file=sys.stderr)
        sys.exit(1)

    out_dir = args.out_dir or (ROOT / "results" / "analysis")
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    sns.set_theme(style="whitegrid", context="notebook")

    stem = "runs_merged" if len(paths) > 1 else paths[0].stem
    export_tables(df, out_dir, stem)

    if args.export_csv:
        p = args.export_csv if args.export_csv.is_absolute() else ROOT / args.export_csv
        p.parent.mkdir(parents=True, exist_ok=True)
        df.drop(columns=["answer"], errors="ignore").to_csv(p, index=False)
        print(f"Wrote {p}")
    if args.export_parquet:
        p = args.export_parquet if args.export_parquet.is_absolute() else ROOT / args.export_parquet
        p.parent.mkdir(parents=True, exist_ok=True)
        df.drop(columns=["answer"], errors="ignore").to_parquet(p, index=False)
        print(f"Wrote {p}")

    _agg_success(df, ["search_type"], "search_type", out_dir)
    _agg_success(df, ["eval_type"], "eval_type", out_dir)
    _agg_success(df, ["search_type", "gravity"], "search_gravity", out_dir)
    _agg_success(df, ["eval_type", "question_index"], "eval_question", out_dir)

    if not args.no_plots:
        plot_heatmap_search_gravity(df, out_dir)
        plot_bars_by_eval_type(df, out_dir)
        plot_thinking_compare(df, out_dir)
        plot_question_index(df, out_dir)
        plot_tokens_vs_correct(df, out_dir)
        plot_by_source_file(df, out_dir)

    ok = (~df["is_error"]) & df["answer_correct"].notna()
    n_ok = int(ok.sum())
    print(f"\nLoaded {len(df)} rows from {len(paths)} file(s). Non-error rows with answer_correct: {n_ok}")
    print(f"Artifacts under: {out_dir}")


if __name__ == "__main__":
    main()
