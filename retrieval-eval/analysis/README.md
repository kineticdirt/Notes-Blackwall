# Retrieval-eval — Data science (Pandas / Conda)

After `run_sequential.py` finishes, each line in `results/sequential_run_<dataset>.jsonl` is one run (permutation × optional `question_index`). This folder turns that JSONL into **tables** and **plots**.

**Primary:** Open **`analysis/retrieval_eval_analysis.ipynb`** in Jupyter (from `retrieval-eval/`) and run all cells for inline graphs and summary tables. If no result files exist, the notebook falls back to `analysis/fixtures/minimal_sequential.jsonl`.

## 1. Environment (Anaconda / Miniconda)

From repo root:

```bash
cd retrieval-eval
conda env create -f environment.yml
```

Activate:

```bash
conda activate retrieval-eval-ds
```

(Optional) Jupyter for ad-hoc exploration:

```bash
jupyter lab
```

Then in a notebook:

```python
import pandas as pd
df = pd.read_parquet("results/analysis/runs_merged.parquet")
df.groupby(["eval_type", "question_index"])["answer_correct"].mean()
```

## 2. JSONL → useful artifacts

| Artifact | Purpose |
|----------|---------|
| `runs_<stem>.parquet` | Full slim table (no `answer` blob); fast for DuckDB/Pandas |
| `runs_<stem>.csv` | Same, Excel-friendly |
| `summary_by_*.csv` | Pre-aggregated rates by search_type, eval_type, gravity, question |
| `*.png` | Heatmaps, bars, per-question lines, token scatter |

Run the analyzer (default: all `results/sequential_run_*.jsonl`):

```bash
cd retrieval-eval
conda activate retrieval-eval-ds
python analysis/analyze_results.py
```

Single file:

```bash
python analysis/analyze_results.py results/sequential_run_work.jsonl
```

Custom export paths:

```bash
python analysis/analyze_results.py results/sequential_run_work.jsonl --export-csv results/analysis/work.csv --export-parquet results/analysis/work.parquet
```

Plots only skipped:

```bash
python analysis/analyze_results.py --no-plots
```

## 3. Column cheat sheet (JSONL → DataFrame)

| Column | Meaning |
|--------|---------|
| `search_type` | e.g. vector, keyword, … |
| `thinking` | LLM extended thinking on/off |
| `gravity` | Haystack size tier (or `n/a` for external) |
| `eval_type` | needle, reasoning, explanation, assistance |
| `question_index` | Which question in that eval_type’s bank |
| `hit_at_k` | Needle/marker found in top-k chunks |
| `answer_correct` | Markers present in model answer |
| `rank` | 1-based rank of first hit chunk |
| `k`, `chunk_size`, `needle_position` | Permutation params |
| `answer_marker` | Primary label for the question |
| `input_tokens`, `output_tokens`, `total_tokens` | Usage |
| `source_file` | Which JSONL row came from (when merging runs) |
| `is_error` | Derived: API/timeout style failure |

## 4. Pip-only alternative

If you prefer venv + pip instead of Conda:

```bash
cd retrieval-eval
python3 -m venv .venv-ds
source .venv-ds/bin/activate
pip install -r requirements-analysis.txt
python analysis/analyze_results.py
```
