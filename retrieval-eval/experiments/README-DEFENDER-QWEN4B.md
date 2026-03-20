# Defender cache API — test cases, Qwen4B LoRA train, MvM vs Claude

Live API default: **`http://localhost:9999`** (`DEFENDER_BASE_URL`). MCP proxy: port **8766** (`DEFENDER_MCP_URL`).

**Kubernetes port-forward runbook:** `live-defender-api/` (scripts + README for `user-abhinav` / `user-ramesh` and stable `svc`/`pod` forward).

## 1. Test cases (single source of truth)

- **`experiments/defender_cache_test_cases.py`** — `DEFENDER_TEST_CASES` (expanded paraphrase suite; see `docs/reports/MVM-DEFENDER-MICROSEARCH-BENCHMARK-REPORT.md`).
- **`experiments/defender_cache_intents.py`** — re-exports for the MvM runner.
- **`experiments/defender_intent_router_dataset.py`** — builds training JSONL from the same list.

## 2. MCP server (unchanged surface)

Four tools → GET `/__cq/cache/{info,ip-map,policy-map,all}`:

```bash
cd retrieval-eval
python3 -m uvicorn experiments.defender_cache_mcp.api:app --host 127.0.0.1 --port 8766
```

## 3. Build dataset + train Qwen4B LoRA (local)

Use the **same venv** you use for retrieval-eval (e.g. `source ../.venv/bin/activate`). If you see `ModuleNotFoundError: No module named 'transformers'`, install nano deps first:

```bash
cd retrieval-eval
pip install -r experiments/requirements-nano.txt

python3 experiments/defender_intent_router_dataset.py
python3 experiments/train_defender_intent_qwen4b.py --epochs 2 --batch-size 1 --lora
```

Output adapter: **`experiments/defender_qwen4b_lora/`** (default).

Optional: `QWEN4B_MODEL_ID=Qwen/Qwen2.5-3B-Instruct` (smaller/faster) before train and before inference.

## 4. Run MvM (Claude vs local 4B)

```bash
export DEFENDER_QWEN4B_LORA="$(pwd)/experiments/defender_qwen4b_lora"
cd retrieval-eval
python3 experiments/mvm_defender_api_runner.py --nano-type qwen4b
python3 experiments/mvm_compare_report.py results/mvm_defender
```

Keyword baseline (no GPU):

```bash
python3 experiments/mvm_defender_api_runner.py --nano-type keyword
```

## 5. MicroSearch training manifest (optional)

```bash
cd ../microsearch
python3 scripts/record_training_run.py --duration-seconds <wall_clock> \
  --spec specs/defender_cache.openapi.json \
  --dataset ../retrieval-eval/experiments/defender_intent_router.jsonl \
  --tools generated/tools_catalog_defender.json \
  --backend local_lora_qwen4b \
  --micro-model Qwen4B+LoRA
```

## Files

| File | Role |
|------|------|
| `defender_cache_test_cases.py` | Eval + training intents |
| `defender_intent_router_dataset.py` | Emit `defender_intent_router.jsonl` |
| `train_defender_intent_qwen4b.py` | LoRA SFT |
| `qwen4b_router.py` | Loads `DEFENDER_QWEN4B_LORA` if set |
| `mvm_defender_api_runner.py` | `--nano-type qwen4b` |
