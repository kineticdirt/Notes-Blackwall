# Retrieval Eval — Sequential Permutation Runner

Runs retrieval evals (needle-in-haystack, etc.) across **all permutations** of search type, thinking on/off, and gravity. Uses one Claude API key; runs **sequentially** to control cost.

---

## Where to paste your API key

**Single place:** create this file and put your key on one line (no quotes):

| Path | What to do |
|------|------------|
| **`retrieval-eval/.api-key`** | Create the file; paste your Claude API key as the first line (e.g. `sk-ant-api03-...`). |

- **Security:** `.api-key` is gitignored; it will never be committed.
- **Example:** See `retrieval-eval/.api-key.example` (copy to `.api-key` and replace the placeholder with your key).

Alternatively, set the environment variable before running:

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

The runner checks **first** for `retrieval-eval/.api-key`, then for `ANTHROPIC_API_KEY`. Use whichever you prefer; the file is the single “paste here” spot.

---

## Run all permutations (sequential)

From the repo root:

```bash
cd retrieval-eval
pip install -r requirements.txt
python3 run_sequential.py
```

(Run from inside `retrieval-eval/` so the key file and modules are found.)

Runs each permutation one after another; logs progress and writes results under `retrieval-eval/results/`.

**Breakdown of responses:** After a run, get a summary (hit@k, answer correct %, by search_type, gravity, thinking, eval_type):

```bash
python3 summarize_results.py
```

Optional: `summarize_results.py results/sequential_run_work.jsonl` or pass specific JSONL files. With no args it summarizes every `results/sequential_run_*.jsonl`.

**Pandas / Conda dashboards:** After JSONL exists, load into DataFrames, CSV/Parquet, and plots:

```bash
conda env create -f environment.yml
conda activate retrieval-eval-ds
python analysis/analyze_results.py
```

See **`analysis/README.md`** for columns, exports, and Jupyter tips. **Notebook:** open `analysis/retrieval_eval_analysis.ipynb` and run all cells for graphs and tables. Smoke test without a full eval: `python analysis/analyze_results.py analysis/fixtures/minimal_sequential.jsonl --out-dir results/analysis_fixture`.

### Quick test (run 3 times for a rule of thumb)

To get a rough sense of variance, run a **limited** job 3 times and compare summaries:

```bash
cd retrieval-eval

# Run 1
python3 run_sequential.py --dataset default --limit 50 --max-external 2 --output results/test_run1.jsonl

# Run 2
python3 run_sequential.py --dataset default --limit 50 --max-external 2 --output results/test_run2.jsonl

# Run 3
python3 run_sequential.py --dataset default --limit 50 --max-external 2 --output results/test_run3.jsonl

# Summarize each and compare
python3 summarize_results.py results/test_run1.jsonl
python3 summarize_results.py results/test_run2.jsonl
python3 summarize_results.py results/test_run3.jsonl
```

Or in one go (same 50 runs, 3 separate output files):

```bash
for i in 1 2 3; do python3 run_sequential.py --dataset default --limit 50 --max-external 2 --output results/test_run$i.jsonl; done
python3 summarize_results.py results/test_run1.jsonl results/test_run2.jsonl results/test_run3.jsonl
```

- **Full run (no limit):** omit `--limit` and `--output` to run all permutations and append to `results/sequential_run_default.jsonl`. Run that command 3 times to append 3 full passes (or use `--output results/full_run1.jsonl` etc. to keep passes separate).

---

## Permutations

| Search type | Thinking | Eval        | Gravity |
|------------|----------|------------|---------|
| substring  | on/off   | needle     | short/medium/long |
| vector     | on/off   | needle     | short/medium/long |
| hybrid     | on/off   | needle     | short/medium/long |
| graph      | on/off   | needle     | short/medium/long |

Each combination is fully implemented and executed in sequence.

---

## Dataset and corpus (ES + RAG)

A **single source of truth** dataset is built from the work question bank (needle, reasoning, explanation, assistance) and the inventory in `docs/plans/WORK_EVAL_PROJECTS_AND_PRODUCTS.md`. It covers **all permutations**: eval_type × question_index × gravity × needle_position, plus optional **multi-needle combination** cases to test whether one needle causes another to be retrieved worse.

### Build the dataset and corpus

From `retrieval-eval/`:

```bash
python3 build_corpus.py
```

This writes:

- **`results/dataset_work.json`** — Case manifest (case_id, doc_id, eval_type, question_index, gravity, needle_position, needle, query, markers, seed). Used by the runner and for ES metadata.
- **`results/corpus_work.jsonl`** — One line per chunk: `doc_id`, `chunk_index`, `text`, `case_id`, `eval_type`, `gravity`. Same format for **Elasticsearch bulk index** and for **RAG** (in-memory Store / GraphQL / thinking).

Optional:

- **`--combos N`** — Add up to N multi-needle combination cases (two needles in one haystack; run two queries to test interference).
- **`--same-type-only`** — When using `--combos`, only pair needles from the same eval_type.

### Use the corpus for RAG and runner

- **RAG (in-memory Store):** For a given `doc_id`, load its chunks from `corpus_work.jsonl` and call `store.ingest_chunks(chunks, doc_id=doc_id)`. The runner can use prebuilt corpus with `--corpus results/corpus_work.jsonl`.
- **Elasticsearch:** Bulk index the same JSONL (e.g. with `ingest_elasticsearch.py`). See below.

### Run with all questions and/or prebuilt corpus

```bash
# All design permutations × one question per eval type (default)
python3 run_sequential.py --dataset work

# All design permutations × every question index (7+5+4+2 = 18 per perm for work)
python3 run_sequential.py --dataset work --all-questions

# Use prebuilt corpus (reproducible chunks; no random haystack at runtime)
python3 build_corpus.py
python3 run_sequential.py --dataset work --corpus results/corpus_work.jsonl --question-index 0
```

### Ingest corpus into Elasticsearch

Requires `pip install elasticsearch`. Set `ELASTICSEARCH_URL` (default `http://localhost:9200`) then:

```bash
python3 ingest_elasticsearch.py
```

Optional: `--index retrieval_eval_work`, `--corpus results/corpus_work.jsonl`, `--url http://...`. Index mapping includes `doc_id`, `chunk_index`, `text`, `case_id`, `eval_type`, `gravity` for filtering and search.

---

## See also

- **MCP vs MicroSearch comparative test frame (MvM):** Plan: **`docs/plans/2026-03-18-MCP-VS-MICROSEARCH-TEST-FRAME.md`**. Run comparison (standard model, same tools, **token cost** as cost metric): from `retrieval-eval/` run **`bash experiments/run_mvm_comparison.sh`**. See **`experiments/README-MVM.md`** for retrieval + API tracks and report.
