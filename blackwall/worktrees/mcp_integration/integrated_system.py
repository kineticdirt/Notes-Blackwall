"""
Integrated MCP System: Combines MCP UI + Toolbox + Server Testing
Complete integration for testing and using MCP capabilities.
"""

from typing import Dict, Optional
from pathlib import Path

from .mcp_ui_integration import MCPUIIntegration
from .toolbox_integration import SyncToolboxIntegration
from .server_tester import MCPServerTester


class IntegratedMCPSystem:
    """
    Integrated MCP System combining:
    - MCP UI (nested markdown)
    - MCP Toolbox (database queries)
    - Server Testing (comprehensive tests)
    """
    
    def __init__(self, 
                 ui_path: Optional[Path] = None,
                 toolbox_url: str = "http://127.0.0.1:5000"):
        """
        Initialize integrated MCP system.
        
        Args:
            ui_path: Path to UI markdown files
            toolbox_url: Toolbox server URL
        """
        # MCP UI Integration
        self.mcp_ui = MCPUIIntegration(ui_path=ui_path)
        
        # Toolbox Integration
        self.toolbox = SyncToolboxIntegration(toolbox_url=toolbox_url)
        self.toolbox.connect()  # Try to connect
        
        # Server Tester
        self.tester = MCPServerTester({
            "command": "npx",
            "args": ["-y", "@toolbox-sdk/server"],
            "env": {}
        })
    
    def get_ui_resource(self, component_id: str) -> Optional[Dict]:
        """Get UI component as MCP resource."""
        return self.mcp_ui.get_resource(f"mcp-ui://{component_id}")
    
    def list_ui_resources(self) -> List[Dict]:
        """List all UI resources."""
        return self.mcp_ui.list_resources()
    
    def query_database(self, tool_name: str, **kwargs) -> Any:
        """
        Query database using Toolbox.
        
        Args:
            tool_name: Name of tool to execute
            **kwargs: Tool parameters
            
        Returns:
            Query results
        """
        return self.toolbox.execute_tool(tool_name, **kwargs)
    
    def test_system(self) -> Dict:
        """
        Test the entire system.
        
        Returns:
            Test results summary
        """
        ui_path = self.mcp_ui.ui_loader.ui_path
        toolbox_url = self.toolbox.async_integration.toolbox_url
        
        results = self.tester.run_all_tests(
            toolbox_url=toolbox_url if self.toolbox.async_integration.connected else None,
            ui_path=ui_path
        )
        
        return self.tester.get_summary()
    
    def get_status(self) -> Dict:
        """Get complete system status."""
        return {
            "mcp_ui": self.mcp_ui.get_status(),
            "toolbox": self.toolbox.get_status(),
            "ui_resources": len(self.mcp_ui.resources),
            "toolbox_tools": self.toolbox.async_integration.get_status().get("total_tools", 0)
        }


def create_integrated_system(ui_path: Optional[Path] = None,
                            toolbox_url: str = "http://127.0.0.1:5000") -> IntegratedMCPSystem:
    """
    Create integrated MCP system.
    
    Args:
        ui_path: Path to UI files
        toolbox_url: Toolbox server URL
        
    Returns:
        IntegratedMCPSystem instance
    """
    return IntegratedMCPSystem(ui_path=ui_path, toolbox_url=toolbox_url)
