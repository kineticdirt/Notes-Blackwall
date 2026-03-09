"""
Weighted multi-criteria scoring system.
"""
from typing import List, Dict, Any
from .scorer import Scorer


class WeightedScorer(Scorer):
    """
    Combines multiple scoring criteria with configurable weights.
    
    Example:
        scorer = WeightedScorer(
            criteria=[TestScorer(), PerformanceScorer()],
            weights=[0.6, 0.4]
        )
        score = scorer.score("competitor1", 1, test_results)
    """
    
    def __init__(self, criteria: List[Scorer], weights: List[float]):
        """
        Initialize weighted scorer.
        
        Args:
            criteria: List of scorer instances
            weights: List of weights (must sum to 1.0)
            
        Raises:
            ValueError: If criteria and weights length mismatch or weights don't sum to 1.0
        """
        if len(criteria) != len(weights):
            raise ValueError("Criteria and weights must have same length")
        
        if abs(sum(weights) - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {sum(weights)}")
        
        self.criteria = criteria
        self.weights = weights
    
    def score(self, competitor_id: str, round_num: int, 
              test_results: Dict[str, Any]) -> float:
        """
        Calculate weighted score.
        
        Args:
            competitor_id: Competitor identifier
            round_num: Round number
            test_results: Test execution results
            
        Returns:
            Weighted score between 0.0 and 100.0
        """
        scores = []
        for criterion in self.criteria:
            try:
                criterion_score = criterion.score(competitor_id, round_num, test_results)
                scores.append(criterion_score)
            except Exception as e:
                # Log error and use 0.0 as fallback
                import logging
                logging.warning(f"Scoring criterion {criterion.name()} failed: {e}")
                scores.append(0.0)
        
        # Calculate weighted sum
        weighted_score = sum(s * w for s, w in zip(scores, self.weights))
        return max(0.0, min(100.0, weighted_score))  # Clamp to [0, 100]
    
    def name(self) -> str:
        """Return name of this scorer."""
        criterion_names = [c.name() for c in self.criteria]
        return f"WeightedScorer({', '.join(criterion_names)})"
