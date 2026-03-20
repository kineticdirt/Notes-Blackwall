"""
Sample REST API + MCP server: real-world patterns (list, get by id, search).
Run: uvicorn experiments.sample_api_mcp.api:app --host 0.0.0.0 --port 8765
Then: MCP at POST http://localhost:8765/mcp (no auth).
"""
from __future__ import annotations

import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from . import data
from .mcp_tools import TOOLS_SCHEMA, execute_tool

app = FastAPI(title="Sample API", description="Real-world style: list, get, search + MCP")


@app.get("/api/posts")
def list_posts(limit: int = 10, offset: int = 0):
    """List posts with optional pagination."""
    end = offset + limit
    return data.POSTS[offset:end]


@app.get("/api/posts/{post_id:int}")
def get_post(post_id: int):
    """Get a single post by id."""
    for p in data.POSTS:
        if p["id"] == post_id:
            return p
    raise HTTPException(status_code=404, detail="Post not found")


@app.get("/api/posts/search")
def search_posts(q: str = ""):
    """Search posts by title or body (case-insensitive)."""
    if not q:
        return data.POSTS[:10]
    ql = q.lower()
    return [p for p in data.POSTS if ql in p["title"].lower() or ql in p["body"].lower()]


@app.get("/api/users")
def list_users(limit: int = 10, offset: int = 0):
    """List users with optional pagination."""
    end = offset + limit
    return data.USERS[offset:end]


@app.get("/api/users/{user_id:int}")
def get_user(user_id: int):
    """Get a single user by id."""
    for u in data.USERS:
        if u["id"] == user_id:
            return u
    raise HTTPException(status_code=404, detail="User not found")


# ---- MCP endpoint (JSON-RPC over POST) ----
@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """JSON-RPC: initialize, tools/list, tools/call. No auth for local sample."""
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
                "serverInfo": {"name": "sample-api-mcp", "version": "0.1.0"},
            },
        })
    if method == "tools/list":
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": TOOLS_SCHEMA},
        })
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
