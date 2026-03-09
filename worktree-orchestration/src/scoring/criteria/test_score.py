"""
Test pass/fail scoring criterion.
"""
from typing import Dict, Any
from ..scorer import Scorer


class TestScoreScorer(Scorer):
    """
    Scores based on test pass/fail status.
    
    - Test passed: 100.0
    - Test failed: 0.0
    """
    
    def score(self, competitor_id: str, round_num: int, 
              test_results: Dict[str, Any]) -> float:
        """
        Calculate score based on test results.
        
        Args:
            competitor_id: Competitor identifier
            round_num: Round number
            test_results: Test execution results with 'test_passed' key
            
        Returns:
            100.0 if test passed, 0.0 if failed
        """
        test_passed = test_results.get("test_passed", False)
        return 100.0 if test_passed else 0.0
    
    def name(self) -> str:
        """Return name of this scorer."""
        return "TestScore"
