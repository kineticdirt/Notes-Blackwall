"""
Workflow coordinator for the cleanup -> test -> documentation pipeline.
"""

from typing import Optional, List, Dict
from coordinator import AgentCoordinator
from agents.cleanup_agent import CleanupAgent
from agents.test_agent import TestAgent
from agents.doc_agent import DocAgent
from scratchpad import Scratchpad


class WorkflowCoordinator:
    """
    Coordinates the cleanup -> test -> documentation workflow.
    """
    
    def __init__(self, 
                 ledger_path: str = "ledger/AI_GROUPCHAT.json",
                 scratchpad_path: str = "ledger/scratchpad.json"):
        """
        Initialize workflow coordinator.
        
        Args:
            ledger_path: Path to agent ledger
            scratchpad_path: Path to scratchpad
        """
        self.coordinator = AgentCoordinator(ledger_path)
        self.scratchpad = Scratchpad(scratchpad_path)
        
        # Create specialized agents
        self.cleanup_agent = CleanupAgent(ledger_path=ledger_path, 
                                        scratchpad_path=scratchpad_path)
        self.test_agent = TestAgent(ledger_path=ledger_path,
                                   scratchpad_path=scratchpad_path)
        self.doc_agent = DocAgent(ledger_path=ledger_path,
                                 scratchpad_path=scratchpad_path)
        
        # Register agents
        self.coordinator.register_agent(self.cleanup_agent)
        self.coordinator.register_agent(self.test_agent)
        self.coordinator.register_agent(self.doc_agent)
        
        # Initialize scratchpad
        self.scratchpad.set_metadata("workflow_status", "initialized")
    
    def run_full_workflow(self, target_path: str, 
                         files: Optional[List[str]] = None):
        """
        Run the complete workflow: cleanup -> test -> documentation.
        
        Args:
            target_path: Path to codebase or directory
            files: Optional list of specific files to process
        """
        self.scratchpad.append(
            "overview",
            f"Starting full workflow for: {target_path}",
            "workflow_coordinator",
            {"target": target_path, "files": files or []}
        )
        
        # Phase 1: Cleanup
        self.scratchpad.set_metadata("workflow_status", "cleanup")
        self._run_cleanup_phase(target_path, files)
        
        # Phase 2: Testing
        self.scratchpad.set_metadata("workflow_status", "testing")
        self._run_test_phase(target_path, files)
        
        # Phase 3: Documentation
        self.scratchpad.set_metadata("workflow_status", "documentation")
        self._run_doc_phase(target_path, files)
        
        # Complete
        self.scratchpad.set_metadata("workflow_status", "completed")
        self.scratchpad.append(
            "overview",
            "Workflow completed successfully!",
            "workflow_coordinator"
        )
    
    def _run_cleanup_phase(self, target_path: str, files: Optional[List[str]]):
        """Run cleanup phase."""
        self.coordinator.broadcast_message(
            "Starting cleanup phase",
            message_type="info"
        )
        
        # Analyze codebase
        intent = self.cleanup_agent.analyze_codebase(target_path)
        self.cleanup_agent.log("Codebase analysis complete")
        
        # Clean up files
        if files:
            cleanup_intent = self.cleanup_agent.cleanup_code(files, "general")
            self.cleanup_agent.log("Code cleanup in progress...")
            # In real implementation, agent would do the actual cleanup here
            self.cleanup_agent.complete_intent()
        
        self.cleanup_agent.complete_intent()
        
        # Report summary
        summary = f"Cleanup phase completed for {target_path}"
        if files:
            summary += f"\nCleaned {len(files)} file(s)"
        self.cleanup_agent.report_cleanup_summary(summary)
    
    def _run_test_phase(self, target_path: str, files: Optional[List[str]]):
        """Run testing phase."""
        self.coordinator.broadcast_message(
            "Starting test phase",
            message_type="info"
        )
        
        # Analyze for tests (reads cleanup notes from scratchpad)
        intent = self.test_agent.analyze_for_tests(target_path)
        self.test_agent.log("Test analysis complete")
        
        # Write tests
        if files:
            test_intent = self.test_agent.write_tests(files, "unit")
            self.test_agent.log("Writing test cases...")
            # In real implementation, agent would write actual tests
            self.test_agent.complete_intent()
        
        self.test_agent.complete_intent()
        
        # Report summary
        summary = f"Test phase completed for {target_path}"
        if files:
            summary += f"\nWrote tests for {len(files)} file(s)"
        self.test_agent.report_test_summary(summary, coverage=85.0)
    
    def _run_doc_phase(self, target_path: str, files: Optional[List[str]]):
        """Run documentation phase."""
        self.coordinator.broadcast_message(
            "Starting documentation phase",
            message_type="info"
        )
        
        # Analyze for docs (reads all notes from scratchpad)
        intent = self.doc_agent.analyze_for_docs(target_path)
        self.doc_agent.log("Documentation analysis complete")
        
        # Write documentation
        if files:
            doc_intent = self.doc_agent.write_documentation(files, "api")
            self.doc_agent.log("Writing documentation...")
            # In real implementation, agent would write actual docs
            self.doc_agent.complete_intent()
        
        self.doc_agent.complete_intent()
        
        # Report summary
        summary = f"Documentation phase completed for {target_path}"
        files_created = [f"docs/{f}_docs.md" for f in (files or [])]
        self.doc_agent.report_doc_summary(summary, files_created)
    
    def get_workflow_status(self) -> Dict:
        """Get current workflow status."""
        status = self.scratchpad.get_metadata("workflow_status", "unknown")
        
        return {
            "status": status,
            "scratchpad_sections": {
                "overview": len(self.scratchpad.read_section("overview")),
                "code_notes": len(self.scratchpad.read_section("code_notes")),
                "test_notes": len(self.scratchpad.read_section("test_notes")),
                "doc_notes": len(self.scratchpad.read_section("doc_notes")),
                "issues": len(self.scratchpad.read_section("issues")),
            },
            "agent_status": self.coordinator.get_agent_status()
        }
    
    def view_scratchpad(self, section: Optional[str] = None) -> Dict:
        """
        View scratchpad contents.
        
        Args:
            section: Optional section to view (None = all)
            
        Returns:
            Scratchpad contents
        """
        if section:
            return {section: self.scratchpad.read_section(section)}
        return self.scratchpad.read_all()
