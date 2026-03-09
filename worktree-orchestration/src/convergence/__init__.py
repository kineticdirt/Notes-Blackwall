"""
Convergence detection for competitive AI orchestration.
"""
from .detector import ConvergenceDetector
from .score_stability import ScoreStabilityDetector

__all__ = ['ConvergenceDetector', 'ScoreStabilityDetector']
