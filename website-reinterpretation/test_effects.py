#!/usr/bin/env python3
"""
Test grainrad-style effects integration.
Ensures everything works and produces visual effects.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from blackwall.worktrees.mcp_integration.advanced_theme import (
    AdvancedTheme,
    AdvancedThemeTransformer,
    DitheringEngine,
    ASCIIConverter,
    ShaderEngine
)


def test_dithering():
    """Test dithering engine."""
    print("=" * 70)
    print("TESTING DITHERING ENGINE")
    print("=" * 70)
    
    engine = DitheringEngine(method="floyd_steinberg")
    
    # Test text dithering
    text = "Hello, World! This is a test of dithering effects."
    dithered = engine.dither_text(text, width=60)
    
    print("\nOriginal text:")
    print(text)
    print("\nDithered text:")
    print(dithered)
    
    # Test pattern generation
    pattern = engine.generate_dither_pattern(10, 5)
    print("\nDither pattern (10x5):")
    for row in pattern[:3]:
        print(f"  {[f'{v:.2f}' for v in row[:5]]}")
    
    print("\n✅ Dithering engine working")


def test_ascii():
    """Test ASCII converter."""
    print("\n" + "=" * 70)
    print("TESTING ASCII CONVERTER")
    print("=" * 70)
    
    converter = ASCIIConverter(width=40, use_extended=True)
    
    # Test placeholder
    placeholder = converter._placeholder_ascii()
    print("\nPlaceholder ASCII:")
    print(placeholder)
    
    # Test banner
    banner = converter.text_to_ascii_banner("TEST")
    print("\nASCII Banner:")
    print(banner)
    
    print("\n✅ ASCII converter working")


def test_shader():
    """Test shader engine."""
    print("\n" + "=" * 70)
    print("TESTING SHADER ENGINE")
    print("=" * 70)
    
    theme = AdvancedTheme(
        name="test",
        dithering={"method": "floyd_steinberg"},
        ascii_config={"width": 80},
        shader_config={
            "noise": 0.15,
            "grain": 0.08,
            "scanlines": True
        },
        ad_blocking={"patterns": [], "enabled": False},
        graphics_mode="hybrid"
    )
    
    engine = ShaderEngine()
    css = engine.generate_shader_css(theme)
    
    print("\nGenerated CSS (first 500 chars):")
    print(css[:500])
    print("...")
    
    # Check for key effects
    assert "scanline" in css.lower() or "scan" in css.lower(), "Scanlines missing"
    assert "noise" in css.lower() or "grain" in css.lower(), "Noise/grain missing"
    assert "shader" in css.lower(), "Shader CSS missing"
    
    print("\n✅ Shader engine working")


def test_theme_transformer():
    """Test complete theme transformer."""
    print("\n" + "=" * 70)
    print("TESTING THEME TRANSFORMER")
    print("=" * 70)
    
    theme = AdvancedTheme(
        name="grainrad-test",
        dithering={"method": "floyd_steinberg", "intensity": 0.7},
        ascii_config={"width": 80, "extended": True},
        shader_config={
            "noise": 0.15,
            "grain": 0.08,
            "scanlines": True,
            "crt_effect": True
        },
        ad_blocking={
            "patterns": ["advertisement", "sponsor"],
            "enabled": True
        },
        graphics_mode="hybrid"
    )
    
    transformer = AdvancedThemeTransformer(theme)
    
    # Test markdown transformation
    test_markdown = """
# Test Document

This is a test document with some content.

![Test Image](https://example.com/image.png)

Some text with **bold** and *italic*.

<div class="advertisement">This is an ad</div>
"""
    
    resource = {
        'content': test_markdown,
        'mimeType': 'text/markdown',
        'metadata': {}
    }
    
    transformed = transformer.transform_resource(resource)
    
    print("\nOriginal markdown length:", len(test_markdown))
    print("Transformed length:", len(transformed['content']))
    print("\nTransformed content preview:")
    print(transformed['content'][:300])
    print("...")
    
    # Check transformations
    assert '<style>' in transformed['content'], "Shader CSS missing"
    assert transformed['metadata'].get('transformed'), "Not marked as transformed"
    
    print("\n✅ Theme transformer working")


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("GRAINRAD EFFECTS INTEGRATION TEST")
    print("=" * 70)
    print("\nTesting existing advanced_theme.py components...")
    
    try:
        test_dithering()
        test_ascii()
        test_shader()
        test_theme_transformer()
        
        print("\n" + "=" * 70)
        print("ALL TESTS PASSED ✅")
        print("=" * 70)
        print("\nEffects are ready to use!")
        print("\nTo enable effects in proxy:")
        print("  ENABLE_EFFECTS=true python3 run_proxy.py")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
