"""
Security-based scoring criterion.
"""
from typing import Dict, Any, Optional
from pathlib import Path
from ..scorer import Scorer


class SecurityScorer(Scorer):
    """
    Scores based on security scan results.
    
    Requires a security adapter to provide vulnerability counts.
    """
    
    def __init__(self, security_adapter: Optional[Any] = None):
        """
        Initialize security scorer.
        
        Args:
            security_adapter: Security adapter instance (optional, will use fallback if None)
        """
        self.security_adapter = security_adapter
    
    def score(self, competitor_id: str, round_num: int, 
              test_results: Dict[str, Any]) -> float:
        """
        Calculate score based on security scan results.
        
        Args:
            competitor_id: Competitor identifier
            round_num: Round number
            test_results: Test execution results (should include worktree_path)
            
        Returns:
            Score between 0.0 and 100.0 (fewer vulnerabilities = higher)
        """
        if not self.security_adapter:
            # No security adapter, return neutral score
            return 50.0
        
        worktree_path = test_results.get("worktree_path")
        if not worktree_path:
            return 50.0
        
        try:
            # Get security scan result
            security_result = self.security_adapter.scan(Path(worktree_path))
            
            # Score based on vulnerability count
            vuln_count = security_result.get("vulnerability_count", 0)
            
            # Simple scoring: 0 vulnerabilities = 100, 10+ = 0
            if vuln_count == 0:
                return 100.0
            elif vuln_count >= 10:
                return 0.0
            else:
                # Linear scaling
                return 100.0 * (1.0 - (vuln_count / 10.0))
        except Exception as e:
            # Log error and return neutral score
            import logging
            logging.warning(f"Security scoring failed: {e}")
            return 50.0
    
    def name(self) -> str:
        """Return name of this scorer."""
        return "Security"
