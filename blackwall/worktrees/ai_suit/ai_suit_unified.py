"""
Unified AI Suit: Combines MCP Jam + MCP Toolbox + Worktree System
Creates a complete "plug and play" AI capability extension system.
"""

from typing import Dict, List, Optional, Any
from .ai_suit_core import AISuit, Capability, CapabilityType
from .mcp_jam import MCPJam, MCPServerInfo
from .toolbox_bridge import ToolboxBridge

# Import our existing systems
from ..unified_system import UnifiedMCPSystem


class UnifiedAISuit(AISuit):
    """
    Unified AI Suit: Complete plug-and-play system.
    
    Combines:
    - MCP Jam (multiple MCP servers)
    - MCP Toolbox (database queries)
    - Worktree System (agents, kanban, workflows)
    - Cross-Chat (communication)
    
    Acts as a "super robotic suit" that extends user abilities.
    """
    
    def __init__(self, suit_id: Optional[str] = None):
        """Initialize unified AI suit."""
        super().__init__(suit_id)
        
        # Initialize components
        self.mcp_jam = MCPJam()
        self.toolbox_bridge = ToolboxBridge()
        self.worktree_system = UnifiedMCPSystem()
        
        # Connect components
        self._integrate_components()
    
    def _integrate_components(self):
        """Integrate all components into the suit."""
        
        # Connect Toolbox
        if self.toolbox_bridge.connect():
            print("✓ Toolbox connected")
            self._register_toolbox_capabilities()
        
        # Register MCP Jam capabilities
        self._register_mcp_jam_capabilities()
        
        # Register Worktree capabilities
        self._register_worktree_capabilities()
        
        # Register Cross-Chat capabilities
        self._register_cross_chat_capabilities()
    
    def _register_toolbox_capabilities(self):
        """Register Toolbox database query capabilities."""
        
        # Kanban queries
        def query_kanban_cards(status: str = "in_progress"):
            return self.toolbox_bridge.execute_query("get_kanban_cards", status=status)
        
        self.extend_ability(
            "query_kanban",
            query_kanban_cards,
            "Query Kanban board cards by status",
            CapabilityType.DATABASE
        )
        
        # Cross-chat queries
        def query_findings(category: str = "bug"):
            return self.toolbox_bridge.execute_query("get_cross_chat_findings", category=category)
        
        self.extend_ability(
            "discover_findings",
            query_findings,
            "Discover findings from other sessions",
            CapabilityType.DATABASE
        )
    
    def _register_mcp_jam_capabilities(self):
        """Register MCP Jam tool capabilities."""
        
        # File operations
        def read_file_cap(file_path: str):
            return self.mcp_jam.call_tool("read_file", file_path=file_path)
        
        self.extend_ability(
            "read_file",
            read_file_cap,
            "Read file contents",
            CapabilityType.TOOL
        )
        
        def write_file_cap(file_path: str, content: str):
            return self.mcp_jam.call_tool("write_file", file_path=file_path, content=content)
        
        self.extend_ability(
            "write_file",
            write_file_cap,
            "Write file contents",
            CapabilityType.TOOL
        )
    
    def _register_worktree_capabilities(self):
        """Register worktree system capabilities."""
        
        # Create worktree
        def create_worktree_cap(name: str, agent_types: List[str] = None):
            return self.worktree_system.worktree_manager.create_worktree(
                name=name,
                agent_types=agent_types or []
            )
        
        self.extend_ability(
            "create_worktree",
            create_worktree_cap,
            "Create a new worktree with agents",
            CapabilityType.AGENT
        )
        
        # Create Kanban board
        def create_kanban_cap(board_id: str, name: str):
            return self.worktree_system.create_kanban_board(board_id, name)
        
        self.extend_ability(
            "create_kanban_board",
            create_kanban_cap,
            "Create a new Kanban board",
            CapabilityType.WORKFLOW
        )
    
    def _register_cross_chat_capabilities(self):
        """Register cross-chat capabilities."""
        
        # Publish finding
        def publish_finding_cap(title: str, content: str, category: str = "general"):
            return self.worktree_system.cross_chat.publish(
                title=title,
                content=content,
                category=category
            )
        
        self.extend_ability(
            "publish_finding",
            publish_finding_cap,
            "Publish a finding to cross-chat",
            CapabilityType.RESOURCE
        )
    
    def add_mcp_server(self, server_id: str, name: str, command: str,
                      args: List[str] = None, env: Dict[str, str] = None):
        """
        Add an MCP server to the jam.
        
        Args:
            server_id: Unique server identifier
            name: Server name
            command: Command to start server
            args: Command arguments
            env: Environment variables
        """
        server_info = MCPServerInfo(
            server_id=server_id,
            name=name,
            command=command,
            args=args or [],
            env=env or {}
        )
        
        self.mcp_jam.add_server(server_info)
        
        # Register tools as capabilities
        connector = self.mcp_jam.servers.get(server_id)
        if connector:
            for tool_name in connector.list_tools():
                def make_tool_handler(tn):
                    return lambda **kwargs: self.mcp_jam.call_tool(tn, server_id=server_id, **kwargs)
                
                self.extend_ability(
                    f"{server_id}_{tool_name}",
                    make_tool_handler(tool_name),
                    f"Tool {tool_name} from {name}",
                    CapabilityType.TOOL
                )
    
    def query(self, natural_language_query: str) -> Any:
        """
        Query the suit using natural language.
        Routes to appropriate capability.
        
        Args:
            natural_language_query: Natural language query
            
        Returns:
            Query result
        """
        query_lower = natural_language_query.lower()
        
        # Simple routing logic (would use LLM in production)
        if "kanban" in query_lower or "card" in query_lower:
            if "high priority" in query_lower:
                return self.use("query_kanban", status="in_progress")
            return self.use("query_kanban")
        
        elif "finding" in query_lower or "bug" in query_lower:
            category = "bug" if "bug" in query_lower else "general"
            return self.use("discover_findings", category=category)
        
        elif "worktree" in query_lower:
            if "create" in query_lower:
                return self.use("create_worktree", name="New Worktree")
            return {"message": "Worktree operations available"}
        
        elif "read file" in query_lower:
            # Extract file path (simplified)
            return {"message": "Use read_file capability with file_path parameter"}
        
        else:
            # Try to find matching capability
            matching = self.discover_capabilities(query_lower)
            if matching:
                return {
                    "message": f"Found {len(matching)} matching capabilities",
                    "capabilities": [c.name for c in matching]
                }
            
            return {"message": "No matching capability found", "query": natural_language_query}
    
    def get_full_status(self) -> Dict:
        """Get complete status of the AI Suit."""
        suit_status = self.get_suit_status()
        mcp_status = self.mcp_jam.get_status()
        toolbox_status = self.toolbox_bridge.get_status()
        
        return {
            **suit_status,
            "mcp_jam": mcp_status,
            "toolbox": toolbox_status,
            "total_extended_abilities": len(self.registry.capabilities)
        }


def create_ai_suit(suit_id: Optional[str] = None) -> UnifiedAISuit:
    """
    Create a new AI Suit instance.
    
    Args:
        suit_id: Optional suit identifier
        
    Returns:
        UnifiedAISuit instance
    """
    return UnifiedAISuit(suit_id=suit_id)
