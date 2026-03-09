"""
Coordinator for managing multiple Claude sub-agents.
Distributes tasks and coordinates agent activities.
"""

from typing import Dict, List, Optional
from agent import BaseAgent
from ledger import AgentLedger
from task_queue import TaskQueue


class AgentCoordinator:
    """
    Coordinates multiple agents and manages task distribution.
    """
    
    def __init__(self, ledger_path: str = "ledger/AI_GROUPCHAT.json"):
        """
        Initialize coordinator.
        
        Args:
            ledger_path: Path to shared ledger
        """
        self.ledger = AgentLedger(ledger_path)
        self.task_queue = TaskQueue(ledger_path)
        self.agents: Dict[str, BaseAgent] = {}
        self.coordinator_id = "coordinator-main"
        
        # Register coordinator
        self.ledger.register_agent(
            self.coordinator_id,
            "coordinator",
            {"role": "task_distribution"}
        )
    
    def register_agent(self, agent: BaseAgent) -> bool:
        """
        Register an agent with the coordinator.
        
        Args:
            agent: Agent instance to register
            
        Returns:
            True if registration successful
        """
        if agent.agent_id in self.agents:
            return False
        
        self.agents[agent.agent_id] = agent
        self.ledger.post_message(
            self.coordinator_id,
            f"Registered agent: {agent.agent_id} ({agent.agent_type})"
        )
        return True
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent."""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.cleanup()
            del self.agents[agent_id]
            self.ledger.post_message(
                self.coordinator_id,
                f"Unregistered agent: {agent_id}"
            )
    
    def assign_task(self, task_description: str, 
                   agent_type: Optional[str] = None,
                   priority: int = 5,
                   metadata: Optional[Dict] = None) -> str:
        """
        Assign a task to an agent.
        
        Args:
            task_description: Description of the task
            agent_type: Preferred agent type (None = any available)
            priority: Task priority (1-10, higher = more important)
            metadata: Additional task metadata
            
        Returns:
            Task ID
        """
        task_id = self.task_queue.add_task(
            task_description,
            agent_type=agent_type,
            priority=priority,
            metadata=metadata or {}
        )
        
        self.ledger.post_message(
            self.coordinator_id,
            f"Task assigned: {task_description}",
            message_type="task"
        )
        
        return task_id
    
    def get_available_agents(self, agent_type: Optional[str] = None) -> List[BaseAgent]:
        """
        Get list of available agents.
        
        Args:
            agent_type: Filter by agent type
            
        Returns:
            List of available agents
        """
        available = []
        for agent in self.agents.values():
            if agent.status == "idle":
                if agent_type is None or agent.agent_type == agent_type:
                    available.append(agent)
        return available
    
    def distribute_tasks(self):
        """Distribute pending tasks to available agents."""
        pending_tasks = self.task_queue.get_pending_tasks()
        available_agents = self.get_available_agents()
        
        for task in pending_tasks:
            # Find suitable agent
            agent = None
            
            # Try to match agent type
            if task.get("agent_type"):
                for a in available_agents:
                    if a.agent_type == task["agent_type"]:
                        agent = a
                        break
            
            # If no match, use any available agent
            if not agent and available_agents:
                agent = available_agents[0]
            
            if agent:
                # Assign task to agent
                self.task_queue.assign_task(task["id"], agent.agent_id)
                agent.log(f"Assigned task: {task['description']}", message_type="task")
                available_agents.remove(agent)
    
    def get_agent_status(self) -> Dict:
        """Get status of all agents."""
        status = {
            "total_agents": len(self.agents),
            "agents": {}
        }
        
        for agent_id, agent in self.agents.items():
            status["agents"][agent_id] = {
                "type": agent.agent_type,
                "status": agent.status,
                "current_intent": agent.current_intent
            }
        
        return status
    
    def broadcast_message(self, message: str, message_type: str = "info"):
        """Broadcast a message to all agents."""
        return self.ledger.post_message(
            self.coordinator_id,
            message,
            message_type=message_type
        )
    
    def get_coordination_summary(self) -> Dict:
        """Get summary of coordination state."""
        return {
            "agents": self.get_agent_status(),
            "pending_tasks": len(self.task_queue.get_pending_tasks()),
            "active_tasks": len(self.task_queue.get_active_tasks()),
            "completed_tasks": len(self.task_queue.get_completed_tasks())
        }
