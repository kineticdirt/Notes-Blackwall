"""
Agent integration for MCP servers - makes it easy for AI agents to use MCP servers.
"""

from typing import Dict, List, Any, Optional
import asyncio

from .server_framework import MCPServerRegistry, MCPServer


class MCPAgentBridge:
    """
    Bridge between AI agents and MCP servers.
    Provides easy access to tools, prompts, and resources.
    """
    
    def __init__(self, registry: Optional[MCPServerRegistry] = None):
        """
        Initialize agent bridge.
        
        Args:
            registry: MCP server registry (creates new one if not provided)
        """
        self.registry = registry or MCPServerRegistry()
        self._discovered_tools: Optional[Dict[str, List[Dict[str, Any]]]] = None
        self._discovered_prompts: Optional[Dict[str, List[Dict[str, Any]]]] = None
        self._discovered_resources: Optional[Dict[str, List[Dict[str, Any]]]] = None
    
    async def initialize(self):
        """Initialize bridge and discover available tools/prompts/resources."""
        self._discovered_tools = self.registry.discover_tools()
        self._discovered_prompts = self.registry.discover_prompts()
        self._discovered_resources = self.registry.discover_resources()
    
    def get_available_tools(self, server_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get available tools, optionally filtered by server.
        
        Args:
            server_id: Optional server ID to filter by
            
        Returns:
            List of tool schemas
        """
        if not self._discovered_tools:
            self._discovered_tools = self.registry.discover_tools()
        
        if server_id:
            return self._discovered_tools.get(server_id, [])
        
        # Flatten all tools from all servers
        all_tools = []
        for tools in self._discovered_tools.values():
            all_tools.extend(tools)
        return all_tools
    
    def get_available_prompts(self, server_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get available prompts, optionally filtered by server.
        
        Args:
            server_id: Optional server ID to filter by
            
        Returns:
            List of prompt schemas
        """
        if not self._discovered_prompts:
            self._discovered_prompts = self.registry.discover_prompts()
        
        if server_id:
            return self._discovered_prompts.get(server_id, [])
        
        # Flatten all prompts from all servers
        all_prompts = []
        for prompts in self._discovered_prompts.values():
            all_prompts.extend(prompts)
        return all_prompts
    
    def get_available_resources(self, server_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get available resources, optionally filtered by server.
        
        Args:
            server_id: Optional server ID to filter by
            
        Returns:
            List of resource schemas
        """
        if not self._discovered_resources:
            self._discovered_resources = self.registry.discover_resources()
        
        if server_id:
            return self._discovered_resources.get(server_id, [])
        
        # Flatten all resources from all servers
        all_resources = []
        for resources in self._discovered_resources.values():
            all_resources.extend(resources)
        return all_resources
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any],
                          server_id: Optional[str] = None) -> Any:
        """
        Execute a tool, automatically finding the server if not specified.
        
        Args:
            tool_name: Name of tool to execute
            parameters: Tool parameters
            server_id: Optional server ID (will search if not provided)
            
        Returns:
            Tool execution result
        """
        if server_id:
            return await self.registry.execute_tool(server_id, tool_name, parameters)
        
        # Search for tool across all servers
        for sid, server in self.registry.servers.items():
            if tool_name in server.tools:
                return await server.execute_tool(tool_name, parameters)
        
        raise ValueError(f"Tool '{tool_name}' not found in any server")
    
    async def render_prompt(self, prompt_name: str, context: Dict[str, Any],
                           server_id: Optional[str] = None) -> str:
        """
        Render a prompt, automatically finding the server if not specified.
        
        Args:
            prompt_name: Name of prompt template
            context: Context variables for template
            server_id: Optional server ID (will search if not provided)
            
        Returns:
            Rendered prompt string
        """
        if server_id:
            return await self.registry.render_prompt(server_id, prompt_name, context)
        
        # Search for prompt across all servers
        for sid, server in self.registry.servers.items():
            if prompt_name in server.prompts:
                return await server.render_prompt(prompt_name, context)
        
        raise ValueError(f"Prompt '{prompt_name}' not found in any server")
    
    def find_tool_server(self, tool_name: str) -> Optional[str]:
        """Find which server contains a tool."""
        for server_id, server in self.registry.servers.items():
            if tool_name in server.tools:
                return server_id
        return None
    
    def find_prompt_server(self, prompt_name: str) -> Optional[str]:
        """Find which server contains a prompt."""
        for server_id, server in self.registry.servers.items():
            if prompt_name in server.prompts:
                return server_id
        return None
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a tool."""
        for server in self.registry.servers.values():
            if tool_name in server.tools:
                tool = server.tools[tool_name]
                return {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                    "resource_access": tool.resource_access,
                    "access_level": tool.access_level.value,
                    "server_id": tool.server_id,
                    "metadata": tool.metadata
                }
        return None
    
    def get_prompt_info(self, prompt_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a prompt."""
        for server in self.registry.servers.values():
            if prompt_name in server.prompts:
                prompt = server.prompts[prompt_name]
                return {
                    "name": prompt.name,
                    "description": prompt.description,
                    "template": prompt.template,
                    "variables": prompt.variables,
                    "resource_access": prompt.resource_access,
                    "access_level": prompt.access_level.value,
                    "metadata": prompt.metadata
                }
        return None
    
    def list_servers(self) -> List[Dict[str, Any]]:
        """List all registered servers with summary information."""
        servers = []
        for server_id, server in self.registry.servers.items():
            servers.append({
                "server_id": server_id,
                "name": server.name,
                "description": server.description,
                "tool_count": len(server.tools),
                "prompt_count": len(server.prompts),
                "resource_count": len(server.resources),
                "backend_connected": server._connected if server.backend else None
            })
        return servers
    
    async def shutdown(self):
        """Shutdown bridge and all servers."""
        await self.registry.shutdown_all()


class EnhancedMCPAgent:
    """
    Enhanced agent class that integrates with MCP servers.
    Provides easy access to tools, prompts, and resources with full context.
    """
    
    def __init__(self, agent_id: str, bridge: Optional[MCPAgentBridge] = None):
        """
        Initialize enhanced agent.
        
        Args:
            agent_id: Unique agent identifier
            bridge: MCP agent bridge (creates new one if not provided)
        """
        self.agent_id = agent_id
        self.bridge = bridge or MCPAgentBridge()
        self._initialized = False
    
    async def initialize(self):
        """Initialize agent and bridge."""
        await self.bridge.initialize()
        self._initialized = True
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get all available tools."""
        return self.bridge.get_available_tools()
    
    def get_prompts(self) -> List[Dict[str, Any]]:
        """Get all available prompts."""
        return self.bridge.get_available_prompts()
    
    def get_resources(self) -> List[Dict[str, Any]]:
        """Get all available resources."""
        return self.bridge.get_available_resources()
    
    async def use_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Use a tool with automatic server discovery.
        
        Args:
            tool_name: Name of tool to use
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
        """
        if not self._initialized:
            await self.initialize()
        
        return await self.bridge.execute_tool(tool_name, kwargs)
    
    async def use_prompt(self, prompt_name: str, **context) -> str:
        """
        Use a prompt template with automatic server discovery.
        
        Args:
            prompt_name: Name of prompt template
            **context: Context variables for template
            
        Returns:
            Rendered prompt string
        """
        if not self._initialized:
            await self.initialize()
        
        return await self.bridge.render_prompt(prompt_name, context)
    
    def describe_capabilities(self) -> Dict[str, Any]:
        """Describe agent capabilities."""
        return {
            "agent_id": self.agent_id,
            "tools_available": len(self.get_tools()),
            "prompts_available": len(self.get_prompts()),
            "resources_available": len(self.get_resources()),
            "servers": self.bridge.list_servers()
        }
    
    async def shutdown(self):
        """Shutdown agent and bridge."""
        await self.bridge.shutdown()
        self._initialized = False
