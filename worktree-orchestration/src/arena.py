"""
Competition arena orchestration.
"""
import subprocess
import shutil
import hashlib
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import json


class RoundState:
    """Round state enumeration."""
    PENDING = "pending"
    ACTIVE = "active"
    TESTING = "testing"
    COMPLETED = "completed"


class Arena:
    """Main competition arena orchestrator."""
    
    def __init__(self, worktree_manager, competitor_registry, artifact_store, config):
        self.worktree_manager = worktree_manager
        self.competitor_registry = competitor_registry
        self.artifact_store = artifact_store
        self.config = config
        self.round_states = {}  # round_num -> state
    
    def start_round(self, round_num: int) -> None:
        """
        Start a competition round.
        
        Args:
            round_num: Round number (1-indexed)
            
        Raises:
            ValueError: If round already active or invalid
        """
        if round_num < 1 or round_num > self.config.competition.rounds:
            raise ValueError(f"Invalid round number: {round_num}")
        
        if self.round_states.get(round_num) == RoundState.ACTIVE:
            raise ValueError(f"Round {round_num} is already active")
        
        # Create worktrees for all competitors
        competitors = self.competitor_registry.list_competitors()
        if len(competitors) > self.config.competition.max_competitors:
            raise ValueError(f"Too many competitors: {len(competitors)} > {self.config.competition.max_competitors}")
        
        for competitor in competitors:
            try:
                self.worktree_manager.create_worktree(competitor.competitor_id, round_num)
            except ValueError as e:
                # Worktree might already exist, that's okay
                pass
        
        self.round_states[round_num] = RoundState.ACTIVE
    
    def submit_solution(self, competitor_id: str, round_num: int, solution_path: Path) -> str:
        """
        Submit a solution for a competitor.
        
        Args:
            competitor_id: Competitor identifier
            round_num: Round number
            solution_path: Path to solution files
            
        Returns:
            Solution artifact ID
        """
        if self.round_states.get(round_num) != RoundState.ACTIVE:
            raise ValueError(f"Round {round_num} is not active")
        
        competitor = self.competitor_registry.get_competitor(competitor_id)
        if not competitor:
            raise ValueError(f"Competitor not found: {competitor_id}")
        
        worktree = self.worktree_manager.get_worktree(competitor_id, round_num)
        if not worktree:
            raise ValueError(f"Worktree not found for {competitor_id} in round {round_num}")
        
        # Copy solution files to worktree
        solution_dir = worktree.path / "solution"
        if solution_path.is_file():
            shutil.copy2(solution_path, solution_dir / solution_path.name)
        elif solution_path.is_dir():
            for item in solution_path.iterdir():
                dest = solution_dir / item.name
                if item.is_dir():
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
        else:
            raise ValueError(f"Solution path does not exist: {solution_path}")
        
        # Collect file metadata
        files = []
        for file_path in solution_dir.rglob("*"):
            if file_path.is_file():
                files.append({
                    "path": str(file_path.relative_to(worktree.path)),
                    "size": file_path.stat().st_size,
                    "hash": self._file_hash(file_path)
                })
        
        # Store artifact
        artifact_id = self.artifact_store.store_solution(
            round_num, competitor_id, worktree.path, files
        )
        
        return artifact_id
    
    def submit_critique(self, competitor_id: str, round_num: int,
                       target_solution_id: str, critique_path: Path) -> str:
        """
        Submit a critique.
        
        Args:
            competitor_id: Competitor identifier
            round_num: Round number
            target_solution_id: Target solution artifact ID
            critique_path: Path to critique file
            
        Returns:
            Critique artifact ID
        """
        if self.round_states.get(round_num) != RoundState.ACTIVE:
            raise ValueError(f"Round {round_num} is not active")
        
        # Read critique text
        if critique_path.is_file():
            critique_text = critique_path.read_text()
        else:
            raise ValueError(f"Critique file not found: {critique_path}")
        
        # Store artifact
        artifact_id = self.artifact_store.store_critique(
            round_num, competitor_id, target_solution_id, critique_text
        )
        
        return artifact_id
    
    def test_round(self, round_num: int) -> Dict[str, Any]:
        """
        Execute tests for all solutions in a round.
        
        Args:
            round_num: Round number
            
        Returns:
            Test results dictionary
        """
        if self.round_states.get(round_num) != RoundState.ACTIVE:
            raise ValueError(f"Round {round_num} is not active")
        
        self.round_states[round_num] = RoundState.TESTING
        
        worktrees = self.worktree_manager.list_worktrees(round_num)
        results = []
        
        for worktree in worktrees:
            result = self._execute_tests(worktree)
            results.append(result)
        
        self.round_states[round_num] = RoundState.ACTIVE
        
        return {
            "round_num": round_num,
            "test_time": datetime.now().isoformat(),
            "results": results
        }
    
    def end_round(self, round_num: int) -> Dict[str, Any]:
        """
        End a round and collect final results.
        
        Args:
            round_num: Round number
            
        Returns:
            Round results dictionary
        """
        if self.round_states.get(round_num) not in [RoundState.ACTIVE, RoundState.TESTING]:
            raise ValueError(f"Round {round_num} is not in a valid state to end")
        
        # Run final tests if not already done
        test_results = self.test_round(round_num)
        
        # Collect artifacts
        artifacts = self.artifact_store.list_artifacts(round_num)
        
        # Create results summary
        round_results = {
            "round_num": round_num,
            "start_time": datetime.now().isoformat(),  # TODO: Track actual start time
            "end_time": datetime.now().isoformat(),
            "test_results": test_results,
            "artifacts": artifacts
        }
        
        # Store results
        round_dir = self.artifact_store._get_round_dir(round_num)
        results_file = round_dir / "results.json"
        with open(results_file, 'w') as f:
            json.dump(round_results, f, indent=2)
        
        # Cleanup worktrees if configured
        if self.config.worktree.cleanup_after_round:
            self.worktree_manager.cleanup_all(round_num)
        
        self.round_states[round_num] = RoundState.COMPLETED
        
        return round_results
    
    def _execute_tests(self, worktree: 'Worktree') -> Dict[str, Any]:
        """Execute tests for a single worktree."""
        test_command = self.config.arena.test_command.split()
        timeout = self.config.arena.timeout_seconds
        
        try:
            result = subprocess.run(
                test_command,
                cwd=worktree.path,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "competitor_id": worktree.competitor_id,
                "test_passed": result.returncode == 0,
                "test_output": result.stdout,
                "test_error": result.stderr,
                "test_duration_ms": 0,  # TODO: Measure actual duration
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "competitor_id": worktree.competitor_id,
                "test_passed": False,
                "test_output": "",
                "test_error": f"Test execution exceeded timeout of {timeout}s",
                "test_duration_ms": timeout * 1000,
                "exit_code": -1
            }
        except Exception as e:
            return {
                "competitor_id": worktree.competitor_id,
                "test_passed": False,
                "test_output": "",
                "test_error": str(e),
                "test_duration_ms": 0,
                "exit_code": -1
            }
    
    def _file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
