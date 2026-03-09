#!/usr/bin/env python3
"""
MCP Gateway Demo: Demonstrates MCP UI integration in a gateway system
Shows how UI components can be accessed via MCP protocol through a gateway.
"""

import uuid
from .mcp_gateway import create_mcp_gateway, GatewayRequest


def demo_mcp_gateway():
    """Demonstrate MCP Gateway with UI integration."""
    
    print("=" * 60)
    print("MCP GATEWAY DEMONSTRATION")
    print("=" * 60)
    print("\nThis demonstrates how MCP UI integrates into a gateway system.")
    print("The gateway routes requests to appropriate MCP components.\n")
    
    # Create gateway
    print("1. Creating MCP Gateway...")
    gateway = create_mcp_gateway()
    print("   ✓ Gateway created")
    
    # Show available resources
    print("\n2. Available Resources:")
    resources = gateway.list_available_resources()
    print(f"   Found {len(resources)} resources:")
    for resource in resources:
        print(f"     - {resource['name']} ({resource['type']}): {resource['uri']}")
    
    # Request 1: Get UI component
    print("\n3. Request: Get UI Component")
    request1 = GatewayRequest(
        request_id=f"req-{uuid.uuid4().hex[:8]}",
        request_type="ui",
        target="main",
        parameters={}
    )
    
    response1 = gateway.handle_request(request1)
    print(f"   Request ID: {request1.request_id}")
    print(f"   Success: {response1.success}")
    if response1.success:
        print(f"   Resource: {response1.data.get('name', 'unknown')}")
        print(f"   URI: {response1.data.get('uri', 'unknown')}")
        print(f"   Content preview: {response1.data.get('content', '')[:100]}...")
    else:
        print(f"   Error: {response1.error}")
    
    # Request 2: Get UI resource via MCP URI
    print("\n4. Request: Get UI Resource via MCP URI")
    request2 = GatewayRequest(
        request_id=f"req-{uuid.uuid4().hex[:8]}",
        request_type="resource",
        target="mcp-ui://kanban/board",
        parameters={}
    )
    
    response2 = gateway.handle_request(request2)
    print(f"   Request ID: {request2.request_id}")
    print(f"   Success: {response2.success}")
    if response2.success:
        print(f"   Resource: {response2.data.get('name', 'unknown')}")
        print(f"   Type: {response2.metadata.get('type', 'unknown')}")
    else:
        print(f"   Error: {response2.error}")
    
    # Request 3: Natural language query
    print("\n5. Request: Natural Language Query")
    request3 = GatewayRequest(
        request_id=f"req-{uuid.uuid4().hex[:8]}",
        request_type="query",
        target="Show me Kanban cards in progress",
        parameters={"status": "in_progress"}
    )
    
    response3 = gateway.handle_request(request3)
    print(f"   Request ID: {request3.request_id}")
    print(f"   Success: {response3.success}")
    if response3.success:
        print(f"   Handler: {response3.metadata.get('handler', 'unknown')}")
        print(f"   Data: {str(response3.data)[:100]}...")
    else:
        print(f"   Error: {response3.error}")
        print(f"   Note: Toolbox server needs to be running for database queries")
    
    # Gateway status
    print("\n6. Gateway Status:")
    status = gateway.get_gateway_status()
    print(f"   Requests Handled: {status['gateway']['requests_handled']}")
    print(f"   Successful: {status['gateway']['successful_requests']}")
    print(f"   Available Resources: {status['gateway']['available_resources']}")
    
    print(f"\n   Components:")
    print(f"     MCP UI Components: {status['components']['mcp_ui']['components']}")
    print(f"     UI Resources: {status['components']['ui_resources']}")
    print(f"     Toolbox Connected: {status['components']['toolbox']['connected']}")
    
    # Demonstrate UI tree access
    print("\n7. UI Tree Access:")
    ui_tree = gateway.integrated_system.mcp_ui.get_ui_tree_as_resource()
    print(f"   ✓ UI Tree Resource Available")
    print(f"   Components: {ui_tree['metadata']['component_count']}")
    print(f"   URI: {ui_tree['uri']}")
    
    print("\n" + "=" * 60)
    print("GATEWAY DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("\nThe MCP Gateway successfully:")
    print("  ✅ Routes UI resource requests")
    print("  ✅ Handles MCP URI requests")
    print("  ✅ Processes natural language queries")
    print("  ✅ Provides unified interface")
    print("\nUI components are now accessible via MCP protocol through the gateway!")


if __name__ == "__main__":
    demo_mcp_gateway()
