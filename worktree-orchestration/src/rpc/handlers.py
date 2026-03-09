"""
JSON-RPC method handlers for critique arena.

Handlers integrate with event bus to emit events.
"""
import logging
from typing import Any, Dict, List, Optional

from ..core.event_bus import get_event_bus
from ..core.event_types import (
    CritiqueRequested,
    CritiqueSubmitted,
    EventType,
)

logger = logging.getLogger(__name__)


class CritiqueArenaHandlers:
    """
    JSON-RPC handlers for critique arena operations.
    
    All handlers emit events to the event bus.
    """
    
    def __init__(self):
        self.event_bus = get_event_bus()
        # In-memory storage (in production, use artifact store)
        self._solutions: Dict[int, Dict[str, Dict[str, Any]]] = {}  # round_id -> solution_id -> data
        self._critiques: Dict[str, Dict[str, Any]] = {}  # critique_id -> data
    
    async def critique_request(
        self,
        competitor_id: str,
        round_id: int,
        target_solution_id: str
    ) -> Dict[str, Any]:
        """
        Request a critique (JSON-RPC method: critique.request).
        
        Emits CritiqueRequested event.
        """
        # Emit event
        event = CritiqueRequested(
            competitor_id=competitor_id,
            round_id=round_id,
            target_solution_id=target_solution_id
        )
        await self.event_bus.emit(event)
        
        # Get target solution info
        target_solution = self._solutions.get(round_id, {}).get(target_solution_id)
        
        return {
            "critique_id": f"crit_{competitor_id}_{target_solution_id}",
            "target_solution": target_solution or {},
            "status": "requested"
        }
    
    async def critique_submit(
        self,
        competitor_id: str,
        critique_id: str,
        critique: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submit a critique (JSON-RPC method: critique.submit).
        
        Emits CritiqueSubmitted event.
        """
        # Extract data
        target_solution_id = critique.get("target_solution_id", "")
        critique_text = critique.get("text", "")
        scores = critique.get("scores", {})
        
        # Store critique
        self._critiques[critique_id] = {
            "critique_id": critique_id,
            "competitor_id": competitor_id,
            "target_solution_id": target_solution_id,
            "critique_text": critique_text,
            "scores": scores
        }
        
        # Emit event
        event = CritiqueSubmitted(
            critique_id=critique_id,
            competitor_id=competitor_id,
            target_solution_id=target_solution_id,
            critique_text=critique_text,
            scores=scores
        )
        await self.event_bus.emit(event)
        
        return {
            "critique_id": critique_id,
            "status": "submitted"
        }
    
    async def solutions_list(
        self,
        round_id: int,
        competitor_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List solutions for a round (JSON-RPC method: solutions.list).
        
        Optionally filter by competitor_id.
        """
        round_solutions = self._solutions.get(round_id, {})
        
        solutions = list(round_solutions.values())
        
        # Filter by competitor if specified
        if competitor_id:
            solutions = [
                s for s in solutions
                if s.get("competitor_id") == competitor_id
            ]
        
        return solutions
    
    async def solution_get(
        self,
        solution_id: str,
        round_id: int
    ) -> Dict[str, Any]:
        """
        Get a specific solution (JSON-RPC method: solution.get).
        """
        solution = self._solutions.get(round_id, {}).get(solution_id)
        
        if not solution:
            raise ValueError(f"Solution not found: {solution_id}")
        
        return solution
    
    def register_solution(self, round_id: int, solution_data: Dict[str, Any]):
        """Register a solution (called by solution manager)."""
        if round_id not in self._solutions:
            self._solutions[round_id] = {}
        
        solution_id = solution_data["solution_id"]
        self._solutions[round_id][solution_id] = solution_data
