"""
Bottom N elimination strategy.
"""
from typing import List, Dict
from .eliminator import Eliminator


class BottomNEliminator(Eliminator):
    """
    Eliminates the bottom N competitors by score.
    
    Example:
        eliminator = BottomNEliminator(eliminate_per_round=2)
        eliminated = eliminator.eliminate({"comp1": 80.0, "comp2": 50.0, "comp3": 30.0})
        # Returns ["comp3"] (lowest score)
    """
    
    def __init__(self, eliminate_per_round: int = 1):
        """
        Initialize bottom N eliminator.
        
        Args:
            eliminate_per_round: Number of competitors to eliminate per round
        """
        self.eliminate_per_round = eliminate_per_round
    
    def eliminate(self, scores: Dict[str, float], 
                  min_competitors: int = 1) -> List[str]:
        """
        Eliminate bottom N competitors.
        
        Args:
            scores: Dictionary mapping competitor_id -> score
            min_competitors: Minimum number of competitors to keep
            
        Returns:
            List of competitor IDs to eliminate
        """
        if not scores:
            return []
        
        # Sort by score (ascending: lowest first)
        sorted_competitors = sorted(scores.items(), key=lambda x: x[1])
        
        # Calculate how many we can eliminate
        current_count = len(sorted_competitors)
        max_eliminate = max(0, current_count - min_competitors)
        eliminate_count = min(self.eliminate_per_round, max_eliminate)
        
        if eliminate_count == 0:
            return []
        
        # Return bottom N competitor IDs
        eliminated = [comp_id for comp_id, _ in sorted_competitors[:eliminate_count]]
        return eliminated
    
    def name(self) -> str:
        """Return name of this elimination strategy."""
        return f"BottomN({self.eliminate_per_round})"
