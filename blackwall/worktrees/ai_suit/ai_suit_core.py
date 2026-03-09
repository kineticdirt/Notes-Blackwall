"""
AI Suit Core: The plug-and-play capability extension system.
Acts like a "super robotic suit" that extends user abilities.
"""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class CapabilityType(Enum):
    """Types of capabilities."""
    TOOL = "tool"  # MCP tool
    RESOURCE = "resource"  # MCP resource
    DATABASE = "database"  # Database query via Toolbox
    WORKFLOW = "workflow"  # Workflow execution
    AGENT = "agent"  # Agent coordination
    SKILL = "skill"  # Skill definition


@dataclass
class Capability:
    """
    A capability that extends user abilities.
    Can be a tool, resource, database query, workflow, etc.
    """
    capability_id: str
    name: str
    capability_type: CapabilityType
    description: str
    enabled: bool = True
    metadata: Dict = field(default_factory=dict)
    handler: Optional[Callable] = None
    dependencies: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        if not self.capability_id:
            self.capability_id = f"cap-{uuid.uuid4().hex[:12]}"
    
    def execute(self, **kwargs) -> Any:
        """Execute this capability."""
        if not self.enabled:
            raise RuntimeError(f"Capability {self.name} is disabled")
        
        if not self.handler:
            raise RuntimeError(f"Capability {self.name} has no handler")
        
        return self.handler(**kwargs)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "capability_id": self.capability_id,
            "name": self.name,
            "type": self.capability_type.value,
            "description": self.description,
            "enabled": self.enabled,
            "metadata": self.metadata,
            "dependencies": self.dependencies,
            "created_at": self.created_at
        }


class CapabilityRegistry:
    """
    Registry for managing capabilities.
    Acts as the "suit" that holds all extensions.
    """
    
    def __init__(self):
        """Initialize capability registry."""
        self.capabilities: Dict[str, Capability] = {}
        self.capabilities_by_type: Dict[CapabilityType, List[Capability]] = {
            cap_type: [] for cap_type in CapabilityType
        }
    
    def register(self, capability: Capability):
        """Register a capability."""
        self.capabilities[capability.capability_id] = capability
        self.capabilities_by_type[capability.capability_type].append(capability)
    
    def get(self, capability_id: str) -> Optional[Capability]:
        """Get capability by ID."""
        return self.capabilities.get(capability_id)
    
    def get_by_name(self, name: str) -> Optional[Capability]:
        """Get capability by name."""
        for cap in self.capabilities.values():
            if cap.name == name:
                return cap
        return None
    
    def list_enabled(self, capability_type: Optional[CapabilityType] = None) -> List[Capability]:
        """List enabled capabilities."""
        if capability_type:
            return [c for c in self.capabilities_by_type[capability_type] if c.enabled]
        return [c for c in self.capabilities.values() if c.enabled]
    
    def enable(self, capability_id: str):
        """Enable a capability."""
        cap = self.get(capability_id)
        if cap:
            cap.enabled = True
    
    def disable(self, capability_id: str):
        """Disable a capability."""
        cap = self.get(capability_id)
        if cap:
            cap.enabled = False


class AISuit:
    """
    AI Suit: Plug-and-play capability extension system.
    
    Acts like a "super robotic suit" that extends user abilities:
    - User asks for something
    - AI Suit routes to appropriate capability
    - Capability executes
    - Result returned to user
    
    Capabilities can be:
    - MCP Tools (file operations, API calls, etc.)
    - Database queries (via MCP Toolbox)
    - Workflows (Airflow-style)
    - Agents (coordination)
    - Resources (data access)
    """
    
    def __init__(self, suit_id: Optional[str] = None):
        """
        Initialize AI Suit.
        
        Args:
            suit_id: Unique suit identifier
        """
        self.suit_id = suit_id or f"suit-{uuid.uuid4().hex[:12]}"
        self.registry = CapabilityRegistry()
        self.active_capabilities: Dict[str, Any] = {}
        
        # Component integrations
        self.mcp_jam: Optional['MCPJam'] = None
        self.toolbox_bridge: Optional['ToolboxBridge'] = None
        
        # State
        self.enabled = True
        self.created_at = datetime.now().isoformat()
    
    def plug_in(self, capability: Capability):
        """
        Plug in a capability (add to suit).
        
        Args:
            capability: Capability to add
        """
        self.registry.register(capability)
        print(f"✓ Plugged in: {capability.name} ({capability.capability_type.value})")
    
    def unplug(self, capability_id: str):
        """
        Unplug a capability (remove from suit).
        
        Args:
            capability_id: Capability ID to remove
        """
        capability = self.registry.get(capability_id)
        if capability:
            self.registry.disable(capability_id)
            print(f"✓ Unplugged: {capability.name}")
    
    def use(self, capability_name: str, **kwargs) -> Any:
        """
        Use a capability (execute it).
        
        Args:
            capability_name: Name of capability to use
            **kwargs: Arguments for capability
            
        Returns:
            Result of capability execution
        """
        capability = self.registry.get_by_name(capability_name)
        if not capability:
            raise ValueError(f"Capability '{capability_name}' not found")
        
        if not capability.enabled:
            raise RuntimeError(f"Capability '{capability_name}' is disabled")
        
        return capability.execute(**kwargs)
    
    def discover_capabilities(self, query: Optional[str] = None) -> List[Capability]:
        """
        Discover available capabilities.
        
        Args:
            query: Optional search query
            
        Returns:
            List of matching capabilities
        """
        if query:
            # Simple search
            query_lower = query.lower()
            return [
                cap for cap in self.registry.capabilities.values()
                if query_lower in cap.name.lower() or query_lower in cap.description.lower()
            ]
        
        return list(self.registry.capabilities.values())
    
    def get_suit_status(self) -> Dict:
        """Get status of the AI Suit."""
        return {
            "suit_id": self.suit_id,
            "enabled": self.enabled,
            "total_capabilities": len(self.registry.capabilities),
            "enabled_capabilities": len(self.registry.list_enabled()),
            "capabilities_by_type": {
                cap_type.value: len(caps)
                for cap_type, caps in self.registry.capabilities_by_type.items()
            },
            "mcp_jam_connected": self.mcp_jam is not None,
            "toolbox_connected": self.toolbox_bridge is not None
        }
    
    def extend_ability(self, ability_name: str, handler: Callable, 
                      description: str = "", capability_type: CapabilityType = CapabilityType.TOOL):
        """
        Extend user ability by adding a new capability.
        
        Args:
            ability_name: Name of the ability
            handler: Function that implements the ability
            description: Description of the ability
            capability_type: Type of capability
        """
        capability = Capability(
            capability_id=f"cap-{uuid.uuid4().hex[:12]}",
            name=ability_name,
            capability_type=capability_type,
            description=description,
            handler=handler
        )
        
        self.plug_in(capability)
        return capability.capability_id
