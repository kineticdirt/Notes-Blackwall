"""
Research agent - specializes in research and analysis.
"""

from typing import Optional
from agent import BaseAgent


class ResearchAgent(BaseAgent):
    """
    Agent specialized in research and analysis tasks.
    """
    
    def __init__(self, agent_id: Optional[str] = None,
                 ledger_path: str = "ledger/AI_GROUPCHAT.json"):
        """Initialize research agent."""
        super().__init__(
            agent_id=agent_id,
            agent_type="research",
            ledger_path=ledger_path
        )
        self.metadata = {
            "specialization": "research_analysis",
            "capabilities": ["research", "analyze", "document", "summarize"]
        }
    
    def research_topic(self, topic: str):
        """Research a topic."""
        return self.declare_intent(
            f"Researching: {topic}",
            resources=[]
        )
    
    def analyze_codebase(self, analysis_description: str):
        """Analyze codebase."""
        return self.declare_intent(
            f"Analyzing: {analysis_description}",
            resources=[]
        )
