"""
Integration of coordination system with cross-chat and worktrees.
Enables agents to coordinate, share time estimates, and handle hanging processes.
"""

from typing import Dict, Optional
from .cross_chat import CrossChatBridge, Finding
from .agent_coordination import AgentCoordinator, AgentAction, TimeEstimate
import uuid
from datetime import datetime


class CoordinatedCrossChatBridge(CrossChatBridge):
    """
    Enhanced cross-chat bridge with agent coordination.
    Adds time estimation, hanging detection, and action tracking.
    """
    
    def __init__(self, session_id: Optional[str] = None,
                session_name: Optional[str] = None,
                coordinator: Optional[AgentCoordinator] = None):
        """
        Initialize coordinated cross-chat bridge.
        
        Args:
            session_id: Session ID
            session_name: Session name
            coordinator: Agent coordinator (creates new if None)
        """
        super().__init__(session_id, session_name)
        
        if coordinator is None:
            from .agent_coordination import AgentCoordinator
            coordinator = AgentCoordinator()
        
        self.coordinator = coordinator
        
        # Register this session as an agent
        self.coordinator.register_agent(
            agent_id=self.session_id,
            timeout_seconds=300.0  # 5 minute default timeout
        )
    
    def publish_with_time_estimate(self, title: str, content: str,
                                  estimated_seconds: float,
                                  category: str = "general",
                                  tags: Optional[list] = None,
                                  **kwargs) -> str:
        """
        Publish a finding with time estimate.
        
        Args:
            title: Finding title
            content: Finding content
            estimated_seconds: Estimated time to process this finding
            category: Category
            tags: Tags
            **kwargs: Additional arguments for publish
            
        Returns:
            Finding ID
        """
        finding_id = self.publish(title, content, category=category, tags=tags, **kwargs)
        
        # Provide time estimate
        self.coordinator.provide_time_estimate(
            operation_id=finding_id,
            agent_id=self.session_id,
            estimated_seconds=estimated_seconds,
            confidence=0.7
        )
        
        return finding_id
    
    def request_time_estimate(self, operation_id: str,
                             target_session_id: Optional[str] = None) -> Optional[TimeEstimate]:
        """
        Request a time estimate for an operation.
        
        Args:
            operation_id: Operation identifier
            target_session_id: Target session (None = any session)
            
        Returns:
            TimeEstimate if available
        """
        return self.coordinator.request_time_estimate(
            operation_id=operation_id,
            agent_id=target_session_id or "any"
        )
    
    def start_operation(self, operation_description: str,
                       expected_duration_seconds: Optional[float] = None) -> str:
        """
        Start tracking an operation.
        
        Args:
            operation_description: Description of operation
            expected_duration_seconds: Expected duration
            
        Returns:
            Operation ID
        """
        operation_id = f"op-{uuid.uuid4().hex[:12]}"
        
        self.coordinator.start_action(
            action_id=operation_id,
            agent_id=self.session_id,
            action_type="operation",
            description=operation_description,
            expected_duration_seconds=expected_duration_seconds
        )
        
        return operation_id
    
    def complete_operation(self, operation_id: str, success: bool = True):
        """Mark an operation as completed."""
        self.coordinator.complete_action(operation_id, success=success)
    
    def wait_for_other_session(self, session_id: str,
                              timeout_seconds: float = 300.0) -> bool:
        """
        Wait for another session to become idle.
        
        Args:
            session_id: Session to wait for
            timeout_seconds: Maximum wait time
            
        Returns:
            True if session became idle, False if timeout
        """
        return self.coordinator.wait_for_agent(session_id, timeout_seconds)
    
    def check_hanging_sessions(self) -> list:
        """Check for hanging sessions."""
        return self.coordinator.get_hanging_agents()
    
    def send_heartbeat(self):
        """Send heartbeat to indicate this session is active."""
        super().heartbeat()  # Cross-chat heartbeat
        self.coordinator.heartbeat(self.session_id)  # Coordination heartbeat
    
    def get_coordination_status(self) -> Dict:
        """Get coordination status for this session."""
        status = self.coordinator.get_agent_status(self.session_id)
        
        # Add cross-chat info
        listeners = self.verify_listeners()
        
        return {
            **status,
            "cross_chat_listeners": listeners["listener_count"],
            "session_id": self.session_id,
            "session_name": self.session_name
        }


def create_coordinated_bridge(session_name: Optional[str] = None) -> CoordinatedCrossChatBridge:
    """
    Create a coordinated cross-chat bridge.
    
    Args:
        session_name: Session name
        
    Returns:
        CoordinatedCrossChatBridge instance
    """
    return CoordinatedCrossChatBridge(session_name=session_name)
