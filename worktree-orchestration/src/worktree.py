"""
Directory-based worktree management.
"""
import shutil
from pathlib import Path
from typing import Optional, List
from datetime import datetime


class Worktree:
    """Represents a single worktree."""
    
    def __init__(self, competitor_id: str, round_num: int, path: Path):
        self.competitor_id = competitor_id
        self.round_num = round_num
        self.path = path
        self.created_at = datetime.now()
    
    def exists(self) -> bool:
        """Check if worktree directory exists."""
        return self.path.exists() and self.path.is_dir()
    
    def cleanup(self) -> None:
        """Remove worktree directory."""
        if self.exists():
            shutil.rmtree(self.path)


class WorktreeManager:
    """Manages worktree creation and isolation."""
    
    def __init__(self, base_path: Path, template_path: Optional[Path] = None):
        self.base_path = base_path
        self.template_path = template_path
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def create_worktree(self, competitor_id: str, round_num: int) -> Worktree:
        """
        Create a new worktree for a competitor in a round.
        
        Args:
            competitor_id: Unique competitor identifier
            round_num: Round number (1-indexed)
            
        Returns:
            Worktree object
            
        Raises:
            ValueError: If worktree already exists or invalid inputs
        """
        # Validate inputs
        if not competitor_id or not competitor_id.replace('_', '').replace('-', '').isalnum():
            raise ValueError(f"Invalid competitor_id: {competitor_id}")
        if round_num < 1:
            raise ValueError(f"Round number must be >= 1, got {round_num}")
        
        # Generate worktree path
        worktree_name = f"wt_{competitor_id}_r{round_num:03d}"
        worktree_path = self.base_path / worktree_name
        
        # Check if already exists
        if worktree_path.exists():
            raise ValueError(f"Worktree already exists: {worktree_path}")
        
        # Create worktree directory
        worktree_path.mkdir(parents=True, exist_ok=True)
        
        # Copy template if provided
        if self.template_path and self.template_path.exists():
            for item in self.template_path.iterdir():
                dest = worktree_path / item.name
                if item.is_dir():
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
        
        # Create solution directory
        (worktree_path / "solution").mkdir(exist_ok=True)
        
        # Create metadata file
        metadata = {
            "competitor_id": competitor_id,
            "round_num": round_num,
            "created_at": datetime.now().isoformat(),
            "worktree_name": worktree_name
        }
        import json
        with open(worktree_path / ".metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return Worktree(competitor_id, round_num, worktree_path)
    
    def get_worktree(self, competitor_id: str, round_num: int) -> Optional[Worktree]:
        """
        Get existing worktree.
        
        Args:
            competitor_id: Competitor identifier
            round_num: Round number
            
        Returns:
            Worktree if exists, None otherwise
        """
        worktree_name = f"wt_{competitor_id}_r{round_num:03d}"
        worktree_path = self.base_path / worktree_name
        
        if worktree_path.exists() and worktree_path.is_dir():
            return Worktree(competitor_id, round_num, worktree_path)
        return None
    
    def list_worktrees(self, round_num: Optional[int] = None) -> List[Worktree]:
        """
        List all worktrees, optionally filtered by round.
        
        Args:
            round_num: Optional round number filter
            
        Returns:
            List of Worktree objects
        """
        worktrees = []
        
        if not self.base_path.exists():
            return worktrees
        
        for item in self.base_path.iterdir():
            if not item.is_dir() or not item.name.startswith("wt_"):
                continue
            
            # Parse worktree name: wt_{competitor_id}_r{round_num}
            parts = item.name.split("_r")
            if len(parts) != 2:
                continue
            
            competitor_id = parts[0][3:]  # Remove "wt_" prefix
            try:
                r_num = int(parts[1])
            except ValueError:
                continue
            
            if round_num is None or r_num == round_num:
                worktrees.append(Worktree(competitor_id, r_num, item))
        
        return worktrees
    
    def cleanup_worktree(self, competitor_id: str, round_num: int) -> None:
        """Remove a specific worktree."""
        worktree = self.get_worktree(competitor_id, round_num)
        if worktree:
            worktree.cleanup()
    
    def cleanup_all(self, round_num: Optional[int] = None) -> int:
        """
        Cleanup all worktrees, optionally filtered by round.
        
        Args:
            round_num: Optional round number filter
            
        Returns:
            Number of worktrees cleaned up
        """
        worktrees = self.list_worktrees(round_num)
        count = 0
        for worktree in worktrees:
            worktree.cleanup()
            count += 1
        return count
