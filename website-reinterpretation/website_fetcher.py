"""
Website Fetcher & Parser: Fetches and parses entire websites.
Extracts HTML/CSS/JS/React components and structure.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from html.parser import HTMLParser
from dataclasses import dataclass, field

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    try:
        import requests
        REQUESTS_AVAILABLE = True
    except ImportError:
        REQUESTS_AVAILABLE = False


@dataclass
class WebsiteComponent:
    """A component extracted from a website."""
    component_id: str
    component_type: str  # panel, card, button, header, nav, etc.
    html_content: str
    css_styles: Dict[str, str] = field(default_factory=dict)
    javascript: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.metadata:
            self.metadata = {}


@dataclass
class WebsiteData:
    """Complete website data structure."""
    url: str
    html: str
    css: List[Dict[str, str]] = field(default_factory=list)  # [{url, content}, ...]
    javascript: List[Dict[str, str]] = field(default_factory=list)  # [{url, content}, ...]
    components: List[WebsiteComponent] = field(default_factory=list)
    structure: Dict = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)


class HTMLComponentExtractor(HTMLParser):
    """Extracts UI components from HTML."""
    
    def __init__(self):
        super().__init__()
        self.components: List[Dict] = []
        self.current_tag = None
        self.current_attrs = {}
        self.current_content = []
        self.depth = 0
        self.stack = []
    
    def handle_starttag(self, tag, attrs):
        self.depth += 1
        attrs_dict = dict(attrs)
        
        # Identify component types
        component_type = None
        if tag in ['header', 'nav', 'footer', 'main', 'article', 'section', 'aside']:
            component_type = tag
        elif 'class' in attrs_dict:
            classes = attrs_dict['class'].split()
            if any(c in classes for c in ['card', 'panel', 'widget', 'box']):
                component_type = 'card'
            elif any(c in classes for c in ['button', 'btn', 'link-button']):
                component_type = 'button'
            elif any(c in classes for c in ['nav', 'menu', 'navigation']):
                component_type = 'nav'
            elif any(c in classes for c in ['modal', 'dialog', 'popup']):
                component_type = 'modal'
            elif any(c in classes for c in ['sidebar', 'aside']):
                component_type = 'sidebar'
        
        if component_type or tag in ['div', 'section', 'article', 'aside']:
            self.stack.append({
                'tag': tag,
                'attrs': attrs_dict,
                'type': component_type or 'section',
                'content': [],
                'depth': self.depth
            })
    
    def handle_data(self, data):
        if self.stack:
            self.stack[-1]['content'].append(data.strip())
    
    def handle_endtag(self, tag):
        if self.stack and self.stack[-1]['tag'] == tag:
            component_data = self.stack.pop()
            if component_data['content']:
                component_id = component_data['attrs'].get('id', f"component_{len(self.components)}")
                self.components.append({
                    'id': component_id,
                    'type': component_data['type'],
                    'tag': tag,
                    'attrs': component_data['attrs'],
                    'content': ' '.join([c for c in component_data['content'] if c]),
                    'html': self._build_html(component_data)
                })
        self.depth -= 1
    
    def _build_html(self, component_data):
        """Build HTML representation."""
        attrs_str = ' '.join([f'{k}="{v}"' for k, v in component_data['attrs'].items()])
        content = ' '.join(component_data['content'])
        return f"<{component_data['tag']} {attrs_str}>{content}</{component_data['tag']}>"
    
    def _infer_type(self, tag, attrs):
        """Infer component type."""
        if tag == 'header':
            return 'header'
        elif tag == 'nav':
            return 'nav'
        elif tag == 'footer':
            return 'footer'
        elif tag == 'article':
            return 'card'
        elif tag == 'button':
            return 'button'
        return 'section'


class WebsiteFetcher:
    """Fetches and parses entire websites."""
    
    def __init__(self):
        """Initialize website fetcher."""
        self.session = None
    
    async def fetch_website(self, url: str) -> WebsiteData:
        """
        Fetch entire website and extract components.
        
        Args:
            url: Website URL to fetch
            
        Returns:
            WebsiteData with HTML, CSS, JS, and components
        """
        # Fetch HTML
        html = await self._fetch_html(url)
        
        # Extract CSS
        css_list = self._extract_css(html, url)
        
        # Extract JavaScript
        js_list = self._extract_javascript(html, url)
        
        # Parse DOM and extract components
        components = self._extract_components(html)
        
        # Build structure
        structure = self._build_structure(html)
        
        return WebsiteData(
            url=url,
            html=html,
            css=css_list,
            javascript=js_list,
            components=components,
            structure=structure,
            metadata={
                "component_count": len(components),
                "css_files": len(css_list),
                "js_files": len(js_list)
            }
        )
    
    async def _fetch_html(self, url: str) -> str:
        """Fetch HTML content."""
        if AIOHTTP_AVAILABLE:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    return await response.text()
        elif REQUESTS_AVAILABLE:
            response = requests.get(url, timeout=10)
            return response.text
        else:
            raise ImportError("Need aiohttp or requests to fetch websites")
    
    def _extract_css(self, html: str, base_url: str) -> List[Dict[str, str]]:
        """Extract CSS stylesheets."""
        css_list = []
        
        # Extract <style> tags
        style_pattern = r'<style[^>]*>(.*?)</style>'
        for match in re.finditer(style_pattern, html, re.DOTALL):
            css_list.append({
                "url": "inline",
                "content": match.group(1)
            })
        
        # Extract <link> tags for external CSS
        link_pattern = r'<link[^>]*rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)["\']'
        for match in re.finditer(link_pattern, html):
            css_url = urljoin(base_url, match.group(1))
            css_list.append({
                "url": css_url,
                "content": ""  # Would need to fetch separately
            })
        
        return css_list
    
    def _extract_javascript(self, html: str, base_url: str) -> List[Dict[str, str]]:
        """Extract JavaScript files."""
        js_list = []
        
        # Extract <script> tags
        script_pattern = r'<script[^>]*>(.*?)</script>'
        for match in re.finditer(script_pattern, html, re.DOTALL):
            script_content = match.group(1)
            if script_content.strip():
                js_list.append({
                    "url": "inline",
                    "content": script_content
                })
        
        # Extract external script src
        src_pattern = r'<script[^>]*src=["\']([^"\']+)["\']'
        for match in re.finditer(src_pattern, html):
            js_url = urljoin(base_url, match.group(1))
            js_list.append({
                "url": js_url,
                "content": ""  # Would need to fetch separately
            })
        
        return js_list
    
    def _extract_components(self, html: str) -> List[WebsiteComponent]:
        """Extract UI components from HTML."""
        parser = HTMLComponentExtractor()
        parser.feed(html)
        
        components = []
        css_styles = self._extract_css_styles(html)
        
        for comp_data in parser.components:
            component = WebsiteComponent(
                component_id=comp_data['id'],
                component_type=comp_data['type'],
                html_content=comp_data['html'],
                css_styles={
                    comp_data['id']: css_styles.get(comp_data['id'], ''),
                    **{cls: css_styles.get(cls, '') for cls in comp_data['attrs'].get('class', '').split()}
                },
                metadata={
                    'tag': comp_data['tag'],
                    'attrs': comp_data['attrs'],
                    'content': comp_data['content']
                }
            )
            components.append(component)
        
        return components
    
    def _extract_css_styles(self, html: str) -> Dict[str, str]:
        """Extract CSS styles for specific selectors."""
        css_dict = {}
        
        # Extract <style> tags
        style_pattern = r'<style[^>]*>(.*?)</style>'
        styles = re.findall(style_pattern, html, re.DOTALL)
        
        for style_block in styles:
            # Extract class rules
            class_pattern = r'\.([\w-]+)\s*\{([^}]+)\}'
            for match in re.finditer(class_pattern, style_block):
                css_dict[match.group(1)] = match.group(2)
            
            # Extract ID rules
            id_pattern = r'#([\w-]+)\s*\{([^}]+)\}'
            for match in re.finditer(id_pattern, style_block):
                css_dict[match.group(1)] = match.group(2)
        
        return css_dict
    
    def _build_structure(self, html: str) -> Dict:
        """Build website structure tree."""
        # Simple structure extraction
        structure = {
            "has_header": bool(re.search(r'<header', html, re.IGNORECASE)),
            "has_nav": bool(re.search(r'<nav', html, re.IGNORECASE)),
            "has_main": bool(re.search(r'<main', html, re.IGNORECASE)),
            "has_footer": bool(re.search(r'<footer', html, re.IGNORECASE)),
            "sections": len(re.findall(r'<section', html, re.IGNORECASE)),
            "articles": len(re.findall(r'<article', html, re.IGNORECASE)),
            "divs": len(re.findall(r'<div', html, re.IGNORECASE))
        }
        
        return structure
    
    def detect_react_components(self, html: str, js_list: List[Dict]) -> List[str]:
        """Detect React/Vue/Angular components."""
        components = []
        
        # Look for React component patterns
        react_pattern = r'(?:class|function)\s+(\w+)\s+extends\s+(?:React\.)?Component'
        for js_item in js_list:
            if js_item.get('content'):
                matches = re.findall(react_pattern, js_item['content'])
                components.extend(matches)
        
        # Look for JSX patterns in HTML
        jsx_pattern = r'<(\w+)[A-Z]'
        matches = re.findall(jsx_pattern, html)
        components.extend([m for m in matches if m[0].isupper()])
        
        return list(set(components))


def create_website_fetcher() -> WebsiteFetcher:
    """Create website fetcher instance."""
    return WebsiteFetcher()
