"""
Tests for worktree management.
"""
import pytest
from pathlib import Path
from src.worktree import WorktreeManager, Worktree


def test_create_worktree(tmp_path):
    """Test worktree creation."""
    base_path = tmp_path / "worktrees"
    manager = WorktreeManager(base_path)
    
    worktree = manager.create_worktree("agent_a", 1)
    
    assert worktree.exists()
    assert worktree.competitor_id == "agent_a"
    assert worktree.round_num == 1
    assert (worktree.path / "solution").exists()


def test_worktree_naming(tmp_path):
    """Test worktree naming convention."""
    base_path = tmp_path / "worktrees"
    manager = WorktreeManager(base_path)
    
    worktree = manager.create_worktree("agent_b", 5)
    
    assert worktree.path.name == "wt_agent_b_r005"


def test_duplicate_worktree(tmp_path):
    """Test that duplicate worktrees are rejected."""
    base_path = tmp_path / "worktrees"
    manager = WorktreeManager(base_path)
    
    manager.create_worktree("agent_c", 1)
    
    with pytest.raises(ValueError, match="already exists"):
        manager.create_worktree("agent_c", 1)


def test_list_worktrees(tmp_path):
    """Test listing worktrees."""
    base_path = tmp_path / "worktrees"
    manager = WorktreeManager(base_path)
    
    manager.create_worktree("agent_a", 1)
    manager.create_worktree("agent_b", 1)
    manager.create_worktree("agent_a", 2)
    
    worktrees = manager.list_worktrees()
    assert len(worktrees) == 3
    
    worktrees_round1 = manager.list_worktrees(round_num=1)
    assert len(worktrees_round1) == 2


def test_cleanup_worktree(tmp_path):
    """Test worktree cleanup."""
    base_path = tmp_path / "worktrees"
    manager = WorktreeManager(base_path)
    
    worktree = manager.create_worktree("agent_d", 1)
    assert worktree.exists()
    
    manager.cleanup_worktree("agent_d", 1)
    assert not worktree.exists()
