#!/usr/bin/env python3
"""
Proof of Concept: Complete Whiteboard Implementation
Demonstrates all components working together:
1. Kanban Board in AI native language
2. MCP UI with nested markdown files
3. Resources (markdown + DB)
4. Airflow-style workflows
5. Worktrees for organizing agents
"""

from .unified_system import UnifiedMCPSystem, create_unified_system
from .kanban import KanbanBoard, KanbanCard
from .workflows import WorkflowDAG, WorkflowTask
from pathlib import Path


def demo_kanban_board():
    """Demo: Kanban Board in AI native language."""
    print("=" * 60)
    print("1. KANBAN BOARD (AI Native Language)")
    print("=" * 60)
    
    system = create_unified_system()
    
    # Create Kanban board
    board = system.create_kanban_board("dev-board", "Development Board")
    print(f"\n✓ Created board: {board.name}")
    
    # Add cards
    card1 = KanbanCard(
        card_id="card-1",
        title="Implement authentication",
        description="Add JWT token validation",
        status="todo",
        assignee="agent-1",
        tags=["backend", "security"],
        priority=8
    )
    board.add_card(card1)
    
    card2 = KanbanCard(
        card_id="card-2",
        title="Write tests",
        description="Add unit tests for auth",
        status="in_progress",
        assignee="agent-2",
        tags=["testing"],
        priority=7
    )
    board.add_card(card2)
    
    print(f"✓ Added {len(board.cards)} cards")
    
    # Save to markdown (AI-readable)
    board._save_to_markdown()
    print(f"✓ Saved to: {board.base_path / 'board.md'}")
    
    # Show markdown preview
    markdown = board.to_markdown()
    print(f"\nMarkdown preview (first 500 chars):")
    print("-" * 60)
    print(markdown[:500])
    print("...")
    
    return board


def demo_mcp_ui():
    """Demo: MCP UI with nested markdown files."""
    print("\n" + "=" * 60)
    print("2. MCP UI (Nested Markdown Files)")
    print("=" * 60)
    
    ui_path = Path(".mcp-ui")
    ui_path.mkdir(exist_ok=True)
    
    # Create nested markdown structure
    main_page = ui_path / "main.md"
    main_page.write_text("""---
type: page
title: Main Dashboard
---

# Main Dashboard

Welcome to the MCP UI.

## Sections

- [Kanban Board](kanban/board.md)
- [Workflows](workflows/list.md)
- [Agents](agents/list.md)
""")
    
    kanban_dir = ui_path / "kanban"
    kanban_dir.mkdir(exist_ok=True)
    
    kanban_page = kanban_dir / "board.md"
    kanban_page.write_text("""---
type: panel
title: Kanban Board
---

# Kanban Board

View and manage tasks.

## Columns

- To Do
- In Progress
- Review
- Done
""")
    
    print(f"✓ Created nested markdown UI structure")
    print(f"  - Main page: {main_page}")
    print(f"  - Kanban panel: {kanban_page}")
    
    # Load UI
    system = create_unified_system()
    ui_tree = system.get_ui_tree()
    print(f"\n✓ UI Tree loaded: {len(system.mcp_ui_loader.components)} components")
    
    return ui_tree


def demo_resources():
    """Demo: Resources pointing to nested markdown + DB."""
    print("\n" + "=" * 60)
    print("3. RESOURCES (Markdown + DB)")
    print("=" * 60)
    
    system = create_unified_system()
    
    # Register resources (markdown files)
    system.kanban_db.register_resource(
        resource_id="res-1",
        resource_path=".kanban/dev-board/cards/card-1.md",
        board_id="dev-board",
        card_id="card-1",
        resource_type="card_detail"
    )
    
    system.kanban_db.register_resource(
        resource_id="res-2",
        resource_path=".mcp-ui/kanban/board.md",
        board_id="dev-board",
        resource_type="ui_component"
    )
    
    print("✓ Registered resources:")
    resources = system.kanban_db.get_resources(board_id="dev-board")
    for res in resources:
        print(f"  - {res['resource_id']}: {res['resource_path']}")
    
    return resources


def demo_workflows():
    """Demo: Airflow-style workflows."""
    print("\n" + "=" * 60)
    print("4. WORKFLOWS (Airflow-style)")
    print("=" * 60)
    
    system = create_unified_system()
    
    # Create workflow DAG
    dag = WorkflowDAG(
        dag_id="code-review-workflow",
        description="Code review and testing workflow"
    )
    
    # Add tasks
    task1 = WorkflowTask(
        task_id="task-1",
        task_name="Run tests",
        task_type="bash",
        command="pytest tests/"
    )
    dag.add_task(task1)
    
    task2 = WorkflowTask(
        task_id="task-2",
        task_name="Code review",
        task_type="python",
        dependencies=["task-1"]  # Depends on tests
    )
    dag.add_task(task2)
    
    task3 = WorkflowTask(
        task_id="task-3",
        task_name="Deploy",
        task_type="bash",
        command="deploy.sh",
        dependencies=["task-2"]  # Depends on review
    )
    dag.add_task(task3)
    
    # Register DAG
    system.workflow_engine.register_dag(dag)
    print(f"✓ Created workflow: {dag.dag_id}")
    print(f"  Tasks: {len(dag.tasks)}")
    print(f"  Dependencies: task-1 -> task-2 -> task-3")
    
    # Show markdown
    dag_file = Path(".workflows/dags") / f"{dag.dag_id}.md"
    if dag_file.exists():
        print(f"\n✓ Saved to: {dag_file}")
        print(f"\nMarkdown preview:")
        print("-" * 60)
        print(dag_file.read_text()[:400])
        print("...")
    
    return dag


def demo_worktrees():
    """Demo: Worktrees for organizing agents."""
    print("\n" + "=" * 60)
    print("5. WORKTREES (Agent Organization)")
    print("=" * 60)
    
    system = create_unified_system()
    
    # Create worktree
    worktree = system.worktree_manager.create_worktree(
        name="Development Team",
        description="Team for development tasks",
        agent_types=["code", "test", "doc"],
        skills=["code-analysis", "documentation"]
    )
    
    print(f"✓ Created worktree: {worktree.worktree_id}")
    print(f"  Name: {worktree.config.name}")
    print(f"  Agents: {len(worktree.agents)}")
    print(f"  Skills: {len(worktree.skills)}")
    
    # Assign task
    task_id = system.worktree_manager.assign_task_to_worktree(
        worktree_id=worktree.worktree_id,
        task_description="Review code changes",
        agent_type="code",
        priority=8
    )
    print(f"✓ Assigned task: {task_id}")
    
    return worktree


def demo_cross_chat():
    """Demo: Cross-chat communication."""
    print("\n" + "=" * 60)
    print("6. CROSS-CHAT COMMUNICATION")
    print("=" * 60)
    
    system = create_unified_system()
    
    # Publish finding
    finding_id = system.cross_chat.publish(
        title="Kanban board created",
        content="Created dev-board with 2 cards",
        category="info",
        tags=["kanban", "setup"]
    )
    print(f"✓ Published finding: {finding_id}")
    
    # Discover findings
    findings = system.cross_chat.discover(limit=5)
    print(f"✓ Discovered {len(findings)} findings")
    
    # Send heartbeat
    system.cross_chat.send_heartbeat()
    print("✓ Sent heartbeat")
    
    return findings


def main():
    """Run complete proof of concept demo."""
    print("\n" + "=" * 60)
    print("PROOF OF CONCEPT: COMPLETE WHITEBOARD IMPLEMENTATION")
    print("=" * 60)
    print("\nDemonstrating all components:")
    print("1. Kanban Board (AI native language)")
    print("2. MCP UI (nested markdown)")
    print("3. Resources (markdown + DB)")
    print("4. Workflows (Airflow-style)")
    print("5. Worktrees (agent organization)")
    print("6. Cross-chat communication")
    print("\n")
    
    # Run demos
    board = demo_kanban_board()
    ui_tree = demo_mcp_ui()
    resources = demo_resources()
    dag = demo_workflows()
    worktree = demo_worktrees()
    findings = demo_cross_chat()
    
    # System status
    print("\n" + "=" * 60)
    print("SYSTEM STATUS")
    print("=" * 60)
    
    system = create_unified_system()
    status = system.get_system_status()
    
    print(f"\n✓ Worktrees: {status['worktrees']}")
    print(f"✓ Kanban boards: {status['kanban_boards']}")
    print(f"✓ Workflows: {status['workflows']}")
    print(f"✓ UI components: {status['ui_components']}")
    print(f"✓ Cross-chat sessions: {status['cross_chat_sessions']}")
    
    print("\n" + "=" * 60)
    print("PROOF OF CONCEPT COMPLETE!")
    print("=" * 60)
    print("\nAll components are working and integrated.")
    print("Check the following directories:")
    print("  - .kanban/        - Kanban boards (markdown)")
    print("  - .mcp-ui/        - MCP UI (nested markdown)")
    print("  - .workflows/     - Workflows (Airflow-style)")
    print("  - .worktrees/    - Worktrees (agent organization)")
    print("  - .crosschat/    - Cross-chat registry")


if __name__ == "__main__":
    main()
