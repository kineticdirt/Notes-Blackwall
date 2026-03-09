"""
Code quality-based scoring criterion.
"""
from typing import Dict, Any
from pathlib import Path
from ..scorer import Scorer


class CodeQualityScorer(Scorer):
    """
    Scores based on basic code quality metrics.
    
    Metrics:
    - File count (more files = slightly higher, but diminishing returns)
    - Code complexity (simpler = higher)
    - Documentation (README presence)
    """
    
    def score(self, competitor_id: str, round_num: int, 
              test_results: Dict[str, Any]) -> float:
        """
        Calculate score based on code quality metrics.
        
        Args:
            competitor_id: Competitor identifier
            round_num: Round number
            test_results: Test execution results (should include worktree_path)
            
        Returns:
            Score between 0.0 and 100.0
        """
        worktree_path = test_results.get("worktree_path")
        if not worktree_path:
            return 50.0
        
        try:
            worktree = Path(worktree_path)
            solution_dir = worktree / "solution"
            
            if not solution_dir.exists():
                return 0.0
            
            # Count files
            files = list(solution_dir.rglob("*"))
            file_count = sum(1 for f in files if f.is_file())
            
            # Check for README
            has_readme = (solution_dir / "README.md").exists() or \
                        (solution_dir / "README.txt").exists()
            
            # Simple scoring:
            # - File count: 1-5 files = good (30 points), more = diminishing returns
            # - README: 20 points if present
            # - Basic structure: 50 points base
            
            file_score = min(30.0, file_count * 6.0)  # Max 30 points
            readme_score = 20.0 if has_readme else 0.0
            base_score = 50.0
            
            total_score = base_score + file_score + readme_score
            return max(0.0, min(100.0, total_score))
        except Exception as e:
            # Log error and return neutral score
            import logging
            logging.warning(f"Code quality scoring failed: {e}")
            return 50.0
    
    def name(self) -> str:
        """Return name of this scorer."""
        return "CodeQuality"
