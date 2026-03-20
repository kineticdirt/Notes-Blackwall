# MicroSearch framework — definition and metrics

## Definition

**MicroSearch** is the arm where a **small model** (or deterministic rules) performs **predigestion**: intent → tool + arguments, optional retrieval expansion, optional summarization of top‑k context—before or instead of billing a **frontier** model for every hop.

**Baseline arms** (for comparison):

| Arm | Role |
|-----|------|
| **MCP + Claude Sonnet** | Frontier selects tool/args (or answers from context); MCP executes `tools/call`. |
| **Pure MCP** | Same as above: no micro router; tools/list + tools/call only. |

**MicroSearch** uses the **same executor** (HTTP MCP or direct API) so latency and accuracy differences isolate **who decides** (frontier vs micro), not the backend.

---

## Dimensions (extended)

### 1. Creation / setup (unchanged)

- TTFR, MCP connect, model load.

### 2. Speed / latency (unchanged)

- Retrieval: `retrieval_latency_ms`, `answer_latency_ms`, `total_latency_ms`.
- API: `tool_selection_latency_ms`, `tool_call_latency_ms`, `total_latency_ms`.

### 3. Accuracy (unchanged)

- Retrieval: `hit_at_k`, `answer_correct`, …
- API: `tool_correct`, `args_valid`, `response_success`, …

### 4. Token / dollar cost (unchanged)

- `input_tokens`, `output_tokens`, `cost_usd` per arm (MicroSearch selection path = 0 for frontier when not used).

### 5. **Training time and training-data provenance (new)**

One-time or periodic cost to produce / refresh the micro model or routing dataset **from API surface area**.

| Field | Type | Description |
|-------|------|-------------|
| `training_duration_seconds` | number | Wall-clock time for the training job (fine-tune, LoRA, or batch dataset generation + validation). |
| `training_data_generation_seconds` | number (optional) | If separate: time for frontier model to generate JSONL examples from OpenAPI/endpoints only. |
| `openapi_spec_paths` | string[] | Paths or URIs to specs used (OpenAPI 3.x JSON/YAML). |
| `openapi_sha256` | string (optional) | Hash of canonical spec for reproducibility. |
| `num_openapi_operations` | integer | Count of path×method operations ingested. |
| `num_training_examples` | integer | Rows in supervised dataset (intent → tool + args). |
| `training_backend` | string | e.g. `hf_jobs`, `local_unsloth`, `jsonl_only`, `cursor_manual`. |
| `frontier_model_training_data` | string (optional) | Model that authored examples, e.g. `claude-sonnet-4-20250514`. |

**Recording:** Use `microsearch/scripts/record_training_run.py` after each training or dataset-build. Output appends to `microsearch/results/training_runs.jsonl` (create `results/` on first run).

**Comparison:** When reporting MvM results, attach the latest training run summary so total cost of ownership includes **amortized training** (e.g. `training_duration_seconds / expected_requests_per_day`) if desired.

---

## Inputs allowed for training data

- **OpenAPI 3.0 / 3.1** (JSON or YAML): full spec, including `paths`, `operationId`, `parameters`, `requestBody`, `components.schemas`.
- **Ad-hoc endpoint list**: markdown/JSON list of method, path, summary—paste into the frontier prompt alongside or instead of a full spec.
- **Existing MCP `tools/list` JSON**: can be produced by your MCP server and fed to the same prompt as the tool surface.

All specs are allowed; extremely large specs should be split or summarized in the prompt with a link/path reference.

---

## Presentation of results

Use the existing report (time + content breakdown + speed comparison):

```bash
cd retrieval-eval
python3 experiments/mvm_compare_report.py results/mvm
```

Optionally summarize training runs:

```bash
cd microsearch
python3 scripts/summarize_training_runs.py
```

---

## Test suite mapping

| Goal | Location |
|------|----------|
| Claude Sonnet + MCP tool selection vs micro | `retrieval-eval/experiments/mvm_sample_api_runner.py` (sample API) or `mvm_api_runner.py` (Atlassian) |
| Retrieval track (same as before) | `retrieval-eval/experiments/mvm_retrieval_runner.py` |
| Comparison table | `retrieval-eval/experiments/mvm_compare_report.py` |

Wrap your **test API** with an MCP server (see `templates/MCP_SERVER_FROM_OPENAPI.md`), point `SAMPLE_MCP_URL` (or your env) at it, align **intents** with `training/*.jsonl`, then run the same runners.
