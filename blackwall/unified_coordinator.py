"""
Unified Blackwall coordinator that integrates:
- Agent system (coordination, subagents)
- Protection system (text + image)
- MCP integration (tools and resources)
- LSP integration (code intelligence)
"""

from typing import Optional, List, Dict
from pathlib import Path

# Import from agent-system
import sys
agent_system_path = Path(__file__).parent.parent / "agent-system"
if agent_system_path.exists():
    sys.path.insert(0, str(agent_system_path))
    from enhanced_workflow_coordinator import EnhancedWorkflowCoordinator
    from lsp_manager import LSPManager
else:
    EnhancedWorkflowCoordinator = None
    LSPManager = None

# Import Blackwall agents
from agents.protection_agent import ProtectionAgent
from agents.detection_agent import DetectionAgent
from agents.mcp_aware_agent import MCPAwareAgent
from core.unified_processor import UnifiedProcessor
from database.registry import BlackwallRegistry
from mcp.mcp_integration import MCPIntegration


class BlackwallCoordinator:
    """
    Unified coordinator for the entire Blackwall system.
    Integrates agents, protection, MCP, and LSP.
    """
    
    def __init__(self, project_path: str = "."):
        """
        Initialize Blackwall coordinator.
        
        Args:
            project_path: Path to project directory
        """
        self.project_path = project_path
        
        # Initialize MCP integration
        self.mcp = MCPIntegration()
        
        # Initialize LSP manager (if available)
        if LSPManager:
            self.lsp_manager = LSPManager()
            self._setup_lsp()
        else:
            self.lsp_manager = None
        
        # Initialize workflow coordinator (if available)
        if EnhancedWorkflowCoordinator:
            self.workflow_coordinator = EnhancedWorkflowCoordinator(
                project_path=project_path
            )
        else:
            self.workflow_coordinator = None
        
        # Initialize Blackwall-specific agents
        self.protection_agent = ProtectionAgent()
        self.detection_agent = DetectionAgent()
        
        # Initialize processors
        self.processor = UnifiedProcessor()
        self.registry = BlackwallRegistry()
        
        # Register agents
        if self.workflow_coordinator:
            self.workflow_coordinator.coordinator.register_agent(self.protection_agent)
            self.workflow_coordinator.coordinator.register_agent(self.detection_agent)
    
    def _setup_lsp(self):
        """Setup LSP for detected languages."""
        if not self.lsp_manager:
            return
        
        languages = self.lsp_manager.detect_project_languages(self.project_path)
        if languages:
            print(f"Detected languages: {', '.join(languages)}")
            
            # Get LSP installation commands
            commands = self.lsp_manager.get_installation_commands(languages)
            if commands:
                print("\nInstall LSP plugins in Claude Code:")
                for cmd in commands:
                    print(f"  {cmd}")
    
    def protect_content(self, content_path: str, 
                      content_type: str = "auto",
                      poison_strength: float = 0.1) -> Dict:
        """
        Protect content using Blackwall.
        
        Args:
            content_path: Path to content file
            content_type: "text", "image", or "auto"
            poison_strength: Strength of poisoning
            
        Returns:
            Protection result
        """
        return self.protection_agent.protect_content(content_path, content_type)
    
    def detect_content(self, content_path: str,
                     content_type: str = "auto") -> Dict:
        """
        Detect watermark in content.
        
        Args:
            content_path: Path to content file
            content_type: "text", "image", or "auto"
            
        Returns:
            Detection result
        """
        return self.detection_agent.detect_watermark(content_path, content_type)
    
    def run_workflow(self, target_path: str, files: Optional[List[str]] = None):
        """Run cleanup -> test -> documentation workflow."""
        if self.workflow_coordinator:
            self.workflow_coordinator.run_workflow_with_lsp(target_path, files)
        else:
            print("Workflow coordinator not available")
    
    def get_system_status(self) -> Dict:
        """Get complete system status."""
        status = {
            "mcp_tools": self.mcp.list_tools(),
            "mcp_resources": [r["name"] for r in self.mcp.list_resources()],
            "agents": {
                "protection": self.protection_agent.agent_id,
                "detection": self.detection_agent.agent_id
            }
        }
        
        if self.lsp_manager:
            languages = self.lsp_manager.detect_project_languages(self.project_path)
            status["lsp"] = {
                "detected_languages": languages,
                "available_lsps": list(self.lsp_manager.available_lsps.keys())
            }
        
        if self.workflow_coordinator:
            status["workflow"] = self.workflow_coordinator.get_workflow_status()
        
        return status
