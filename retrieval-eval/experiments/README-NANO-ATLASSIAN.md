# Nano as primary interface; MCP fallback

The **small model replaces the MCP server** as the primary interface: it feeds and interfaces with your API (Jira, Confluence, etc.) and acts as the **AI in the middle**. Focus on **logic and repeatability**; use **MCP only as fallback** when the nano can’t handle the request.

## 1. Env (no secrets in code)

From your MCP config (e.g. `~/.cursor/mcp.json`), set:

```bash
export ATLASSIAN_MCP_URL=https://ztaib-qj3ty3na-e4l2dawa5a-uc.a.run.app/mcp
export ATLASSIAN_MCP_BEARER=<your Bearer token>
```

Optional for Jira/Confluence calls that need a cloud ID:

```bash
export ATLASSIAN_CLOUD_ID=<cloud UUID from getAccessibleAtlassianResources>
```

## 2. Run: nano primary, MCP fallback

**Recommended:** `nano_primary_mcp_fallback.py` — nano (logic + optional SmolLM) → primary executor (MCP today); on no-tool or failure → MCP fallback.

```bash
cd retrieval-eval
python3 experiments/nano_primary_mcp_fallback.py "what Atlassian resources can I access?"
python3 experiments/nano_primary_mcp_fallback.py "list Confluence spaces" --smol
python3 experiments/nano_primary_mcp_fallback.py --list-tools-only
```

Legacy (nano → MCP only): `nano_atlassian_runner.py`.

## 3. SmolLM3-3B (when keyword logic has no match)

Install deps (~6GB+ RAM or GPU for 3B):

```bash
pip install -r experiments/requirements-nano.txt
```

Then:

```bash
python3 experiments/nano_primary_mcp_fallback.py "search Jira for recent bugs" --smol
```

The first `--smol` run will download `HuggingFaceTB/SmolLM3-3B-Base` once.

## 4. SSL certificate errors

If you see `SSL: CERTIFICATE_VERIFY_FAILED`, fix your Python/cert store (e.g. macOS: run the “Install Certificates” command from your Python install, or use a venv with certifi).

## Files

| File | Role |
|------|------|
| `atlassian_http_mcp.py` | HTTP MCP client (POST JSON-RPC, Bearer). Used by primary executor and fallback. |
| `smol_nano.py` | SmolLM3-3B: intent + tool list → JSON (tool, arguments). |
| `nano_primary_mcp_fallback.py` | **Nano primary**, MCP fallback; logic + repeatability first. |
| `nano_atlassian_runner.py` | Legacy: nano → MCP only (no fallback flow). |
