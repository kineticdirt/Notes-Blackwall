"""
Fallback security adapter when no security tools are available.
"""
from pathlib import Path
from typing import Dict, Any
from ..base import SecurityAdapter


class FallbackSecurityAdapter(SecurityAdapter):
    """
    Fallback adapter that returns neutral security results.
    
    Used when semgrep/snyk are not available.
    """
    
    def scan(self, worktree_path: Path) -> Dict[str, Any]:
        """
        Return neutral security scan results.
        
        Args:
            worktree_path: Path to worktree directory
            
        Returns:
            Dictionary with neutral results
        """
        return {
            "vulnerability_count": 0,
            "vulnerabilities": [],
            "scan_successful": True,
            "error": None,
            "adapter": "fallback",
            "note": "No security tools available, using neutral score"
        }
    
    def is_available(self) -> bool:
        """Fallback adapter is always available."""
        return True
    
    def name(self) -> str:
        """Return name of this adapter."""
        return "FallbackSecurity"
