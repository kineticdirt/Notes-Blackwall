"""
Blackwall agents - MCP-aware agents for content protection.
"""

from .mcp_aware_agent import MCPAwareAgent
from .protection_agent import ProtectionAgent
from .detection_agent import DetectionAgent

# Import workflow agents from agent-system if available
import sys
from pathlib import Path
agent_system_path = Path(__file__).parent.parent.parent / "agent-system" / "agents"
if agent_system_path.exists():
    sys.path.insert(0, str(agent_system_path.parent))
    try:
        from agents.cleanup_agent import CleanupAgent
        from agents.test_agent import TestAgent
        from agents.doc_agent import DocAgent
    except ImportError:
        CleanupAgent = None
        TestAgent = None
        DocAgent = None
else:
    CleanupAgent = None
    TestAgent = None
    DocAgent = None

__all__ = [
    'MCPAwareAgent',
    'ProtectionAgent', 
    'DetectionAgent',
    'CleanupAgent',
    'TestAgent',
    'DocAgent'
]
