"""
Weighted scorer plugin.

Calculates composite score from test results, diversity bonus, and critiques.
"""
from typing import List

from ..base import Critique, ScorerPlugin, Score, Solution, TestResults


class WeightedScorer(ScorerPlugin):
    """
    Weighted scorer with configurable weights.
    
    Score = test_score * test_weight + diversity_bonus * diversity_weight + critique_score * critique_weight
    """
    
    def __init__(
        self,
        test_weight: float = 0.7,
        diversity_weight: float = 0.2,
        critique_weight: float = 0.1
    ):
        """
        Initialize scorer.
        
        Args:
            test_weight: Weight for test results (default 0.7)
            diversity_weight: Weight for diversity bonus (default 0.2)
            critique_weight: Weight for critique scores (default 0.1)
        """
        self.test_weight = test_weight
        self.diversity_weight = diversity_weight
        self.critique_weight = critique_weight
    
    def calculate_score(
        self,
        solution: Solution,
        test_results: TestResults,
        critiques: List[Critique]
    ) -> Score:
        """
        Calculate composite score.
        
        Args:
            solution: Solution to score
            test_results: Test execution results
            critiques: List of critiques for this solution
        
        Returns:
            Score object with breakdown
        """
        # Test score (0.0-1.0)
        test_score = 1.0 if test_results.passed else 0.0
        
        # Diversity bonus (from solution metadata)
        diversity_bonus = solution.metadata.get("diversity_score", 0.0) if solution.metadata else 0.0
        
        # Critique score (average of critique scores)
        critique_score = 0.0
        if critiques:
            # Average the "correctness" scores from critiques
            correctness_scores = [
                c.scores.get("correctness", 0.0) / 10.0  # Normalize to 0-1
                for c in critiques
            ]
            critique_score = sum(correctness_scores) / len(correctness_scores)
        
        # Weighted combination
        total = (
            test_score * self.test_weight +
            diversity_bonus * self.diversity_weight +
            critique_score * self.critique_weight
        )
        
        return Score(
            solution_id=solution.solution_id,
            test_score=test_score,
            diversity_bonus=diversity_bonus,
            critique_score=critique_score,
            total=total,
            breakdown={
                "test_score": test_score,
                "test_weight": self.test_weight,
                "diversity_bonus": diversity_bonus,
                "diversity_weight": self.diversity_weight,
                "critique_score": critique_score,
                "critique_weight": self.critique_weight
            }
        )
