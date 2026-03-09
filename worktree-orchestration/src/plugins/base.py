"""
Base plugin interfaces.

All plugins inherit from base classes defined here.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class TaskSpec:
    """Task specification."""
    name: str
    description: str
    constraints: List[str]
    test_suite: str  # Path to test suite
    metadata: Dict[str, Any]


@dataclass
class ValidationResult:
    """Solution validation result."""
    valid: bool
    errors: List[str]
    warnings: List[str] = None


@dataclass
class Solution:
    """Solution representation."""
    solution_id: str
    competitor_id: str
    round_id: int
    files: List[Dict[str, Any]]  # [{path, size, hash}]
    worktree_path: Path
    metadata: Dict[str, Any] = None


@dataclass
class SolutionContext:
    """Context for solution generation."""
    round_id: int
    task_spec: TaskSpec
    existing_solutions: List[Solution]
    critiques: List[Dict[str, Any]]
    round_history: List[Dict[str, Any]]


@dataclass
class TestResults:
    """Test execution results."""
    solution_id: str
    passed: bool
    output: str
    error: str
    duration_ms: int
    exit_code: int


@dataclass
class Critique:
    """Critique representation."""
    critique_id: str
    competitor_id: str
    target_solution_id: str
    critique_text: str
    scores: Dict[str, float]


@dataclass
class Score:
    """Score representation."""
    solution_id: str
    test_score: float
    diversity_bonus: float
    critique_score: float
    total: float
    breakdown: Dict[str, float]


@dataclass
class BehaviorProfile:
    """Archetype behavior profile."""
    archetype_id: str
    risk_tolerance: float  # 0.0-1.0
    innovation_level: float  # 0.0-1.0
    convergence_avoidance: float  # 0.0-1.0
    metadata: Dict[str, Any]


@dataclass
class Strategy:
    """Competitor strategy."""
    competitor_id: str
    approach: str
    parameters: Dict[str, Any]


class TaskPlugin(ABC):
    """Plugin for defining competition tasks."""
    
    @abstractmethod
    def get_task_spec(self) -> TaskSpec:
        """Return task specification."""
        pass
    
    @abstractmethod
    def validate_solution(self, solution_path: Path) -> ValidationResult:
        """Validate solution structure."""
        pass
    
    @abstractmethod
    def get_test_command(self, solution_path: Path) -> List[str]:
        """Return test command for this task."""
        pass


class SolutionPlugin(ABC):
    """Plugin for solution generation strategies."""
    
    @abstractmethod
    async def generate_solution(
        self,
        competitor_id: str,
        round_id: int,
        task_spec: TaskSpec,
        context: SolutionContext
    ) -> Solution:
        """Generate a solution."""
        pass
    
    @abstractmethod
    def get_archetype(self) -> str:
        """Return archetype identifier."""
        pass


class ScorerPlugin(ABC):
    """Plugin for scoring solutions."""
    
    @abstractmethod
    def calculate_score(
        self,
        solution: Solution,
        test_results: TestResults,
        critiques: List[Critique]
    ) -> Score:
        """Calculate composite score."""
        pass


class ArchetypePlugin(ABC):
    """Plugin defining competitor archetype behavior."""
    
    @abstractmethod
    def get_behavior_profile(self) -> BehaviorProfile:
        """Return behavior profile."""
        pass
    
    @abstractmethod
    async def adapt_strategy(
        self,
        competitor_id: str,
        round_history: List[Dict[str, Any]],
        current_rankings: List[Dict[str, Any]]
    ) -> Strategy:
        """Adapt strategy based on history."""
        pass
