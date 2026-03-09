#!/usr/bin/env python3
"""
Complete MCP Integration Demo
Tests MCP UI + Toolbox + Server integration
"""

from .integrated_system import create_integrated_system
from pathlib import Path


def demo_complete_integration():
    """Demonstrate complete MCP integration."""
    
    print("=" * 60)
    print("COMPLETE MCP INTEGRATION DEMO")
    print("=" * 60)
    print("\nTesting:")
    print("  1. MCP UI Integration")
    print("  2. MCP Toolbox Integration")
    print("  3. Server Testing")
    print("  4. Combined Workflow")
    print()
    
    # Create integrated system
    system = create_integrated_system()
    
    # 1. MCP UI
    print("=" * 60)
    print("1. MCP UI INTEGRATION")
    print("=" * 60)
    
    ui_resources = system.list_ui_resources()
    print(f"\n✓ Found {len(ui_resources)} UI resources")
    
    for resource in ui_resources[:3]:
        print(f"  - {resource['name']}: {resource['uri']}")
    
    # Get UI tree
    tree = system.mcp_ui.get_ui_tree_as_resource()
    print(f"\n✓ UI Tree: {tree['metadata']['component_count']} components")
    
    # 2. Toolbox
    print("\n" + "=" * 60)
    print("2. MCP TOOLBOX INTEGRATION")
    print("=" * 60)
    
    toolbox_status = system.toolbox.get_status()
    print(f"\nToolbox Status:")
    print(f"  Connected: {toolbox_status['connected']}")
    print(f"  URL: {toolbox_status['toolbox_url']}")
    print(f"  Toolsets: {toolbox_status['available_toolsets']}")
    
    if toolbox_status['connected']:
        # Try to load toolset
        try:
            tools = system.toolbox.load_toolset("kanban_toolset")
            print(f"\n✓ Loaded kanban_toolset: {len(tools)} tools")
        except Exception as e:
            print(f"\n⚠ Toolset loading: {e}")
    
    # 3. Server Testing
    print("\n" + "=" * 60)
    print("3. SERVER TESTING")
    print("=" * 60)
    
    test_results = system.test_system()
    print(f"\nTest Results:")
    print(f"  Total: {test_results['total_tests']}")
    print(f"  Passed: {test_results['passed']}")
    print(f"  Failed: {test_results['failed']}")
    print(f"  Success Rate: {test_results['success_rate']:.1%}")
    
    # 4. Combined Workflow
    print("\n" + "=" * 60)
    print("4. COMBINED WORKFLOW")
    print("=" * 60)
    
    print("\nWorkflow: UI → Toolbox → Results")
    
    # Step 1: Get UI component
    ui_component = system.get_ui_resource("main")
    if ui_component:
        print(f"✓ Got UI component: {ui_component['name']}")
    
    # Step 2: Query via Toolbox
    if toolbox_status['connected']:
        try:
            result = system.query_database("get_kanban_cards", status="in_progress")
            print(f"✓ Queried database via Toolbox")
            print(f"  Tool: {result.get('tool', 'unknown')}")
        except Exception as e:
            print(f"⚠ Database query: {e}")
    
    # Step 3: Combine
    print("✓ Combined workflow complete")
    
    # Final Status
    print("\n" + "=" * 60)
    print("SYSTEM STATUS")
    print("=" * 60)
    
    status = system.get_status()
    print(f"\nMCP UI:")
    print(f"  Components: {status['mcp_ui']['components']}")
    print(f"  Resources: {status['ui_resources']}")
    
    print(f"\nToolbox:")
    print(f"  Connected: {status['toolbox']['connected']}")
    print(f"  Tools: {status['toolbox_tools']}")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    demo_complete_integration()
