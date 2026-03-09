"""
Base adapter interface for external tools.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any


class Adapter(ABC):
    """Abstract base class for external tool adapters."""
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the tool/service is available.
        
        Returns:
            True if available, False otherwise
        """
        pass
    
    @abstractmethod
    def name(self) -> str:
        """Return name of this adapter."""
        pass


class SecurityAdapter(Adapter):
    """Abstract base class for security scanning adapters."""
    
    @abstractmethod
    def scan(self, worktree_path: Path) -> Dict[str, Any]:
        """
        Scan worktree for security vulnerabilities.
        
        Args:
            worktree_path: Path to worktree directory
            
        Returns:
            Dictionary with scan results:
            {
                "vulnerability_count": int,
                "vulnerabilities": List[Dict],
                "scan_successful": bool,
                "error": Optional[str]
            }
        """
        pass
