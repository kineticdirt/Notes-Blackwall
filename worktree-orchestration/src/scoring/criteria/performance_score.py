"""
Performance-based scoring criterion.
"""
from typing import Dict, Any, List
from ..scorer import Scorer


class PerformanceScorer(Scorer):
    """
    Scores based on execution time (faster = higher score).
    
    Normalizes execution time across all competitors in the round.
    """
    
    def score(self, competitor_id: str, round_num: int, 
              test_results: Dict[str, Any]) -> float:
        """
        Calculate score based on performance.
        
        Args:
            competitor_id: Competitor identifier
            round_num: Round number
            test_results: Test execution results with 'test_duration_ms' key
            
        Returns:
            Score between 0.0 and 100.0 (faster = higher)
        """
        duration_ms = test_results.get("test_duration_ms", 0)
        
        # If no duration recorded, return neutral score
        if duration_ms == 0:
            return 50.0
        
        # For MVP: Simple inverse relationship
        # TODO: Normalize against all competitors in round
        # For now: assume 1 second = 100 points, scale down
        max_duration_ms = 10000  # 10 seconds = 0 points
        if duration_ms >= max_duration_ms:
            return 0.0
        
        # Linear scaling: faster = higher score
        score = 100.0 * (1.0 - (duration_ms / max_duration_ms))
        return max(0.0, min(100.0, score))
    
    def name(self) -> str:
        """Return name of this scorer."""
        return "Performance"
    
    @staticmethod
    def normalize_scores(durations_ms: List[float]) -> Dict[str, float]:
        """
        Normalize performance scores across all competitors.
        
        Args:
            durations_ms: List of durations in milliseconds
            
        Returns:
            Dictionary mapping duration -> normalized score
        """
        if not durations_ms:
            return {}
        
        min_duration = min(durations_ms)
        max_duration = max(durations_ms)
        
        if max_duration == min_duration:
            # All same duration, return equal scores
            return {d: 100.0 for d in durations_ms}
        
        # Normalize: fastest gets 100, slowest gets 0
        normalized = {}
        for duration in durations_ms:
            score = 100.0 * (1.0 - (duration - min_duration) / (max_duration - min_duration))
            normalized[duration] = max(0.0, min(100.0, score))
        
        return normalized
