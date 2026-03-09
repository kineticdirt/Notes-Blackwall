"""
MCP Jam: Connects multiple MCP servers together.
"Jam" multiple MCP servers into one unified interface.
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class MCPServerInfo:
    """Information about an MCP server."""
    server_id: str
    name: str
    command: str
    args: List[str]
    env: Dict[str, str]
    tools: List[str] = None
    resources: List[str] = None
    
    def __post_init__(self):
        if self.tools is None:
            self.tools = []
        if self.resources is None:
            self.resources = []


class MCPServerConnector:
    """
    Connects to an MCP server.
    In a real implementation, this would use MCP SDK to connect.
    """
    
    def __init__(self, server_info: MCPServerInfo):
        """
        Initialize MCP server connector.
        
        Args:
            server_info: Server information
        """
        self.server_info = server_info
        self.connected = False
        self.available_tools: List[str] = []
        self.available_resources: List[str] = []
    
    def connect(self) -> bool:
        """Connect to MCP server."""
        # In real implementation, would use MCP SDK
        # For now, simulate connection
        self.connected = True
        self.available_tools = self.server_info.tools or []
        self.available_resources = self.server_info.resources or []
        return True
    
    def disconnect(self):
        """Disconnect from MCP server."""
        self.connected = False
    
    def list_tools(self) -> List[str]:
        """List available tools."""
        return self.available_tools
    
    def list_resources(self) -> List[str]:
        """List available resources."""
        return self.available_resources
    
    def call_tool(self, tool_name: str, **kwargs) -> Any:
        """Call a tool on the MCP server."""
        if not self.connected:
            raise RuntimeError("Not connected to MCP server")
        
        if tool_name not in self.available_tools:
            raise ValueError(f"Tool '{tool_name}' not available")
        
        # In real implementation, would call via MCP protocol
        return {"tool": tool_name, "args": kwargs, "status": "called"}


class MCPJam:
    """
    MCP Jam: Jams multiple MCP servers together.
    Provides unified access to tools and resources from multiple servers.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize MCP Jam.
        
        Args:
            config_path: Path to MCP servers configuration
        """
        self.config_path = config_path or Path(".mcp-jam") / "servers.json"
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.servers: Dict[str, MCPServerConnector] = {}
        self.server_configs: Dict[str, MCPServerInfo] = {}
        
        self._load_config()
        self._connect_servers()
    
    def _load_config(self):
        """Load MCP server configurations."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    for server_id, server_config in config.get("servers", {}).items():
                        server_info = MCPServerInfo(
                            server_id=server_id,
                            name=server_config.get("name", server_id),
                            command=server_config.get("command", ""),
                            args=server_config.get("args", []),
                            env=server_config.get("env", {}),
                            tools=server_config.get("tools", []),
                            resources=server_config.get("resources", [])
                        )
                        self.server_configs[server_id] = server_info
            except Exception as e:
                print(f"Warning: Failed to load MCP config: {e}")
    
    def _connect_servers(self):
        """Connect to all configured servers."""
        for server_id, server_info in self.server_configs.items():
            connector = MCPServerConnector(server_info)
            if connector.connect():
                self.servers[server_id] = connector
                print(f"✓ Connected to MCP server: {server_info.name}")
    
    def add_server(self, server_info: MCPServerInfo):
        """Add a new MCP server."""
        self.server_configs[server_info.server_id] = server_info
        
        connector = MCPServerConnector(server_info)
        if connector.connect():
            self.servers[server_info.server_id] = connector
        
        # Save config
        self._save_config()
    
    def _save_config(self):
        """Save server configuration."""
        config = {
            "servers": {
                server_id: {
                    "name": info.name,
                    "command": info.command,
                    "args": info.args,
                    "env": info.env,
                    "tools": info.tools,
                    "resources": info.resources
                }
                for server_id, info in self.server_configs.items()
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def list_all_tools(self) -> Dict[str, List[str]]:
        """List all tools from all servers."""
        return {
            server_id: connector.list_tools()
            for server_id, connector in self.servers.items()
        }
    
    def list_all_resources(self) -> Dict[str, List[str]]:
        """List all resources from all servers."""
        return {
            server_id: connector.list_resources()
            for server_id, connector in self.servers.items()
        }
    
    def call_tool(self, tool_name: str, server_id: Optional[str] = None, **kwargs) -> Any:
        """
        Call a tool from any server.
        
        Args:
            tool_name: Name of tool to call
            server_id: Specific server ID (None = search all)
            **kwargs: Tool arguments
            
        Returns:
            Tool result
        """
        if server_id:
            if server_id not in self.servers:
                raise ValueError(f"Server {server_id} not found")
            return self.servers[server_id].call_tool(tool_name, **kwargs)
        
        # Search all servers
        for server_id, connector in self.servers.items():
            if tool_name in connector.list_tools():
                return connector.call_tool(tool_name, **kwargs)
        
        raise ValueError(f"Tool '{tool_name}' not found in any server")
    
    def get_status(self) -> Dict:
        """Get MCP Jam status."""
        return {
            "connected_servers": len(self.servers),
            "servers": {
                server_id: {
                    "name": info.name,
                    "tools": len(connector.list_tools()),
                    "resources": len(connector.list_resources())
                }
                for server_id, (info, connector) in zip(
                    self.server_configs.keys(),
                    zip(self.server_configs.values(), self.servers.values())
                )
            }
        }
