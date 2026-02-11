"""
Unified Worktree Manager: Integrates worktrees, skills, subagents, and database.
This is the main entry point for the worktree system.
"""

from pathlib import Path
from typing import Dict, List, Optional
import sys

# Add agent-system to path
agent_system_path = Path(__file__).parent.parent.parent / "agent-system"
if agent_system_path.exists():
    sys.path.insert(0, str(agent_system_path))
    from agent import BaseAgent
    from coordinator import AgentCoordinator
    from agents.code_agent import CodeAgent
    from agents.cleanup_agent import CleanupAgent
    from agents.test_agent import TestAgent
    from agents.doc_agent import DocAgent
    from agents.research_agent import ResearchAgent
    from agents.review_agent import ReviewAgent
else:
    BaseAgent = None
    AgentCoordinator = None
    CodeAgent = None
    CleanupAgent = None
    TestAgent = None
    DocAgent = None
    ResearchAgent = None
    ReviewAgent = None

from .worktree import Worktree, WorktreeManager, WorktreeConfig
from .worktree_db import WorktreeDatabase, TaskCompletion
from .skills.skill_loader import SkillLoader, SkillRegistry
from .skills.skill import Skill


class UnifiedWorktreeManager:
    """
    Unified manager that integrates:
    - Worktrees (agent organization)
    - Skills (nested markdown capabilities)
    - Subagents (specialized agents)
    - Database (UI and task tracking)
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize unified worktree manager.
        
        Args:
            base_path: Base path for worktrees (defaults to .worktrees)
        """
        self.base_path = base_path or Path(".worktrees")
        self.worktree_manager = WorktreeManager(base_path=self.base_path)
        self.db = WorktreeDatabase(db_path=self.base_path / "worktree.db")
        
        # Skills registry
        skills_path = Path(".skills")
        self.skill_registry = SkillRegistry(skills_path=skills_path)
        
        # Load skills into database
        self._sync_skills_to_db()
    
    def _sync_skills_to_db(self):
        """Sync skills from registry to database."""
        for skill_name, skill in self.skill_registry.skills.items():
            self.db.register_skill(skill_name, skill.to_dict(), 
                                  str(skill.file_path) if skill.file_path else None)
    
    def create_worktree(self, name: str,
                       description: str = "",
                       agent_types: Optional[List[str]] = None,
                       skills: Optional[List[str]] = None,
                       metadata: Optional[Dict] = None) -> Worktree:
        """
        Create a new worktree with skills and agents.
        
        Args:
            name: Name of the worktree
            description: Description
            agent_types: List of agent types to create
            skills: List of skill names to load
            metadata: Additional metadata
            
        Returns:
            Created Worktree instance
        """
        # Create worktree
        worktree = self.worktree_manager.create_worktree(
            name=name,
            description=description,
            agent_types=agent_types or [],
            skills=skills or [],
            metadata=metadata or {}
        )
        
        # Load skills into worktree
        if skills:
            for skill_name in skills:
                skill = self.skill_registry.get_skill(skill_name)
                if skill:
                    worktree.load_skill(skill_name, skill.to_dict())
        
        # Create subagents based on agent_types
        if agent_types:
            for agent_type in agent_types:
                agent = self._create_subagent(agent_type, worktree.worktree_id)
                if agent:
                    worktree.add_agent(agent)
        
        # Save to database
        self.db.save_worktree(
            worktree_id=worktree.worktree_id,
            name=name,
            description=description,
            config=worktree.config.__dict__,
            status=worktree.status
        )
        
        return worktree
    
    def _create_subagent(self, agent_type: str, worktree_id: str) -> Optional[BaseAgent]:
        """
        Create a subagent based on type.
        
        Args:
            agent_type: Type of agent (code, cleanup, test, doc, research, review)
            worktree_id: Worktree ID for agent context
            
        Returns:
            Agent instance or None
        """
        if not BaseAgent:
            return None
        
        agent_id = f"{agent_type}-{worktree_id[:8]}"
        
        # Map agent types to agent classes
        agent_classes = {
            "code": CodeAgent,
            "cleanup": CleanupAgent,
            "test": TestAgent,
            "doc": DocAgent,
            "research": ResearchAgent,
            "review": ReviewAgent
        }
        
        agent_class = agent_classes.get(agent_type)
        if not agent_class:
            # Fallback to BaseAgent
            return BaseAgent(agent_id=agent_id, agent_type=agent_type)
        
        try:
            return agent_class(agent_id=agent_id)
        except Exception as e:
            print(f"Warning: Failed to create {agent_type} agent: {e}")
            return BaseAgent(agent_id=agent_id, agent_type=agent_type)
    
    def assign_task_to_worktree(self, worktree_id: str, task_description: str,
                               agent_type: Optional[str] = None,
                               priority: int = 5,
                               metadata: Optional[Dict] = None) -> str:
        """
        Assign a task to a worktree.
        
        Args:
            worktree_id: ID of worktree
            task_description: Task description
            agent_type: Preferred agent type
            priority: Task priority
            metadata: Additional metadata
            
        Returns:
            Task ID
        """
        worktree = self.worktree_manager.get_worktree(worktree_id)
        if not worktree:
            raise ValueError(f"Worktree {worktree_id} not found")
        
        task_id = worktree.assign_task(
            task_description=task_description,
            agent_type=agent_type,
            priority=priority,
            metadata=metadata
        )
        
        # Save to database
        self.db.save_task(
            task_id=task_id,
            worktree_id=worktree_id,
            task_description=task_description,
            agent_id=None,
            status="pending",
            priority=priority,
            metadata=metadata
        )
        
        return task_id
    
    def complete_task(self, task_id: str, worktree_id: str, agent_id: str,
                     status: str = "completed", result: Optional[Dict] = None,
                     started_at: Optional[str] = None,
                     completed_at: Optional[str] = None):
        """
        Mark a task as completed.
        
        Args:
            task_id: Task ID
            worktree_id: Worktree ID
            agent_id: Agent that completed the task
            status: Completion status
            result: Task result
            started_at: Start timestamp
            completed_at: Completion timestamp
        """
        from datetime import datetime
        
        if not started_at:
            started_at = datetime.now().isoformat()
        if not completed_at:
            completed_at = datetime.now().isoformat()
        
        # Calculate duration
        start_dt = datetime.fromisoformat(started_at)
        end_dt = datetime.fromisoformat(completed_at)
        duration = (end_dt - start_dt).total_seconds()
        
        completion = TaskCompletion(
            task_id=task_id,
            worktree_id=worktree_id,
            agent_id=agent_id,
            task_description="",  # Will be filled from task
            status=status,
            result=result,
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=duration
        )
        
        self.db.save_task_completion(completion)
        
        # Update task status in database
        self.db.save_task(
            task_id=task_id,
            worktree_id=worktree_id,
            task_description="",
            agent_id=agent_id,
            status=status,
            metadata=result
        )
    
    def get_worktree_status(self, worktree_id: str) -> Dict:
        """Get comprehensive status of a worktree."""
        worktree = self.worktree_manager.get_worktree(worktree_id)
        if not worktree:
            return {}
        
        status = worktree.get_status()
        
        # Add database info
        db_worktree = self.db.get_worktree(worktree_id)
        if db_worktree:
            status["db_info"] = db_worktree
        
        # Add task completions
        completions = self.db.get_task_completions(worktree_id=worktree_id, limit=10)
        status["recent_completions"] = completions
        
        return status
    
    def list_all_worktrees(self) -> List[Dict]:
        """List all worktrees with their status."""
        return self.worktree_manager.list_worktrees()
    
    def get_available_skills(self) -> List[Dict]:
        """Get all available skills."""
        return self.skill_registry.list_skills()
    
    def reload_skills(self):
        """Reload skills from disk."""
        self.skill_registry.reload()
        self._sync_skills_to_db()
