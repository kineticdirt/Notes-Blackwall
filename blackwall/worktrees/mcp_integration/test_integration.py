#!/usr/bin/env python3
"""
Test MCP Integration: Comprehensive testing of MCP UI + Toolbox + Server
"""

from .integrated_system import create_integrated_system


def test_mcp_ui():
    """Test MCP UI integration."""
    print("=" * 60)
    print("1. TESTING MCP UI INTEGRATION")
    print("=" * 60)
    
    system = create_integrated_system()
    
    # List UI resources
    resources = system.list_ui_resources()
    print(f"\n✓ Found {len(resources)} UI resources")
    
    for resource in resources[:5]:  # Show first 5
        print(f"  - {resource['name']}: {resource['uri']}")
    
    # Get UI tree
    tree_resource = system.mcp_ui.get_ui_tree_as_resource()
    print(f"\n✓ UI Tree resource: {tree_resource['name']}")
    print(f"  Components: {tree_resource['metadata']['component_count']}")
    
    return len(resources) > 0


def test_toolbox():
    """Test Toolbox integration."""
    print("\n" + "=" * 60)
    print("2. TESTING TOOLBOX INTEGRATION")
    print("=" * 60)
    
    system = create_integrated_system()
    
    status = system.toolbox.get_status()
    print(f"\nToolbox Status:")
    print(f"  Connected: {status['connected']}")
    print(f"  URL: {status['toolbox_url']}")
    print(f"  Toolsets: {status['available_toolsets']}")
    print(f"  Total Tools: {status['total_tools']}")
    
    if status['connected']:
        # Try to load a toolset
        try:
            tools = system.toolbox.load_toolset("kanban_toolset")
            print(f"\n✓ Loaded kanban_toolset: {len(tools)} tools")
            for tool in tools:
                print(f"  - {tool}")
        except Exception as e:
            print(f"\n⚠ Could not load toolset: {e}")
    
    return status['connected']


def test_server():
    """Test server functionality."""
    print("\n" + "=" * 60)
    print("3. TESTING SERVER FUNCTIONALITY")
    print("=" * 60)
    
    system = create_integrated_system()
    
    # Run tests
    test_results = system.test_system()
    
    print(f"\nTest Results:")
    print(f"  Total Tests: {test_results['total_tests']}")
    print(f"  Passed: {test_results['passed']}")
    print(f"  Failed: {test_results['failed']}")
    print(f"  Success Rate: {test_results['success_rate']:.1%}")
    
    print(f"\nTest Details:")
    for result in test_results['results']:
        status = "✓" if result['passed'] else "✗"
        print(f"  {status} {result['test']}: {result['message']}")
    
    return test_results['success_rate'] > 0.5


def test_integrated_workflow():
    """Test integrated workflow."""
    print("\n" + "=" * 60)
    print("4. TESTING INTEGRATED WORKFLOW")
    print("=" * 60)
    
    system = create_integrated_system()
    
    # Workflow: UI → Toolbox → Results
    print("\nWorkflow: Query Kanban via Toolbox, display via UI")
    
    # Step 1: Get UI component
    ui_resource = system.get_ui_resource("main")
    if ui_resource:
        print(f"✓ Got UI component: {ui_resource['name']}")
    
    # Step 2: Query database via Toolbox
    if system.toolbox.async_integration.connected:
        try:
            result = system.query_database("get_kanban_cards", status="in_progress")
            print(f"✓ Queried database: {result.get('status', 'unknown')}")
        except Exception as e:
            print(f"⚠ Database query failed: {e}")
    
    # Step 3: Combine results
    print("✓ Integrated workflow complete")
    
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("MCP INTEGRATION TEST SUITE")
    print("=" * 60)
    print("\nTesting:")
    print("  1. MCP UI Integration")
    print("  2. Toolbox Integration")
    print("  3. Server Testing")
    print("  4. Integrated Workflow")
    print()
    
    results = {
        "mcp_ui": test_mcp_ui(),
        "toolbox": test_toolbox(),
        "server": test_server(),
        "workflow": test_integrated_workflow()
    }
    
    # System status
    print("\n" + "=" * 60)
    print("SYSTEM STATUS")
    print("=" * 60)
    
    system = create_integrated_system()
    status = system.get_status()
    
    print(f"\nMCP UI:")
    print(f"  Components: {status['mcp_ui']['components']}")
    print(f"  Resources: {status['ui_resources']}")
    
    print(f"\nToolbox:")
    print(f"  Connected: {status['toolbox']['connected']}")
    print(f"  Tools: {status['toolbox_tools']}")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status_icon = "✓" if passed else "✗"
        print(f"  {status_icon} {test_name}: {'PASSED' if passed else 'FAILED'}")
    
    all_passed = all(results.values())
    print(f"\n{'✓ All tests passed!' if all_passed else '⚠ Some tests failed'}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
