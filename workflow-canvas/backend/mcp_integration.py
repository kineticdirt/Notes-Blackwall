"""
MCP (Model Context Protocol) integration for workflow canvas.
Allows connecting and orchestrating MCP tools in workflows.
"""

from typing import Dict, List, Any, Optional, AsyncIterator
import asyncio
import json
from datetime import datetime
import uuid


class MCPTool:
    """Represents an MCP tool that can be used in workflows."""
    
    def __init__(self, tool_id: str, name: str, description: str, 
                 parameters: Dict[str, Any], server: Optional[str] = None):
        """
        Initialize MCP tool.
        
        Args:
            tool_id: Unique tool identifier
            name: Tool name
            description: Tool description
            parameters: Tool parameters schema
            server: MCP server identifier (optional)
        """
        self.tool_id = tool_id
        self.name = name
        self.description = description
        self.parameters = parameters
        self.server = server
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "server": self.server,
            "created_at": self.created_at
        }


class MCPToolRegistry:
    """Registry of available MCP tools."""
    
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self._initialize_default_tools()
    
    def _initialize_default_tools(self):
        """Initialize default MCP tools."""
        # File operations
        self.register_tool(MCPTool(
            tool_id="mcp_file_read",
            name="Read File",
            description="Read content from a file",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path"}
                },
                "required": ["path"]
            },
            server="filesystem"
        ))
        
        self.register_tool(MCPTool(
            tool_id="mcp_file_write",
            name="Write File",
            description="Write content to a file",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path"},
                    "content": {"type": "string", "description": "File content"}
                },
                "required": ["path", "content"]
            },
            server="filesystem"
        ))
        
        # Database operations
        self.register_tool(MCPTool(
            tool_id="mcp_db_query",
            name="Database Query",
            description="Execute a database query",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "SQL query"},
                    "database": {"type": "string", "description": "Database name"}
                },
                "required": ["query"]
            },
            server="database"
        ))
        
        # HTTP operations
        self.register_tool(MCPTool(
            tool_id="mcp_http_request",
            name="HTTP Request",
            description="Make an HTTP request",
            parameters={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Request URL"},
                    "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"]},
                    "headers": {"type": "object", "description": "Request headers"},
                    "body": {"type": "object", "description": "Request body"}
                },
                "required": ["url", "method"]
            },
            server="http"
        ))
        
        # AI/LLM operations
        self.register_tool(MCPTool(
            tool_id="mcp_llm_complete",
            name="LLM Complete",
            description="Complete text using LLM",
            parameters={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Prompt text"},
                    "model": {"type": "string", "description": "Model name"},
                    "temperature": {"type": "number", "description": "Temperature"}
                },
                "required": ["prompt"]
            },
            server="llm"
        ))
    
    def register_tool(self, tool: MCPTool):
        """Register an MCP tool."""
        self.tools[tool.tool_id] = tool
    
    def get_tool(self, tool_id: str) -> Optional[MCPTool]:
        """Get a tool by ID."""
        return self.tools.get(tool_id)
    
    def list_tools(self) -> List[Dict]:
        """List all registered tools."""
        return [tool.to_dict() for tool in self.tools.values()]
    
    def get_tools_by_server(self, server: str) -> List[Dict]:
        """Get tools by server."""
        return [
            tool.to_dict() for tool in self.tools.values()
            if tool.server == server
        ]


class MCPExecutor:
    """Executes MCP tools in workflows."""
    
    def __init__(self):
        self.registry = MCPToolRegistry()
        self.execution_history: List[Dict] = []
    
    async def execute_tool(self, tool_id: str, parameters: Dict[str, Any],
                          context: Optional[Dict] = None) -> Any:
        """
        Execute an MCP tool.
        
        Args:
            tool_id: Tool identifier
            parameters: Tool parameters
            context: Execution context
            
        Returns:
            Tool execution result
        """
        tool = self.registry.get_tool(tool_id)
        if not tool:
            raise ValueError(f"Tool {tool_id} not found")
        
        # Simulate MCP tool execution
        # In production, this would call actual MCP servers
        result = await self._execute_mcp_tool(tool, parameters, context)
        
        # Log execution
        self.execution_history.append({
            "tool_id": tool_id,
            "parameters": parameters,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    async def _execute_mcp_tool(self, tool: MCPTool, parameters: Dict,
                                context: Optional[Dict]) -> Any:
        """Execute a specific MCP tool."""
        # Simulate execution based on tool type
        if tool.tool_id == "mcp_file_read":
            # In production, would use actual file system MCP
            return {"content": f"Simulated file content from {parameters.get('path')}"}
        
        elif tool.tool_id == "mcp_file_write":
            return {"success": True, "path": parameters.get("path")}
        
        elif tool.tool_id == "mcp_db_query":
            return {"rows": [], "count": 0}
        
        elif tool.tool_id == "mcp_http_request":
            # In production, would make actual HTTP request
            return {
                "status": 200,
                "body": {"message": "Simulated HTTP response"}
            }
        
        elif tool.tool_id == "mcp_llm_complete":
            # In production, would call actual LLM
            return {
                "text": f"Simulated LLM completion for: {parameters.get('prompt')[:50]}..."
            }
        
        else:
            return {"result": "Tool executed", "parameters": parameters}
    
    async def execute_tool_stream(self, tool_id: str, parameters: Dict[str, Any],
                                 context: Optional[Dict] = None) -> AsyncIterator[Dict]:
        """Execute tool with streaming output."""
        yield {
            "type": "tool_start",
            "tool_id": tool_id,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            result = await self.execute_tool(tool_id, parameters, context)
            yield {
                "type": "tool_progress",
                "tool_id": tool_id,
                "progress": 0.5,
                "timestamp": datetime.now().isoformat()
            }
            
            yield {
                "type": "tool_complete",
                "tool_id": tool_id,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            yield {
                "type": "tool_error",
                "tool_id": tool_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
