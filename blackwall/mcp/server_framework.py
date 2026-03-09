"""
MCP Server Framework for creating reusable MCP servers that connect to larger backend services.
Enables easy creation of MCP servers with tools, prompts, and full resource access.
"""

from typing import Dict, List, Any, Optional, Callable, AsyncIterator, Union
from abc import ABC, abstractmethod
import asyncio
import json
from datetime import datetime
from pathlib import Path
import inspect
from dataclasses import dataclass, field
from enum import Enum


class ResourceAccess(Enum):
    """Resource access levels for tools and prompts."""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    FULL = "full"
    NONE = "none"


@dataclass
class MCPResource:
    """Represents an MCP resource with access control."""
    uri: str
    name: str
    description: str
    mime_type: str = "application/json"
    access_level: ResourceAccess = ResourceAccess.READ_ONLY
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPToolDefinition:
    """Enhanced tool definition with resource access."""
    name: str
    description: str
    parameters: Dict[str, Any]
    resource_access: List[str] = field(default_factory=list)  # List of resource URIs
    access_level: ResourceAccess = ResourceAccess.NONE
    handler: Optional[Callable] = None
    server_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_mcp_schema(self) -> Dict[str, Any]:
        """Convert to MCP tool schema."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": self.parameters.get("properties", {}),
                "required": self.parameters.get("required", [])
            },
            "metadata": {
                **self.metadata,
                "resource_access": self.resource_access,
                "access_level": self.access_level.value
            }
        }


@dataclass
class MCPPromptTemplate:
    """Prompt template with resource context."""
    name: str
    description: str
    template: str
    resource_access: List[str] = field(default_factory=list)
    access_level: ResourceAccess = ResourceAccess.READ_ONLY
    variables: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def render(self, context: Dict[str, Any], resources: Optional[Dict[str, Any]] = None) -> str:
        """Render prompt template with context and resources."""
        # Inject resource data into context
        if resources:
            context["_resources"] = resources
        
        # Render template
        prompt = self.template
        for var in self.variables:
            value = context.get(var, "")
            prompt = prompt.replace(f"{{{var}}}", str(value))
        
        # Add resource context if available
        if resources and self.resource_access:
            resource_context = "\n\n## Available Resources:\n"
            for uri in self.resource_access:
                if uri in resources:
                    resource_context += f"- {uri}: {json.dumps(resources[uri], indent=2)}\n"
            prompt += resource_context
        
        return prompt


class BackendConnection(ABC):
    """Abstract base class for backend connections."""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to backend service."""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from backend service."""
        pass
    
    @abstractmethod
    async def execute(self, method: str, params: Dict[str, Any]) -> Any:
        """Execute a method on the backend."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to backend."""
        pass


class HTTPBackendConnection(BackendConnection):
    """HTTP-based backend connection."""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None,
                 headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = headers or {}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
        self._connected = False
    
    async def connect(self) -> bool:
        """Connect to HTTP backend."""
        try:
            try:
                import aiohttp
            except ImportError:
                raise ImportError("aiohttp is required for HTTP backend. Install with: pip install aiohttp")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health", headers=self.headers) as resp:
                    if resp.status == 200:
                        self._connected = True
                        return True
        except Exception as e:
            print(f"Connection error: {e}")
        return False
    
    async def disconnect(self):
        """Disconnect from HTTP backend."""
        self._connected = False
    
    async def execute(self, method: str, params: Dict[str, Any]) -> Any:
        """Execute HTTP request."""
        if not self._connected:
            raise RuntimeError("Not connected to backend")
        
        try:
            import aiohttp
        except ImportError:
            raise ImportError("aiohttp is required for HTTP backend. Install with: pip install aiohttp")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/{method}",
                json=params,
                headers=self.headers
            ) as resp:
                return await resp.json()
    
    def is_connected(self) -> bool:
        """Check connection status."""
        return self._connected


class MCPServer:
    """Reusable MCP server that connects to larger backend services."""
    
    def __init__(self, server_id: str, name: str, description: str,
                 backend: Optional[BackendConnection] = None):
        """
        Initialize MCP server.
        
        Args:
            server_id: Unique server identifier
            name: Server name
            description: Server description
            backend: Backend connection (optional)
        """
        self.server_id = server_id
        self.name = name
        self.description = description
        self.backend = backend
        
        self.tools: Dict[str, MCPToolDefinition] = {}
        self.prompts: Dict[str, MCPPromptTemplate] = {}
        self.resources: Dict[str, MCPResource] = {}
        
        self._connected = False
    
    async def initialize(self):
        """Initialize server and connect to backend if available."""
        if self.backend:
            self._connected = await self.backend.connect()
            if not self._connected:
                raise RuntimeError(f"Failed to connect to backend for {self.server_id}")
    
    async def shutdown(self):
        """Shutdown server and disconnect from backend."""
        if self.backend:
            await self.backend.disconnect()
        self._connected = False
    
    def register_tool(self, tool: MCPToolDefinition):
        """Register a tool with the server."""
        tool.server_id = self.server_id
        self.tools[tool.name] = tool
    
    def register_prompt(self, prompt: MCPPromptTemplate):
        """Register a prompt template with the server."""
        self.prompts[prompt.name] = prompt
    
    def register_resource(self, resource: MCPResource):
        """Register a resource with the server."""
        self.resources[resource.uri] = resource
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any],
                          resource_context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute a tool with resource context.
        
        Args:
            tool_name: Name of tool to execute
            parameters: Tool parameters
            resource_context: Pre-loaded resource data
            
        Returns:
            Tool execution result
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found in server '{self.server_id}'")
        
        tool = self.tools[tool_name]
        
        # Load resources if needed
        if tool.resource_access and not resource_context:
            resource_context = await self.load_resources(tool.resource_access, tool.access_level)
        
        # Execute tool handler
        if tool.handler:
            if inspect.iscoroutinefunction(tool.handler):
                if resource_context:
                    return await tool.handler(parameters, resource_context, self.backend)
                return await tool.handler(parameters, None, self.backend)
            else:
                if resource_context:
                    return tool.handler(parameters, resource_context, self.backend)
                return tool.handler(parameters, None, self.backend)
        
        # Default: execute via backend if available
        if self.backend and self._connected:
            return await self.backend.execute(tool_name, parameters)
        
        raise RuntimeError(f"No handler or backend available for tool '{tool_name}'")
    
    async def load_resources(self, resource_uris: List[str],
                           access_level: ResourceAccess = ResourceAccess.READ_ONLY) -> Dict[str, Any]:
        """
        Load resources with specified access level.
        
        Args:
            resource_uris: List of resource URIs to load
            access_level: Required access level
            
        Returns:
            Dictionary of resource data
        """
        resources = {}
        
        for uri in resource_uris:
            if uri not in self.resources:
                continue
            
            resource = self.resources[uri]
            
            # Check access level
            if access_level == ResourceAccess.FULL and resource.access_level != ResourceAccess.FULL:
                continue
            if access_level == ResourceAccess.READ_WRITE and resource.access_level == ResourceAccess.READ_ONLY:
                continue
            
            # Load resource data
            # In production, this would fetch from actual resource store
            resources[uri] = {
                "uri": uri,
                "name": resource.name,
                "data": resource.metadata.get("data", {}),
                "access_level": resource.access_level.value
            }
        
        return resources
    
    async def render_prompt(self, prompt_name: str, context: Dict[str, Any]) -> str:
        """
        Render a prompt template with resource context.
        
        Args:
            prompt_name: Name of prompt template
            context: Context variables for template
            
        Returns:
            Rendered prompt string
        """
        if prompt_name not in self.prompts:
            raise ValueError(f"Prompt '{prompt_name}' not found in server '{self.server_id}'")
        
        prompt = self.prompts[prompt_name]
        
        # Load resources if needed
        resources = None
        if prompt.resource_access:
            resources = await self.load_resources(prompt.resource_access, prompt.access_level)
        
        return prompt.render(context, resources)
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get all tool schemas in MCP format."""
        return [tool.to_mcp_schema() for tool in self.tools.values()]
    
    def get_prompt_schemas(self) -> List[Dict[str, Any]]:
        """Get all prompt schemas in MCP format."""
        return [
            {
                "name": prompt.name,
                "description": prompt.description,
                "arguments": [
                    {"name": var, "description": f"Variable: {var}"}
                    for var in prompt.variables
                ],
                "metadata": {
                    **prompt.metadata,
                    "resource_access": prompt.resource_access,
                    "access_level": prompt.access_level.value
                }
            }
            for prompt in self.prompts.values()
        ]
    
    def get_resource_schemas(self) -> List[Dict[str, Any]]:
        """Get all resource schemas in MCP format."""
        return [
            {
                "uri": resource.uri,
                "name": resource.name,
                "description": resource.description,
                "mimeType": resource.mime_type,
                "metadata": {
                    **resource.metadata,
                    "access_level": resource.access_level.value
                }
            }
            for resource in self.resources.values()
        ]
    
    def export_config(self) -> Dict[str, Any]:
        """Export server configuration."""
        return {
            "server_id": self.server_id,
            "name": self.name,
            "description": self.description,
            "backend": {
                "type": type(self.backend).__name__ if self.backend else None,
                "connected": self._connected
            },
            "tools": [tool.to_mcp_schema() for tool in self.tools.values()],
            "prompts": self.get_prompt_schemas(),
            "resources": self.get_resource_schemas()
        }


class MCPServerRegistry:
    """Registry for managing multiple MCP servers."""
    
    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
        self._initialized = False
    
    async def register_server(self, server: MCPServer):
        """Register and initialize an MCP server."""
        await server.initialize()
        self.servers[server.server_id] = server
        self._initialized = True
    
    async def unregister_server(self, server_id: str):
        """Unregister and shutdown an MCP server."""
        if server_id in self.servers:
            await self.servers[server_id].shutdown()
            del self.servers[server_id]
    
    def get_server(self, server_id: str) -> Optional[MCPServer]:
        """Get a server by ID."""
        return self.servers.get(server_id)
    
    def list_servers(self) -> List[str]:
        """List all registered server IDs."""
        return list(self.servers.keys())
    
    async def execute_tool(self, server_id: str, tool_name: str,
                          parameters: Dict[str, Any]) -> Any:
        """Execute a tool on a specific server."""
        server = self.get_server(server_id)
        if not server:
            raise ValueError(f"Server '{server_id}' not found")
        return await server.execute_tool(tool_name, parameters)
    
    async def render_prompt(self, server_id: str, prompt_name: str,
                           context: Dict[str, Any]) -> str:
        """Render a prompt from a specific server."""
        server = self.get_server(server_id)
        if not server:
            raise ValueError(f"Server '{server_id}' not found")
        return await server.render_prompt(prompt_name, context)
    
    def discover_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """Discover all tools across all servers."""
        tools = {}
        for server_id, server in self.servers.items():
            tools[server_id] = server.get_tool_schemas()
        return tools
    
    def discover_prompts(self) -> Dict[str, List[Dict[str, Any]]]:
        """Discover all prompts across all servers."""
        prompts = {}
        for server_id, server in self.servers.items():
            prompts[server_id] = server.get_prompt_schemas()
        return prompts
    
    def discover_resources(self) -> Dict[str, List[Dict[str, Any]]]:
        """Discover all resources across all servers."""
        resources = {}
        for server_id, server in self.servers.items():
            resources[server_id] = server.get_resource_schemas()
        return resources
    
    async def shutdown_all(self):
        """Shutdown all registered servers."""
        for server in self.servers.values():
            await server.shutdown()
        self.servers.clear()
        self._initialized = False
    
    def export_all_configs(self) -> Dict[str, Any]:
        """Export all server configurations."""
        return {
            server_id: server.export_config()
            for server_id, server in self.servers.items()
        }
