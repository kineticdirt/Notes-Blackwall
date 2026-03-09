"""
Self-coordinating agent system.
Agents that discover each other and coordinate autonomously.
"""

from typing import Dict, List, Optional
from pathlib import Path
import json
from datetime import datetime


class SelfCoordinator:
    """
    Self-coordinating system where agents discover and work together autonomously.
    """
    
    def __init__(self, coordination_file: str = ".blackwall/coordination.json"):
        """
        Initialize self-coordinator.
        
        Args:
            coordination_file: Path to coordination state file
        """
        self.coordination_file = Path(coordination_file)
        self.coordination_file.parent.mkdir(parents=True, exist_ok=True)
        self.agent_registry = {}
        self.active_coordinations = []
        self._load_state()
    
    def _load_state(self):
        """Load coordination state."""
        if self.coordination_file.exists():
            try:
                with open(self.coordination_file, 'r') as f:
                    state = json.load(f)
                    self.agent_registry = state.get('agents', {})
                    self.active_coordinations = state.get('coordinations', [])
            except:
                pass
    
    def _save_state(self):
        """Save coordination state."""
        state = {
            'agents': self.agent_registry,
            'coordinations': self.active_coordinations,
            'timestamp': datetime.now().isoformat()
        }
        with open(self.coordination_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def register_agent(self, agent_id: str, agent_type: str, 
                       capabilities: List[str], location: str = "local"):
        """
        Register an agent in the self-coordinating network.
        
        Args:
            agent_id: Agent identifier
            agent_type: Type of agent
            capabilities: List of agent capabilities
            location: Agent location
        """
        self.agent_registry[agent_id] = {
            'agent_id': agent_id,
            'agent_type': agent_type,
            'capabilities': capabilities,
            'location': location,
            'registered_at': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat(),
            'status': 'active'
        }
        
        self._save_state()
        
        # Autonomously notify other agents
        self._autonomous_discovery()
    
    def _autonomous_discovery(self):
        """Autonomously discover and connect agents."""
        # Agents discover each other through registry
        # In actual implementation, would use network discovery or shared state
        
        if len(self.agent_registry) > 1:
            print(f"[Self-Coordinator] {len(self.agent_registry)} agents discovered")
    
    def find_agents_by_capability(self, capability: str) -> List[Dict]:
        """
        Autonomously find agents with a specific capability.
        
        Args:
            capability: Capability to search for
            
        Returns:
            List of matching agents
        """
        matching = []
        for agent_id, agent_info in self.agent_registry.items():
            if capability in agent_info.get('capabilities', []):
                matching.append(agent_info)
        
        return matching
    
    def autonomous_coordinate(self, task_description: str) -> Dict:
        """
        Autonomously coordinate agents to complete a task.
        
        Args:
            task_description: Task to complete
            
        Returns:
            Coordination result
        """
        # Analyze task to determine needed capabilities
        required_capabilities = self._analyze_task_requirements(task_description)
        
        # Find agents with required capabilities
        selected_agents = []
        for capability in required_capabilities:
            agents = self.find_agents_by_capability(capability)
            if agents:
                selected_agents.append(agents[0])  # Select first available
        
        # Create coordination
        coordination_id = f"coord-{datetime.now().timestamp()}"
        coordination = {
            'id': coordination_id,
            'task': task_description,
            'agents': [a['agent_id'] for a in selected_agents],
            'status': 'active',
            'created_at': datetime.now().isoformat()
        }
        
        self.active_coordinations.append(coordination)
        self._save_state()
        
        return {
            'coordination_id': coordination_id,
            'agents': selected_agents,
            'status': 'coordinated'
        }
    
    def _analyze_task_requirements(self, task: str) -> List[str]:
        """
        Autonomously analyze task to determine required capabilities.
        
        Args:
            task: Task description
            
        Returns:
            List of required capabilities
        """
        task_lower = task.lower()
        capabilities = []
        
        if any(word in task_lower for word in ['protect', 'watermark', 'poison']):
            capabilities.append('protection')
        if any(word in task_lower for word in ['detect', 'find', 'scan']):
            capabilities.append('detection')
        if any(word in task_lower for word in ['clean', 'refactor']):
            capabilities.append('cleanup')
        if any(word in task_lower for word in ['test', 'coverage']):
            capabilities.append('testing')
        if any(word in task_lower for word in ['doc', 'documentation']):
            capabilities.append('documentation')
        
        return capabilities if capabilities else ['general']
    
    def get_coordination_status(self) -> Dict:
        """Get status of self-coordination."""
        return {
            'registered_agents': len(self.agent_registry),
            'active_coordinations': len([c for c in self.active_coordinations 
                                       if c['status'] == 'active']),
            'agents': list(self.agent_registry.values())
        }
