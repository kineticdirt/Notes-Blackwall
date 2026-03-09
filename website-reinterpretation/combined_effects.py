"""
Combined Effects System
Combines multiple effects: ASCII, Dithering, Halftone, Matrix Rain, etc.
Based on Efecto and grainrad techniques.
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

sys.path.insert(0, str(Path(__file__).parent.parent))

from blackwall.worktrees.mcp_integration.advanced_theme import (
    AdvancedTheme,
    AdvancedThemeTransformer,
    DitheringEngine,
    ASCIIConverter,
    ShaderEngine,
    AdBlocker
)


@dataclass
class EffectConfig:
    """Configuration for a single effect."""
    name: str
    enabled: bool = True
    intensity: float = 1.0
    params: Dict = None
    
    def __post_init__(self):
        if self.params is None:
            self.params = {}


class CombinedEffectsProcessor:
    """Processes content with multiple combined effects."""
    
    def __init__(self, effects: List[str] = None):
        """
        Initialize combined effects processor.
        
        Args:
            effects: List of effect names to enable
                    Options: ascii, dithering, halftone, matrix_rain, dots,
                             contour, pixel_sort, blockify, threshold,
                             edge_detection, crosshatch, wave_lines,
                             noise_field, voronoi, vhs
        """
        if effects is None:
            effects = ["dithering", "ascii", "scanlines", "grain"]
        
        self.effects = effects
        self.dithering_engine = DitheringEngine(method="floyd_steinberg")
        self.ascii_converter = ASCIIConverter(width=80, use_extended=True)
        self.shader_engine = ShaderEngine()
        self.ad_blocker = AdBlocker(["advertisement", "sponsor", "promo"])
        
        # Effect configurations
        self.effect_configs = {
            "ascii": EffectConfig("ascii", enabled="ascii" in effects),
            "dithering": EffectConfig("dithering", enabled="dithering" in effects),
            "halftone": EffectConfig("halftone", enabled="halftone" in effects),
            "matrix_rain": EffectConfig("matrix_rain", enabled="matrix_rain" in effects),
            "dots": EffectConfig("dots", enabled="dots" in effects),
            "contour": EffectConfig("contour", enabled="contour" in effects),
            "pixel_sort": EffectConfig("pixel_sort", enabled="pixel_sort" in effects),
            "blockify": EffectConfig("blockify", enabled="blockify" in effects),
            "threshold": EffectConfig("threshold", enabled="threshold" in effects),
            "edge_detection": EffectConfig("edge_detection", enabled="edge_detection" in effects),
            "crosshatch": EffectConfig("crosshatch", enabled="crosshatch" in effects),
            "wave_lines": EffectConfig("wave_lines", enabled="wave_lines" in effects),
            "noise_field": EffectConfig("noise_field", enabled="noise_field" in effects),
            "voronoi": EffectConfig("voronoi", enabled="voronoi" in effects),
            "vhs": EffectConfig("vhs", enabled="vhs" in effects),
            "scanlines": EffectConfig("scanlines", enabled="scanlines" in effects),
            "grain": EffectConfig("grain", enabled="grain" in effects),
        }
    
    def generate_combined_css(self) -> str:
        """Generate CSS combining all enabled effects."""
        css_parts = []
        
        # Base shader CSS
        theme = AdvancedTheme(
            name="combined-effects",
            dithering={"method": "floyd_steinberg", "intensity": 0.7},
            ascii_config={"width": 80, "extended": True},
            shader_config={
                "noise": 0.15 if self.effect_configs["grain"].enabled else 0.0,
                "grain": 0.08 if self.effect_configs["grain"].enabled else 0.0,
                "scanlines": self.effect_configs["scanlines"].enabled,
                "crt_effect": True
            },
            ad_blocking={"patterns": [], "enabled": False},
            graphics_mode="hybrid"
        )
        
        base_css = self.shader_engine.generate_shader_css(theme)
        css_parts.append(base_css)
        
        # Additional effect CSS
        if self.effect_configs["halftone"].enabled:
            css_parts.append(self._halftone_css())
        
        if self.effect_configs["matrix_rain"].enabled:
            css_parts.append(self._matrix_rain_css())
        
        if self.effect_configs["dots"].enabled:
            css_parts.append(self._dots_css())
        
        if self.effect_configs["contour"].enabled:
            css_parts.append(self._contour_css())
        
        if self.effect_configs["pixel_sort"].enabled:
            css_parts.append(self._pixel_sort_css())
        
        if self.effect_configs["blockify"].enabled:
            css_parts.append(self._blockify_css())
        
        if self.effect_configs["threshold"].enabled:
            css_parts.append(self._threshold_css())
        
        if self.effect_configs["edge_detection"].enabled:
            css_parts.append(self._edge_detection_css())
        
        if self.effect_configs["crosshatch"].enabled:
            css_parts.append(self._crosshatch_css())
        
        if self.effect_configs["wave_lines"].enabled:
            css_parts.append(self._wave_lines_css())
        
        if self.effect_configs["noise_field"].enabled:
            css_parts.append(self._noise_field_css())
        
        if self.effect_configs["voronoi"].enabled:
            css_parts.append(self._voronoi_css())
        
        if self.effect_configs["vhs"].enabled:
            css_parts.append(self._vhs_css())
        
        return "\n\n".join(css_parts)
    
    def _halftone_css(self) -> str:
        """Halftone effect CSS."""
        return """
/* Halftone effect */
img, video {
    filter: contrast(1.5) brightness(0.9);
    image-rendering: pixelated;
}

.halftone-overlay {
    position: relative;
}

.halftone-overlay::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: radial-gradient(circle, #000 1px, transparent 1px);
    background-size: 4px 4px;
    opacity: 0.3;
    pointer-events: none;
}
"""
    
    def _matrix_rain_css(self) -> str:
        """Matrix rain effect CSS."""
        return """
/* Matrix rain effect */
@keyframes matrix-rain {
    0% { transform: translateY(-100%); }
    100% { transform: translateY(100vh); }
}

.matrix-rain {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 10000;
    background: repeating-linear-gradient(
        0deg,
        rgba(0, 255, 0, 0.03),
        rgba(0, 255, 0, 0.03) 2px,
        transparent 2px,
        transparent 4px
    );
    animation: matrix-rain 10s linear infinite;
}
"""
    
    def _dots_css(self) -> str:
        """Dots effect CSS."""
        return """
/* Dots effect */
body {
    background-image: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
    background-size: 8px 8px;
}
"""
    
    def _contour_css(self) -> str:
        """Contour/edge detection CSS."""
        return """
/* Contour effect */
img {
    filter: contrast(2) brightness(0.8) drop-shadow(0 0 2px #fff);
}
"""
    
    def _pixel_sort_css(self) -> str:
        """Pixel sort effect CSS."""
        return """
/* Pixel sort effect */
img {
    image-rendering: pixelated;
    filter: contrast(1.3) saturate(1.2);
}
"""
    
    def _blockify_css(self) -> str:
        """Blockify effect CSS."""
        return """
/* Blockify effect */
img {
    image-rendering: pixelated;
    image-rendering: -moz-crisp-edges;
    image-rendering: crisp-edges;
}
"""
    
    def _threshold_css(self) -> str:
        """Threshold effect CSS."""
        return """
/* Threshold effect */
img {
    filter: contrast(2) brightness(0.5);
}
"""
    
    def _edge_detection_css(self) -> str:
        """Edge detection CSS."""
        return """
/* Edge detection */
img {
    filter: contrast(3) brightness(0.7) drop-shadow(0 0 3px #00ff88);
}
"""
    
    def _crosshatch_css(self) -> str:
        """Crosshatch effect CSS."""
        return """
/* Crosshatch effect */
body {
    background-image: 
        repeating-linear-gradient(45deg, transparent, transparent 2px, rgba(255,255,255,0.05) 2px, rgba(255,255,255,0.05) 4px),
        repeating-linear-gradient(-45deg, transparent, transparent 2px, rgba(255,255,255,0.05) 2px, rgba(255,255,255,0.05) 4px);
}
"""
    
    def _wave_lines_css(self) -> str:
        """Wave lines effect CSS."""
        return """
/* Wave lines effect */
@keyframes wave {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

body::before {
    animation: wave 3s ease-in-out infinite;
}
"""
    
    def _noise_field_css(self) -> str:
        """Noise field effect CSS."""
        return """
/* Noise field effect */
body::after {
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='1.2' numOctaves='6'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.2'/%3E%3C/svg%3E");
}
"""
    
    def _voronoi_css(self) -> str:
        """Voronoi effect CSS."""
        return """
/* Voronoi effect */
body {
    background-image: 
        radial-gradient(circle at 20% 30%, rgba(0,255,136,0.1) 0%, transparent 50%),
        radial-gradient(circle at 80% 70%, rgba(0,255,136,0.1) 0%, transparent 50%);
}
"""
    
    def _vhs_css(self) -> str:
        """VHS effect CSS."""
        return """
/* VHS effect */
@keyframes vhs-scan {
    0% { transform: translateY(0); opacity: 1; }
    50% { transform: translateY(2px); opacity: 0.98; }
    100% { transform: translateY(0); opacity: 1; }
}

body {
    animation: vhs-scan 0.1s infinite;
}

/* VHS color distortion */
body::before {
    background: 
        linear-gradient(0deg, rgba(255,0,0,0.1) 0%, transparent 50%),
        linear-gradient(0deg, rgba(0,255,0,0.1) 50%, transparent 100%);
}
"""
    
    def process_html(self, html_content: str) -> str:
        """Process HTML with combined effects."""
        # Generate combined CSS
        combined_css = self.generate_combined_css()
        
        # Inject CSS into HTML
        if '<head>' in html_content:
            html_content = html_content.replace('<head>', f'<head>\n<style>\n{combined_css}\n</style>')
        elif '<html>' in html_content:
            html_content = html_content.replace('<html>', f'<html>\n<head>\n<style>\n{combined_css}\n</style>\n</head>')
        else:
            html_content = f'<head><style>{combined_css}</style></head>{html_content}'
        
        # Add matrix rain overlay if enabled
        if self.effect_configs["matrix_rain"].enabled:
            if '</body>' in html_content:
                html_content = html_content.replace('</body>', '<div class="matrix-rain"></div></body>')
            elif '<body>' in html_content:
                # Insert before closing body or at end
                html_content = html_content.replace('<body>', '<body><div class="matrix-rain"></div>')
            else:
                html_content += '<div class="matrix-rain"></div>'
        
        return html_content


def create_combined_effects_processor(effects: List[str]) -> CombinedEffectsProcessor:
    """Create combined effects processor."""
    return CombinedEffectsProcessor(effects=effects)
