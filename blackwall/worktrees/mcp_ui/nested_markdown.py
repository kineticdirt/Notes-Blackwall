"""
Nested Markdown: System for managing nested markdown files.
MCP UI is implemented using nested markdown files.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class MarkdownNode:
    """A node in the nested markdown structure."""
    path: Path
    content: str
    children: List['MarkdownNode'] = None
    parent: Optional['MarkdownNode'] = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.metadata is None:
            self.metadata = {}


class NestedMarkdown:
    """
    Manages nested markdown files.
    Supports hierarchical structure with parent-child relationships.
    """
    
    def __init__(self, base_path: Path):
        """
        Initialize nested markdown system.
        
        Args:
            base_path: Base path for markdown files
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.nodes: Dict[str, MarkdownNode] = {}
        self._load_tree()
    
    def _load_tree(self):
        """Load markdown tree from filesystem."""
        for md_file in self.base_path.rglob("*.md"):
            relative_path = md_file.relative_to(self.base_path)
            node_id = str(relative_path.with_suffix(''))
            
            content = md_file.read_text()
            node = MarkdownNode(path=md_file, content=content)
            
            # Extract links to child files
            child_links = self._extract_child_links(content)
            node.metadata = {"child_links": child_links}
            
            self.nodes[node_id] = node
        
        # Build parent-child relationships
        self._build_relationships()
    
    def _extract_child_links(self, content: str) -> List[str]:
        """Extract links to child markdown files."""
        # Find markdown links: [text](path/to/file.md)
        pattern = r'\[([^\]]+)\]\(([^)]+\.md)\)'
        matches = re.findall(pattern, content)
        return [match[1] for match in matches]
    
    def _build_relationships(self):
        """Build parent-child relationships."""
        for node_id, node in self.nodes.items():
            child_links = node.metadata.get("child_links", [])
            for child_link in child_links:
                # Resolve child path
                try:
                    child_path = (node.path.parent / child_link).resolve()
                    if child_path.exists() and child_path.is_relative_to(self.base_path.resolve()):
                        child_relative = child_path.relative_to(self.base_path.resolve())
                        child_id = str(child_relative.with_suffix(''))
                        
                        if child_id in self.nodes:
                            child_node = self.nodes[child_id]
                            child_node.parent = node
                            node.children.append(child_node)
                except (ValueError, FileNotFoundError):
                    # Skip if path resolution fails
                    pass
    
    def get_node(self, node_id: str) -> Optional[MarkdownNode]:
        """Get node by ID."""
        return self.nodes.get(node_id)
    
    def get_children(self, node_id: str) -> List[MarkdownNode]:
        """Get children of a node."""
        node = self.get_node(node_id)
        if node:
            return node.children
        return []
    
    def get_tree(self, root_id: Optional[str] = None) -> Dict:
        """Get tree structure starting from root."""
        if root_id is None:
            # Find root nodes (nodes without parents)
            root_nodes = [n for n in self.nodes.values() if n.parent is None]
            if root_nodes:
                root_id = str(root_nodes[0].path.relative_to(self.base_path).with_suffix(''))
            else:
                return {}
        
        node = self.get_node(root_id)
        if not node:
            return {}
        
        return self._node_to_dict(node)
    
    def _node_to_dict(self, node: MarkdownNode) -> Dict:
        """Convert node to dictionary."""
        return {
            "id": str(node.path.relative_to(self.base_path).with_suffix('')),
            "path": str(node.path),
            "content_preview": node.content[:200],
            "children": [self._node_to_dict(child) for child in node.children]
        }
