"""
MCP UI Integration: Integrates nested markdown UI with MCP protocol.
Makes UI components accessible via MCP resources.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from ..mcp_ui import MCPUILoader, MCPUIComponent


class MCPUIIntegration:
    """
    Integrates MCP UI (nested markdown) with MCP protocol.
    Exposes UI components as MCP resources.
    """
    
    def __init__(self, ui_path: Optional[Path] = None):
        """
        Initialize MCP UI integration.
        
        Args:
            ui_path: Path to UI markdown files
        """
        self.ui_loader = MCPUILoader(ui_path=ui_path)
        self.resources: Dict[str, Dict] = {}
        self._register_ui_resources()
    
    def _register_ui_resources(self):
        """Register UI components as MCP resources."""
        for component_id, component in self.ui_loader.components.items():
            resource_uri = f"mcp-ui://{component_id}"
            
            self.resources[resource_uri] = {
                "uri": resource_uri,
                "name": component.title,
                "description": f"MCP UI component: {component.title}",
                "mimeType": "text/markdown",
                "content": component.content,
                "metadata": {
                    "component_id": component_id,
                    "component_type": component.component_type,
                    "children": [c.component_id for c in component.children]
                }
            }
    
    def get_resource(self, uri: str) -> Optional[Dict]:
        """
        Get MCP resource by URI.
        
        Args:
            uri: Resource URI (e.g., "mcp-ui://main")
            
        Returns:
            Resource data or None
        """
        return self.resources.get(uri)
    
    def list_resources(self) -> List[Dict]:
        """List all MCP UI resources."""
        return list(self.resources.values())
    
    def get_ui_tree_as_resource(self) -> Dict:
        """Get UI tree as MCP resource."""
        tree = self.ui_loader.get_ui_tree()
        
        return {
            "uri": "mcp-ui://tree",
            "name": "MCP UI Tree",
            "description": "Complete UI component tree",
            "mimeType": "application/json",
            "content": json.dumps(tree, indent=2),
            "metadata": {
                "type": "ui_tree",
                "component_count": len(self.ui_loader.components)
            }
        }
    
    def render_component(self, component_id: str, context: Optional[Dict] = None) -> str:
        """
        Render a UI component with context.
        
        Args:
            component_id: Component ID
            context: Optional context data
            
        Returns:
            Rendered markdown content
        """
        component = self.ui_loader.get_component(component_id)
        if not component:
            return ""
        
        content = component.content
        
        # Simple template rendering (can be enhanced)
        if context:
            for key, value in context.items():
                content = content.replace(f"{{{{{key}}}}}", str(value))
        
        return content
    
    def get_status(self) -> Dict:
        """Get MCP UI integration status."""
        return {
            "components": len(self.ui_loader.components),
            "resources": len(self.resources),
            "ui_path": str(self.ui_loader.ui_path)
        }
