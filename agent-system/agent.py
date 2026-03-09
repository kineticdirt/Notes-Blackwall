"""
Base agent class for Claude sub-agents.
"""

import uuid
from typing import Optional, Dict, List
from datetime import datetime

from ledger import AgentLedger


class BaseAgent:
    """
    Base class for all Claude sub-agents.
    Provides communication, intent declaration, and coordination.
    """
    
    def __init__(self, agent_id: Optional[str] = None, 
                 agent_type: str = "generic",
                 ledger_path: str = "ledger/AI_GROUPCHAT.json"):
        """
        Initialize agent.
        
        Args:
            agent_id: Unique agent identifier (auto-generated if None)
            agent_type: Type of agent
            ledger_path: Path to shared ledger
        """
        self.agent_id = agent_id or f"{agent_type}-{uuid.uuid4().hex[:8]}"
        self.agent_type = agent_type
        self.ledger = AgentLedger(ledger_path)
        self.status = "idle"
        self.current_intent = None
        self.metadata = {}
        
        # Register with ledger
        self.ledger.register_agent(self.agent_id, self.agent_type, self.metadata)
        self.log("Agent initialized")
    
    def log(self, message: str, message_type: str = "info"):
        """Log a message to the ledger."""
        return self.ledger.post_message(
            self.agent_id,
            message,
            message_type=message_type
        )
    
    def declare_intent(self, intent: str, resources: Optional[List[str]] = None) -> str:
        """
        Declare an intent before taking action.
        Prevents race conditions with other agents.
        
        Args:
            intent: Description of intended action
            resources: Resources that will be used
            
        Returns:
            Intent ID
        """
        self.current_intent = self.ledger.declare_intent(
            self.agent_id,
            intent,
            resources
        )
        self.status = "working"
        self.ledger.update_agent_status(self.agent_id, "working")
        return self.current_intent
    
    def complete_intent(self):
        """Mark current intent as completed."""
        if self.current_intent:
            self.ledger.complete_intent(self.current_intent, self.agent_id)
            self.current_intent = None
            self.status = "idle"
            self.ledger.update_agent_status(self.agent_id, "idle")
    
    def acquire_resource(self, resource: str, timeout: int = 30) -> bool:
        """
        Acquire a lock on a resource.
        
        Args:
            resource: Resource identifier
            timeout: Lock timeout in seconds
            
        Returns:
            True if lock acquired
        """
        acquired = self.ledger.acquire_lock(self.agent_id, resource, timeout)
        if acquired:
            self.log(f"Acquired lock on {resource}")
        else:
            self.log(f"Failed to acquire lock on {resource}", message_type="warning")
        return acquired
    
    def release_resource(self, resource: str):
        """Release a lock on a resource."""
        self.ledger.release_lock(self.agent_id, resource)
        self.log(f"Released lock on {resource}")
    
    def send_message(self, target_agent: str, message: str):
        """Send a direct message to another agent."""
        return self.ledger.post_message(
            self.agent_id,
            message,
            target_agent=target_agent,
            message_type="message"
        )
    
    def get_messages(self, since: Optional[str] = None) -> List[Dict]:
        """Get messages for this agent."""
        return self.ledger.get_messages(
            agent_id=self.agent_id,
            since=since
        )
    
    def check_for_conflicts(self) -> List[Dict]:
        """Check for conflicting intents or locks."""
        ledger_data = self.ledger._read_ledger()
        conflicts = []
        
        # Check intents
        for intent in ledger_data.get("intents", []):
            if (intent["status"] == "active" and 
                intent["agent_id"] != self.agent_id):
                conflicts.append({
                    "type": "intent",
                    "agent": intent["agent_id"],
                    "intent": intent["intent"]
                })
        
        # Check locks
        for resource, lock_info in ledger_data.get("locks", {}).items():
            if lock_info["agent_id"] != self.agent_id:
                conflicts.append({
                    "type": "lock",
                    "agent": lock_info["agent_id"],
                    "resource": resource
                })
        
        return conflicts
    
    def update_status(self, status: str):
        """Update agent status."""
        self.status = status
        self.ledger.update_agent_status(self.agent_id, status)
    
    def get_state(self) -> Dict:
        """Get current agent state."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.status,
            "current_intent": self.current_intent,
            "metadata": self.metadata
        }
    
    def cleanup(self):
        """Cleanup when agent is done."""
        if self.current_intent:
            self.complete_intent()
        self.update_status("inactive")
        self.log("Agent cleanup complete")
