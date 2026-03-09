#!/usr/bin/env python3
"""
AI Suit Demo: Plug-and-Play AI Capability Extension
Demonstrates the "super robotic suit" that extends user abilities.
"""

from .ai_suit_unified import create_ai_suit


def demo_ai_suit():
    """Demonstrate AI Suit capabilities."""
    
    print("=" * 60)
    print("AI SUIT: PLUG-AND-PLAY CAPABILITY EXTENSION")
    print("=" * 60)
    print("\nThink of this as a 'super robotic suit' that extends your abilities!")
    print("You ask for something → AI Suit routes to capability → You get result\n")
    
    # Create AI Suit
    print("1. Creating AI Suit...")
    suit = create_ai_suit("demo-suit")
    print(f"   ✓ Suit ID: {suit.suit_id}")
    
    # Show status
    print("\n2. AI Suit Status:")
    status = suit.get_full_status()
    print(f"   Total Capabilities: {status['total_extended_abilities']}")
    print(f"   Enabled: {status['enabled_capabilities']}")
    print(f"   MCP Servers: {status['mcp_jam']['connected_servers']}")
    print(f"   Toolbox Connected: {status['toolbox']['connected']}")
    
    # List capabilities
    print("\n3. Available Capabilities:")
    capabilities = suit.discover_capabilities()
    for cap in capabilities[:10]:  # Show first 10
        print(f"   - {cap.name}: {cap.description}")
    
    # Demonstrate natural language queries
    print("\n4. Natural Language Queries:")
    
    queries = [
        "Show me Kanban cards in progress",
        "What bugs have been found?",
        "Create a new worktree",
        "Read a file"
    ]
    
    for query in queries:
        print(f"\n   Query: \"{query}\"")
        try:
            result = suit.query(query)
            print(f"   Result: {str(result)[:100]}...")
        except Exception as e:
            print(f"   Error: {e}")
    
    # Demonstrate capability usage
    print("\n5. Direct Capability Usage:")
    try:
        # Query Kanban
        result = suit.use("query_kanban", status="in_progress")
        print(f"   ✓ Queried Kanban board")
        
        # Discover findings
        result = suit.use("discover_findings", category="bug")
        print(f"   ✓ Discovered findings")
        
    except Exception as e:
        print(f"   Note: {e} (some capabilities require running services)")
    
    # Add custom capability
    print("\n6. Extending Abilities (Plug-in):")
    
    def custom_capability(text: str):
        return f"Processed: {text.upper()}"
    
    cap_id = suit.extend_ability(
        "process_text",
        custom_capability,
        "Process text to uppercase",
        suit.registry.capabilities[list(suit.registry.capabilities.keys())[0]].capability_type
    )
    print(f"   ✓ Added custom capability: process_text")
    
    # Use custom capability
    result = suit.use("process_text", text="hello world")
    print(f"   Result: {result}")
    
    print("\n" + "=" * 60)
    print("AI SUIT DEMO COMPLETE")
    print("=" * 60)
    print("\nThe AI Suit extends your abilities by:")
    print("  ✅ Connecting to MCP servers (tools)")
    print("  ✅ Querying databases (Toolbox)")
    print("  ✅ Managing worktrees and agents")
    print("  ✅ Cross-chat communication")
    print("  ✅ Custom capabilities (plug-and-play)")
    print("\nYou can now:")
    print("  - Query databases naturally")
    print("  - Use MCP tools seamlessly")
    print("  - Coordinate agents")
    print("  - Extend abilities on the fly")


if __name__ == "__main__":
    demo_ai_suit()
