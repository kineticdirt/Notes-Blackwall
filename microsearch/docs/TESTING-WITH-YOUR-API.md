# Testing with your test API

Use this checklist to run the full framework against **your** test API file (OpenAPI or endpoint list).

## 1. Add your API surface

- Put your **OpenAPI 3.x** file under `microsearch/specs/` (e.g. `specs/my-api.openapi.json`).
- If you only have an endpoint list (method + path + short description), you can paste that into the training-data prompt instead; the OpenAPI converter is optional but recommended for consistent tool names.

## 2. Generate MCP-style tool catalog

From repo root or `microsearch/`:

```bash
cd microsearch
python3 scripts/openapi_to_mcp_tools.py specs/my-api.openapi.json -o generated/tools_catalog.json
```

Use `--strip-meta` to omit `_meta` (method/path) from the JSON if your runner expects strict MCP tool shape.

## 3. Generate training data (frontier model)

- Open **`microsearch/prompts/training_data_generation.md`**.
- Paste `generated/tools_catalog.json` and your OpenAPI (or excerpt) into the prompt.
- Run in **Claude** or **Cursor**; save the model output as **`microsearch/training/intents.jsonl`** (one JSON object per line; validate with the schema in `schemas/training_dataset.schema.json`).

## 4. Record training run (optional but recommended)

After you generate the dataset (and/or after any fine-tune):

```bash
cd microsearch
python3 scripts/record_training_run.py --duration-seconds 0 --generation-seconds 120 \
  --spec specs/my-api.openapi.json \
  --dataset training/intents.jsonl \
  --tools generated/tools_catalog.json \
  --backend jsonl_only \
  --frontier claude-sonnet-4-20250514
```

Use real wall-clock seconds for `--duration-seconds` if you actually ran a training job.

## 5. Expose your API as MCP

You need an MCP server that implements **tools/list** and **tools/call** for the same tools as `tools_catalog.json`.

- **Option A:** Implement by hand (see **`microsearch/templates/MCP_SERVER_FROM_OPENAPI.md`** and **`retrieval-eval/experiments/sample_api_mcp/`**).
- **Option B:** Use any generator (FastMCP, OpenAPI-based MCP template, etc.) so that **tools/list** matches the catalog.

Start the server and note the MCP URL (e.g. `http://127.0.0.1:8765/mcp`).

## 6. Define test intents

The API track needs **(intent, expected_tool, expected_args)** for each test case.

- For the **sample API**, intents live in **`retrieval-eval/experiments/sample_api_intents.py`** (see `SampleIntent`, `get_sample_intents()`).
- For **your API**, add a similar module or JSONL of intents and point the runner at it (or extend `mvm_sample_api_runner.py` to load intents from a file).

Ensure each intent’s `expected_tool` matches a tool name from `tools_catalog.json`.

## 7. Run MvM API track

From **`retrieval-eval/`**:

```bash
cd retrieval-eval
# Set your MCP URL (sample API default: http://127.0.0.1:8765/mcp)
export SAMPLE_MCP_URL=http://127.0.0.1:8765/mcp

# Claude API key for MCP arm
# (paste key in retrieval-eval/.api-key or set ANTHROPIC_API_KEY)

python3 experiments/mvm_sample_api_runner.py --limit 5 --nano-type keyword
# or --nano-type qwen4b if you have the 4B router wired
```

If your API is not the sample API, use a runner that calls your MCP (e.g. duplicate `mvm_sample_api_runner.py` and change `list_tools` / `call_tool` to your client and intents to your list).

## 8. View comparison results

```bash
cd retrieval-eval
python3 experiments/mvm_compare_report.py results/mvm
```

Optional: summarize training runs:

```bash
cd microsearch
python3 scripts/summarize_training_runs.py
```

---

## Summary

| Step | Where | Output |
|------|--------|--------|
| OpenAPI → tools | `microsearch/scripts/openapi_to_mcp_tools.py` | `generated/tools_catalog.json` |
| Training data | `microsearch/prompts/` + Claude/Cursor | `training/intents.jsonl` |
| Training time | `microsearch/scripts/record_training_run.py` | `results/training_runs.jsonl` |
| MCP server | Your code + `templates/MCP_SERVER_FROM_OPENAPI.md` | Running server URL |
| Test intents | Your module or JSONL | Intent list for runner |
| MvM run | `retrieval-eval/experiments/mvm_sample_api_runner.py` (or your runner) | `results/mvm/*.jsonl` |
| Report | `retrieval-eval/experiments/mvm_compare_report.py` | Comparison table + speed + cost |
