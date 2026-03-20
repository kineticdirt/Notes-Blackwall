"""Load retrieval-eval JSONL into a DataFrame. Used by the CLI and the Jupyter notebook."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def _is_error_row(answer: object, err: object) -> bool:
    if err is not None and not (isinstance(err, float) and pd.isna(err)):
        return True
    if answer is None or (isinstance(answer, float) and pd.isna(answer)):
        return False
    s = str(answer).strip()
    return s.startswith("(error:")


def load_jsonl(root: Path, paths: list[Path]) -> pd.DataFrame:
    """Load one or more JSONL files under root into a single DataFrame."""
    rows: list[dict] = []
    for path in paths:
        full = path if path.is_absolute() else root / path
        if not full.exists():
            continue
        with open(full, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                r = dict(r)
                r["source_file"] = full.name
                rows.append(r)
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["is_error"] = df.apply(
        lambda x: _is_error_row(x.get("answer"), x.get("error")),
        axis=1,
    )
    for col in ("hit_at_k", "answer_correct", "thinking"):
        if col in df.columns:
            df[col] = df[col].astype("boolean") if df[col].dtype == object else df[col]
    return df


def get_default_jsonl_paths(root: Path) -> list[Path]:
    """Result paths: results/sequential_run_*.jsonl, or fixture if none."""
    results_dir = root / "results"
    paths = sorted(results_dir.glob("sequential_run_*.jsonl"))
    if paths:
        return paths
    fixture = root / "analysis" / "fixtures" / "minimal_sequential.jsonl"
    if fixture.exists():
        return [fixture]
    return []
