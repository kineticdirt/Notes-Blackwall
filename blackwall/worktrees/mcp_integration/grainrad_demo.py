#!/usr/bin/env python3
"""
Grainrad-inspired Demo: Advanced theme with dithering, ASCII, shaders, and ad blocking.
Demonstrates the expanded MCP UI system with grainrad.com aesthetic.
"""

import asyncio
from pathlib import Path
from .ui_transformer import UIProxyBarrier
from .mcp_ui_integration import MCPUIIntegration
from .advanced_theme import (
    AdvancedTheme,
    AdvancedThemeTransformer,
    DitheringEngine,
    ASCIIConverter,
    ShaderEngine,
    AdBlocker
)


def create_grainrad_theme() -> AdvancedTheme:
    """Create a grainrad-inspired theme."""
    return AdvancedTheme(
        name="grainrad-inspired",
        dithering={
            "method": "floyd_steinberg",
            "intensity": 0.7
        },
        ascii_config={
            "width": 80,
            "extended": True,
            "contrast": 1.2
        },
        shader_config={
            "noise": 0.15,
            "grain": 0.08,
            "scanlines": True,
            "crt_effect": True
        },
        ad_blocking={
            "patterns": [
                "advertisement",
                "ad-banner",
                "sponsor",
                "promo",
                "adsbygoogle"
            ],
            "enabled": True
        },
        graphics_mode="hybrid",  # ASCII + Dither + Shader
        metadata={
            "inspiration": "grainrad.com",
            "aesthetic": "retro-terminal"
        }
    )


def demo_ascii_conversion():
    """Demonstrate ASCII art conversion."""
    print("=" * 60)
    print("ASCII ART CONVERSION")
    print("=" * 60)
    
    converter = ASCIIConverter(width=60, use_extended=True)
    
    print("\n1. Text to ASCII Banner:")
    banner = converter.text_to_ascii_banner("GRAINRAD STYLE")
    print(banner)
    
    print("\n2. Placeholder ASCII Art:")
    placeholder = converter._placeholder_ascii()
    print(placeholder)
    
    print("\n3. ASCII Character Set:")
    print(f"   Standard: {converter.ASCII_CHARS}")
    print(f"   Extended: {converter.ASCII_CHARS_EXTENDED[:30]}...")


def demo_dithering():
    """Demonstrate dithering effects."""
    print("\n" + "=" * 60)
    print("DITHERING EFFECTS")
    print("=" * 60)
    
    engine = DitheringEngine(method="floyd_steinberg")
    
    print("\n1. Dithering Text:")
    text = "This is a sample text that will be dithered."
    dithered = engine.dither_text(text, width=60)
    print(f"   Original: {text}")
    print(f"   Dithered:")
    print(f"   {dithered}")
    
    print("\n2. Dithering Pattern Generation:")
    pattern = engine.generate_dither_pattern(10, 5)
    print("   Pattern preview (10x5):")
    for row in pattern[:3]:
        print(f"   {[f'{v:.2f}' for v in row[:5]]}")


def demo_shader_effects():
    """Demonstrate shader effects."""
    print("\n" + "=" * 60)
    print("SHADER EFFECTS")
    print("=" * 60)
    
    theme = create_grainrad_theme()
    shader_engine = ShaderEngine()
    
    print("\n1. Generating Shader CSS:")
    css = shader_engine.generate_shader_css(theme)
    print(f"   ✓ Generated {len(css)} characters of CSS")
    print(f"   Includes:")
    print(f"     - Noise/grain effects")
    print(f"     - Scanline effects")
    print(f"     - CRT-style rendering")
    
    # Show preview
    print("\n2. CSS Preview:")
    preview_lines = css.split('\n')[:15]
    for line in preview_lines:
        if line.strip():
            print(f"   {line}")


def demo_ad_blocking():
    """Demonstrate ad blocking."""
    print("\n" + "=" * 60)
    print("AD BLOCKING")
    print("=" * 60)
    
    patterns = ["advertisement", "ad-banner", "sponsor", "promo"]
    blocker = AdBlocker(patterns)
    
    print(f"\n1. Ad Blocker initialized with {len(patterns)} patterns:")
    for pattern in patterns:
        print(f"   - {pattern}")
    
    print("\n2. Testing ad detection:")
    test_elements = [
        {"attrs": {"class": "advertisement banner"}},
        {"attrs": {"class": "content article"}},
        {"attrs": {"id": "sponsor-box"}},
        {"attrs": {"id": "main-content"}},
    ]
    
    for i, element in enumerate(test_elements):
        is_ad = blocker.is_ad(element)
        status = "🚫 AD" if is_ad else "✓ Content"
        print(f"   Element {i+1}: {status}")
    
    print("\n3. Removing ads from HTML:")
    html_with_ads = """
    <div class="content">Real content here</div>
    <div class="advertisement">Ad content</div>
    <div class="sponsor-banner">Sponsored</div>
    <div class="main-article">Article content</div>
    """
    
    cleaned = blocker.remove_ads_from_html(html_with_ads)
    print(f"   Original length: {len(html_with_ads)} chars")
    print(f"   Cleaned length: {len(cleaned)} chars")
    print(f"   Ads blocked: {blocker.blocked_count}")


def demo_advanced_theme():
    """Demonstrate advanced theme transformation."""
    print("\n" + "=" * 60)
    print("ADVANCED THEME TRANSFORMATION")
    print("=" * 60)
    
    # Create theme
    theme = create_grainrad_theme()
    print(f"\n1. Theme created: {theme.name}")
    print(f"   Graphics mode: {theme.graphics_mode}")
    print(f"   Dithering: {theme.dithering['method']}")
    print(f"   ASCII: {theme.ascii_config['width']} chars wide")
    print(f"   Shaders: Enabled")
    print(f"   Ad blocking: {len(theme.ad_blocking['patterns'])} patterns")
    
    # Create transformer
    transformer = AdvancedThemeTransformer(theme)
    
    # Transform a resource
    print("\n2. Transforming resource:")
    original_resource = {
        "uri": "mcp-ui://main",
        "name": "Main Dashboard",
        "mimeType": "text/markdown",
        "content": """# Main Dashboard

Welcome to the MCP UI.

![Logo](https://example.com/logo.png)

## Sections

- [Kanban Board](kanban/board.md)
- [Workflows](workflows/list.md)

<div class="advertisement">Ad content here</div>

## Content

Real content here.
        """,
        "metadata": {}
    }
    
    transformed = transformer.transform_resource(original_resource)
    
    print(f"   ✓ Resource transformed")
    print(f"     Theme: {transformed['metadata']['theme']}")
    print(f"     Graphics mode: {transformed['metadata']['graphics_mode']}")
    print(f"     Ads blocked: {transformed['metadata'].get('ads_blocked', 0)}")
    print(f"     Transformed: {transformed['metadata']['transformed']}")
    
    # Show content preview
    print("\n3. Transformed content preview:")
    preview = transformed['content'][:300]
    print(f"   {preview}...")


def demo_complete_system():
    """Demonstrate complete system integration."""
    print("\n" + "=" * 60)
    print("COMPLETE SYSTEM INTEGRATION")
    print("=" * 60)
    
    # Create base integration
    base_integration = MCPUIIntegration()
    
    # Create advanced theme
    theme = create_grainrad_theme()
    
    # Create transformer
    transformer = AdvancedThemeTransformer(theme)
    
    # Create barrier with advanced theme
    print("\n1. Setting up system:")
    print(f"   Base integration: {len(base_integration.resources)} resources")
    print(f"   Theme: {theme.name}")
    print(f"   Mode: {theme.graphics_mode}")
    
    # Transform resources
    print("\n2. Transforming resources:")
    transformed_count = 0
    for uri, resource in list(base_integration.resources.items()):
        transformed = transformer.transform_resource(resource)
        base_integration.resources[uri] = transformed
        transformed_count += 1
        print(f"   ✓ {uri}")
    
    print(f"\n   Transformed {transformed_count} resources")
    
    # Show stats
    print("\n3. System Statistics:")
    total_ads_blocked = sum(
        r.get('metadata', {}).get('ads_blocked', 0)
        for r in base_integration.resources.values()
    )
    print(f"   Resources: {len(base_integration.resources)}")
    print(f"   Theme applied: {theme.name}")
    print(f"   Total ads blocked: {total_ads_blocked}")
    
    print("\n" + "=" * 60)
    print("SYSTEM READY")
    print("=" * 60)
    print("\nThe advanced theme system provides:")
    print("  ✅ Dithering effects (Floyd-Steinberg style)")
    print("  ✅ ASCII art conversion for graphics")
    print("  ✅ Shader-based rendering (noise, grain, scanlines)")
    print("  ✅ Selective ad blocking")
    print("  ✅ Grainrad.com-inspired aesthetic")


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("GRAINRAD-INSPIRED ADVANCED THEME DEMONSTRATION")
    print("=" * 60)
    print("\nDemonstrating:")
    print("  1. ASCII art conversion")
    print("  2. Dithering effects")
    print("  3. Shader-based graphics")
    print("  4. Ad blocking")
    print("  5. Complete theme transformation")
    print("  6. System integration\n")
    
    demo_ascii_conversion()
    demo_dithering()
    demo_shader_effects()
    demo_ad_blocking()
    demo_advanced_theme()
    demo_complete_system()


if __name__ == "__main__":
    main()
