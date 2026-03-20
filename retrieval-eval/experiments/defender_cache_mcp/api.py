"""
Defender mitigator cache API + MCP server. Proxies to DEFENDER_BASE_URL (default http://localhost:9999).
Run: uvicorn experiments.defender_cache_mcp.api:app --host 127.0.0.1 --port 8766
MCP: POST http://127.0.0.1:8766/mcp
"""
from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse

from fastapi import FastAPI

from .mcp_tools import TOOLS_SCHEMA, execute_tool

app = FastAPI(title="Defender cache MCP", description="Proxy to __cq/cache/*")


@app.post("/mcp")
async def mcp_endpoint(request: Request):
    body = await request.json()
    msg_id = body.get("id")
    method = body.get("method")
    params = body.get("params") or {}
    if method == "initialize":
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "serverInfo": {"name": "defender-cache-mcp", "version": "0.1.0"},
            },
        })
    if method == "tools/list":
        return JSONResponse({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS_SCHEMA}})
    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments") or {}
        if not name:
            return JSONResponse({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32602, "message": "Missing name"}})
        text, is_error = execute_tool(name, arguments)
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"content": [{"type": "text", "text": text}], "isError": is_error},
        })
    return JSONResponse({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method not found: {method}"}})
