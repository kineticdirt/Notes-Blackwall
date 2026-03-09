"""
Advanced Theme System: Dithering + ASCII + Shaders
Inspired by grainrad.com aesthetic.
"""

import re
import base64
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import math


@dataclass
class AdvancedTheme:
    """Advanced theme with dithering, ASCII, and shader support."""
    name: str
    dithering: Dict[str, any]  # dithering config
    ascii_config: Dict[str, any]  # ASCII art config
    shader_config: Dict[str, any]  # Shader config
    ad_blocking: Dict[str, List[str]]  # Ad patterns to block
    graphics_mode: str  # "ascii", "dither", "shader", "hybrid"
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class DitheringEngine:
    """Dithering effects for graphics."""
    
    # Floyd-Steinberg dithering matrix
    FLOYD_STEINBERG = [
        [0, 0, 7/16],
        [3/16, 5/16, 1/16]
    ]
    
    # Ordered dithering (Bayer matrix 4x4)
    BAYER_4X4 = [
        [0, 8, 2, 10],
        [12, 4, 14, 6],
        [3, 11, 1, 9],
        [15, 7, 13, 5]
    ]
    
    def __init__(self, method: str = "floyd_steinberg"):
        """
        Initialize dithering engine.
        
        Args:
            method: Dithering method ("floyd_steinberg", "ordered", "atkinson")
        """
        self.method = method
    
    def dither_text(self, text: str, width: int = 80) -> str:
        """
        Apply dithering effect to text (ASCII art style).
        
        Args:
            text: Input text
            width: Output width
            
        Returns:
            Dithered ASCII text
        """
        lines = text.split('\n')
        dithered = []
        
        for line in lines:
            if len(line) > width:
                line = line[:width]
            
            # Apply dithering pattern
            dithered_line = ""
            for i, char in enumerate(line):
                if self.method == "floyd_steinberg":
                    # Simulate dithering with character density
                    density = ord(char) % 16
                    if density < 4:
                        dithered_line += " "
                    elif density < 8:
                        dithered_line += "."
                    elif density < 12:
                        dithered_line += ":"
                    else:
                        dithered_line += char
                else:
                    dithered_line += char
            
            dithered.append(dithered_line)
        
        return '\n'.join(dithered)
    
    def generate_dither_pattern(self, width: int, height: int) -> List[List[int]]:
        """
        Generate dithering pattern.
        
        Args:
            width: Pattern width
            height: Pattern height
            
        Returns:
            2D pattern array
        """
        pattern = []
        
        if self.method == "ordered":
            # Bayer ordered dithering
            for y in range(height):
                row = []
                for x in range(width):
                    bayer_x = x % 4
                    bayer_y = y % 4
                    value = self.BAYER_4X4[bayer_y][bayer_x] / 16.0
                    row.append(value)
                pattern.append(row)
        else:
            # Floyd-Steinberg style
            for y in range(height):
                row = []
                for x in range(width):
                    # Simple noise pattern
                    value = ((x + y) % 8) / 8.0
                    row.append(value)
                pattern.append(row)
        
        return pattern


class ASCIIConverter:
    """Convert images/graphics to ASCII art."""
    
    # ASCII character gradient (dark to light)
    ASCII_CHARS = " .:-=+*#%@"
    # Extended gradient for better quality
    ASCII_CHARS_EXTENDED = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
    
    def __init__(self, width: int = 80, use_extended: bool = True):
        """
        Initialize ASCII converter.
        
        Args:
            width: Output width in characters
            use_extended: Use extended character set
        """
        self.width = width
        self.chars = self.ASCII_CHARS_EXTENDED if use_extended else self.ASCII_CHARS
    
    def image_to_ascii(self, image_data: bytes, format: str = "auto") -> str:
        """
        Convert image to ASCII art.
        
        Args:
            image_data: Image bytes
            format: Image format ("auto", "png", "jpg", etc.)
            
        Returns:
            ASCII art string
        """
        try:
            from PIL import Image
            import io
            
            # Load image
            img = Image.open(io.BytesIO(image_data))
            
            # Convert to grayscale
            img = img.convert('L')
            
            # Resize to fit width
            aspect_ratio = img.height / img.width
            height = int(self.width * aspect_ratio * 0.5)  # 0.5 for character aspect
            
            img = img.resize((self.width, height))
            
            # Convert to ASCII
            pixels = img.getdata()
            ascii_art = []
            
            for i in range(0, len(pixels), self.width):
                row = pixels[i:i+self.width]
                ascii_row = ''.join([
                    self.chars[min(int(pixel / 255 * (len(self.chars) - 1)), len(self.chars) - 1)]
                    for pixel in row
                ])
                ascii_art.append(ascii_row)
            
            return '\n'.join(ascii_art)
        
        except ImportError:
            # Fallback: return placeholder
            return self._placeholder_ascii()
        except Exception as e:
            return f"[ASCII Conversion Error: {str(e)}]"
    
    def url_to_ascii(self, url: str) -> str:
        """
        Convert image URL to ASCII art.
        
        Args:
            url: Image URL
            
        Returns:
            ASCII art string
        """
        try:
            import requests
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return self.image_to_ascii(response.content)
        except Exception:
            pass
        
        return self._placeholder_ascii()
    
    def _placeholder_ascii(self) -> str:
        """Generate placeholder ASCII art."""
        return """
    ╔═══════════════════════════════╗
    ║   [IMAGE PLACEHOLDER]         ║
    ║                               ║
    ║   ASCII representation        ║
    ║   would appear here           ║
    ╚═══════════════════════════════╝
        """
    
    def text_to_ascii_banner(self, text: str) -> str:
        """Convert text to ASCII banner."""
        # Simple ASCII banner
        border = "═" * (len(text) + 4)
        return f"""
╔{border}╗
║  {text}  ║
╚{border}╝
        """.strip()


class ShaderEngine:
    """Shader-based graphics rendering."""
    
    def __init__(self):
        """Initialize shader engine."""
        pass
    
    def generate_shader_css(self, theme: AdvancedTheme) -> str:
        """
        Generate CSS with shader effects.
        
        Args:
            theme: Advanced theme configuration
            
        Returns:
            CSS with shader effects
        """
        shader_config = theme.shader_config
        
        # GLSL-like shader effects via CSS
        css = f"""
/* Shader-based graphics */
:root {{
    --shader-noise: {shader_config.get('noise', 0.1)};
    --shader-grain: {shader_config.get('grain', 0.05)};
    --shader-scanlines: {shader_config.get('scanlines', True)};
}}

body {{
    background: 
        repeating-linear-gradient(
            0deg,
            rgba(0, 0, 0, var(--shader-grain)),
            rgba(0, 0, 0, var(--shader-grain)) 1px,
            transparent 1px,
            transparent 2px
        ),
        var(--background-color);
    
    position: relative;
}}

/* Scanline effect */
body::before {{
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0, 0, 0, 0.03) 2px,
        rgba(0, 0, 0, 0.03) 4px
    );
    pointer-events: none;
    z-index: 9999;
}}

/* Grain/noise effect */
body::after {{
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.1'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 9998;
    opacity: var(--shader-noise);
}}

/* Dithering effect on images */
img {{
    image-rendering: pixelated;
    image-rendering: -moz-crisp-edges;
    image-rendering: crisp-edges;
    filter: contrast(1.2) brightness(0.95);
}}
"""
        return css


class AdBlocker:
    """Selective ad blocking through MCP UI transformation."""
    
    def __init__(self, patterns: List[str]):
        """
        Initialize ad blocker.
        
        Args:
            patterns: List of ad patterns/selectors to block
        """
        self.patterns = patterns
        self.blocked_count = 0
    
    def is_ad(self, element: Dict) -> bool:
        """
        Check if element is an ad.
        
        Args:
            element: Element metadata
            
        Returns:
            True if ad, False otherwise
        """
        # Check class names
        classes = element.get('attrs', {}).get('class', '').lower()
        for pattern in self.patterns:
            if pattern.lower() in classes:
                return True
        
        # Check IDs
        element_id = element.get('attrs', {}).get('id', '').lower()
        for pattern in self.patterns:
            if pattern.lower() in element_id:
                return True
        
        # Check common ad patterns
        ad_keywords = ['ad', 'advertisement', 'sponsor', 'promo', 'banner']
        for keyword in ad_keywords:
            if keyword in classes or keyword in element_id:
                return True
        
        return False
    
    def remove_ads_from_html(self, html: str) -> str:
        """
        Remove ads from HTML content.
        
        Args:
            html: HTML content
            
        Returns:
            HTML with ads removed
        """
        import re
        
        # Remove elements matching ad patterns
        for pattern in self.patterns:
            # Remove by class
            html = re.sub(
                rf'<[^>]*class="[^"]*{re.escape(pattern)}[^"]*"[^>]*>.*?</[^>]+>',
                '',
                html,
                flags=re.DOTALL | re.IGNORECASE
            )
            # Remove by ID
            html = re.sub(
                rf'<[^>]*id="[^"]*{re.escape(pattern)}[^"]*"[^>]*>.*?</[^>]+>',
                '',
                html,
                flags=re.DOTALL | re.IGNORECASE
            )
        
        # Remove common ad patterns
        ad_patterns = [
            r'<div[^>]*class="[^"]*ad[^"]*"[^>]*>.*?</div>',
            r'<iframe[^>]*>.*?</iframe>',  # Many ads are iframes
        ]
        
        for pattern in ad_patterns:
            html = re.sub(pattern, '', html, flags=re.DOTALL | re.IGNORECASE)
        
        self.blocked_count += html.count('<!-- AD REMOVED -->')
        return html
    
    def remove_ads_from_markdown(self, markdown: str) -> str:
        """
        Remove ads from markdown content.
        
        Args:
            markdown: Markdown content
            
        Returns:
            Markdown with ads removed
        """
        lines = markdown.split('\n')
        filtered = []
        skip_block = False
        
        for line in lines:
            # Check for ad patterns
            is_ad_line = any(pattern.lower() in line.lower() for pattern in self.patterns)
            
            if is_ad_line:
                skip_block = True
                continue
            
            if skip_block and line.strip() == '':
                skip_block = False
                continue
            
            if not skip_block:
                filtered.append(line)
        
        return '\n'.join(filtered)


class AdvancedThemeTransformer:
    """Advanced theme transformer with dithering, ASCII, shaders, and ad blocking."""
    
    def __init__(self, theme: AdvancedTheme):
        """
        Initialize advanced theme transformer.
        
        Args:
            theme: Advanced theme configuration
        """
        self.theme = theme
        self.dithering_engine = DitheringEngine(method=theme.dithering.get('method', 'floyd_steinberg'))
        self.ascii_converter = ASCIIConverter(
            width=theme.ascii_config.get('width', 80),
            use_extended=theme.ascii_config.get('extended', True)
        )
        self.shader_engine = ShaderEngine()
        self.ad_blocker = AdBlocker(theme.ad_blocking.get('patterns', []))
    
    def transform_resource(self, resource: Dict) -> Dict:
        """
        Transform resource with advanced theme.
        
        Args:
            resource: Original resource
            
        Returns:
            Transformed resource
        """
        if resource.get('mimeType') != 'text/markdown':
            return resource
        
        content = resource.get('content', '')
        
        # Step 1: Remove ads
        content = self.ad_blocker.remove_ads_from_markdown(content)
        
        # Step 2: Convert images to ASCII if in ASCII mode
        if self.theme.graphics_mode in ['ascii', 'hybrid']:
            content = self._replace_images_with_ascii(content)
        
        # Step 3: Apply dithering if enabled
        if self.theme.graphics_mode in ['dither', 'hybrid']:
            content = self._apply_dithering(content)
        
        # Step 4: Generate shader CSS
        shader_css = self.shader_engine.generate_shader_css(self.theme)
        
        # Step 5: Wrap with theme
        themed_content = f"""---
theme: {self.theme.name}
graphics_mode: {self.theme.graphics_mode}
---

<style>
{shader_css}
</style>

{content}
"""
        
        # Create transformed resource
        transformed = resource.copy()
        transformed['content'] = themed_content
        transformed['metadata'] = transformed.get('metadata', {}).copy()
        transformed['metadata']['theme'] = self.theme.name
        transformed['metadata']['graphics_mode'] = self.theme.graphics_mode
        transformed['metadata']['ads_blocked'] = self.ad_blocker.blocked_count
        transformed['metadata']['transformed'] = True
        
        return transformed
    
    def _replace_images_with_ascii(self, markdown: str) -> str:
        """Replace image references with ASCII art."""
        # Find image patterns: ![alt](url)
        pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        
        def replace_image(match):
            alt_text = match.group(1)
            url = match.group(2)
            
            # Try to convert to ASCII
            ascii_art = self.ascii_converter.url_to_ascii(url)
            
            # Wrap in code block for formatting
            return f"\n```\n{ascii_art}\n```\n*{alt_text}*\n"
        
        return re.sub(pattern, replace_image, markdown)
    
    def _apply_dithering(self, markdown: str) -> str:
        """Apply dithering effect to text."""
        lines = markdown.split('\n')
        dithered_lines = []
        
        for line in lines:
            # Apply dithering to non-code blocks
            if not line.strip().startswith('```'):
                dithered_line = self.dithering_engine.dither_text(line)
                dithered_lines.append(dithered_line)
            else:
                dithered_lines.append(line)
        
        return '\n'.join(dithered_lines)
