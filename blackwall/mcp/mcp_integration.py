"""
MCP (Model Context Protocol) integration for Blackwall.
MCP enables tools and resources to be exposed to Claude.
"""

from typing import Dict, List, Optional, Any
import json
from pathlib import Path


class MCPIntegration:
    """
    Integrates Blackwall with Model Context Protocol.
    Exposes Blackwall tools and resources to Claude via MCP.
    """
    
    def __init__(self):
        """Initialize MCP integration."""
        self.available_tools = self._discover_tools()
        self.available_resources = self._discover_resources()
    
    def _discover_tools(self) -> Dict[str, Dict]:
        """
        Discover available MCP tools.
        These are the tools available in the Claude environment.
        """
        # These are the tools available in this Claude environment
        # They're part of the Blackwall system
        tools = {
            "read_file": {
                "name": "read_file",
                "description": "Read file contents",
                "parameters": {
                    "target_file": {"type": "string", "description": "File path"}
                }
            },
            "write_file": {
                "name": "write_file",
                "description": "Write content to file",
                "parameters": {
                    "file_path": {"type": "string"},
                    "contents": {"type": "string"}
                }
            },
            "codebase_search": {
                "name": "codebase_search",
                "description": "Semantic search in codebase",
                "parameters": {
                    "query": {"type": "string"},
                    "target_directories": {"type": "array"}
                }
            },
            "grep": {
                "name": "grep",
                "description": "Search for patterns in files",
                "parameters": {
                    "pattern": {"type": "string"},
                    "path": {"type": "string"}
                }
            },
            "run_terminal_cmd": {
                "name": "run_terminal_cmd",
                "description": "Execute terminal command",
                "parameters": {
                    "command": {"type": "string"},
                    "is_background": {"type": "boolean"}
                }
            },
            "read_lints": {
                "name": "read_lints",
                "description": "Read linter errors",
                "parameters": {
                    "paths": {"type": "array"}
                }
            }
        }
        
        return tools
    
    def _discover_resources(self) -> Dict[str, Dict]:
        """
        Discover available MCP resources.
        Resources are data that can be accessed by tools.
        """
        resources = {
            "ledger": {
                "uri": "ledger://ai_groupchat",
                "name": "AI GroupChat Ledger",
                "description": "Shared communication ledger for agents",
                "mimeType": "application/json"
            },
            "scratchpad": {
                "uri": "scratchpad://shared",
                "name": "Shared Scratchpad",
                "description": "Shared notes and context for agents",
                "mimeType": "application/json"
            },
            "registry": {
                "uri": "registry://blackwall",
                "name": "Blackwall Registry",
                "description": "Content tracking registry",
                "mimeType": "application/json"
            }
        }
        
        return resources
    
    def get_tool_schema(self, tool_name: str) -> Optional[Dict]:
        """Get schema for a specific tool."""
        return self.available_tools.get(tool_name)
    
    def list_tools(self) -> List[str]:
        """List all available tool names."""
        return list(self.available_tools.keys())
    
    def list_resources(self) -> List[Dict]:
        """List all available resources."""
        return list(self.available_resources.values())
    
    def create_mcp_server_config(self) -> Dict:
        """
        Create MCP server configuration for Blackwall.
        This would be used to expose Blackwall as an MCP server.
        """
        config = {
            "name": "blackwall-mcp",
            "version": "0.1.0",
            "description": "Blackwall AI Protection System MCP Server",
            "tools": list(self.available_tools.values()),
            "resources": list(self.available_resources.values())
        }
        
        return config
    
    def export_mcp_config(self, output_path: str = "blackwall_mcp_config.json"):
        """Export MCP configuration to file."""
        config = self.create_mcp_server_config()
        
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return output_path
