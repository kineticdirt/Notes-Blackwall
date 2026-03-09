"""
Score stability-based convergence detection.
"""
from typing import List, Dict
import statistics
from .detector import ConvergenceDetector


class ScoreStabilityDetector(ConvergenceDetector):
    """
    Detects convergence when score variance stabilizes below threshold.
    
    Checks if score variance across competitors is stable over recent rounds.
    """
    
    def __init__(self, threshold: float = 0.05, window_size: int = 3):
        """
        Initialize score stability detector.
        
        Args:
            threshold: Maximum variance threshold (0.0-1.0)
            window_size: Number of recent rounds to check
        """
        self.threshold = threshold
        self.window_size = window_size
    
    def is_converged(self, round_scores: List[Dict[str, float]]) -> bool:
        """
        Check if scores have converged.
        
        Args:
            round_scores: List of score dictionaries (one per round)
            
        Returns:
            True if converged, False otherwise
        """
        if len(round_scores) < self.window_size:
            return False
        
        # Get recent rounds
        recent_rounds = round_scores[-self.window_size:]
        
        # Calculate variance for each round
        variances = []
        for round_scores_dict in recent_rounds:
            if not round_scores_dict:
                continue
            
            scores = list(round_scores_dict.values())
            if len(scores) < 2:
                continue
            
            # Normalize scores to [0, 1] for variance calculation
            max_score = max(scores) if scores else 1.0
            if max_score == 0:
                continue
            
            normalized_scores = [s / max_score for s in scores]
            variance = statistics.variance(normalized_scores) if len(normalized_scores) > 1 else 0.0
            variances.append(variance)
        
        if not variances:
            return False
        
        # Check if all variances are below threshold
        max_variance = max(variances)
        return max_variance < self.threshold
    
    def name(self) -> str:
        """Return name of this convergence detector."""
        return f"ScoreStability(threshold={self.threshold}, window={self.window_size})"
