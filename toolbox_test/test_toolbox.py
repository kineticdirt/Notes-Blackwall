#!/usr/bin/env python3
"""
Test MCP Toolbox Integration
Tests how MCP Toolbox can integrate with our worktree system.
"""

import asyncio
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from toolbox_core import ToolboxClient
    TOOLBOX_AVAILABLE = True
except ImportError:
    TOOLBOX_AVAILABLE = False
    print("⚠ toolbox-core not installed. Install with: pip install toolbox-core")


async def test_toolbox_integration():
    """Test MCP Toolbox integration with our system."""
    
    if not TOOLBOX_AVAILABLE:
        print("Skipping toolbox tests - toolbox-core not installed")
        return
    
    print("=" * 60)
    print("MCP TOOLBOX INTEGRATION TEST")
    print("=" * 60)
    
    # Connect to toolbox server (assuming it's running)
    url = "http://127.0.0.1:5000"
    
    try:
        async with ToolboxClient(url) as client:
            print(f"\n✓ Connected to Toolbox server at {url}")
            
            # Load worktree toolset
            print("\n1. Loading worktree toolset...")
            try:
                tools = await client.load_toolset("worktree_toolset")
                print(f"   ✓ Loaded {len(tools)} tools")
                for tool in tools:
                    print(f"     - {tool.name()}: {tool.description()}")
            except Exception as e:
                print(f"   ✗ Failed to load toolset: {e}")
                print("   (Make sure toolbox server is running with tools.yaml)")
            
            # Test individual tool
            print("\n2. Testing individual tool...")
            try:
                tool = await client.load_tool("get_kanban_cards")
                print(f"   ✓ Loaded tool: {tool.name()}")
                print(f"   Description: {tool.description()}")
                
                # Get input schema
                schema = tool.input_schema()
                print(f"   Input schema: {schema}")
            except Exception as e:
                print(f"   ✗ Failed to load tool: {e}")
            
    except Exception as e:
        print(f"\n✗ Failed to connect to Toolbox server: {e}")
        print("\nTo start the server:")
        print("  npx @toolbox-sdk/server --tools-file toolbox_test/tools.yaml")


def identify_use_cases():
    """Identify use cases for MCP Toolbox integration."""
    
    print("\n" + "=" * 60)
    print("USE CASES FOR MCP TOOLBOX INTEGRATION")
    print("=" * 60)
    
    use_cases = [
        {
            "title": "AI-Powered Kanban Board Queries",
            "description": "AI agents can query Kanban boards using natural language",
            "example": "Show me all high-priority cards assigned to agent-1",
            "benefit": "Natural language interaction with Kanban boards"
        },
        {
            "title": "Cross-Chat Discovery",
            "description": "AI can discover findings from other sessions via SQL queries",
            "example": "What bugs have other sessions found related to authentication?",
            "benefit": "AI can leverage collective knowledge"
        },
        {
            "title": "Workflow Status Monitoring",
            "description": "AI can check workflow execution status",
            "example": "What workflows are currently running?",
            "benefit": "Real-time workflow monitoring"
        },
        {
            "title": "Task Analysis",
            "description": "AI can analyze task patterns and suggest improvements",
            "example": "Which agents complete tasks fastest?",
            "benefit": "Data-driven agent optimization"
        },
        {
            "title": "Resource Discovery",
            "description": "AI can find related markdown files and resources",
            "example": "What resources are linked to card-123?",
            "benefit": "Context-aware resource access"
        },
        {
            "title": "Database-Backed AI Tools",
            "description": "Our SQLite databases become queryable by AI agents",
            "example": "All our worktree, kanban, and workflow data is accessible",
            "benefit": "Unified data access layer"
        }
    ]
    
    for i, use_case in enumerate(use_cases, 1):
        print(f"\n{i}. {use_case['title']}")
        print(f"   Description: {use_case['description']}")
        print(f"   Example: \"{use_case['example']}\"")
        print(f"   Benefit: {use_case['benefit']}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("MCP TOOLBOX FOR DATABASES - TEST & USE CASES")
    print("=" * 60)
    
    # Identify use cases
    identify_use_cases()
    
    # Test integration
    if TOOLBOX_AVAILABLE:
        asyncio.run(test_toolbox_integration())
    else:
        print("\n" + "=" * 60)
        print("INSTALLATION INSTRUCTIONS")
        print("=" * 60)
        print("\n1. Install toolbox-core:")
        print("   pip install toolbox-core")
        print("\n2. Start toolbox server:")
        print("   npx @toolbox-sdk/server --tools-file toolbox_test/tools.yaml")
        print("\n3. Run this test:")
        print("   python toolbox_test/test_toolbox.py")
