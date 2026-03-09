"""
Abstract base class for elimination strategies.
"""
from abc import ABC, abstractmethod
from typing import List, Dict


class Eliminator(ABC):
    """Abstract base class for elimination strategies."""
    
    @abstractmethod
    def eliminate(self, scores: Dict[str, float], 
                  min_competitors: int = 1) -> List[str]:
        """
        Determine which competitors to eliminate.
        
        Args:
            scores: Dictionary mapping competitor_id -> score
            min_competitors: Minimum number of competitors to keep
            
        Returns:
            List of competitor IDs to eliminate
        """
        pass
    
    @abstractmethod
    def name(self) -> str:
        """Return name of this elimination strategy."""
        pass
