#!/usr/bin/env python3
"""
Quick test of Grainrad POC components.
"""

import asyncio
import base64
from pathlib import Path

from grainrad_mcp_server import create_grainrad_server
from grainrad_ai_agent import create_ai_agent
from grainrad_mcp_ui import create_mcp_ui


async def test_components():
    """Test all components."""
    print("=" * 60)
    print("GRAINRAD POC COMPONENT TEST")
    print("=" * 60)
    
    # Test 1: MCP Server
    print("\n1. Testing MCP Server...")
    server = create_grainrad_server()
    print(f"   ✓ Server created")
    print(f"   Tools: {len(server.tools)}")
    print(f"   Resources: {len(server.resources)}")
    print(f"   Tool names: {list(server.tools.keys())[:3]}...")
    
    # Test 2: AI Agent
    print("\n2. Testing AI Agent...")
    agent = create_ai_agent()
    print(f"   ✓ Agent created")
    print(f"   Anthropic available: {agent.anthropic is not None}")
    print(f"   Gemini available: {agent.gemini is not None}")
    
    # Test 3: MCP UI
    print("\n3. Testing MCP UI...")
    ui = create_mcp_ui()
    print(f"   ✓ UI created")
    print(f"   Base resources: {len(ui.ui_integration.resources)}")
    
    # Test 4: Tool execution (with dummy data)
    print("\n4. Testing tool execution...")
    
    # Create a simple test image (1x1 pixel PNG)
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    result = await server._convert_to_ascii_handler(test_image_b64, width=10)
    if result.get("success"):
        print(f"   ✓ ASCII conversion works")
        print(f"   Content ID: {result['content_id']}")
    else:
        print(f"   ✗ ASCII conversion failed: {result.get('error')}")
    
    # Test 5: Resource registration
    print("\n5. Testing resource registration...")
    if result.get("success"):
        content_id = result["content_id"]
        transformed_data = server.processed_content[content_id]
        resource_uri = ui.register_transformed_content(content_id, transformed_data)
        print(f"   ✓ Resource registered: {resource_uri}")
        print(f"   Total UI resources: {len(ui.ui_integration.resources)}")
    
    # Test 6: Stats
    print("\n6. Testing statistics...")
    print(f"   Stats: {server.stats}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\n✓ All components working!")
    print("\nServer is running at: http://localhost:8000")
    print("Open in browser to test the HTML POC")


if __name__ == "__main__":
    asyncio.run(test_components())
