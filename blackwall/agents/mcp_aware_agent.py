"""
MCP-aware base agent that understands and uses available tools.
These tools are part of the Blackwall system.
"""

from typing import Dict, List, Optional, Any
import json
from pathlib import Path

# Import base agent functionality
import sys
agent_system_path = Path(__file__).parent.parent.parent / "agent-system"
if agent_system_path.exists():
    sys.path.insert(0, str(agent_system_path))
    from agent import BaseAgent
    from ledger import AgentLedger
else:
    BaseAgent = None
    AgentLedger = None

import sys
from pathlib import Path

# Add blackwall root to path
blackwall_root = Path(__file__).parent.parent
sys.path.insert(0, str(blackwall_root))

try:
    from mcp.mcp_integration import MCPIntegration
except ImportError:
    # Fallback: create minimal MCP integration
    class MCPIntegration:
        def list_tools(self):
            return ["read_file", "write_file", "codebase_search", "grep", 
                   "run_terminal_cmd", "read_lints", "list_dir", "glob_file_search"]
        def get_tool_schema(self, name):
            return {"name": name}
        def list_resources(self):
            return []


class MCPAwareAgent:
    """
    Base agent that is aware of MCP tools and resources.
    These tools (read_file, write_file, etc.) are part of Blackwall.
    """
    
    # Available MCP tools in Blackwall system
    AVAILABLE_TOOLS = [
        "read_file",
        "write_file", 
        "search_replace",
        "codebase_search",
        "grep",
        "run_terminal_cmd",
        "read_lints",
        "list_dir",
        "glob_file_search",
        "delete_file"
    ]
    
    def __init__(self, agent_id: Optional[str] = None,
                 agent_type: str = "mcp-aware",
                 ledger_path: str = "ledger/AI_GROUPCHAT.json"):
        """
        Initialize MCP-aware agent.
        
        Args:
            agent_id: Unique agent identifier
            agent_type: Type of agent
            ledger_path: Path to ledger
        """
        self.agent_id = agent_id or f"{agent_type}-{self._generate_id()}"
        self.agent_type = agent_type
        self.mcp = MCPIntegration()
        self.available_tools = self.mcp.list_tools()
        
        # Initialize base agent if available
        if BaseAgent:
            self.base_agent = BaseAgent(agent_id=self.agent_id,
                                      agent_type=agent_type,
                                      ledger_path=ledger_path)
            self.ledger = self.base_agent.ledger
        else:
            self.base_agent = None
            self.ledger = None
        
        self.status = "idle"
        self.current_intent = None
    
    def _generate_id(self) -> str:
        """Generate unique ID."""
        import uuid
        return uuid.uuid4().hex[:8]
    
    def declare_intent(self, intent: str, resources: Optional[List[str]] = None) -> str:
        """Declare intent (uses base agent if available)."""
        if self.base_agent:
            return self.base_agent.declare_intent(intent, resources)
        # Fallback: just log
        self.log(f"Intent: {intent}")
        return "intent-placeholder"
    
    def log(self, message: str, message_type: str = "info"):
        """Log message to ledger."""
        if self.base_agent:
            return self.base_agent.log(message, message_type)
        # Fallback: print
        print(f"[{self.agent_id}] {message}")
    
    def get_available_tools(self) -> List[str]:
        """Get list of available MCP tools."""
        return self.available_tools
    
    def can_use_tool(self, tool_name: str) -> bool:
        """Check if agent can use a specific tool."""
        return tool_name in self.available_tools
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict]:
        """Get information about a tool."""
        return self.mcp.get_tool_schema(tool_name)
    
    def use_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Use an MCP tool.
        Note: In actual implementation, this would call the tool via MCP protocol.
        For now, this documents what tools are available.
        
        Args:
            tool_name: Name of tool to use
            **kwargs: Tool parameters
            
        Returns:
            Tool result (placeholder - actual implementation would call tool)
        """
        if not self.can_use_tool(tool_name):
            raise ValueError(f"Tool '{tool_name}' not available")
        
        tool_info = self.get_tool_info(tool_name)
        self.log(f"Using tool: {tool_name} with params: {kwargs}")
        
        # In actual implementation, this would:
        # 1. Call MCP server with tool name and params
        # 2. Wait for result
        # 3. Return result
        
        # For now, return placeholder
        return {"tool": tool_name, "params": kwargs, "status": "called"}
    
    def get_mcp_resources(self) -> List[Dict]:
        """Get available MCP resources."""
        return self.mcp.list_resources()
    
    def access_resource(self, resource_uri: str) -> Optional[Dict]:
        """
        Access an MCP resource.
        
        Args:
            resource_uri: Resource URI (e.g., "ledger://ai_groupchat")
            
        Returns:
            Resource data
        """
        resources = self.get_mcp_resources()
        for resource in resources:
            if resource["uri"] == resource_uri:
                self.log(f"Accessing resource: {resource['name']}")
                # In actual implementation, would fetch resource via MCP
                return resource
        return None
