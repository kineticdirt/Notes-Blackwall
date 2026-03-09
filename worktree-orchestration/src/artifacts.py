"""
Artifact storage and retrieval.
"""
import json
import hashlib
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class SolutionArtifact(BaseModel):
    """Solution artifact."""
    competitor_id: str
    round_num: int
    timestamp: str
    worktree_path: str
    files: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CritiqueArtifact(BaseModel):
    """Critique artifact."""
    competitor_id: str
    round_num: int
    target_solution_id: str
    timestamp: str
    critique_text: str
    scores: Dict[str, int] = Field(default_factory=dict)


class ArtifactStore:
    """Manages artifact storage."""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.rounds_dir = cache_dir / "rounds"
        self.rounds_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_round_dir(self, round_num: int) -> Path:
        """Get directory for a specific round."""
        round_dir = self.rounds_dir / f"round_{round_num:03d}"
        round_dir.mkdir(parents=True, exist_ok=True)
        (round_dir / "solutions").mkdir(exist_ok=True)
        (round_dir / "critiques").mkdir(exist_ok=True)
        return round_dir
    
    def store_solution(self, round_num: int, competitor_id: str, 
                      worktree_path: Path, files: List[Dict[str, Any]]) -> str:
        """
        Store solution artifact.
        
        Args:
            round_num: Round number
            competitor_id: Competitor identifier
            worktree_path: Path to worktree
            files: List of file metadata
            
        Returns:
            Artifact ID
        """
        round_dir = self._get_round_dir(round_num)
        timestamp = datetime.now().isoformat()
        
        artifact = SolutionArtifact(
            competitor_id=competitor_id,
            round_num=round_num,
            timestamp=timestamp,
            worktree_path=str(worktree_path),
            files=files
        )
        
        artifact_id = f"{competitor_id}_{int(datetime.now().timestamp())}"
        artifact_file = round_dir / "solutions" / f"{artifact_id}.json"
        
        # Atomic write
        temp_file = artifact_file.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(artifact.dict(), f, indent=2)
        temp_file.rename(artifact_file)
        
        return artifact_id
    
    def store_critique(self, round_num: int, competitor_id: str,
                      target_solution_id: str, critique_text: str,
                      scores: Optional[Dict[str, int]] = None) -> str:
        """
        Store critique artifact.
        
        Args:
            round_num: Round number
            competitor_id: Competitor identifier
            target_solution_id: Target solution artifact ID
            critique_text: Critique text
            scores: Optional scoring dictionary
            
        Returns:
            Artifact ID
        """
        round_dir = self._get_round_dir(round_num)
        timestamp = datetime.now().isoformat()
        
        artifact = CritiqueArtifact(
            competitor_id=competitor_id,
            round_num=round_num,
            target_solution_id=target_solution_id,
            timestamp=timestamp,
            critique_text=critique_text,
            scores=scores or {}
        )
        
        artifact_id = f"{competitor_id}_{target_solution_id}_{int(datetime.now().timestamp())}"
        artifact_file = round_dir / "critiques" / f"{artifact_id}.json"
        
        # Atomic write
        temp_file = artifact_file.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(artifact.dict(), f, indent=2)
        temp_file.rename(artifact_file)
        
        return artifact_id
    
    def list_artifacts(self, round_num: int) -> Dict[str, List[str]]:
        """
        List all artifacts for a round.
        
        Args:
            round_num: Round number
            
        Returns:
            Dictionary with 'solutions' and 'critiques' lists
        """
        round_dir = self._get_round_dir(round_num)
        
        solutions = []
        if (round_dir / "solutions").exists():
            solutions = [f.stem for f in (round_dir / "solutions").glob("*.json")]
        
        critiques = []
        if (round_dir / "critiques").exists():
            critiques = [f.stem for f in (round_dir / "critiques").glob("*.json")]
        
        return {
            "solutions": sorted(solutions),
            "critiques": sorted(critiques)
        }
    
    def get_artifact(self, round_num: int, artifact_type: str, artifact_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an artifact.
        
        Args:
            round_num: Round number
            artifact_type: 'solutions' or 'critiques'
            artifact_id: Artifact identifier
            
        Returns:
            Artifact data if found, None otherwise
        """
        round_dir = self._get_round_dir(round_num)
        artifact_file = round_dir / artifact_type / f"{artifact_id}.json"
        
        if not artifact_file.exists():
            return None
        
        try:
            with open(artifact_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None
