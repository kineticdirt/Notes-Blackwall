"""
MCP tool definitions and execution for sample API (real-world patterns).
"""
from __future__ import annotations

import json
from . import data

TOOLS_SCHEMA = [
    {
        "name": "listPosts",
        "description": "List posts with optional pagination. Returns up to limit posts starting at offset.",
        "inputSchema": {
            "type": "object",
            "properties": {"limit": {"type": "integer", "description": "Max items (default 10)"}, "offset": {"type": "integer", "description": "Skip N items"}},
            "required": [],
        },
    },
    {
        "name": "getPost",
        "description": "Get a single post by id.",
        "inputSchema": {"type": "object", "properties": {"id": {"type": "integer"}}, "required": ["id"]},
    },
    {
        "name": "searchPosts",
        "description": "Search posts by title or body (case-insensitive).",
        "inputSchema": {"type": "object", "properties": {"q": {"type": "string"}}, "required": ["q"]},
    },
    {
        "name": "listUsers",
        "description": "List users with optional pagination.",
        "inputSchema": {
            "type": "object",
            "properties": {"limit": {"type": "integer"}, "offset": {"type": "integer"}},
            "required": [],
        },
    },
    {
        "name": "getUser",
        "description": "Get a single user by id.",
        "inputSchema": {"type": "object", "properties": {"id": {"type": "integer"}}, "required": ["id"]},
    },
]


def execute_tool(name: str, arguments: dict) -> tuple[str, bool]:
    """Run tool against in-memory data. Returns (text_content, is_error)."""
    args = arguments or {}
    try:
        if name == "listPosts":
            limit = int(args.get("limit", 10))
            offset = int(args.get("offset", 0))
            out = data.POSTS[offset : offset + limit]
        elif name == "getPost":
            pid = int(args.get("id"))
            out = next((p for p in data.POSTS if p["id"] == pid), None)
            if out is None:
                return json.dumps({"error": "Post not found"}), True
        elif name == "searchPosts":
            q = str(args.get("q", "")).strip()
            if not q:
                out = data.POSTS[:10]
            else:
                ql = q.lower()
                out = [p for p in data.POSTS if ql in p["title"].lower() or ql in p["body"].lower()]
        elif name == "listUsers":
            limit = int(args.get("limit", 10))
            offset = int(args.get("offset", 0))
            out = data.USERS[offset : offset + limit]
        elif name == "getUser":
            uid = int(args.get("id"))
            out = next((u for u in data.USERS if u["id"] == uid), None)
            if out is None:
                return json.dumps({"error": "User not found"}), True
        else:
            return json.dumps({"error": f"Unknown tool: {name}"}), True
        return json.dumps(out, indent=2), False
    except (TypeError, ValueError) as e:
        return json.dumps({"error": str(e)}), True
