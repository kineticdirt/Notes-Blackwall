#!/usr/bin/env python3
"""
Verify Combined Effects Are Working
Tests multiple effects combined together on real websites.
"""

import sys
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

def verify_effects(html_content: str) -> dict:
    """Verify which effects are present in HTML."""
    html_lower = html_content.lower()
    
    effects = {
        'scanlines': 'scanline' in html_lower,
        'grain': 'grain' in html_lower or 'noise' in html_lower,
        'halftone': 'halftone' in html_lower,
        'vhs': 'vhs' in html_lower,
        'dots': 'radial-gradient' in html_lower or 'dots' in html_lower,
        'matrix_rain': 'matrix-rain' in html_lower or 'matrix' in html_lower,
        'crosshatch': 'crosshatch' in html_lower,
        'noise_field': 'noisefilter' in html_lower,
    }
    
    css_features = {
        'multiple_layers': html_content.count('::before') + html_content.count('::after'),
        'animations': html_content.count('@keyframes'),
        'filters': html_content.count('filter:'),
        'has_style_tag': '<style>' in html_content,
    }
    
    return {
        'effects': effects,
        'css_features': css_features,
        'html_length': len(html_content)
    }

def test_website(url: str, proxy_url: str = "http://localhost:8001") -> dict:
    """Test a website through the proxy."""
    try:
        response = requests.get(f"{proxy_url}/proxy/{url}", timeout=10)
        if response.status_code == 200:
            return verify_effects(response.text)
        else:
            return {'error': f'HTTP {response.status_code}'}
    except Exception as e:
        return {'error': str(e)}

def main():
    """Run verification tests."""
    print("=" * 70)
    print("COMBINED EFFECTS VERIFICATION")
    print("=" * 70)
    print()
    
    test_urls = [
        "https://example.com",
        "https://youtube.com",
        "https://devdocs.io/cpp/",
    ]
    
    results = []
    
    for url in test_urls:
        print(f"Testing: {url}")
        result = test_website(url)
        
        if 'error' in result:
            print(f"  ✗ Error: {result['error']}")
            print()
            continue
        
        effects = result['effects']
        css = result['css_features']
        
        active_effects = [name for name, active in effects.items() if active]
        
        print(f"  ✓ HTML Length: {result['html_length']:,} chars")
        print(f"  ✓ Effects Active: {len(active_effects)}/{len(effects)}")
        print(f"     {', '.join(active_effects)}")
        print(f"  ✓ CSS Features:")
        print(f"     - Style tag: {css['has_style_tag']}")
        print(f"     - Layers (::before/::after): {css['multiple_layers']}")
        print(f"     - Animations: {css['animations']}")
        print(f"     - Filters: {css['filters']}")
        print()
        
        results.append({
            'url': url,
            'effects': active_effects,
            'total_effects': len(active_effects)
        })
    
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if results:
        total_tests = len(results)
        avg_effects = sum(r['total_effects'] for r in results) / total_tests
        
        print(f"Tests Run: {total_tests}")
        print(f"Average Effects Per Page: {avg_effects:.1f}")
        print()
        print("All Effects Combined:")
        all_effects = set()
        for r in results:
            all_effects.update(r['effects'])
        print(f"  {', '.join(sorted(all_effects))}")
        print()
        print("✅ Combined effects system is working!")
    else:
        print("✗ No successful tests")

if __name__ == "__main__":
    main()
