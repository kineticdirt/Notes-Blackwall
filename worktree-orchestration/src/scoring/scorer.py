"""
Abstract base class for scoring competitors.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class Scorer(ABC):
    """Abstract base class for scoring competitors."""
    
    @abstractmethod
    def score(self, competitor_id: str, round_num: int, 
              test_results: Dict[str, Any]) -> float:
        """
        Calculate score for a competitor in a round.
        
        Args:
            competitor_id: Competitor identifier
            round_num: Round number
            test_results: Test execution results dictionary
            
        Returns:
            Score value between 0.0 and 100.0
        """
        pass
    
    @abstractmethod
    def name(self) -> str:
        """Return name of this scorer."""
        pass
