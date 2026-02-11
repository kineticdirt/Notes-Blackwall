#!/usr/bin/env python3
"""
CLI for managing worktrees, skills, and subagents.
"""

import argparse
import json
from pathlib import Path
from typing import Optional

from .worktree_manager import UnifiedWorktreeManager


def create_worktree(args):
    """Create a new worktree."""
    manager = UnifiedWorktreeManager()
    
    agent_types = args.agent_types.split(",") if args.agent_types else []
    skills = args.skills.split(",") if args.skills else []
    
    worktree = manager.create_worktree(
        name=args.name,
        description=args.description or "",
        agent_types=agent_types,
        skills=skills,
        metadata={}
    )
    
    print(f"Created worktree: {worktree.worktree_id}")
    print(f"Name: {worktree.config.name}")
    print(f"Agents: {len(worktree.agents)}")
    print(f"Skills: {len(worktree.skills)}")


def list_worktrees(args):
    """List all worktrees."""
    manager = UnifiedWorktreeManager()
    worktrees = manager.list_all_worktrees()
    
    if not worktrees:
        print("No worktrees found.")
        return
    
    print(f"\nFound {len(worktrees)} worktree(s):\n")
    for wt in worktrees:
        print(f"  ID: {wt['worktree_id']}")
        print(f"  Name: {wt['name']}")
        print(f"  Status: {wt['status']}")
        print(f"  Agents: {wt['agent_count']}")
        print(f"  Skills: {len(wt.get('skills', []))}")
        print()


def show_worktree(args):
    """Show details of a worktree."""
    manager = UnifiedWorktreeManager()
    status = manager.get_worktree_status(args.worktree_id)
    
    if not status:
        print(f"Worktree {args.worktree_id} not found.")
        return
    
    print(json.dumps(status, indent=2))


def assign_task(args):
    """Assign a task to a worktree."""
    manager = UnifiedWorktreeManager()
    
    task_id = manager.assign_task_to_worktree(
        worktree_id=args.worktree_id,
        task_description=args.description,
        agent_type=args.agent_type,
        priority=args.priority,
        metadata={}
    )
    
    print(f"Assigned task: {task_id}")
    print(f"Worktree: {args.worktree_id}")
    print(f"Description: {args.description}")


def list_skills(args):
    """List all available skills."""
    manager = UnifiedWorktreeManager()
    skills = manager.get_available_skills()
    
    if not skills:
        print("No skills found.")
        return
    
    print(f"\nFound {len(skills)} skill(s):\n")
    for skill in skills:
        print(f"  Name: {skill['name']}")
        print(f"  Description: {skill['description']}")
        print(f"  Tools: {', '.join(skill.get('tools', []))}")
        print(f"  Version: {skill.get('version', '1.0.0')}")
        print()


def reload_skills(args):
    """Reload skills from disk."""
    manager = UnifiedWorktreeManager()
    manager.reload_skills()
    print("Skills reloaded.")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Worktree Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Create worktree
    create_parser = subparsers.add_parser("create", help="Create a new worktree")
    create_parser.add_argument("name", help="Worktree name")
    create_parser.add_argument("-d", "--description", help="Worktree description")
    create_parser.add_argument("-a", "--agent-types", help="Comma-separated agent types")
    create_parser.add_argument("-s", "--skills", help="Comma-separated skill names")
    create_parser.set_defaults(func=create_worktree)
    
    # List worktrees
    list_parser = subparsers.add_parser("list", help="List all worktrees")
    list_parser.set_defaults(func=list_worktrees)
    
    # Show worktree
    show_parser = subparsers.add_parser("show", help="Show worktree details")
    show_parser.add_argument("worktree_id", help="Worktree ID")
    show_parser.set_defaults(func=show_worktree)
    
    # Assign task
    task_parser = subparsers.add_parser("task", help="Assign a task")
    task_parser.add_argument("worktree_id", help="Worktree ID")
    task_parser.add_argument("description", help="Task description")
    task_parser.add_argument("-t", "--agent-type", help="Preferred agent type")
    task_parser.add_argument("-p", "--priority", type=int, default=5, help="Priority (1-10)")
    task_parser.set_defaults(func=assign_task)
    
    # List skills
    skills_parser = subparsers.add_parser("skills", help="List all skills")
    skills_parser.set_defaults(func=list_skills)
    
    # Reload skills
    reload_parser = subparsers.add_parser("reload-skills", help="Reload skills from disk")
    reload_parser.set_defaults(func=reload_skills)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    args.func(args)


if __name__ == "__main__":
    main()
