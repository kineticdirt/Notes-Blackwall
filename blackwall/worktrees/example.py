#!/usr/bin/env python3
"""
Example usage of the worktree system.
"""

from pathlib import Path
import sys

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agent-system"))

from worktree_manager import UnifiedWorktreeManager


def main():
    """Example usage."""
    print("=== Worktree System Example ===\n")
    
    # Initialize manager
    print("1. Initializing worktree manager...")
    manager = UnifiedWorktreeManager()
    
    # List available skills
    print("\n2. Available skills:")
    skills = manager.get_available_skills()
    for skill in skills:
        print(f"   - {skill['name']}: {skill['description']}")
    
    # Create a worktree
    print("\n3. Creating worktree 'Development Team'...")
    worktree = manager.create_worktree(
        name="Development Team",
        description="Team for development and testing tasks",
        agent_types=["code", "test", "doc"],
        skills=["code-analysis", "documentation"]
    )
    print(f"   Created: {worktree.worktree_id}")
    print(f"   Agents: {len(worktree.agents)}")
    print(f"   Skills: {len(worktree.skills)}")
    
    # Assign a task
    print("\n4. Assigning task...")
    task_id = manager.assign_task_to_worktree(
        worktree_id=worktree.worktree_id,
        task_description="Analyze codebase for quality issues",
        agent_type="code",
        priority=7
    )
    print(f"   Task ID: {task_id}")
    
    # Get status
    print("\n5. Worktree status:")
    status = manager.get_worktree_status(worktree.worktree_id)
    print(f"   Name: {status['name']}")
    print(f"   Agents: {status['agent_count']}")
    print(f"   Skills: {len(status['skills'])}")
    
    # List all worktrees
    print("\n6. All worktrees:")
    worktrees = manager.list_all_worktrees()
    for wt in worktrees:
        print(f"   - {wt['name']} ({wt['worktree_id']})")
    
    print("\n=== Example Complete ===")


if __name__ == "__main__":
    main()
