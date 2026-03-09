"""
RADICAL archetype plugin.

Bold refactor, new patterns, functional/reactive/event-driven,
focus on scalability/innovation/tech debt.
"""
from typing import Dict, List

from ..base import ArchetypePlugin, BehaviorProfile, Strategy


class RadicalArchetype(ArchetypePlugin):
    """RADICAL archetype: bold, innovative, risk-taking."""
    
    def get_behavior_profile(self) -> BehaviorProfile:
        """Return RADICAL behavior profile."""
        return BehaviorProfile(
            archetype_id="radical",
            risk_tolerance=0.9,  # High risk tolerance
            innovation_level=0.95,  # Very high innovation
            convergence_avoidance=0.85,  # Actively avoid convergence
            metadata={
                "prefers": ["functional", "reactive", "event-driven"],
                "avoids": ["imperative", "procedural", "tight coupling"],
                "focus": ["scalability", "innovation", "tech debt reduction"]
            }
        )
    
    async def adapt_strategy(
        self,
        competitor_id: str,
        round_history: List[Dict],
        current_rankings: List[Dict]
    ) -> Strategy:
        """
        Adapt strategy based on history.
        
        RADICAL: If ranking low, take bigger risks. If ranking high, innovate more.
        """
        # Find current rank
        current_rank = None
        for i, ranking in enumerate(current_rankings):
            if ranking.get("competitor_id") == competitor_id:
                current_rank = i + 1
                break
        
        # Calculate convergence in recent rounds
        recent_convergence = 0.0
        if round_history:
            recent = round_history[-3:]  # Last 3 rounds
            convergence_scores = [
                r.get("convergence_metric", 0.0) for r in recent
            ]
            recent_convergence = sum(convergence_scores) / len(convergence_scores) if convergence_scores else 0.0
        
        # Strategy adaptation
        if current_rank and current_rank > len(current_rankings) / 2:
            # Below median: take bigger risks
            approach = "high_risk_innovation"
            parameters = {
                "experiment_with_patterns": True,
                "break_conventions": True,
                "max_similarity_threshold": 0.70  # Lower threshold = more unique
            }
        elif recent_convergence > 0.80:
            # High convergence: actively diverge
            approach = "active_divergence"
            parameters = {
                "explicitly_avoid_similar_solutions": True,
                "prefer_unconventional_approaches": True,
                "max_similarity_threshold": 0.65
            }
        else:
            # Normal: innovate but maintain quality
            approach = "balanced_innovation"
            parameters = {
                "prefer_functional_patterns": True,
                "focus_on_scalability": True,
                "max_similarity_threshold": 0.75
            }
        
        return Strategy(
            competitor_id=competitor_id,
            approach=approach,
            parameters=parameters
        )
