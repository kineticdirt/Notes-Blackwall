"""
Autonomous agent base class.
Agents that operate independently and make their own decisions.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from datetime import datetime


class AutonomousAgent:
    """
    Base class for autonomous agents.
    Agents that operate independently with minimal supervision.
    """
    
    def __init__(self, agent_id: Optional[str] = None, agent_type: str = "autonomous"):
        """
        Initialize autonomous agent.
        
        Args:
            agent_id: Unique agent identifier
            agent_type: Type of agent
        """
        import uuid
        self.agent_id = agent_id or f"{agent_type}-{uuid.uuid4().hex[:8]}"
        self.agent_type = agent_type
        self.status = "idle"
        self.current_goals = []
        self.decision_log = []
        self.state_file = Path(f".blackwall/agents/{self.agent_id}.json")
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load previous state
        self._load_state()
    
    def _load_state(self):
        """Load agent state from disk."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    self.current_goals = state.get('goals', [])
                    self.decision_log = state.get('decisions', [])
            except:
                pass
    
    def _save_state(self):
        """Save agent state to disk."""
        state = {
            'agent_id': self.agent_id,
            'agent_type': self.agent_type,
            'status': self.status,
            'goals': self.current_goals,
            'decisions': self.decision_log[-50:],  # Keep last 50
            'timestamp': datetime.now().isoformat()
        }
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def autonomous_decision(self, context: Dict) -> Dict:
        """
        Make an autonomous decision based on context.
        
        Args:
            context: Context for decision
            
        Returns:
            Decision dictionary
        """
        # Autonomous decision-making logic
        decision = {
            'timestamp': datetime.now().isoformat(),
            'agent_id': self.agent_id,
            'context': context,
            'decision': self._make_decision(context),
            'confidence': self._calculate_confidence(context)
        }
        
        self.decision_log.append(decision)
        self._save_state()
        
        return decision
    
    def _make_decision(self, context: Dict) -> str:
        """
        Core decision-making logic.
        Override in subclasses for specific behavior.
        
        Args:
            context: Decision context
            
        Returns:
            Decision string
        """
        # Default: analyze and decide
        if 'goal' in context:
            return f"Pursuing goal: {context['goal']}"
        return "Continuing current task"
    
    def _calculate_confidence(self, context: Dict) -> float:
        """
        Calculate confidence in decision.
        
        Args:
            context: Decision context
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        # Default confidence calculation
        return 0.8  # High confidence by default
    
    def set_autonomous_goal(self, goal_description: str) -> str:
        """
        Set an autonomous goal for this agent.
        
        Args:
            goal_description: Goal to achieve
            
        Returns:
            Goal ID
        """
        import uuid
        goal_id = str(uuid.uuid4())[:12]
        
        goal = {
            'id': goal_id,
            'description': goal_description,
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'progress': 0.0
        }
        
        self.current_goals.append(goal)
        self.status = "working"
        self._save_state()
        
        # Autonomously start working on goal
        self._autonomous_work_on_goal(goal)
        
        return goal_id
    
    def _autonomous_work_on_goal(self, goal: Dict):
        """
        Autonomously work on a goal.
        Override in subclasses for specific behavior.
        
        Args:
            goal: Goal dictionary
        """
        # Default: log goal
        print(f"[{self.agent_id}] Autonomously working on: {goal['description']}")
        
        # Make autonomous decision
        decision = self.autonomous_decision({
            'goal': goal['description'],
            'action': 'start_work'
        })
        
        # Update progress
        goal['progress'] = 0.1
        self._save_state()
    
    def complete_goal(self, goal_id: str, result: Optional[Dict] = None):
        """
        Mark a goal as completed.
        
        Args:
            goal_id: Goal ID
            result: Optional result data
        """
        for goal in self.current_goals:
            if goal['id'] == goal_id:
                goal['status'] = 'completed'
                goal['completed_at'] = datetime.now().isoformat()
                goal['progress'] = 1.0
                if result:
                    goal['result'] = result
                break
        
        # Update status if no active goals
        if not any(g['status'] == 'active' for g in self.current_goals):
            self.status = "idle"
        
        self._save_state()
    
    def autonomous_adapt(self, feedback: Dict):
        """
        Autonomously adapt based on feedback.
        
        Args:
            feedback: Feedback dictionary
        """
        # Learn from feedback
        adaptation = {
            'timestamp': datetime.now().isoformat(),
            'feedback': feedback,
            'adaptation': self._determine_adaptation(feedback)
        }
        
        self.decision_log.append(adaptation)
        self._save_state()
    
    def _determine_adaptation(self, feedback: Dict) -> str:
        """
        Determine how to adapt based on feedback.
        
        Args:
            feedback: Feedback dictionary
            
        Returns:
            Adaptation description
        """
        # Default: adjust strategy
        if feedback.get('success', False):
            return "Continue current strategy"
        else:
            return "Adjust strategy based on failure"
    
    def get_autonomous_status(self) -> Dict:
        """Get autonomous agent status."""
        return {
            'agent_id': self.agent_id,
            'agent_type': self.agent_type,
            'status': self.status,
            'active_goals': len([g for g in self.current_goals if g['status'] == 'active']),
            'recent_decisions': self.decision_log[-5:],
            'autonomous': True
        }
