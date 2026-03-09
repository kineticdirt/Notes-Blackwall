"""
Review agent - specializes in code review and quality assurance.
"""

from typing import Optional, List
from agent import BaseAgent


class ReviewAgent(BaseAgent):
    """
    Agent specialized in code review and QA.
    """
    
    def __init__(self, agent_id: Optional[str] = None,
                 ledger_path: str = "ledger/AI_GROUPCHAT.json"):
        """Initialize review agent."""
        super().__init__(
            agent_id=agent_id,
            agent_type="review",
            ledger_path=ledger_path
        )
        self.metadata = {
            "specialization": "code_review",
            "capabilities": ["review_code", "suggest_improvements", "check_quality"]
        }
    
    def review_code(self, review_description: str, files: List[str]):
        """Review code in specified files."""
        return self.declare_intent(
            f"Reviewing: {review_description}",
            resources=files
        )
