"""
Dynamic MCP client: connect to MCP services on the fly and expose their tools.
Loads server config from PI_MCP_CONFIG or .mcp.json (mcpServers key).
Supports stdio (command/args) and optional streamable-http (url/headers).
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent

# Optional: MCP SDK for real connections
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    ClientSession = None
    StdioServerParameters = None
    stdio_client = None


def _config_path() -> Path:
    path = os.environ.get("PI_MCP_CONFIG", "")
    if path:
        return Path(path).resolve()
    # Default: project .mcp.json
    for candidate in [REPO_ROOT / ".mcp.json", Path.cwd() / ".mcp.json"]:
        if candidate.exists():
            return candidate
    return REPO_ROOT / ".mcp.json"


def _load_server_config() -> Dict[str, Any]:
    """Load MCP servers from PI_MCP_CONFIG/.mcp.json and from user config (assistant/config/user_config.yaml). Merged."""
    result = {}
    path = _config_path()
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            servers = data.get("mcpServers") or data.get("servers") or {}
            result.update(dict(servers))
        except (json.JSONDecodeError, OSError):
            pass
    try:
        from assistant.user_config_loader import get_user_config_mcp_servers
        result.update(get_user_config_mcp_servers())
    except Exception:
        pass
    return result


def _mcp_tool_to_openai(tool: Any, server_id: str) -> Dict[str, Any]:
    """Convert MCP tool to OpenAI function tool format. Prefix name with server_id to avoid clashes."""
    name = getattr(tool, "name", str(tool))
    desc = getattr(tool, "description", None) or ""
    params = getattr(tool, "inputSchema", None) or {}
    prefixed_name = f"{server_id}_{name}" if server_id else name
    return {
        "type": "function",
        "function": {
            "name": prefixed_name,
            "description": desc,
            "parameters": params if isinstance(params, dict) else {"type": "object", "properties": {}},
        },
    }


async def _connect_stdio(server_id: str, config: Dict[str, Any]) -> Optional[ClientSession]:
    """Connect to one stdio MCP server. Returns ClientSession or None."""
    if not MCP_AVAILABLE:
        return None
    cmd = config.get("command")
    args = config.get("args") or []
    env = config.get("env") or {}
    if not cmd:
        return None
    params = StdioServerParameters(command=cmd, args=list(args), env=env)
    try:
        read, write = await stdio_client(params)
        session = ClientSession(read, write)
        await session.initialize()
        return session
    except Exception:
        return None


class MCPDynamicPool:
    """Holds connections to MCP servers and routes tool calls."""

    def __init__(self):
        self.sessions: Dict[str, Any] = {}
        self.tool_to_server: Dict[str, str] = {}
        self.openai_tools: List[Dict[str, Any]] = []
        self._config = _load_server_config()

    async def connect_all(self) -> None:
        """Connect to all stdio servers in config. HTTP servers can be added later."""
        if not MCP_AVAILABLE:
            return
        for server_id, config in self._config.items():
            if config.get("url") or config.get("transport") == "streamable-http":
                continue
            session = await _connect_stdio(server_id, config)
            if session is None:
                continue
            self.sessions[server_id] = session
            try:
                resp = await session.list_tools()
                tools = getattr(resp, "tools", []) or []
                for t in tools:
                    name = getattr(t, "name", None) or str(t)
                    prefixed = f"{server_id}_{name}"
                    self.tool_to_server[prefixed] = server_id
                    self.openai_tools.append(_mcp_tool_to_openai(t, server_id))
            except Exception:
                await session.__aexit__(None, None, None)
                del self.sessions[server_id]

    def get_openai_tools(self) -> List[Dict[str, Any]]:
        return list(self.openai_tools)

    def get_all_tool_names(self) -> List[str]:
        return list(self.tool_to_server.keys())

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call a tool by its prefixed name. Returns result string."""
        server_id = self.tool_to_server.get(tool_name)
        if not server_id:
            return f"Unknown MCP tool: {tool_name}"
        session = self.sessions.get(server_id)
        if session is None:
            return f"MCP server not connected: {server_id}"
        raw_name = tool_name[len(server_id) + 1:] if tool_name.startswith(server_id + "_") else tool_name
        try:
            result = await session.call_tool(raw_name, arguments)
            content = getattr(result, "content", None)
            if content is None:
                return str(result)
            if isinstance(content, list):
                parts = []
                for c in content:
                    if getattr(c, "type", None) == "text":
                        parts.append(getattr(c, "text", str(c)))
                    else:
                        parts.append(str(c))
                return "\n".join(parts)
            if isinstance(content, str):
                return content
            return json.dumps(content) if isinstance(content, (dict, list)) else str(content)
        except Exception as e:
            return f"Tool error: {e}"

    async def close_all(self) -> None:
        for session in self.sessions.values():
            try:
                await session.__aexit__(None, None, None)
            except Exception:
                pass
        self.sessions.clear()
        self.tool_to_server.clear()
        self.openai_tools.clear()


# Global pool (lazy init)
_pool: Optional[MCPDynamicPool] = None


def get_pool() -> MCPDynamicPool:
    global _pool
    if _pool is None:
        _pool = MCPDynamicPool()
    return _pool


def run_async(coro):
    return asyncio.run(coro)


def ensure_connected() -> bool:
    """Connect to all configured MCP servers (sync wrapper)."""
    pool = get_pool()
    if not pool.sessions and not pool.openai_tools:
        run_async(pool.connect_all())
    return len(pool.sessions) > 0


def get_dynamic_tool_definitions() -> List[Dict[str, Any]]:
    """OpenAI-format tool definitions from all connected MCP servers."""
    ensure_connected()
    return get_pool().get_openai_tools()


def get_dynamic_tool_names() -> List[str]:
    ensure_connected()
    return get_pool().get_all_tool_names()


def call_dynamic_tool_sync(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Call an MCP tool synchronously."""
    return run_async(get_pool().call_tool(tool_name, arguments))
