"""
Worktree system for organizing multiple agents.
Worktrees provide logical grouping and isolation for agent teams.
"""

from .worktree import Worktree, WorktreeManager
from .worktree_db import WorktreeDatabase
from .worktree_manager import UnifiedWorktreeManager
from .cross_chat import CrossChatBridge, CrossChatRegistry, Finding

__all__ = [
    'Worktree', 
    'WorktreeManager', 
    'WorktreeDatabase', 
    'UnifiedWorktreeManager',
    'CrossChatBridge',
    'CrossChatRegistry',
    'Finding'
]
