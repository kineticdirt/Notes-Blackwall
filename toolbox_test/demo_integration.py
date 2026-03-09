#!/usr/bin/env python3
"""
Demo: MCP Toolbox Integration with Our System
Shows how AI agents can query our databases using natural language.
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from blackwall.worktrees.unified_system import create_unified_system
from blackwall.worktrees.kanban import KanbanCard


def setup_test_data():
    """Set up test data in our databases."""
    print("Setting up test data...")
    
    system = create_unified_system()
    
    # Create Kanban board with cards
    board = system.create_kanban_board("demo-board", "Demo Board")
    
    card1 = KanbanCard(
        card_id="card-1",
        title="Fix authentication bug",
        description="JWT token validation issue",
        status="in_progress",
        assignee="agent-1",
        priority=9,
        tags=["bug", "security"]
    )
    board.add_card(card1)
    
    card2 = KanbanCard(
        card_id="card-2",
        title="Add unit tests",
        description="Write tests for auth module",
        status="todo",
        assignee="agent-2",
        priority=7,
        tags=["testing"]
    )
    board.add_card(card2)
    
    # Save to database
    system.kanban_db.save_card(card1, "demo-board")
    system.kanban_db.save_card(card2, "demo-board")
    
    # Publish cross-chat findings
    finding_id = system.cross_chat.publish(
        title="Authentication vulnerability found",
        content="JWT tokens not properly validated",
        category="bug",
        tags=["authentication", "security"]
    )
    
    print(f"✓ Created Kanban board with 2 cards")
    print(f"✓ Published cross-chat finding: {finding_id}")
    
    return system


def demonstrate_use_cases():
    """Demonstrate use cases for MCP Toolbox."""
    
    print("\n" + "=" * 60)
    print("MCP TOOLBOX USE CASES DEMONSTRATION")
    print("=" * 60)
    
    use_cases = [
        {
            "scenario": "AI Agent needs to find high-priority bugs",
            "toolbox_query": "SELECT * FROM cards WHERE status = 'in_progress' AND priority >= 8",
            "natural_language": "Show me all high-priority cards in progress",
            "benefit": "AI can query Kanban board without knowing SQL"
        },
        {
            "scenario": "AI Agent wants to discover what other sessions found",
            "toolbox_query": "SELECT * FROM findings WHERE category = 'bug' ORDER BY created_at DESC",
            "natural_language": "What bugs have other sessions discovered?",
            "benefit": "Cross-chat discovery through natural language"
        },
        {
            "scenario": "AI Agent needs to check workflow status",
            "toolbox_query": "SELECT * FROM workflow_executions WHERE status = 'running'",
            "natural_language": "What workflows are currently running?",
            "benefit": "Real-time workflow monitoring"
        },
        {
            "scenario": "AI Agent wants to analyze task performance",
            "toolbox_query": """
                SELECT agent_id, 
                       AVG(duration_seconds) as avg_time,
                       COUNT(*) as task_count
                FROM task_completions
                GROUP BY agent_id
                ORDER BY avg_time
            """,
            "natural_language": "Which agents complete tasks fastest?",
            "benefit": "Data-driven optimization"
        },
        {
            "scenario": "AI Agent needs to find related resources",
            "toolbox_query": "SELECT * FROM resources WHERE card_id = 'card-1'",
            "natural_language": "What markdown files are linked to this card?",
            "benefit": "Context-aware resource discovery"
        }
    ]
    
    for i, use_case in enumerate(use_cases, 1):
        print(f"\n{i}. {use_case['scenario']}")
        print(f"   Natural Language: \"{use_case['natural_language']}\"")
        print(f"   Toolbox Query: {use_case['toolbox_query'][:80]}...")
        print(f"   Benefit: {use_case['benefit']}")


def show_integration_benefits():
    """Show benefits of integrating MCP Toolbox."""
    
    print("\n" + "=" * 60)
    print("INTEGRATION BENEFITS")
    print("=" * 60)
    
    benefits = [
        "✅ Natural Language Queries: AI can query databases using plain English",
        "✅ Unified Access: All our SQLite databases accessible through one interface",
        "✅ Framework Agnostic: Works with LangChain, LlamaIndex, Genkit, etc.",
        "✅ Type Safety: SQL tools have defined schemas and parameters",
        "✅ Security: Centralized database access control",
        "✅ Real-time: Direct database access for up-to-date information",
        "✅ Extensible: Easy to add new SQL tools as needed",
        "✅ Standard Protocol: Uses MCP (Model Context Protocol) standard"
    ]
    
    for benefit in benefits:
        print(f"  {benefit}")


def main():
    """Main demo function."""
    print("\n" + "=" * 60)
    print("MCP TOOLBOX INTEGRATION DEMO")
    print("=" * 60)
    
    # Set up test data
    system = setup_test_data()
    
    # Show use cases
    demonstrate_use_cases()
    
    # Show benefits
    show_integration_benefits()
    
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("\n1. Install toolbox-core:")
    print("   pip install toolbox-core")
    print("\n2. Start toolbox server:")
    print("   npx @toolbox-sdk/server --tools-file toolbox_test/tools.yaml")
    print("\n3. Use in your AI agents:")
    print("   from toolbox_core import ToolboxClient")
    print("   async with ToolboxClient('http://127.0.0.1:5000') as client:")
    print("       tools = await client.load_toolset('worktree_toolset')")
    print("\n4. AI can now query your databases using natural language!")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
