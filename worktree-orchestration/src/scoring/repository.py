"""
Repository for storing and retrieving scores.
"""
import json
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime


class ScoreRepository:
    """Manages score storage and retrieval."""
    
    def __init__(self, cache_dir: Path):
        """
        Initialize score repository.
        
        Args:
            cache_dir: Base cache directory (.shared-cache/)
        """
        self.cache_dir = cache_dir
        self.scores_dir = cache_dir / "scores"
        self.scores_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, round_num: int, competitor_id: str, score: float, 
             metadata: Optional[Dict] = None) -> None:
        """
        Save score for a competitor in a round.
        
        Args:
            round_num: Round number
            competitor_id: Competitor identifier
            score: Score value (0-100)
            metadata: Optional metadata dictionary
        """
        round_dir = self.scores_dir / f"round_{round_num:03d}"
        round_dir.mkdir(parents=True, exist_ok=True)
        
        score_file = round_dir / f"{competitor_id}.json"
        score_data = {
            "competitor_id": competitor_id,
            "round_num": round_num,
            "score": score,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        with open(score_file, 'w') as f:
            json.dump(score_data, f, indent=2)
    
    def get(self, round_num: int, competitor_id: str) -> Optional[float]:
        """
        Get score for a competitor in a round.
        
        Args:
            round_num: Round number
            competitor_id: Competitor identifier
            
        Returns:
            Score value or None if not found
        """
        round_dir = self.scores_dir / f"round_{round_num:03d}"
        score_file = round_dir / f"{competitor_id}.json"
        
        if not score_file.exists():
            return None
        
        try:
            with open(score_file, 'r') as f:
                data = json.load(f)
            return data.get("score")
        except Exception:
            return None
    
    def get_all(self, round_num: int) -> Dict[str, float]:
        """
        Get all scores for a round.
        
        Args:
            round_num: Round number
            
        Returns:
            Dictionary mapping competitor_id -> score
        """
        round_dir = self.scores_dir / f"round_{round_num:03d}"
        scores = {}
        
        if not round_dir.exists():
            return scores
        
        for score_file in round_dir.glob("*.json"):
            competitor_id = score_file.stem
            score = self.get(round_num, competitor_id)
            if score is not None:
                scores[competitor_id] = score
        
        return scores
    
    def get_historical(self, competitor_id: str, max_rounds: Optional[int] = None) -> List[float]:
        """
        Get historical scores for a competitor across rounds.
        
        Args:
            competitor_id: Competitor identifier
            max_rounds: Maximum number of rounds to retrieve (None = all)
            
        Returns:
            List of scores in chronological order
        """
        scores = []
        
        # Find all rounds
        round_dirs = sorted(self.scores_dir.glob("round_*"))
        if max_rounds:
            round_dirs = round_dirs[-max_rounds:]
        
        for round_dir in round_dirs:
            try:
                round_num = int(round_dir.name.split("_")[1])
                score = self.get(round_num, competitor_id)
                if score is not None:
                    scores.append(score)
            except (ValueError, IndexError):
                continue
        
        return scores
