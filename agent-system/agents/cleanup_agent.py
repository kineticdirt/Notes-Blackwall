"""
Cleanup agent - specializes in code cleanup and refactoring.
"""

from typing import Optional, List
from agent import BaseAgent
from scratchpad import Scratchpad


class CleanupAgent(BaseAgent):
    """
    Agent specialized in code cleanup and refactoring.
    """
    
    def __init__(self, agent_id: Optional[str] = None,
                 ledger_path: str = "ledger/AI_GROUPCHAT.json",
                 scratchpad_path: str = "ledger/scratchpad.json"):
        """Initialize cleanup agent."""
        super().__init__(
            agent_id=agent_id,
            agent_type="cleanup",
            ledger_path=ledger_path
        )
        self.scratchpad = Scratchpad(scratchpad_path)
        self.metadata = {
            "specialization": "code_cleanup",
            "capabilities": ["cleanup", "refactor", "format", "lint", "optimize"]
        }
    
    def analyze_codebase(self, target_path: str) -> str:
        """
        Analyze codebase for cleanup opportunities.
        
        Args:
            target_path: Path to codebase or file
            
        Returns:
            Intent ID
        """
        intent = self.declare_intent(
            f"Analyzing codebase for cleanup: {target_path}",
            resources=[target_path]
        )
        
        self.log(f"Starting codebase analysis: {target_path}")
        
        # Append findings to scratchpad
        self.scratchpad.append(
            "code_notes",
            f"Cleanup Agent: Analyzing {target_path} for cleanup opportunities",
            self.agent_id,
            {"intent_id": intent, "target": target_path}
        )
        
        return intent
    
    def cleanup_code(self, files: List[str], cleanup_type: str = "general"):
        """
        Clean up code in specified files.
        
        Args:
            files: List of files to clean up
            cleanup_type: Type of cleanup (general, format, lint, optimize)
            
        Returns:
            Intent ID
        """
        intent = self.declare_intent(
            f"Cleaning up code: {cleanup_type}",
            resources=files
        )
        
        self.log(f"Starting cleanup ({cleanup_type}): {', '.join(files)}")
        
        # Append to scratchpad
        self.scratchpad.append(
            "code_notes",
            f"Cleanup Agent: Cleaning up {len(files)} file(s) - Type: {cleanup_type}",
            self.agent_id,
            {"intent_id": intent, "files": files, "type": cleanup_type}
        )
        
        return intent
    
    def report_cleanup_summary(self, summary: str):
        """Report cleanup summary to scratchpad."""
        self.scratchpad.append(
            "code_notes",
            f"CLEANUP SUMMARY:\n{summary}",
            self.agent_id,
            {"type": "summary"}
        )
        self.log("Cleanup summary added to scratchpad")
    
    def report_issues(self, issues: List[str]):
        """Report issues found during cleanup."""
        for issue in issues:
            self.scratchpad.append(
                "issues",
                f"Cleanup Issue: {issue}",
                self.agent_id
            )
