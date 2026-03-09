"""
Event type definitions for the event-driven architecture.

All events inherit from base Event class and use Pydantic for validation.
"""
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Event type enumeration."""
    # Round events
    ROUND_STARTED = "round.started"
    ROUND_ENDED = "round.ended"
    ROUND_CONVERGED = "round.converged"
    
    # Solution events
    SOLUTION_SUBMITTED = "solution.submitted"
    SOLUTION_VALIDATED = "solution.validated"
    SOLUTION_REJECTED = "solution.rejected"
    SOLUTION_ACCEPTED = "solution.accepted"
    
    # Critique events
    CRITIQUE_REQUESTED = "critique.requested"
    CRITIQUE_SUBMITTED = "critique.submitted"
    CRITIQUE_EVALUATED = "critique.evaluated"
    
    # Test events
    TEST_STARTED = "test.started"
    TEST_COMPLETED = "test.completed"
    TEST_FAILED = "test.failed"
    
    # Scoring events
    SCORE_CALCULATED = "score.calculated"
    RANK_UPDATED = "rank.updated"
    CONVERGENCE_CALCULATED = "convergence.calculated"


class Event(BaseModel):
    """Base event class."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: EventType
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True


# Round Events
class RoundStarted(Event):
    """Round started event."""
    type: EventType = EventType.ROUND_STARTED
    round_id: int
    task_spec: Dict[str, Any]
    competitor_ids: List[str]


class RoundEnded(Event):
    """Round ended event."""
    type: EventType = EventType.ROUND_ENDED
    round_id: int
    results: Dict[str, Any]


class RoundConverged(Event):
    """Round converged event (solutions too similar)."""
    type: EventType = EventType.ROUND_CONVERGED
    round_id: int
    convergence_score: float
    cluster_info: Dict[str, Any]


# Solution Events
class SolutionSubmitted(Event):
    """Solution submitted event."""
    type: EventType = EventType.SOLUTION_SUBMITTED
    competitor_id: str
    round_id: int
    solution_id: str
    files: List[Dict[str, Any]]  # [{path, size, hash}]
    worktree_path: Path


class SolutionValidated(Event):
    """Solution validation completed."""
    type: EventType = EventType.SOLUTION_VALIDATED
    solution_id: str
    valid: bool
    errors: List[str] = Field(default_factory=list)


class SolutionRejected(Event):
    """Solution rejected (similarity threshold exceeded)."""
    type: EventType = EventType.SOLUTION_REJECTED
    solution_id: str
    reason: str
    similarity_to_existing: float
    similar_solution_ids: List[str] = Field(default_factory=list)


class SolutionAccepted(Event):
    """Solution accepted (passed diversity check)."""
    type: EventType = EventType.SOLUTION_ACCEPTED
    solution_id: str
    diversity_score: float
    cluster_id: Optional[str] = None


# Critique Events
class CritiqueRequested(Event):
    """Critique requested event."""
    type: EventType = EventType.CRITIQUE_REQUESTED
    competitor_id: str
    round_id: int
    target_solution_id: str


class CritiqueSubmitted(Event):
    """Critique submitted event."""
    type: EventType = EventType.CRITIQUE_SUBMITTED
    critique_id: str
    competitor_id: str
    target_solution_id: str
    critique_text: str
    scores: Dict[str, float]  # {clarity, correctness, efficiency}


class CritiqueEvaluated(Event):
    """Critique evaluation completed."""
    type: EventType = EventType.CRITIQUE_EVALUATED
    critique_id: str
    score: float


# Test Events
class TestStarted(Event):
    """Test execution started."""
    type: EventType = EventType.TEST_STARTED
    solution_id: str
    test_suite: str


class TestCompleted(Event):
    """Test execution completed."""
    type: EventType = EventType.TEST_COMPLETED
    solution_id: str
    passed: bool
    output: str
    error: str = ""
    duration_ms: int


class TestFailed(Event):
    """Test execution failed (timeout/error)."""
    type: EventType = EventType.TEST_FAILED
    solution_id: str
    error: str
    timeout: bool = False


# Scoring Events
class ScoreCalculated(Event):
    """Score calculated for a solution."""
    type: EventType = EventType.SCORE_CALCULATED
    solution_id: str
    scores: Dict[str, float]  # {test_score, diversity_bonus, critique_score, total}
    test_results: Dict[str, Any]


class RankUpdated(Event):
    """Rankings updated for a round."""
    type: EventType = EventType.RANK_UPDATED
    round_id: int
    rankings: List[Dict[str, Any]]  # [{competitor_id, solution_id, score, rank}]


class ConvergenceCalculated(Event):
    """Convergence metric calculated."""
    type: EventType = EventType.CONVERGENCE_CALCULATED
    round_id: int
    convergence_metric: float
    cluster_sizes: Dict[str, int]


# Union type for all events
OrchestrationEvent = Union[
    RoundStarted,
    RoundEnded,
    RoundConverged,
    SolutionSubmitted,
    SolutionValidated,
    SolutionRejected,
    SolutionAccepted,
    CritiqueRequested,
    CritiqueSubmitted,
    CritiqueEvaluated,
    TestStarted,
    TestCompleted,
    TestFailed,
    ScoreCalculated,
    RankUpdated,
    ConvergenceCalculated,
]
