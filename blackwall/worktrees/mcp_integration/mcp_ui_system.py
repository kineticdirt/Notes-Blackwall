"""
MCP UI System: Enhanced UI system using nested markdown files.
Provides UI components that can be rendered and interacted with.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from .mcp_ui import MCPUILoader, MCPUIComponent


@dataclass
class UIWidget:
    """A UI widget component."""
    widget_id: str
    widget_type: str  # card, list, form, chart, etc.
    title: str
    content: str
    data_source: Optional[str] = None  # Toolbox tool, MCP resource, etc.
    actions: List[Dict] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


class MCPUISystem:
    """
    Enhanced MCP UI system with widget support and data binding.
    """
    
    def __init__(self, ui_path: Optional[Path] = None):
        """
        Initialize MCP UI system.
        
        Args:
            ui_path: Path to UI markdown files
        """
        if ui_path is None:
            ui_path = Path(".mcp-ui")
        
        self.ui_path = Path(ui_path)
        self.loader = MCPUILoader(ui_path=self.ui_path)
        self.widgets: Dict[str, UIWidget] = {}
        self._load_widgets()
    
    def _load_widgets(self):
        """Load widgets from markdown files."""
        for component_id, component in self.loader.components.items():
            # Convert components to widgets
            widget = self._component_to_widget(component)
            if widget:
                self.widgets[widget.widget_id] = widget
    
    def _component_to_widget(self, component: MCPUIComponent) -> Optional[UIWidget]:
        """Convert UI component to widget."""
        # Extract widget type from metadata
        widget_type = component.metadata.get('widget_type', 'panel')
        
        # Extract data source
        data_source = component.metadata.get('data_source')
        
        # Extract actions
        actions = component.metadata.get('actions', [])
        
        return UIWidget(
            widget_id=component.component_id,
            widget_type=widget_type,
            title=component.title,
            content=component.content,
            data_source=data_source,
            actions=actions,
            metadata=component.metadata
        )
    
    def create_dashboard(self, dashboard_id: str, widgets: List[str]) -> Dict:
        """
        Create a dashboard with widgets.
        
        Args:
            dashboard_id: Dashboard identifier
            widgets: List of widget IDs
            
        Returns:
            Dashboard configuration
        """
        dashboard = {
            "dashboard_id": dashboard_id,
            "widgets": [],
            "layout": "grid"
        }
        
        for widget_id in widgets:
            if widget_id in self.widgets:
                widget = self.widgets[widget_id]
                dashboard["widgets"].append({
                    "id": widget.widget_id,
                    "type": widget.widget_type,
                    "title": widget.title,
                    "data_source": widget.data_source
                })
        
        # Save dashboard
        dashboard_file = self.ui_path / "dashboards" / f"{dashboard_id}.json"
        dashboard_file.parent.mkdir(parents=True, exist_ok=True)
        dashboard_file.write_text(json.dumps(dashboard, indent=2))
        
        return dashboard
    
    def render_widget(self, widget_id: str, data: Optional[Dict] = None) -> Dict:
        """
        Render a widget with data.
        
        Args:
            widget_id: Widget identifier
            data: Optional data to bind
            
        Returns:
            Rendered widget
        """
        if widget_id not in self.widgets:
            raise ValueError(f"Widget {widget_id} not found")
        
        widget = self.widgets[widget_id]
        
        rendered = {
            "id": widget.widget_id,
            "type": widget.widget_type,
            "title": widget.title,
            "content": widget.content,
            "data": data or {}
        }
        
        return rendered
    
    def get_ui_tree(self) -> Dict:
        """Get UI component tree."""
        return self.loader.get_ui_tree()
    
    def get_widgets(self) -> List[Dict]:
        """Get all widgets."""
        return [widget.__dict__ for widget in self.widgets.values()]
