"""
Diversity threshold enforcement.

Enforces similarity thresholds and diversity requirements.
"""
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .similarity import SimilarityAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class DiversityConfig:
    """Configuration for diversity enforcement."""
    min_similarity_threshold: float = 0.85  # Reject if >85% similar
    max_cluster_size: int = 3  # Max solutions per cluster
    diversity_bonus: float = 0.1  # Bonus score for unique solutions
    convergence_threshold: float = 0.90  # Round converged if avg similarity >90%
    
    # Similarity weights
    ast_weight: float = 0.6
    structure_weight: float = 0.3
    hash_weight: float = 0.1


class DiversityEnforcer:
    """
    Enforces diversity thresholds on solution submissions.
    
    Prevents solution convergence by rejecting overly similar solutions.
    """
    
    def __init__(self, config: Optional[DiversityConfig] = None):
        self.config = config or DiversityConfig()
        self.analyzer = SimilarityAnalyzer()
        
        # Track solutions per round: round_id -> [(solution_id, path)]
        self._round_solutions: Dict[int, List[Tuple[str, Path]]] = {}
    
    def register_solution(self, round_id: int, solution_id: str, solution_path: Path):
        """Register an accepted solution for a round."""
        if round_id not in self._round_solutions:
            self._round_solutions[round_id] = []
        
        self._round_solutions[round_id].append((solution_id, solution_path))
    
    def check_diversity(
        self,
        round_id: int,
        solution_id: str,
        solution_path: Path
    ) -> Tuple[bool, Optional[str], float, List[str]]:
        """
        Check if solution meets diversity requirements.
        
        Args:
            round_id: Round number
            solution_id: Solution identifier
            solution_path: Path to solution directory
        
        Returns:
            Tuple of (accepted, reason, similarity_score, similar_solution_ids)
            - accepted: True if solution passes diversity check
            - reason: Rejection reason if not accepted
            - similarity_score: Highest similarity to existing solutions
            - similar_solution_ids: List of similar solution IDs
        """
        existing = self._round_solutions.get(round_id, [])
        
        if not existing:
            # First solution in round, always accept
            return True, None, 0.0, []
        
        # Find most similar solutions
        similar = self.analyzer.find_most_similar(
            solution_path,
            existing,
            threshold=self.config.min_similarity_threshold
        )
        
        if not similar:
            # No similar solutions found, accept
            return True, None, 0.0, []
        
        # Check similarity threshold
        highest_sim = similar[0][1]
        similar_ids = [sid for sid, _ in similar]
        
        if highest_sim >= self.config.min_similarity_threshold:
            reason = (
                f"Solution too similar to existing solutions "
                f"(similarity: {highest_sim:.2f}, threshold: {self.config.min_similarity_threshold})"
            )
            return False, reason, highest_sim, similar_ids
        
        # Check cluster size
        cluster_size = len(similar) + 1  # +1 for new solution
        if cluster_size > self.config.max_cluster_size:
            reason = (
                f"Solution would exceed max cluster size "
                f"(would be {cluster_size}, max: {self.config.max_cluster_size})"
            )
            return False, reason, highest_sim, similar_ids
        
        # Passes diversity check
        return True, None, highest_sim, similar_ids
    
    def calculate_diversity_score(
        self,
        round_id: int,
        solution_id: str,
        solution_path: Path
    ) -> float:
        """
        Calculate diversity score for a solution.
        
        Higher score = more unique solution.
        Used for diversity bonus in scoring.
        
        Returns:
            Diversity score [0.0, 1.0]
        """
        existing = self._round_solutions.get(round_id, [])
        
        if not existing:
            return 1.0  # First solution is maximally diverse
        
        # Find most similar solution
        similar = self.analyzer.find_most_similar(
            solution_path,
            existing,
            threshold=0.0  # Check all solutions
        )
        
        if not similar:
            return 1.0
        
        # Diversity score = 1 - highest_similarity
        highest_sim = similar[0][1]
        return max(0.0, 1.0 - highest_sim)
    
    def calculate_convergence(self, round_id: int) -> Tuple[float, Dict[str, int]]:
        """
        Calculate convergence metric for a round.
        
        Args:
            round_id: Round number
        
        Returns:
            Tuple of (convergence_metric, cluster_sizes)
            - convergence_metric: Average similarity across all solution pairs [0.0, 1.0]
            - cluster_sizes: Dict mapping cluster_id to size
        """
        solutions = self._round_solutions.get(round_id, [])
        
        if len(solutions) < 2:
            return 0.0, {}
        
        # Calculate pairwise similarities
        similarities = []
        for i, (sid1, path1) in enumerate(solutions):
            for sid2, path2 in solutions[i+1:]:
                sim = self.analyzer.calculate_similarity(path1, path2)
                similarities.append(sim)
        
        # Average similarity
        convergence = sum(similarities) / len(similarities) if similarities else 0.0
        
        # Simple clustering: group solutions with similarity > threshold
        clusters = self._cluster_solutions(solutions)
        cluster_sizes = {cid: len(sols) for cid, sols in clusters.items()}
        
        return convergence, cluster_sizes
    
    def _cluster_solutions(
        self,
        solutions: List[Tuple[str, Path]]
    ) -> Dict[str, List[Tuple[str, Path]]]:
        """Group solutions into clusters based on similarity."""
        clusters: Dict[str, List[Tuple[str, Path]]] = {}
        
        for solution_id, solution_path in solutions:
            # Find cluster this solution belongs to
            assigned = False
            for cluster_id, cluster_solutions in clusters.items():
                # Check similarity to any solution in cluster
                for _, existing_path in cluster_solutions:
                    sim = self.analyzer.calculate_similarity(solution_path, existing_path)
                    if sim >= self.config.min_similarity_threshold:
                        clusters[cluster_id].append((solution_id, solution_path))
                        assigned = True
                        break
                if assigned:
                    break
            
            # Create new cluster if no match found
            if not assigned:
                cluster_id = f"cluster_{len(clusters)}"
                clusters[cluster_id] = [(solution_id, solution_path)]
        
        return clusters
    
    def clear_round(self, round_id: int):
        """Clear solutions for a round (cleanup)."""
        if round_id in self._round_solutions:
            del self._round_solutions[round_id]
