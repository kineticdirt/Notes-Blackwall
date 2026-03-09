"""
Code agent - specializes in writing and modifying code.
"""

from typing import Optional, List
from agent import BaseAgent


class CodeAgent(BaseAgent):
    """
    Agent specialized in code implementation and modification.
    """
    
    def __init__(self, agent_id: Optional[str] = None,
                 ledger_path: str = "ledger/AI_GROUPCHAT.json"):
        """Initialize code agent."""
        super().__init__(
            agent_id=agent_id,
            agent_type="code",
            ledger_path=ledger_path
        )
        self.metadata = {
            "specialization": "code_implementation",
            "capabilities": ["write_code", "modify_code", "refactor", "debug"]
        }
    
    def implement_feature(self, feature_description: str, 
                         files: Optional[List[str]] = None):
        """
        Implement a feature.
        
        Args:
            feature_description: Description of feature to implement
            files: Files that will be modified
        """
        intent = self.declare_intent(
            f"Implementing: {feature_description}",
            resources=files or []
        )
        
        self.log(f"Starting implementation: {feature_description}")
        
        # Check for conflicts
        conflicts = self.check_for_conflicts()
        if conflicts:
            self.log(f"Conflicts detected: {conflicts}", message_type="warning")
        
        return intent
    
    def refactor_code(self, refactor_description: str, files: List[str]):
        """Refactor code in specified files."""
        return self.declare_intent(
            f"Refactoring: {refactor_description}",
            resources=files
        )
