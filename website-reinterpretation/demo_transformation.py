#!/usr/bin/env python3
"""
Demo: Transform a website using the complete system
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from website_proxy import create_website_proxy


async def demo_transformation():
    """Demonstrate website transformation."""
    print("=" * 70)
    print("WEBSITE REINTERPRETATION DEMO")
    print("=" * 70)
    
    # Create proxy
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    proxy = create_website_proxy(anthropic_key=anthropic_key)
    
    # Test URL
    test_url = "https://example.com"
    
    print(f"\nTransforming: {test_url}")
    print("This will:")
    print("  1. Fetch website HTML/CSS/JS")
    print("  2. Extract components")
    print("  3. Use AI with MCP prompts to analyze")
    print("  4. Transform components to ASCII/dithered/shaded panes")
    print("  5. Render final website\n")
    
    try:
        result = await proxy.intercept_and_transform(test_url, use_cache=False)
        
        print("✓ Transformation complete!")
        print(f"\nResults:")
        print(f"  Panes created: {result['panes_count']}")
        print(f"  HTML length: {len(result['html'])} chars")
        print(f"  CSS length: {len(result['css'])} chars")
        
        if result.get('verification'):
            ver = result['verification']
            print(f"\nAI Verification:")
            print(f"  Status: {'PASS' if ver.get('verified') else 'FAIL'}")
            print(f"  Provider: {ver.get('provider', 'none')}")
        
        # Save to file
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        (output_dir / "transformed.html").write_text(result['html'])
        (output_dir / "transformed.css").write_text(result['css'])
        
        print(f"\n✓ Saved to: {output_dir}/")
        print(f"  - transformed.html")
        print(f"  - transformed.css")
        
        print("\n" + "=" * 70)
        print("DEMO COMPLETE")
        print("=" * 70)
        print("\nOpen transformed.html in browser to see the result!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(demo_transformation())
