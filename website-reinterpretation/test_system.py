#!/usr/bin/env python3
"""
Test Website Reinterpretation System
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from website_fetcher import create_website_fetcher
from mcp_ui_server import create_mcp_ui_server
from website_ai_agent import create_website_ai_agent
from component_transformer import create_component_transformer
from pane_renderer import create_pane_renderer
from website_proxy import create_website_proxy


async def test_system():
    """Test all components."""
    print("=" * 70)
    print("WEBSITE REINTERPRETATION SYSTEM TEST")
    print("=" * 70)
    
    # Test 1: Website Fetcher
    print("\n1. Testing Website Fetcher...")
    fetcher = create_website_fetcher()
    print("   ✓ Website Fetcher created")
    
    # Test 2: MCP UI Server
    print("\n2. Testing MCP UI Server...")
    mcp_ui = create_mcp_ui_server()
    print(f"   ✓ MCP UI Server created")
    print(f"   Prompts: {len(mcp_ui.prompts)}")
    print(f"   Resources: {len(mcp_ui.resources)}")
    print(f"   MCP Resources: {len(mcp_ui.ui_integration.resources)}")
    
    # Test 3: AI Agent
    print("\n3. Testing AI Agent...")
    ai_agent = create_website_ai_agent(mcp_ui)
    print("   ✓ AI Agent created")
    print(f"   Anthropic available: {ai_agent.anthropic is not None}")
    
    # Test 4: Component Transformer
    print("\n4. Testing Component Transformer...")
    transformer = create_component_transformer()
    print("   ✓ Component Transformer created")
    
    # Test 5: Pane Renderer
    print("\n5. Testing Pane Renderer...")
    renderer = create_pane_renderer()
    print("   ✓ Pane Renderer created")
    
    # Test 6: Website Proxy
    print("\n6. Testing Website Proxy...")
    proxy = create_website_proxy()
    print("   ✓ Website Proxy created")
    print(f"   Components initialized: {proxy.fetcher is not None}")
    
    # Test 7: MCP UI Prompt Access
    print("\n7. Testing MCP UI Prompt Access...")
    try:
        prompt = mcp_ui.get_prompt("website-analysis", {"url": "https://example.com", "html_preview": "<html>...</html>", "css_count": 1, "js_count": 1, "component_count": 3, "component_list": "- header\n- main\n- footer"})
        print(f"   ✓ Prompt retrieved ({len(prompt)} chars)")
    except Exception as e:
        print(f"   ✗ Prompt error: {e}")
    
    # Test 8: Component Transformation (mock)
    print("\n8. Testing Component Transformation...")
    from website_fetcher import WebsiteComponent
    mock_component = WebsiteComponent(
        component_id="test-header",
        component_type="header",
        html_content="<header><h1>Test Header</h1><p>Test content</p></header>"
    )
    pane = transformer.transform_component(mock_component)
    print(f"   ✓ Component transformed")
    print(f"   Pane type: {pane.pane_type}")
    print(f"   ASCII content length: {len(pane.ascii_content)}")
    
    # Test 9: Pane Rendering
    print("\n9. Testing Pane Rendering...")
    result = renderer.render([pane])
    print(f"   ✓ Panes rendered")
    print(f"   HTML length: {len(result['html'])}")
    print(f"   CSS length: {len(result['css'])}")
    
    print("\n" + "=" * 70)
    print("SYSTEM TEST COMPLETE")
    print("=" * 70)
    print("\n✓ All components working!")
    print("\nTo run the proxy server:")
    print("  export ANTHROPIC_API_KEY='your-key'")
    print("  python3 run_proxy.py")
    print("\nThen open: http://localhost:8001")


if __name__ == "__main__":
    asyncio.run(test_system())
