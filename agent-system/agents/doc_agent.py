"""
Documentation agent - specializes in writing documentation.
"""

from typing import Optional, List
from agent import BaseAgent
from scratchpad import Scratchpad


class DocAgent(BaseAgent):
    """
    Agent specialized in writing documentation.
    """
    
    def __init__(self, agent_id: Optional[str] = None,
                 ledger_path: str = "ledger/AI_GROUPCHAT.json",
                 scratchpad_path: str = "ledger/scratchpad.json"):
        """Initialize documentation agent."""
        super().__init__(
            agent_id=agent_id,
            agent_type="documentation",
            ledger_path=ledger_path
        )
        self.scratchpad = Scratchpad(scratchpad_path)
        self.metadata = {
            "specialization": "documentation",
            "capabilities": ["write_docs", "api_docs", "readme", "guides", "comments"]
        }
    
    def analyze_for_docs(self, target_path: str) -> str:
        """
        Analyze codebase to identify documentation needs.
        
        Args:
            target_path: Path to codebase or file
            
        Returns:
            Intent ID
        """
        intent = self.declare_intent(
            f"Analyzing documentation needs: {target_path}",
            resources=[target_path]
        )
        
        self.log(f"Analyzing documentation needs: {target_path}")
        
        # Read notes from other agents
        code_notes = self.scratchpad.read_section("code_notes")
        test_notes = self.scratchpad.read_section("test_notes")
        
        self.scratchpad.append(
            "doc_notes",
            f"Doc Agent: Analyzing {target_path} for documentation. "
            f"Reviewing {len(code_notes)} code notes and {len(test_notes)} test notes.",
            self.agent_id,
            {"intent_id": intent, "target": target_path}
        )
        
        return intent
    
    def write_documentation(self, files: List[str], doc_type: str = "api") -> str:
        """
        Write documentation for specified files.
        
        Args:
            files: List of files to document
            doc_type: Type of documentation (api, readme, guide, inline)
            
        Returns:
            Intent ID
        """
        intent = self.declare_intent(
            f"Writing {doc_type} documentation",
            resources=files
        )
        
        self.log(f"Writing {doc_type} documentation for: {', '.join(files)}")
        
        # Gather context from scratchpad
        code_notes = self.scratchpad.get_latest("code_notes", 30)
        test_notes = self.scratchpad.get_latest("test_notes", 20)
        issues = self.scratchpad.get_latest("issues", 10)
        
        self.scratchpad.append(
            "doc_notes",
            f"Doc Agent: Writing {doc_type} docs for {len(files)} file(s). "
            f"Using context: {len(code_notes)} code notes, {len(test_notes)} test notes, "
            f"{len(issues)} issues.",
            self.agent_id,
            {"intent_id": intent, "files": files, "type": doc_type}
        )
        
        return intent
    
    def report_doc_summary(self, summary: str, files_created: List[str]):
        """Report documentation summary to scratchpad."""
        content = f"DOCUMENTATION SUMMARY:\n{summary}\n\nFiles Created:\n"
        content += "\n".join(f"  - {f}" for f in files_created)
        
        self.scratchpad.append(
            "doc_notes",
            content,
            self.agent_id,
            {"type": "summary", "files": files_created}
        )
        self.log("Documentation summary added to scratchpad")
    
    def create_overview(self, overview: str):
        """Create project overview in scratchpad."""
        self.scratchpad.append(
            "overview",
            f"PROJECT OVERVIEW:\n{overview}",
            self.agent_id,
            {"type": "overview"}
        )
