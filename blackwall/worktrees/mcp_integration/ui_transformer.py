"""
UI Transformer: Expands MCP UI into a transformation/proxy layer.
Can analyze websites, generate components, and apply personal theming.
Acts as a 'barrier' that transforms UI resources before serving them.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from urllib.parse import urlparse, urljoin
import html
from html.parser import HTMLParser


@dataclass
class Theme:
    """Personal theme configuration."""
    name: str
    colors: Dict[str, str]  # primary, secondary, background, text, etc.
    fonts: Dict[str, str]  # heading, body, monospace
    spacing: Dict[str, str]  # small, medium, large
    styles: Dict[str, str]  # Custom CSS
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ExtractedComponent:
    """Component extracted from a website."""
    component_id: str
    component_type: str  # header, nav, card, button, etc.
    html_content: str
    css_styles: Dict[str, str]  # element_id -> CSS
    markdown_content: str
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class HTMLComponentExtractor(HTMLParser):
    """Extracts UI components from HTML."""
    
    def __init__(self):
        super().__init__()
        self.components: List[Dict] = []
        self.current_tag = None
        self.current_attrs = {}
        self.current_content = []
        self.depth = 0
        
    def handle_starttag(self, tag, attrs):
        self.depth += 1
        attrs_dict = dict(attrs)
        
        # Identify component types
        component_type = None
        if tag in ['header', 'nav', 'footer', 'main', 'article', 'section', 'aside']:
            component_type = tag
        elif 'class' in attrs_dict:
            classes = attrs_dict['class'].split()
            if 'card' in classes or 'panel' in classes:
                component_type = 'card'
            elif 'button' in classes or 'btn' in classes:
                component_type = 'button'
            elif 'nav' in classes or 'menu' in classes:
                component_type = 'nav'
        
        if component_type:
            self.current_tag = tag
            self.current_attrs = attrs_dict
            self.current_content = []
    
    def handle_data(self, data):
        if self.current_tag:
            self.current_content.append(data.strip())
    
    def handle_endtag(self, tag):
        if self.current_tag == tag and self.current_content:
            component_id = self.current_attrs.get('id', f"component_{len(self.components)}")
            self.components.append({
                'id': component_id,
                'type': self._infer_type(self.current_tag, self.current_attrs),
                'tag': tag,
                'attrs': self.current_attrs,
                'content': ' '.join(self.current_content),
                'html': f"<{tag} {self._attrs_to_str(self.current_attrs)}>{' '.join(self.current_content)}</{tag}>"
            })
            self.current_tag = None
            self.current_content = []
        self.depth -= 1
    
    def _infer_type(self, tag, attrs):
        """Infer component type from tag and attributes."""
        classes = attrs.get('class', '').split()
        if 'card' in classes or tag == 'article':
            return 'card'
        elif 'button' in classes or tag == 'button':
            return 'button'
        elif tag == 'nav' or 'nav' in classes:
            return 'nav'
        elif tag == 'header':
            return 'header'
        elif tag == 'footer':
            return 'footer'
        return 'section'
    
    def _attrs_to_str(self, attrs):
        """Convert attributes dict to string."""
        return ' '.join([f'{k}="{v}"' for k, v in attrs.items()])


class WebsiteAnalyzer:
    """Analyzes websites and extracts UI components."""
    
    def __init__(self):
        self.extracted_components: List[ExtractedComponent] = []
    
    async def analyze_url(self, url: str) -> List[ExtractedComponent]:
        """
        Analyze a website URL and extract UI components.
        
        Args:
            url: Website URL to analyze
            
        Returns:
            List of extracted components
        """
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    html_content = await response.text()
                    return self.analyze_html(html_content, base_url=url)
        except ImportError:
            # Fallback to requests if aiohttp not available
            import requests
            response = requests.get(url)
            return self.analyze_html(response.text, base_url=url)
    
    def analyze_html(self, html_content: str, base_url: str = "") -> List[ExtractedComponent]:
        """
        Analyze HTML content and extract components.
        
        Args:
            html_content: HTML content
            base_url: Base URL for resolving links
            
        Returns:
            List of extracted components
        """
        # Extract CSS
        css_styles = self._extract_css(html_content)
        
        # Extract components
        parser = HTMLComponentExtractor()
        parser.feed(html_content)
        
        components = []
        for i, comp_data in enumerate(parser.components):
            # Convert HTML to markdown
            markdown = self._html_to_markdown(comp_data['html'])
            
            component = ExtractedComponent(
                component_id=comp_data['id'],
                component_type=comp_data['type'],
                html_content=comp_data['html'],
                css_styles={comp_data['id']: css_styles.get(comp_data['id'], '')},
                markdown_content=markdown,
                metadata={
                    'tag': comp_data['tag'],
                    'attrs': comp_data['attrs'],
                    'source_url': base_url
                }
            )
            components.append(component)
        
        self.extracted_components.extend(components)
        return components
    
    def _extract_css(self, html_content: str) -> Dict[str, str]:
        """Extract CSS styles from HTML."""
        css_dict = {}
        
        # Extract <style> tags
        style_pattern = r'<style[^>]*>(.*?)</style>'
        styles = re.findall(style_pattern, html_content, re.DOTALL)
        
        for style_block in styles:
            # Extract class/id rules
            class_pattern = r'\.([\w-]+)\s*\{([^}]+)\}'
            id_pattern = r'#([\w-]+)\s*\{([^}]+)\}'
            
            for match in re.finditer(class_pattern, style_block):
                css_dict[match.group(1)] = match.group(2)
            for match in re.finditer(id_pattern, style_block):
                css_dict[match.group(1)] = match.group(2)
        
        return css_dict
    
    def _html_to_markdown(self, html_content: str) -> str:
        """Convert HTML to markdown."""
        # Simple HTML to markdown conversion
        # Remove HTML tags, preserve structure
        
        # Headers
        html_content = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', html_content, flags=re.DOTALL)
        
        # Links
        html_content = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', html_content, flags=re.DOTALL)
        
        # Images
        html_content = re.sub(r'<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*>', r'![\2](\1)', html_content)
        
        # Lists
        html_content = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1', html_content, flags=re.DOTALL)
        
        # Remove remaining HTML tags
        html_content = re.sub(r'<[^>]+>', '', html_content)
        
        # Decode HTML entities
        html_content = html.unescape(html_content)
        
        return html_content.strip()


class ThemeTransformer:
    """Transforms UI components with personal themes."""
    
    def __init__(self, theme: Theme):
        """
        Initialize theme transformer.
        
        Args:
            theme: Personal theme configuration
        """
        self.theme = theme
    
    def transform_resource(self, resource: Dict) -> Dict:
        """
        Transform a resource with theme.
        
        Args:
            resource: Original resource dict
            
        Returns:
            Transformed resource dict
        """
        if resource.get('mimeType') != 'text/markdown':
            return resource
        
        content = resource.get('content', '')
        
        # Apply theme transformations
        transformed_content = self._apply_theme_to_markdown(content)
        
        # Create transformed resource
        transformed = resource.copy()
        transformed['content'] = transformed_content
        transformed['metadata'] = transformed.get('metadata', {}).copy()
        transformed['metadata']['theme'] = self.theme.name
        transformed['metadata']['transformed'] = True
        
        return transformed
    
    def _apply_theme_to_markdown(self, markdown: str) -> str:
        """Apply theme to markdown content."""
        # Add theme CSS as HTML block
        theme_css = self._generate_theme_css()
        
        # Wrap content with theme styling
        themed_content = f"""---
theme: {self.theme.name}
---

<style>
{theme_css}
</style>

{markdown}
"""
        return themed_content
    
    def _generate_theme_css(self) -> str:
        """Generate CSS from theme."""
        css = f"""
:root {{
    --primary-color: {self.theme.colors.get('primary', '#007bff')};
    --secondary-color: {self.theme.colors.get('secondary', '#6c757d')};
    --background-color: {self.theme.colors.get('background', '#ffffff')};
    --text-color: {self.theme.colors.get('text', '#000000')};
    --heading-font: {self.theme.fonts.get('heading', 'Arial, sans-serif')};
    --body-font: {self.theme.fonts.get('body', 'Arial, sans-serif')};
    --spacing-small: {self.theme.spacing.get('small', '0.5rem')};
    --spacing-medium: {self.theme.spacing.get('medium', '1rem')};
    --spacing-large: {self.theme.spacing.get('large', '2rem')};
}}

body {{
    background-color: var(--background-color);
    color: var(--text-color);
    font-family: var(--body-font);
}}

h1, h2, h3, h4, h5, h6 {{
    font-family: var(--heading-font);
    color: var(--primary-color);
}}

a {{
    color: var(--primary-color);
}}

{self.theme.styles.get('custom', '')}
"""
        return css


class UIProxyBarrier:
    """
    UI Proxy Barrier: Intercepts and transforms UI resources.
    Acts as a transformation layer between source and consumer.
    """
    
    def __init__(self, 
                 base_integration,
                 theme: Optional[Theme] = None,
                 transformations: Optional[List] = None):
        """
        Initialize UI proxy barrier.
        
        Args:
            base_integration: Base MCP UI integration
            theme: Optional personal theme
            transformations: Optional list of transformation functions
        """
        self.base_integration = base_integration
        self.theme = theme
        self.transformations = transformations or []
        self.analyzer = WebsiteAnalyzer()
        self.generated_components: Dict[str, ExtractedComponent] = {}
        
        if theme:
            self.theme_transformer = ThemeTransformer(theme)
        else:
            self.theme_transformer = None
    
    async def analyze_and_generate(self, url: str, component_prefix: str = "web") -> List[str]:
        """
        Analyze a website and generate MCP UI components.
        
        Args:
            url: Website URL to analyze
            component_prefix: Prefix for generated component IDs
            
        Returns:
            List of generated component IDs
        """
        components = await self.analyzer.analyze_url(url)
        
        generated_ids = []
        for component in components:
            component_id = f"{component_prefix}/{component.component_id}"
            
            # Register as MCP resource
            resource_uri = f"mcp-ui://{component_id}"
            self.base_integration.resources[resource_uri] = {
                "uri": resource_uri,
                "name": component.component_id.replace('_', ' ').title(),
                "description": f"Generated from {component.metadata.get('source_url', url)}",
                "mimeType": "text/markdown",
                "content": component.markdown_content,
                "metadata": {
                    "component_id": component_id,
                    "component_type": component.component_type,
                    "generated": True,
                    "source_url": component.metadata.get('source_url', url),
                    "original_html": component.html_content,
                    "css_styles": component.css_styles
                }
            }
            
            self.generated_components[component_id] = component
            generated_ids.append(component_id)
        
        return generated_ids
    
    def get_resource(self, uri: str) -> Optional[Dict]:
        """
        Get resource with transformations applied.
        
        Args:
            uri: Resource URI
            
        Returns:
            Transformed resource or None
        """
        # Get base resource
        resource = self.base_integration.get_resource(uri)
        if not resource:
            return None
        
        # Apply transformations
        transformed = resource.copy()
        
        # Apply theme if available
        if self.theme_transformer:
            transformed = self.theme_transformer.transform_resource(transformed)
        
        # Apply custom transformations
        for transform_func in self.transformations:
            transformed = transform_func(transformed)
        
        return transformed
    
    def list_resources(self) -> List[Dict]:
        """List all resources (including generated ones)."""
        return self.base_integration.list_resources()
    
    def create_theme_from_preferences(self, 
                                      colors: Dict[str, str],
                                      fonts: Dict[str, str],
                                      spacing: Dict[str, str],
                                      name: str = "personal") -> Theme:
        """
        Create a personal theme from preferences.
        
        Args:
            colors: Color preferences
            fonts: Font preferences
            spacing: Spacing preferences
            name: Theme name
            
        Returns:
            Theme object
        """
        theme = Theme(
            name=name,
            colors=colors,
            fonts=fonts,
            spacing=spacing,
            styles={}
        )
        self.theme = theme
        self.theme_transformer = ThemeTransformer(theme)
        return theme
