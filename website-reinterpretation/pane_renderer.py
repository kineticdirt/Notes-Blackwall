"""
Visual Pane Renderer: Renders transformed components as visual panes.
Generates final HTML/CSS output with ASCII/dithered/shaded effects.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from blackwall.worktrees.mcp_integration.advanced_theme import ShaderEngine, AdvancedTheme
from component_transformer import VisualPane


class PaneRenderer:
    """Renders visual panes into final HTML/CSS."""
    
    def __init__(self):
        """Initialize pane renderer."""
        self.shader_engine = ShaderEngine()
    
    def render(self, panes: List[VisualPane], layout: str = "vertical") -> Dict[str, str]:
        """
        Render panes into final HTML/CSS.
        
        Args:
            panes: List of visual panes to render
            layout: Layout type ("vertical", "horizontal", "grid")
            
        Returns:
            Dict with "html" and "css" keys
        """
        # Generate HTML
        html = self._generate_html(panes, layout)
        
        # Generate CSS
        css = self._generate_css(panes)
        
        return {
            "html": html,
            "css": css,
            "panes_count": len(panes)
        }
    
    def _generate_html(self, panes: List[VisualPane], layout: str) -> str:
        """Generate HTML structure."""
        html_parts = [
            "<!DOCTYPE html>",
            "<html lang='en'>",
            "<head>",
            "<meta charset='UTF-8'>",
            "<meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            "<title>Transformed Website</title>",
            "<link rel='stylesheet' href='style.css'>",
            "</head>",
            "<body>",
            "<div class='grainrad-container'>"
        ]
        
        # Add panes
        for pane in panes:
            pane_html = self._render_pane_html(pane)
            html_parts.append(pane_html)
        
        html_parts.extend([
            "</div>",
            "</body>",
            "</html>"
        ])
        
        return "\n".join(html_parts)
    
    def _render_pane_html(self, pane: VisualPane) -> str:
        """Render individual pane as HTML."""
        pane_class = f"pane-{pane.pane_type}"
        dither_class = "dithered" if pane.dithering else ""
        shader_class = "shaded" if pane.shaders else ""
        
        # Escape ASCII content for HTML
        ascii_escaped = pane.ascii_content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        return f"""
<div class="pane {pane_class} {dither_class} {shader_class}" id="{pane.pane_id}">
    <pre class="ascii-content">{ascii_escaped}</pre>
</div>
""".strip()
    
    def _generate_css(self, panes: List[VisualPane]) -> str:
        """Generate CSS with shader effects."""
        # Base CSS
        css_parts = [
            "/* Grainrad Theme CSS */",
            "* { margin: 0; padding: 0; box-sizing: border-box; }",
            "",
            "body {",
            "    font-family: 'Courier New', monospace;",
            "    background-color: #1a1a1a;",
            "    color: #00ff88;",
            "    padding: 2rem;",
            "    position: relative;",
            "}"
        ]
        
        # Shader effects (from first pane with shaders or default)
        shader_pane = next((p for p in panes if p.shaders), None)
        if shader_pane:
            theme = AdvancedTheme(
                name="grainrad",
                dithering={},
                ascii_config={},
                shader_config={
                    "noise": shader_pane.shaders.get("noise", 0.15),
                    "grain": shader_pane.shaders.get("grain", 0.08),
                    "scanlines": shader_pane.shaders.get("scanlines", True)
                },
                ad_blocking={},
                graphics_mode="hybrid"
            )
            shader_css = self.shader_engine.generate_shader_css(theme)
            css_parts.append("\n/* Shader Effects */")
            css_parts.append(shader_css)
        
        # Container styles
        css_parts.extend([
            "",
            ".grainrad-container {",
            "    max-width: 1200px;",
            "    margin: 0 auto;",
            "    display: flex;",
            "    flex-direction: column;",
            "    gap: 2rem;",
            "}"
        ])
        
        # Pane styles
        css_parts.extend([
            "",
            ".pane {",
            "    background: rgba(0, 0, 0, 0.5);",
            "    border: 1px solid #00ff88;",
            "    padding: 1rem;",
            "    position: relative;",
            "}",
            "",
            ".ascii-content {",
            "    font-family: 'Courier New', monospace;",
            "    font-size: 0.8rem;",
            "    line-height: 1.4;",
            "    white-space: pre;",
            "    color: #00ff88;",
            "    margin: 0;",
            "}"
        ])
        
        # Dithering effects
        css_parts.extend([
            "",
            ".dithered {",
            "    background-image: repeating-linear-gradient(",
            "        45deg,",
            "        transparent,",
            "        transparent 2px,",
            "        rgba(0, 255, 136, 0.05) 2px,",
            "        rgba(0, 255, 136, 0.05) 4px",
            "    );",
            "}"
        ])
        
        # Specific pane types
        css_parts.extend([
            "",
            ".pane-panel {",
            "    border-style: double;",
            "}",
            "",
            ".pane-card {",
            "    border-radius: 0;",
            "    border-style: solid;",
            "}",
            "",
            ".pane-button {",
            "    display: inline-block;",
            "    cursor: pointer;",
            "    transition: opacity 0.2s;",
            "}",
            "",
            ".pane-button:hover {",
            "    opacity: 0.8;",
            "}",
            "",
            ".pane-nav {",
            "    border-style: double;",
            "    border-width: 2px;",
            "}"
        ])
        
        return "\n".join(css_parts)
    
    def render_to_file(self, panes: List[VisualPane], output_dir: Path, layout: str = "vertical"):
        """
        Render panes to HTML/CSS files.
        
        Args:
            panes: List of visual panes
            output_dir: Output directory
            layout: Layout type
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        result = self.render(panes, layout)
        
        # Write HTML
        html_file = output_dir / "index.html"
        html_file.write_text(result["html"])
        
        # Write CSS
        css_file = output_dir / "style.css"
        css_file.write_text(result["css"])
        
        return {
            "html_file": str(html_file),
            "css_file": str(css_file),
            "panes": len(panes)
        }


def create_pane_renderer() -> PaneRenderer:
    """Create pane renderer instance."""
    return PaneRenderer()
