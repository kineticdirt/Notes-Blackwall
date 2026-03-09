"""
MCP UI Loader: Loads UI components from nested markdown files.
"""

from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from .nested_markdown import NestedMarkdown, MarkdownNode


@dataclass
class MCPUIComponent:
    """An MCP UI component loaded from markdown."""
    component_id: str
    component_type: str  # page, panel, widget, etc.
    title: str
    content: str
    children: List['MCPUIComponent'] = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.metadata is None:
            self.metadata = {}


class MCPUILoader:
    """
    Loads MCP UI from nested markdown files.
    """
    
    def __init__(self, ui_path: Optional[Path] = None):
        """
        Initialize MCP UI loader.
        
        Args:
            ui_path: Path to UI markdown files (defaults to .mcp-ui)
        """
        if ui_path is None:
            ui_path = Path(".mcp-ui")
        
        self.ui_path = Path(ui_path)
        self.nested_md = NestedMarkdown(self.ui_path)
        self.components: Dict[str, MCPUIComponent] = {}
        self._load_components()
    
    def _load_components(self):
        """Load UI components from markdown."""
        for node_id, node in self.nested_md.nodes.items():
            component = self._node_to_component(node)
            if component:
                self.components[component.component_id] = component
    
    def _node_to_component(self, node: MarkdownNode) -> Optional[MCPUIComponent]:
        """Convert markdown node to UI component."""
        # Extract frontmatter if present
        content = node.content
        frontmatter = {}
        
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                import yaml
                try:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                    content = parts[2].strip()
                except:
                    pass
        
        component_id = str(node.path.relative_to(self.ui_path).with_suffix(''))
        component_type = frontmatter.get('type', 'page')
        title = frontmatter.get('title', component_id)
        
        component = MCPUIComponent(
            component_id=component_id,
            component_type=component_type,
            title=title,
            content=content,
            metadata=frontmatter
        )
        
        # Add children
        for child_node in node.children:
            child_component = self._node_to_component(child_node)
            if child_component:
                component.children.append(child_component)
        
        return component
    
    def get_component(self, component_id: str) -> Optional[MCPUIComponent]:
        """Get component by ID."""
        return self.components.get(component_id)
    
    def get_ui_tree(self) -> Dict:
        """Get UI component tree."""
        tree = self.nested_md.get_tree()
        
        # Convert to component tree
        def convert_node(node_dict):
            component_id = node_dict['id']
            component = self.components.get(component_id)
            if component:
                return {
                    "id": component.component_id,
                    "type": component.component_type,
                    "title": component.title,
                    "children": [convert_node(child) for child in node_dict.get('children', [])]
                }
            return node_dict
        
        if tree:
            return convert_node(tree)
        return {}
