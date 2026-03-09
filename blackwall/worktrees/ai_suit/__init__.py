"""
AI Suit: Plug-and-Play AI Capability Extension System
Combines MCP Toolbox + MCP Servers into a unified "super robotic suit"
that fundamentally extends user abilities.

Think of it as: User → AI Suit → Extended Capabilities
"""

from .ai_suit_core import AISuit, Capability, CapabilityRegistry
from .mcp_jam import MCPJam, MCPServerConnector
from .toolbox_bridge import ToolboxBridge

__all__ = [
    'AISuit',
    'Capability',
    'CapabilityRegistry',
    'MCPJam',
    'MCPServerConnector',
    'ToolboxBridge'
]
