#!/usr/bin/env python3
"""
Test Combined Effects System
Actually tests multiple effects working together.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from combined_effects import CombinedEffectsProcessor, EffectConfig


def test_combined_effects():
    """Test combining multiple effects."""
    print("=" * 70)
    print("TESTING COMBINED EFFECTS")
    print("=" * 70)
    
    # Test 1: ASCII + Dithering + Scanlines + Grain
    print("\n1. Testing: ASCII + Dithering + Scanlines + Grain")
    processor1 = CombinedEffectsProcessor(
        effects=["ascii", "dithering", "scanlines", "grain"]
    )
    css1 = processor1.generate_combined_css()
    print(f"   ✓ CSS generated: {len(css1)} chars")
    print(f"   ✓ Effects enabled: {[e for e, c in processor1.effect_configs.items() if c.enabled]}")
    
    # Test 2: Multiple effects combination
    print("\n2. Testing: Halftone + VHS + Matrix Rain + Dots")
    processor2 = CombinedEffectsProcessor(
        effects=["halftone", "vhs", "matrix_rain", "dots", "scanlines"]
    )
    css2 = processor2.generate_combined_css()
    print(f"   ✓ CSS generated: {len(css2)} chars")
    print(f"   ✓ Effects enabled: {[e for e, c in processor2.effect_configs.items() if c.enabled]}")
    
    # Test 3: All effects
    print("\n3. Testing: All Effects Combined")
    all_effects = [
        "ascii", "dithering", "halftone", "matrix_rain", "dots",
        "contour", "pixel_sort", "blockify", "threshold", "edge_detection",
        "crosshatch", "wave_lines", "noise_field", "voronoi", "vhs",
        "scanlines", "grain"
    ]
    processor3 = CombinedEffectsProcessor(effects=all_effects)
    css3 = processor3.generate_combined_css()
    print(f"   ✓ CSS generated: {len(css3)} chars")
    print(f"   ✓ All {len(all_effects)} effects enabled")
    
    # Test 4: HTML processing
    print("\n4. Testing HTML Processing")
    sample_html = """<!DOCTYPE html>
<html>
<head>
    <title>Test</title>
</head>
<body>
    <h1>Hello World</h1>
    <p>This is a test page.</p>
    <img src="test.jpg" alt="Test image">
</body>
</html>"""
    
    processor4 = CombinedEffectsProcessor(
        effects=["dithering", "scanlines", "grain", "halftone", "vhs"]
    )
    processed = processor4.process_html(sample_html)
    
    print(f"   ✓ Original HTML length: {len(sample_html)}")
    print(f"   ✓ Processed HTML length: {len(processed)}")
    print(f"   ✓ CSS injected: {'<style>' in processed}")
    print(f"   ✓ Matrix rain overlay: {'matrix-rain' in processed}")
    
    # Show CSS preview
    if '<style>' in processed:
        style_start = processed.find('<style>')
        style_end = processed.find('</style>')
        css_preview = processed[style_start:style_end+8][:500]
        print(f"\n   CSS Preview (first 500 chars):")
        print(f"   {css_preview}...")
    
    print("\n✅ Combined effects working!")
    
    return processor4


def test_with_real_website():
    """Test with actual website content."""
    print("\n" + "=" * 70)
    print("TESTING WITH REAL WEBSITE")
    print("=" * 70)
    
    import aiohttp
    import asyncio
    
    async def fetch_and_process():
        processor = CombinedEffectsProcessor(
            effects=["dithering", "scanlines", "grain", "halftone", "vhs", "matrix_rain"]
        )
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get('https://example.com', timeout=aiohttp.ClientTimeout(total=10)) as response:
                    html = await response.text()
                    
                    print(f"\n✓ Fetched example.com: {len(html)} chars")
                    
                    # Process with combined effects
                    processed = processor.process_html(html)
                    
                    print(f"✓ Processed: {len(processed)} chars")
                    print(f"✓ CSS injected: {'<style>' in processed}")
                    print(f"✓ Effects present:")
                    print(f"  - Scanlines: {'scanline' in processed.lower()}")
                    print(f"  - Grain: {'grain' in processed.lower()}")
                    print(f"  - Halftone: {'halftone' in processed.lower()}")
                    print(f"  - VHS: {'vhs' in processed.lower()}")
                    print(f"  - Matrix Rain: {'matrix-rain' in processed.lower()}")
                    
                    return processed
            except Exception as e:
                print(f"✗ Error: {e}")
                return None
    
    result = asyncio.run(fetch_and_process())
    
    if result:
        print("\n✅ Real website test successful!")
    else:
        print("\n✗ Real website test failed")
    
    return result


if __name__ == "__main__":
    processor = test_combined_effects()
    test_with_real_website()
    
    print("\n" + "=" * 70)
    print("COMBINED EFFECTS TEST COMPLETE")
    print("=" * 70)
    print("\nTo use combined effects:")
    print("  ENABLE_EFFECTS=true python3 run_proxy.py")
    print("  curl http://localhost:8001/proxy/https://example.com")
