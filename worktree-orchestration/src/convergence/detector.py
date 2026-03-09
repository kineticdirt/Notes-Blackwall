"""
Abstract base class for convergence detection.
"""
from abc import ABC, abstractmethod
from typing import List, Dict


class ConvergenceDetector(ABC):
    """Abstract base class for convergence detection strategies."""
    
    @abstractmethod
    def is_converged(self, round_scores: List[Dict[str, float]]) -> bool:
        """
        Determine if competition has converged.
        
        Args:
            round_scores: List of score dictionaries (one per round)
                          Each dict maps competitor_id -> score
                          
        Returns:
            True if converged, False otherwise
        """
        pass
    
    @abstractmethod
    def name(self) -> str:
        """Return name of this convergence detector."""
        pass
