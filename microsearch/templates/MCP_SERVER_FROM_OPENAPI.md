# Exposing your HTTP API as MCP (for “pure MCP” + Claude Sonnet baseline)

The MvM **API track** needs:

1. An MCP server that implements **`initialize`**, **`tools/list`**, and **`tools/call`** (or your HTTP MCP bridge).
2. Tool names and `inputSchema` aligned with what the **micro model** and **Claude** see.

## Recommended approach

1. **Derive tool definitions** from OpenAPI:
   ```bash
   cd microsearch
   python3 scripts/openapi_to_mcp_tools.py specs/your-api.json -o generated/tools_catalog.json
   ```
2. **Implement handlers** that map each tool name to your REST routes (same as `retrieval-eval/experiments/sample_api_mcp/` does manually).

Reference implementation to copy from:

- `retrieval-eval/experiments/sample_api_mcp/api.py` — FastAPI app + MCP endpoint.
- `retrieval-eval/experiments/sample_api_mcp/mcp_tools.py` — `TOOLS_SCHEMA` + `execute_tool`.
- `retrieval-eval/experiments/sample_http_mcp.py` — HTTP MCP client used by `mvm_sample_api_runner.py`.

## Checklist

- [ ] Each OpenAPI operation you care about has a **stable tool name** (use `operationId` in the spec for consistency).
- [ ] Path and query parameters appear in `inputSchema.properties` with correct `required`.
- [ ] MCP server returns JSON-serializable text from `tools/call`.
- [ ] Set env for runners, e.g. `SAMPLE_MCP_URL=http://127.0.0.1:8765/mcp` (see sample README).

## Generated servers (optional)

You may use **openapi-generator**, **FastMCP**, or **Smithery** templates—any stack is fine as long as **tools/list** matches `tools_catalog.json` and the executor behavior matches your REST API.

## Security

- Do not embed production credentials in tool schemas.
- Prefer short-lived tokens via env on the server side.
