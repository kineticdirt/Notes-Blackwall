# Prompt: generate MicroSearch training data from an API (OpenAPI + endpoints)

Use this with **Claude**, **Cursor**, or any frontier model. Attach:

1. **OpenAPI 3.x** document (JSON or YAML)—full spec preferred; partial specs OK if you list missing paths.
2. **`tools_catalog.json`** — output of `python3 scripts/openapi_to_mcp_tools.py your-spec.json -o generated/tools_catalog.json` (MCP-shaped tools).
3. Optional: **base URL** and **auth rules** (describe placeholders only; never paste real secrets).

---

## System / instructions (paste as system or first message)

You are generating **supervised training data** for a small routing model. The model must map **user intent** → **exactly one** MCP tool name and **JSON arguments** matching the tool's `inputSchema`.

Rules:

- Output **only** valid **JSONL**: one JSON object per line, no markdown fences.
- Each object MUST match this shape (extra keys allowed):
  - `intent` (string): natural, varied user phrasing.
  - `expected_tool` (string): MUST equal a `name` from the provided tools list.
  - `expected_arguments` (object): valid per `inputSchema`; use `"<PLACEHOLDER>"` for secrets, tokens, unknown IDs.
  - `source_operation` (string, optional): e.g. `GET /pets/{petId}`.
  - `tags` (array of strings, optional).
- Cover **every** tool at least twice (different paraphrases).
- Include **edge cases**: missing optional params, pagination, ambiguous wording that still maps to one best tool.
- Include **5–10%** `negative_intent: true` rows where **no** tool should be called (out-of-scope); set `expected_tool` to `"__none__"` and `expected_arguments` to `{}` if your trainer expects that convention, OR omit those rows if your pipeline does not support negatives—state which convention you used in a single leading comment line starting with `#` (then delete that line before JSONL import).
- Do **not** invent tools not in the catalog.

---

## User message template

```
Tools catalog (JSON array):
<<<PASTE tools_catalog.json HERE>>>

OpenAPI spec (full or excerpt):
<<<PASTE OPENAPI HERE OR SAY "see attached file">>>

Task: Emit N=<<<NUMBER>>> lines of JSONL following the rules above.
Prioritize diverse intents aligned with real support and developer queries.
```

---

## After generation

1. Validate lines with `jq` or a small Python loop.
2. Save as `microsearch/training/intents.jsonl` (or project path).
3. Record training time: `python3 scripts/record_training_run.py ...`
