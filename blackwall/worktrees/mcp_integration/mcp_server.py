"""
MCP Server: Exposes our system as an MCP server.
Makes worktrees, Kanban, workflows available via MCP protocol.
"""

import json
import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path

# Try to import MCP SDK
try:
    from mcp import Server, StdioServerParameters
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, Resource
    MCP_SDK_AVAILABLE = True
except ImportError:
    MCP_SDK_AVAILABLE = False
    print("⚠ MCP SDK not installed. Install with: pip install mcp")


class WorktreeMCPServer:
    """
    MCP Server that exposes worktree system capabilities.
    Makes our system accessible via MCP protocol.
    """
    
    def __init__(self):
        """Initialize MCP server."""
        self.server = None
        self.tools: List[Tool] = []
        self.resources: List[Resource] = []
        
        if MCP_SDK_AVAILABLE:
            self._setup_server()
    
    def _setup_server(self):
        """Setup MCP server with tools and resources."""
        if not MCP_SDK_AVAILABLE:
            return
        
        # Define tools
        self.tools = [
            Tool(
                name="create_worktree",
                description="Create a new worktree with agents",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Worktree name"},
                        "agent_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Agent types"
                        }
                    },
                    "required": ["name"]
                }
            ),
            Tool(
                name="query_kanban",
                description="Query Kanban board cards",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "description": "Card status",
                            "enum": ["todo", "in_progress", "review", "done"]
                        }
                    }
                }
            ),
            Tool(
                name="discover_findings",
                description="Discover findings from cross-chat",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Finding category"
                        }
                    }
                }
            )
        ]
        
        # Define resources
        self.resources = [
            Resource(
                uri="worktree://kanban/board",
                name="Kanban Board",
                description="Kanban board state",
                mimeType="application/json"
            ),
            Resource(
                uri="worktree://crosschat/findings",
                name="Cross-Chat Findings",
                description="Findings from cross-chat",
                mimeType="application/json"
            )
        ]
    
    async def handle_tool_call(self, name: str, arguments: Dict) -> Any:
        """
        Handle tool call.
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            Tool result
        """
        if name == "create_worktree":
            from ..unified_system import UnifiedMCPSystem
            system = UnifiedMCPSystem()
            worktree = system.worktree_manager.create_worktree(
                name=arguments.get("name", "New Worktree"),
                agent_types=arguments.get("agent_types", [])
            )
            return {"worktree_id": worktree.worktree_id, "name": worktree.config.name}
        
        elif name == "query_kanban":
            from ..unified_system import UnifiedMCPSystem
            system = UnifiedMCPSystem()
            # Query via Toolbox if available
            return {"status": "queried", "status_filter": arguments.get("status")}
        
        elif name == "discover_findings":
            from ..unified_system import UnifiedMCPSystem
            system = UnifiedMCPSystem()
            findings = system.cross_chat.discover(
                category=arguments.get("category", "general"),
                limit=20
            )
            return {
                "findings": [
                    {"title": f.title, "content": f.content[:100]}
                    for f in findings
                ]
            }
        
        return {"error": f"Unknown tool: {name}"}
    
    async def get_resource(self, uri: str) -> Optional[Dict]:
        """
        Get resource by URI.
        
        Args:
            uri: Resource URI
            
        Returns:
            Resource data
        """
        if uri == "worktree://kanban/board":
            from ..unified_system import UnifiedMCPSystem
            system = UnifiedMCPSystem()
            # Get Kanban board data
            return {"type": "kanban_board", "data": {}}
        
        elif uri == "worktree://crosschat/findings":
            from ..unified_system import UnifiedMCPSystem
            system = UnifiedMCPSystem()
            findings = system.cross_chat.discover(limit=10)
            return {
                "type": "findings",
                "data": [{"title": f.title} for f in findings]
            }
        
        return None
    
    def start(self):
        """Start MCP server (if SDK available)."""
        if not MCP_SDK_AVAILABLE:
            print("⚠ MCP SDK not available. Server cannot start.")
            return
        
        # In real implementation, would use stdio_server
        print("MCP Server would start here (requires MCP SDK setup)")


def create_mcp_server() -> WorktreeMCPServer:
    """Create MCP server instance."""
    return WorktreeMCPServer()
