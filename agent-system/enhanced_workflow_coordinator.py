"""
Enhanced workflow coordinator with LSP integration and subagent support.
"""

from typing import Optional, List, Dict
from workflow_coordinator import WorkflowCoordinator
from lsp_manager import LSPManager
from scratchpad import Scratchpad
from ledger import AgentLedger


class EnhancedWorkflowCoordinator(WorkflowCoordinator):
    """
    Enhanced coordinator with LSP checking and Claude subagent integration.
    """
    
    def __init__(self, 
                 ledger_path: str = "ledger/AI_GROUPCHAT.json",
                 scratchpad_path: str = "ledger/scratchpad.json",
                 project_path: str = "."):
        """
        Initialize enhanced coordinator.
        
        Args:
            ledger_path: Path to agent ledger
            scratchpad_path: Path to scratchpad
            project_path: Path to project directory
        """
        super().__init__(ledger_path, scratchpad_path)
        
        self.project_path = project_path
        self.lsp_manager = LSPManager()
        self.scratchpad = Scratchpad(scratchpad_path)
        
        # Check and setup LSP
        self._setup_lsp()
    
    def _setup_lsp(self):
        """Setup LSP plugins for detected languages."""
        # Detect project languages
        languages = self.lsp_manager.detect_project_languages(self.project_path)
        
        if languages:
            self.scratchpad.append(
                "overview",
                f"Detected project languages: {', '.join(languages)}",
                "enhanced_coordinator",
                {"languages": languages}
            )
            
            # Get required LSPs
            required_lsps = self.lsp_manager.get_required_lsps(languages)
            
            # Check status and log
            lsp_status = []
            for req in required_lsps:
                status = self.lsp_manager.check_lsp_status(req["language"])
                lsp_status.append(status)
                
                if status["binary_available"]:
                    self.scratchpad.append(
                        "code_notes",
                        f"LSP ready for {req['language']}: {req['binary']} found",
                        "enhanced_coordinator"
                    )
                else:
                    self.scratchpad.append(
                        "issues",
                        f"LSP binary missing for {req['language']}: {req['binary']}. "
                        f"Install: {status.get('install_command', 'N/A')}",
                        "enhanced_coordinator"
                    )
            
            # Generate installation commands
            install_commands = self.lsp_manager.get_installation_commands(languages)
            
            if install_commands:
                self.scratchpad.append(
                    "overview",
                    f"LSP Plugin Installation Commands:\n" + 
                    "\n".join(f"  {cmd}" for cmd in install_commands),
                    "enhanced_coordinator",
                    {"type": "lsp_installation"}
                )
            
            # Store LSP info in metadata
            self.scratchpad.set_metadata("detected_languages", languages)
            self.scratchpad.set_metadata("lsp_status", lsp_status)
    
    def run_workflow_with_lsp(self, target_path: str, files: Optional[List[str]] = None):
        """
        Run workflow with LSP-aware processing.
        
        Args:
            target_path: Path to codebase
            files: Optional list of files to process
        """
        # Setup LSP first
        self._setup_lsp()
        
        # Log LSP availability
        languages = self.lsp_manager.detect_project_languages(target_path)
        if languages:
            self.coordinator.broadcast_message(
                f"LSP support available for: {', '.join(languages)}",
                message_type="info"
            )
        
        # Run normal workflow
        self.run_full_workflow(target_path, files)
    
    def get_lsp_report(self) -> Dict:
        """
        Get LSP status report.
        
        Returns:
            Dictionary with LSP status information
        """
        languages = self.lsp_manager.detect_project_languages(self.project_path)
        required = self.lsp_manager.get_required_lsps(languages)
        
        report = {
            "detected_languages": languages,
            "required_lsps": required,
            "installation_commands": self.lsp_manager.get_installation_commands(languages),
            "status": {}
        }
        
        for lang in languages:
            report["status"][lang] = self.lsp_manager.check_lsp_status(lang)
        
        return report
    
    def generate_lsp_setup_guide(self) -> str:
        """
        Generate LSP setup guide.
        
        Returns:
            Setup guide as markdown string
        """
        languages = self.lsp_manager.detect_project_languages(self.project_path)
        required = self.lsp_manager.get_required_lsps(languages)
        
        guide = ["# LSP Setup Guide", ""]
        
        if not languages:
            guide.append("No programming languages detected in project.")
            return "\n".join(guide)
        
        guide.append(f"## Detected Languages: {', '.join(languages)}")
        guide.append("")
        
        guide.append("## Required LSP Plugins")
        guide.append("")
        guide.append("Install these plugins in Claude Code:")
        guide.append("")
        
        install_commands = self.lsp_manager.get_installation_commands(languages)
        for cmd in install_commands:
            guide.append(f"```")
            guide.append(cmd)
            guide.append("```")
            guide.append("")
        
        guide.append("## Language Server Binaries")
        guide.append("")
        
        for req in required:
            guide.append(f"### {req['language'].upper()}")
            guide.append(f"- **Plugin**: `{req['plugin']}`")
            guide.append(f"- **Binary**: `{req['binary']}`")
            
            if req['binary_available']:
                guide.append(f"- **Status**: ✅ Available")
            else:
                guide.append(f"- **Status**: ❌ Not found")
                install_cmd = self.lsp_manager._get_install_command(req['binary'])
                guide.append(f"- **Install**: {install_cmd}")
            
            guide.append("")
        
        return "\n".join(guide)
