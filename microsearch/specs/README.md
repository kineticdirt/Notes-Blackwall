# API specs

Place **OpenAPI 3.x** files here (e.g. `my-api.openapi.json` or `.yaml`).

- Do not commit specs that contain secrets or internal-only URLs.
- Generate tool catalog: from `microsearch/` run  
  `python3 scripts/openapi_to_mcp_tools.py specs/your-file.json -o generated/tools_catalog.json`
