"""
Task queue for agent coordination.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import hashlib
import threading


class TaskQueue:
    """
    Manages task queue for agent coordination.
    """
    
    def __init__(self, ledger_path: str = "ledger/AI_GROUPCHAT.json"):
        """
        Initialize task queue.
        
        Args:
            ledger_path: Path to ledger (tasks stored in ledger)
        """
        self.ledger_path = Path(ledger_path)
        self.lock = threading.Lock()
    
    def _read_ledger(self) -> Dict:
        """Read ledger."""
        with self.lock:
            try:
                with open(self.ledger_path, 'r') as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                return {"tasks": []}
    
    def _write_ledger(self, data: Dict):
        """Write ledger."""
        with self.lock:
            temp_path = self.ledger_path.with_suffix('.tmp')
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2)
            temp_path.replace(self.ledger_path)
    
    def add_task(self, description: str,
                agent_type: Optional[str] = None,
                priority: int = 5,
                metadata: Optional[Dict] = None) -> str:
        """
        Add a task to the queue.
        
        Args:
            description: Task description
            agent_type: Preferred agent type
            priority: Task priority (1-10)
            metadata: Additional metadata
            
        Returns:
            Task ID
        """
        ledger = self._read_ledger()
        
        if "tasks" not in ledger:
            ledger["tasks"] = []
        
        task_id = hashlib.md5(
            f"{description}{time.time()}".encode()
        ).hexdigest()[:12]
        
        task = {
            "id": task_id,
            "description": description,
            "agent_type": agent_type,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "assigned_to": None,
            "metadata": metadata or {}
        }
        
        ledger["tasks"].append(task)
        
        # Sort by priority
        ledger["tasks"].sort(key=lambda x: x.get("priority", 5), reverse=True)
        
        self._write_ledger(ledger)
        return task_id
    
    def assign_task(self, task_id: str, agent_id: str):
        """Assign a task to an agent."""
        ledger = self._read_ledger()
        
        for task in ledger.get("tasks", []):
            if task["id"] == task_id:
                task["status"] = "active"
                task["assigned_to"] = agent_id
                task["assigned_at"] = datetime.now().isoformat()
                break
        
        self._write_ledger(ledger)
    
    def complete_task(self, task_id: str, result: Optional[Dict] = None):
        """Mark a task as completed."""
        ledger = self._read_ledger()
        
        for task in ledger.get("tasks", []):
            if task["id"] == task_id:
                task["status"] = "completed"
                task["completed_at"] = datetime.now().isoformat()
                if result:
                    task["result"] = result
                break
        
        self._write_ledger(ledger)
    
    def get_pending_tasks(self) -> List[Dict]:
        """Get all pending tasks."""
        ledger = self._read_ledger()
        return [t for t in ledger.get("tasks", []) if t.get("status") == "pending"]
    
    def get_active_tasks(self) -> List[Dict]:
        """Get all active tasks."""
        ledger = self._read_ledger()
        return [t for t in ledger.get("tasks", []) if t.get("status") == "active"]
    
    def get_completed_tasks(self) -> List[Dict]:
        """Get all completed tasks."""
        ledger = self._read_ledger()
        return [t for t in ledger.get("tasks", []) if t.get("status") == "completed"]
