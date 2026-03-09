"""
Component Transformer: Transforms website components into ASCII/dithered/shaded visual panes.
"""

import sys
import re
import base64
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from blackwall.worktrees.mcp_integration.advanced_theme import (
    DitheringEngine,
    ASCIIConverter,
    ShaderEngine
)
from website_fetcher import WebsiteComponent


@dataclass
class VisualPane:
    """A visual pane representing a transformed component."""
    pane_id: str
    pane_type: str  # panel, card, button, image, text, nav, modal
    ascii_content: str
    dithering: Optional[Dict] = None
    shaders: Optional[Dict] = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ComponentTransformer:
    """Transforms website components into visual panes."""
    
    def __init__(self):
        """Initialize component transformer."""
        self.dithering_engine = DitheringEngine(method="floyd_steinberg")
        self.ascii_converter = ASCIIConverter(width=80, use_extended=True)
        self.shader_engine = ShaderEngine()
    
    def transform_component(self, component: WebsiteComponent, strategy: Optional[Dict] = None) -> VisualPane:
        """
        Transform a component into a visual pane.
        
        Args:
            component: Component to transform
            strategy: Optional transformation strategy
            
        Returns:
            VisualPane representing transformed component
        """
        component_type = component.component_type
        
        # Get strategy for this component
        comp_strategy = None
        if strategy and "component_strategies" in strategy:
            for cs in strategy["component_strategies"]:
                if cs.get("component_id") == component.component_id:
                    comp_strategy = cs
                    break
        
        # Default strategy if not found
        if not comp_strategy:
            comp_strategy = self._get_default_strategy(component_type)
        
        # Transform based on type
        if component_type in ["header", "footer", "section", "aside"]:
            return self._transform_panel(component, comp_strategy)
        elif component_type == "card":
            return self._transform_card(component, comp_strategy)
        elif component_type == "button":
            return self._transform_button(component, comp_strategy)
        elif component_type == "nav":
            return self._transform_nav(component, comp_strategy)
        else:
            return self._transform_generic(component, comp_strategy)
    
    def _transform_panel(self, component: WebsiteComponent, strategy: Dict) -> VisualPane:
        """Transform panel component."""
        # Extract title and content
        html = component.html_content
        title = self._extract_title(html)
        content = self._extract_text_content(html)
        
        # Convert to ASCII
        if strategy.get("effects", {}).get("ascii", True):
            ascii_content = self._create_ascii_panel(title, content)
        else:
            ascii_content = f"{title}\n\n{content}"
        
        # Apply dithering if specified
        dithering = None
        if strategy.get("effects", {}).get("dithering", True):
            dithering = {
                "method": strategy.get("parameters", {}).get("dithering_method", "floyd_steinberg"),
                "intensity": strategy.get("parameters", {}).get("dithering_intensity", 0.7)
            }
        
        # Apply shaders if specified
        shaders = None
        if strategy.get("effects", {}).get("shaders", True):
            shaders = {
                "noise": strategy.get("parameters", {}).get("shader_intensity", 0.15),
                "grain": 0.08,
                "scanlines": True
            }
        
        return VisualPane(
            pane_id=component.component_id,
            pane_type="panel",
            ascii_content=ascii_content,
            dithering=dithering,
            shaders=shaders,
            metadata={
                "original_type": component.component_type,
                "original_html": component.html_content[:200]
            }
        )
    
    def _transform_card(self, component: WebsiteComponent, strategy: Dict) -> VisualPane:
        """Transform card component."""
        html = component.html_content
        title = self._extract_title(html)
        content = self._extract_text_content(html)
        
        # Create ASCII card
        ascii_content = self._create_ascii_card(title, content)
        
        # Extract images and convert to ASCII
        images = self._extract_images(html)
        if images:
            ascii_content += "\n\n" + "\n".join([
                f"![{img.get('alt', 'image')}]"
                for img in images[:3]  # Limit to 3 images
            ])
        
        return VisualPane(
            pane_id=component.component_id,
            pane_type="card",
            ascii_content=ascii_content,
            dithering={"method": "floyd_steinberg", "intensity": 0.7},
            shaders={"noise": 0.15, "grain": 0.08, "scanlines": True},
            metadata={"original_type": "card"}
        )
    
    def _transform_button(self, component: WebsiteComponent, strategy: Dict) -> VisualPane:
        """Transform button component."""
        html = component.html_content
        text = self._extract_text_content(html)
        
        # Create ASCII button
        ascii_content = self._create_ascii_button(text)
        
        return VisualPane(
            pane_id=component.component_id,
            pane_type="button",
            ascii_content=ascii_content,
            dithering={"method": "floyd_steinberg", "intensity": 0.5},
            metadata={"original_type": "button", "clickable": True}
        )
    
    def _transform_nav(self, component: WebsiteComponent, strategy: Dict) -> VisualPane:
        """Transform navigation component."""
        html = component.html_content
        links = self._extract_links(html)
        
        # Create ASCII nav bar
        ascii_content = self._create_ascii_nav(links)
        
        return VisualPane(
            pane_id=component.component_id,
            pane_type="nav",
            ascii_content=ascii_content,
            dithering={"method": "floyd_steinberg", "intensity": 0.6},
            metadata={"original_type": "nav", "links": links}
        )
    
    def _transform_generic(self, component: WebsiteComponent, strategy: Dict) -> VisualPane:
        """Transform generic component."""
        html = component.html_content
        content = self._extract_text_content(html)
        
        # Simple ASCII conversion
        ascii_content = self._html_to_ascii(content)
        
        return VisualPane(
            pane_id=component.component_id,
            pane_type="panel",
            ascii_content=ascii_content,
            metadata={"original_type": component.component_type}
        )
    
    def _extract_title(self, html: str) -> str:
        """Extract title from HTML."""
        # Try h1-h6
        for level in range(1, 7):
            match = re.search(rf'<h{level}[^>]*>(.*?)</h{level}>', html, re.DOTALL | re.IGNORECASE)
            if match:
                title = re.sub(r'<[^>]+>', '', match.group(1))
                return title.strip()
        
        # Try title attribute or first text
        match = re.search(r'title=["\']([^"\']+)["\']', html)
        if match:
            return match.group(1)
        
        return "Untitled"
    
    def _extract_text_content(self, html: str) -> str:
        """Extract text content from HTML."""
        # Remove script and style tags
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html)
        
        # Clean up whitespace
        text = ' '.join(text.split())
        
        return text[:500]  # Limit length
    
    def _extract_images(self, html: str) -> List[Dict]:
        """Extract images from HTML."""
        images = []
        pattern = r'<img[^>]*src=["\']([^"\']+)["\'][^>]*(?:alt=["\']([^"\']*)["\'])?[^>]*>'
        
        for match in re.finditer(pattern, html, re.IGNORECASE):
            images.append({
                "src": match.group(1),
                "alt": match.group(2) if match.lastindex >= 2 else ""
            })
        
        return images
    
    def _extract_links(self, html: str) -> List[Dict]:
        """Extract links from HTML."""
        links = []
        pattern = r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>'
        
        for match in re.finditer(pattern, html, re.DOTALL | re.IGNORECASE):
            text = re.sub(r'<[^>]+>', '', match.group(2))
            links.append({
                "url": match.group(1),
                "text": text.strip()
            })
        
        return links
    
    def _create_ascii_panel(self, title: str, content: str) -> str:
        """Create ASCII-bordered panel."""
        width = 60
        title_line = f"║  {title[:width-4]:<{width-4}}  ║"
        border_top = "╔" + "═" * (width - 2) + "╗"
        border_bottom = "╚" + "═" * (width - 2) + "╝"
        separator = "╠" + "═" * (width - 2) + "╣"
        
        # Wrap content
        content_lines = []
        words = content.split()
        current_line = ""
        for word in words:
            if len(current_line + word) < width - 4:
                current_line += word + " "
            else:
                if current_line:
                    content_lines.append(f"║  {current_line.strip():<{width-4}}  ║")
                current_line = word + " "
        if current_line:
            content_lines.append(f"║  {current_line.strip():<{width-4}}  ║")
        
        if not content_lines:
            content_lines = [f"║  {'':<{width-4}}  ║"]
        
        return "\n".join([
            border_top,
            title_line,
            separator,
            *content_lines,
            border_bottom
        ])
    
    def _create_ascii_card(self, title: str, content: str) -> str:
        """Create ASCII card."""
        width = 50
        title_line = f"│ {title[:width-3]:<{width-3}} │"
        border_top = "┌" + "─" * (width - 2) + "┐"
        border_bottom = "└" + "─" * (width - 2) + "┘"
        separator = "├" + "─" * (width - 2) + "┤"
        
        # Wrap content
        content_lines = []
        words = content.split()
        current_line = ""
        for word in words:
            if len(current_line + word) < width - 4:
                current_line += word + " "
            else:
                if current_line:
                    content_lines.append(f"│ {current_line.strip():<{width-3}} │")
                current_line = word + " "
        if current_line:
            content_lines.append(f"│ {current_line.strip():<{width-3}} │")
        
        if not content_lines:
            content_lines = [f"│ {'':<{width-3}} │"]
        
        return "\n".join([
            border_top,
            title_line,
            separator,
            *content_lines,
            border_bottom
        ])
    
    def _create_ascii_button(self, text: str) -> str:
        """Create ASCII button."""
        width = len(text) + 4
        return f"""
┌{'─' * width}┐
│ {text:<{width-2}} │
└{'─' * width}┘
""".strip()
    
    def _create_ascii_nav(self, links: List[Dict]) -> str:
        """Create ASCII navigation bar."""
        nav_items = [f"[{link['text']}]" for link in links[:5]]  # Limit to 5
        nav_line = " ".join(nav_items)
        width = len(nav_line) + 4
        
        return f"""
╔{'═' * width}╗
║ {nav_line:<{width-2}} ║
╚{'═' * width}╝
""".strip()
    
    def _html_to_ascii(self, html: str) -> str:
        """Convert HTML to ASCII."""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html)
        # Clean whitespace
        text = ' '.join(text.split())
        return text
    
    def _get_default_strategy(self, component_type: str) -> Dict:
        """Get default transformation strategy for component type."""
        defaults = {
            "header": {
                "pane_type": "panel",
                "effects": {"ascii": True, "dithering": True, "shaders": True},
                "parameters": {"dithering_method": "floyd_steinberg"}
            },
            "card": {
                "pane_type": "card",
                "effects": {"ascii": True, "dithering": True, "shaders": True},
                "parameters": {}
            },
            "button": {
                "pane_type": "button",
                "effects": {"ascii": True, "dithering": True, "shaders": False},
                "parameters": {}
            },
            "nav": {
                "pane_type": "nav",
                "effects": {"ascii": True, "dithering": True, "shaders": False},
                "parameters": {}
            }
        }
        
        return defaults.get(component_type, {
            "pane_type": "panel",
            "effects": {"ascii": True, "dithering": False, "shaders": False},
            "parameters": {}
        })


def create_component_transformer() -> ComponentTransformer:
    """Create component transformer instance."""
    return ComponentTransformer()
