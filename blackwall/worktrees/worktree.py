"""
Worktree: Logical grouping of agents for organized multi-agent coordination.
Based on the whiteboard design: "Worktrees for organizing multiple agents"
"""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass, asdict, field

import sys
from pathlib import Path

# Add agent-system to path
agent_system_path = Path(__file__).parent.parent.parent / "agent-system"
if agent_system_path.exists():
    sys.path.insert(0, str(agent_system_path))
    from agent import BaseAgent
    from coordinator import AgentCoordinator
else:
    BaseAgent = None
    AgentCoordinator = None


@dataclass
class WorktreeConfig:
    """Configuration for a worktree."""
    name: str
    description: str = ""
    agent_types: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


class Worktree:
    """
    A worktree represents a logical grouping of agents.
    Worktrees provide:
    - Isolation: Agents in different worktrees don't interfere
    - Organization: Group related agents together
    - Resource management: Shared resources within a worktree
    - Skill assignment: Skills are scoped to worktrees
    """
    
    def __init__(self, worktree_id: str, config: WorktreeConfig, 
                 base_path: Optional[Path] = None):
        """
        Initialize a worktree.
        
        Args:
            worktree_id: Unique identifier for this worktree
            config: Worktree configuration
            base_path: Base path for worktree files (defaults to .worktrees/{id})
        """
        self.worktree_id = worktree_id
        self.config = config
        self.base_path = base_path or Path(".worktrees") / worktree_id
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Agent management
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_ids: Set[str] = set()
        
        # Coordinator for this worktree
        ledger_path = str(self.base_path / "ledger" / "AI_GROUPCHAT.json")
        if AgentCoordinator:
            self.coordinator = AgentCoordinator(ledger_path=ledger_path)
        else:
            self.coordinator = None
        
        # Skills registry (loaded from nested markdown)
        self.skills: Dict[str, Dict] = {}
        
        # State
        self.status = "active"
        self.created_at = config.created_at
        self.updated_at = config.updated_at
        
        # Save config
        self._save_config()
    
    def _save_config(self):
        """Save worktree configuration to disk."""
        config_path = self.base_path / "config.json"
        config_data = {
            "worktree_id": self.worktree_id,
            "config": asdict(self.config),
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def add_agent(self, agent: BaseAgent) -> bool:
        """
        Add an agent to this worktree.
        
        Args:
            agent: Agent instance to add
            
        Returns:
            True if agent was added successfully
        """
        if agent.agent_id in self.agent_ids:
            return False
        
        self.agents[agent.agent_id] = agent
        self.agent_ids.add(agent.agent_id)
        
        # Register with coordinator if available
        if self.coordinator:
            self.coordinator.register_agent(agent)
        
        self._update_timestamp()
        return True
    
    def remove_agent(self, agent_id: str) -> bool:
        """
        Remove an agent from this worktree.
        
        Args:
            agent_id: ID of agent to remove
            
        Returns:
            True if agent was removed
        """
        if agent_id not in self.agent_ids:
            return False
        
        agent = self.agents.get(agent_id)
        if agent:
            if self.coordinator:
                self.coordinator.unregister_agent(agent_id)
            agent.cleanup()
        
        del self.agents[agent_id]
        self.agent_ids.remove(agent_id)
        
        self._update_timestamp()
        return True
    
    def assign_task(self, task_description: str,
                   agent_type: Optional[str] = None,
                   priority: int = 5,
                   metadata: Optional[Dict] = None) -> str:
        """
        Assign a task within this worktree.
        
        Args:
            task_description: Description of the task
            agent_type: Preferred agent type
            priority: Task priority (1-10)
            metadata: Additional metadata
            
        Returns:
            Task ID
        """
        if not self.coordinator:
            raise RuntimeError("Coordinator not available")
        
        return self.coordinator.assign_task(
            task_description,
            agent_type=agent_type,
            priority=priority,
            metadata=metadata
        )
    
    def load_skill(self, skill_name: str, skill_data: Dict):
        """
        Load a skill into this worktree.
        Skills are defined in nested markdown files.
        
        Args:
            skill_name: Name of the skill
            skill_data: Skill definition (from markdown)
        """
        self.skills[skill_name] = skill_data
        self._update_timestamp()
    
    def get_agents_by_type(self, agent_type: str) -> List[BaseAgent]:
        """Get all agents of a specific type in this worktree."""
        return [agent for agent in self.agents.values() 
                if agent.agent_type == agent_type]
    
    def get_status(self) -> Dict:
        """Get current status of this worktree."""
        return {
            "worktree_id": self.worktree_id,
            "name": self.config.name,
            "description": self.config.description,
            "status": self.status,
            "agent_count": len(self.agents),
            "agents": list(self.agent_ids),
            "skills": list(self.skills.keys()),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def _update_timestamp(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now().isoformat()
        self.config.updated_at = self.updated_at
        self._save_config()
    
    def cleanup(self):
        """Cleanup worktree resources."""
        for agent in self.agents.values():
            agent.cleanup()
        
        if self.coordinator:
            # Coordinator cleanup handled by agents
            pass
        
        self.status = "inactive"
        self._save_config()


class WorktreeManager:
    """
    Manages multiple worktrees.
    Provides operations for creating, listing, and managing worktrees.
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize worktree manager.
        
        Args:
            base_path: Base path for all worktrees (defaults to .worktrees)
        """
        self.base_path = base_path or Path(".worktrees")
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.worktrees: Dict[str, Worktree] = {}
        self._load_existing_worktrees()
    
    def _load_existing_worktrees(self):
        """Load existing worktrees from disk."""
        if not self.base_path.exists():
            return
        
        for worktree_dir in self.base_path.iterdir():
            if not worktree_dir.is_dir():
                continue
            
            config_path = worktree_dir / "config.json"
            if not config_path.exists():
                continue
            
            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                
                worktree_id = config_data.get("worktree_id")
                config_dict = config_data.get("config", {})
                config = WorktreeConfig(**config_dict)
                
                worktree = Worktree(worktree_id, config, base_path=worktree_dir)
                self.worktrees[worktree_id] = worktree
            except Exception as e:
                print(f"Warning: Failed to load worktree {worktree_dir}: {e}")
    
    def create_worktree(self, name: str,
                       description: str = "",
                       agent_types: Optional[List[str]] = None,
                       skills: Optional[List[str]] = None,
                       metadata: Optional[Dict] = None) -> Worktree:
        """
        Create a new worktree.
        
        Args:
            name: Name of the worktree
            description: Description of the worktree
            agent_types: List of agent types this worktree will contain
            skills: List of skill names to load
            metadata: Additional metadata
            
        Returns:
            Created Worktree instance
        """
        worktree_id = f"wt-{uuid.uuid4().hex[:12]}"
        
        config = WorktreeConfig(
            name=name,
            description=description,
            agent_types=agent_types or [],
            skills=skills or [],
            metadata=metadata or {}
        )
        
        worktree = Worktree(worktree_id, config)
        self.worktrees[worktree_id] = worktree
        
        return worktree
    
    def get_worktree(self, worktree_id: str) -> Optional[Worktree]:
        """Get a worktree by ID."""
        return self.worktrees.get(worktree_id)
    
    def list_worktrees(self) -> List[Dict]:
        """List all worktrees with their status."""
        return [wt.get_status() for wt in self.worktrees.values()]
    
    def delete_worktree(self, worktree_id: str) -> bool:
        """
        Delete a worktree.
        
        Args:
            worktree_id: ID of worktree to delete
            
        Returns:
            True if deleted successfully
        """
        if worktree_id not in self.worktrees:
            return False
        
        worktree = self.worktrees[worktree_id]
        worktree.cleanup()
        
        # Optionally remove directory
        # import shutil
        # shutil.rmtree(worktree.base_path)
        
        del self.worktrees[worktree_id]
        return True
    
    def find_worktree_by_name(self, name: str) -> Optional[Worktree]:
        """Find a worktree by name."""
        for worktree in self.worktrees.values():
            if worktree.config.name == name:
                return worktree
        return None
