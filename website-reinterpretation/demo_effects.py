#!/usr/bin/env python3
"""
Demo: Show grainrad-style effects working on a website.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from blackwall.worktrees.mcp_integration.advanced_theme import (
    AdvancedTheme,
    AdvancedThemeTransformer,
    ShaderEngine
)


def demo_shader_css():
    """Show what the shader CSS looks like."""
    print("=" * 70)
    print("GRAINRAD SHADER EFFECTS DEMO")
    print("=" * 70)
    
    theme = AdvancedTheme(
        name="grainrad-demo",
        dithering={"method": "floyd_steinberg", "intensity": 0.7},
        ascii_config={"width": 80, "extended": True},
        shader_config={
            "noise": 0.15,
            "grain": 0.08,
            "scanlines": True,
            "crt_effect": True
        },
        ad_blocking={"patterns": [], "enabled": False},
        graphics_mode="hybrid"
    )
    
    engine = ShaderEngine()
    css = engine.generate_shader_css(theme)
    
    print("\nGenerated Shader CSS:")
    print("-" * 70)
    print(css)
    print("-" * 70)
    
    print("\n✅ Effects include:")
    print("  - Scanlines (CRT horizontal bands)")
    print("  - Grain/noise texture overlay")
    print("  - Pixelated image rendering")
    print("  - Retro terminal aesthetic")
    
    # Save to file for inspection
    css_file = Path(__file__).parent / "grainrad_effects.css"
    css_file.write_text(css)
    print(f"\n✅ CSS saved to: {css_file}")
    
    return css


def demo_html_injection():
    """Show how effects are injected into HTML."""
    print("\n" + "=" * 70)
    print("HTML INJECTION DEMO")
    print("=" * 70)
    
    sample_html = """<!DOCTYPE html>
<html>
<head>
    <title>Example</title>
</head>
<body>
    <h1>Hello World</h1>
    <p>This is a test page.</p>
</body>
</html>"""
    
    css = demo_shader_css()
    
    # Inject CSS
    if '<head>' in sample_html:
        transformed = sample_html.replace('<head>', f'<head>\n<style>\n{css}\n</style>')
    else:
        transformed = f'<head><style>{css}</style></head>{sample_html}'
    
    print("\nOriginal HTML length:", len(sample_html))
    print("Transformed HTML length:", len(transformed))
    print("\nTransformed HTML preview:")
    print(transformed[:500])
    print("...")
    
    print("\n✅ HTML injection working")


if __name__ == "__main__":
    demo_shader_css()
    demo_html_injection()
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print("\nTo see effects on a real website:")
    print("  ENABLE_EFFECTS=true python3 run_proxy.py")
    print("  curl http://localhost:8001/proxy/https://example.com")
