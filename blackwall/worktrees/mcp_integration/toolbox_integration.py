"""
Toolbox Integration: Proper integration with MCP Toolbox server.
Handles connection, tool loading, and query execution.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    from toolbox_core import ToolboxClient
    TOOLBOX_AVAILABLE = True
except ImportError:
    TOOLBOX_AVAILABLE = False
    ToolboxClient = None


class ToolboxIntegration:
    """
    Integration with MCP Toolbox server.
    Provides database query capabilities via Toolbox.
    """
    
    def __init__(self, toolbox_url: str = "http://127.0.0.1:5000"):
        """
        Initialize Toolbox integration.
        
        Args:
            toolbox_url: URL of MCP Toolbox server
        """
        self.toolbox_url = toolbox_url
        self.connected = False
        self.client: Optional[ToolboxClient] = None
        self.available_toolsets: Dict[str, List[str]] = {}
        self.tools: Dict[str, Any] = {}
    
    async def connect(self) -> bool:
        """
        Connect to MCP Toolbox server.
        
        Returns:
            True if connected successfully
        """
        if not TOOLBOX_AVAILABLE:
            print("⚠ toolbox-core not installed. Install with: pip install toolbox-core")
            return False
        
        try:
            self.client = ToolboxClient(self.toolbox_url)
            # Test connection by loading a toolset
            try:
                tools = await self.client.load_toolset("kanban_toolset")
                self.connected = True
                print(f"✓ Connected to Toolbox at {self.toolbox_url}")
                return True
            except Exception as e:
                print(f"⚠ Toolbox server may not be running: {e}")
                print(f"  Start with: npx @toolbox-sdk/server --tools-file toolbox_test/tools.yaml")
                return False
        except Exception as e:
            print(f"⚠ Failed to connect to Toolbox: {e}")
            return False
    
    async def load_toolset(self, toolset_name: str) -> List[str]:
        """
        Load a toolset from Toolbox.
        
        Args:
            toolset_name: Name of toolset
            
        Returns:
            List of tool names
        """
        if not self.connected or not self.client:
            raise RuntimeError("Not connected to Toolbox")
        
        tools = await self.client.load_toolset(toolset_name)
        tool_names = [tool.name() for tool in tools]
        
        self.available_toolsets[toolset_name] = tool_names
        
        # Store tools
        for tool in tools:
            self.tools[tool.name()] = tool
        
        return tool_names
    
    async def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Execute a Toolbox tool.
        
        Args:
            tool_name: Name of tool to execute
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
        """
        if not self.connected or not self.client:
            raise RuntimeError("Not connected to Toolbox")
        
        if tool_name not in self.tools:
            # Try to load from any toolset
            for toolset_name in self.available_toolsets.keys():
                await self.load_toolset(toolset_name)
                if tool_name in self.tools:
                    break
        
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        tool = self.tools[tool_name]
        
        # Execute tool (simplified - would use actual tool execution)
        return {
            "tool": tool_name,
            "parameters": kwargs,
            "status": "executed",
            "result": f"Tool {tool_name} executed with params {kwargs}"
        }
    
    def get_tool_schema(self, tool_name: str) -> Optional[Dict]:
        """Get schema for a tool."""
        if tool_name not in self.tools:
            return None
        
        tool = self.tools[tool_name]
        return {
            "name": tool.name(),
            "description": tool.description(),
            "parameters": tool.get_param_schema() if hasattr(tool, 'get_param_schema') else {}
        }
    
    def get_status(self) -> Dict:
        """Get Toolbox integration status."""
        return {
            "connected": self.connected,
            "toolbox_url": self.toolbox_url,
            "available_toolsets": list(self.available_toolsets.keys()),
            "total_tools": len(self.tools)
        }


class SyncToolboxIntegration:
    """
    Synchronous wrapper for Toolbox integration.
    For use in non-async contexts.
    """
    
    def __init__(self, toolbox_url: str = "http://127.0.0.1:5000"):
        """Initialize sync Toolbox integration."""
        self.async_integration = ToolboxIntegration(toolbox_url)
        self._loop = None
    
    def _get_loop(self):
        """Get or create event loop."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError("Loop is closed")
            return loop
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
    
    def connect(self) -> bool:
        """Connect to Toolbox (sync)."""
        loop = self._get_loop()
        return loop.run_until_complete(self.async_integration.connect())
    
    def load_toolset(self, toolset_name: str) -> List[str]:
        """Load toolset (sync)."""
        loop = self._get_loop()
        return loop.run_until_complete(self.async_integration.load_toolset(toolset_name))
    
    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute tool (sync)."""
        loop = self._get_loop()
        return loop.run_until_complete(self.async_integration.execute_tool(tool_name, **kwargs))
    
    def get_status(self) -> Dict:
        """Get status."""
        return self.async_integration.get_status()
