"""
Test agent - specializes in writing test cases.
"""

from typing import Optional, List
from agent import BaseAgent
from scratchpad import Scratchpad


class TestAgent(BaseAgent):
    """
    Agent specialized in writing test cases.
    """
    
    def __init__(self, agent_id: Optional[str] = None,
                 ledger_path: str = "ledger/AI_GROUPCHAT.json",
                 scratchpad_path: str = "ledger/scratchpad.json"):
        """Initialize test agent."""
        super().__init__(
            agent_id=agent_id,
            agent_type="test",
            ledger_path=ledger_path
        )
        self.scratchpad = Scratchpad(scratchpad_path)
        self.metadata = {
            "specialization": "test_writing",
            "capabilities": ["write_tests", "unit_tests", "integration_tests", "test_coverage"]
        }
    
    def analyze_for_tests(self, target_path: str) -> str:
        """
        Analyze codebase to identify what needs testing.
        
        Args:
            target_path: Path to codebase or file
            
        Returns:
            Intent ID
        """
        intent = self.declare_intent(
            f"Analyzing for test coverage: {target_path}",
            resources=[target_path]
        )
        
        self.log(f"Analyzing test coverage needs: {target_path}")
        
        # Read code notes from scratchpad (from cleanup agent)
        code_notes = self.scratchpad.read_section("code_notes")
        
        self.scratchpad.append(
            "test_notes",
            f"Test Agent: Analyzing {target_path} for test coverage. Reviewed {len(code_notes)} code notes.",
            self.agent_id,
            {"intent_id": intent, "target": target_path}
        )
        
        return intent
    
    def write_tests(self, files: List[str], test_type: str = "unit") -> str:
        """
        Write tests for specified files.
        
        Args:
            files: List of files to write tests for
            test_type: Type of tests (unit, integration, e2e)
            
        Returns:
            Intent ID
        """
        intent = self.declare_intent(
            f"Writing {test_type} tests",
            resources=files
        )
        
        self.log(f"Writing {test_type} tests for: {', '.join(files)}")
        
        # Read code notes to understand what was cleaned up
        code_notes = self.scratchpad.get_latest("code_notes", 20)
        
        self.scratchpad.append(
            "test_notes",
            f"Test Agent: Writing {test_type} tests for {len(files)} file(s). "
            f"Using context from {len(code_notes)} code notes.",
            self.agent_id,
            {"intent_id": intent, "files": files, "type": test_type}
        )
        
        return intent
    
    def report_test_summary(self, summary: str, coverage: Optional[float] = None):
        """Report test summary to scratchpad."""
        content = f"TEST SUMMARY:\n{summary}"
        if coverage is not None:
            content += f"\nCoverage: {coverage:.1f}%"
        
        self.scratchpad.append(
            "test_notes",
            content,
            self.agent_id,
            {"type": "summary", "coverage": coverage}
        )
        self.log("Test summary added to scratchpad")
    
    def report_test_issues(self, issues: List[str]):
        """Report test-related issues."""
        for issue in issues:
            self.scratchpad.append(
                "issues",
                f"Test Issue: {issue}",
                self.agent_id
            )
