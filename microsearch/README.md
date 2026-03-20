# MicroSearch framework

Self-contained definition for **MicroSearch** (nano/micro model as primary router; MCP + frontier as baseline and fallback). This folder complements **`retrieval-eval/`** (MvM comparison runners and reports).

## What you get

1. **Training data from APIs** — Use a frontier model (Claude, Cursor, etc.) with the prompt in `prompts/` plus an **OpenAPI 3.x** spec and/or endpoint list. Normalize tools with `scripts/openapi_to_mcp_tools.py`.
2. **Training time in the eval frame** — Log wall-clock training duration and provenance with `scripts/record_training_run.py` (see `docs/FRAMEWORK.md`).
3. **Test vs Claude Sonnet + pure MCP** — Use the existing suite:
   - **Sample API + MCP:** `retrieval-eval/experiments/mvm_sample_api_runner.py` + `sample_api_mcp` (see `templates/MCP_SERVER_FROM_OPENAPI.md` to mirror your API).
   - **Atlassian / other:** `retrieval-eval/experiments/mvm_api_runner.py` with env vars.
4. **Comparison results** — Same report as before (latency, accuracy, cost, time breakdown):
   ```bash
   cd retrieval-eval
   python3 experiments/mvm_compare_report.py results/mvm
   ```

## Quick path (after you clear terminal)

```bash
cd "/Users/abhinav/Desktop/Cequence BlackWall/microsearch"
```

1. Put your **OpenAPI** file under `specs/` (e.g. `specs/my-api.openapi.json`).
2. Generate MCP-shaped tool list:
   ```bash
   python3 scripts/openapi_to_mcp_tools.py specs/my-api.openapi.json -o generated/tools_catalog.json
   ```
3. In Cursor or Claude, use `prompts/training_data_generation.md` + `tools_catalog.json` + your spec → save JSONL under `training/` (see `schemas/training_dataset.schema.json`).
4. After fine-tuning or dataset build, record training time:
   ```bash
   python3 scripts/record_training_run.py --duration-seconds 3600 --spec specs/my-api.openapi.json --dataset training/intents.jsonl --tools generated/tools_catalog.json
   ```
5. Run your API + MCP server, then MvM (see `retrieval-eval/experiments/README-MVM.md` and `README-MVM.md` for sample API).

## Layout

| Path | Purpose |
|------|---------|
| `docs/FRAMEWORK.md` | Metrics including **training time**; arms; comparison dimensions |
| `schemas/` | JSON Schemas for training datasets and training-run manifests |
| `prompts/` | Frontier-model prompt to emit training examples from OpenAPI |
| `scripts/` | OpenAPI → tools, record training runs |
| `templates/` | How to expose an HTTP API as MCP for pure-MCP baseline |
| `specs/` | Your OpenAPI files (gitignored examples can live in `examples/`) |
| `training/` | Generated training JSONL (gitignored) |
| `generated/` | Tool catalogs and build artifacts (gitignored) |

## Security

- Do not commit API keys, bearer tokens, or customer OpenAPI with secrets.
- Use placeholders in generated training data for auth headers.

## See also

- `docs/plans/2026-03-18-MCP-VS-MICROSEARCH-TEST-FRAME.md` — MvM test frame
- `docs/plans/MICROSEARCH-ARCHITECTURE-PROBE.md` — architecture probe
- `retrieval-eval/experiments/README-MVM.md` — runners and metrics
