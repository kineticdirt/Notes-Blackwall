#!/usr/bin/env python3
"""
Worktree Manager - Creates and manages worktree directories
"""
import json
import os
import shutil
from pathlib import Path


class WorktreeManager:
    def __init__(self, spec_file="worktree-spec.json"):
        with open(spec_file, 'r') as f:
            self.spec = json.load(f)
        self.base_dir = Path.cwd()
        
    def create_worktrees(self):
        """Create all worktree directories"""
        worktrees = self.spec.get("worktrees", [])
        storage = self.spec.get("storage", {})
        
        # Create storage directories
        for dir_name in ["solutions_dir", "critiques_dir", "results_dir"]:
            if dir_name in storage:
                os.makedirs(storage[dir_name], exist_ok=True)
        
        # Create worktree directories
        created = []
        for wt in worktrees:
            wt_path = self.base_dir / wt["path"]
            wt_path.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories for each worktree
            (wt_path / "solution").mkdir(exist_ok=True)
            (wt_path / "critique").mkdir(exist_ok=True)
            
            created.append(wt_path)
            print(f"✓ Created worktree: {wt['name']} at {wt_path}")
        
        return created
    
    def list_worktrees(self):
        """List all worktrees"""
        return self.spec.get("worktrees", [])
    
    def get_worktree_path(self, worktree_id):
        """Get path for a specific worktree"""
        for wt in self.spec.get("worktrees", []):
            if wt["id"] == worktree_id:
                return self.base_dir / wt["path"]
        return None


if __name__ == "__main__":
    manager = WorktreeManager()
    manager.create_worktrees()
