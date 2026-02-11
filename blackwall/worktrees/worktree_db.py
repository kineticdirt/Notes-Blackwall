"""
Worktree Database: Database layer for UI and Task Completion tracking.
Based on whiteboard: "Resources -> Points to the nested markdown + DB for UI and Task Comp"
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class TaskCompletion:
    """Represents a completed task."""
    task_id: str
    worktree_id: str
    agent_id: str
    task_description: str
    status: str  # completed, failed, cancelled
    result: Optional[Dict] = None
    started_at: str = ""
    completed_at: str = ""
    duration_seconds: float = 0.0
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class WorktreeDatabase:
    """
    Database for tracking worktree state, tasks, and UI data.
    Uses SQLite for persistence.
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize worktree database.
        
        Args:
            db_path: Path to SQLite database (defaults to .worktrees/worktree.db)
        """
        if db_path is None:
            db_path = Path(".worktrees") / "worktree.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Worktrees table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS worktrees (
                worktree_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                config_json TEXT,
                status TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        # Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                worktree_id TEXT NOT NULL,
                agent_id TEXT,
                task_description TEXT NOT NULL,
                status TEXT NOT NULL,
                priority INTEGER DEFAULT 5,
                metadata_json TEXT,
                created_at TEXT,
                started_at TEXT,
                completed_at TEXT,
                FOREIGN KEY (worktree_id) REFERENCES worktrees(worktree_id)
            )
        """)
        
        # Task completions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_completions (
                completion_id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                worktree_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                task_description TEXT NOT NULL,
                status TEXT NOT NULL,
                result_json TEXT,
                started_at TEXT,
                completed_at TEXT,
                duration_seconds REAL,
                metadata_json TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks(task_id),
                FOREIGN KEY (worktree_id) REFERENCES worktrees(worktree_id)
            )
        """)
        
        # UI state table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ui_state (
                key TEXT PRIMARY KEY,
                worktree_id TEXT,
                value_json TEXT,
                updated_at TEXT,
                FOREIGN KEY (worktree_id) REFERENCES worktrees(worktree_id)
            )
        """)
        
        # Skills registry table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skills_registry (
                skill_name TEXT PRIMARY KEY,
                skill_json TEXT NOT NULL,
                file_path TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_worktree(self, worktree_id: str, name: str, description: str,
                     config: Dict, status: str = "active"):
        """Save worktree to database."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO worktrees 
            (worktree_id, name, description, config_json, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 
                COALESCE((SELECT created_at FROM worktrees WHERE worktree_id = ?), ?),
                ?)
        """, (worktree_id, name, description, json.dumps(config), status,
              worktree_id, now, now))
        
        conn.commit()
        conn.close()
    
    def get_worktree(self, worktree_id: str) -> Optional[Dict]:
        """Get worktree from database."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT worktree_id, name, description, config_json, status, 
                   created_at, updated_at
            FROM worktrees
            WHERE worktree_id = ?
        """, (worktree_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            "worktree_id": row[0],
            "name": row[1],
            "description": row[2],
            "config": json.loads(row[3]),
            "status": row[4],
            "created_at": row[5],
            "updated_at": row[6]
        }
    
    def list_worktrees(self) -> List[Dict]:
        """List all worktrees."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT worktree_id, name, description, status, created_at, updated_at
            FROM worktrees
            ORDER BY updated_at DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "worktree_id": row[0],
                "name": row[1],
                "description": row[2],
                "status": row[3],
                "created_at": row[4],
                "updated_at": row[5]
            }
            for row in rows
        ]
    
    def save_task(self, task_id: str, worktree_id: str, task_description: str,
                 agent_id: Optional[str] = None, status: str = "pending",
                 priority: int = 5, metadata: Optional[Dict] = None):
        """Save task to database."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO tasks
            (task_id, worktree_id, agent_id, task_description, status, priority,
             metadata_json, created_at, started_at, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 
                    COALESCE((SELECT created_at FROM tasks WHERE task_id = ?), ?),
                    CASE WHEN ? = 'active' THEN ? ELSE 
                         COALESCE((SELECT started_at FROM tasks WHERE task_id = ?), NULL) END,
                    CASE WHEN ? IN ('completed', 'failed', 'cancelled') THEN ? ELSE NULL END)
        """, (task_id, worktree_id, agent_id, task_description, status, priority,
              json.dumps(metadata or {}), task_id, now,
              status, now if status == "active" else None, task_id,
              status, now if status in ("completed", "failed", "cancelled") else None))
        
        conn.commit()
        conn.close()
    
    def save_task_completion(self, completion: TaskCompletion):
        """Save task completion record."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO task_completions
            (task_id, worktree_id, agent_id, task_description, status,
             result_json, started_at, completed_at, duration_seconds, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (completion.task_id, completion.worktree_id, completion.agent_id,
              completion.task_description, completion.status,
              json.dumps(completion.result or {}),
              completion.started_at, completion.completed_at,
              completion.duration_seconds, json.dumps(completion.metadata)))
        
        conn.commit()
        conn.close()
    
    def get_task_completions(self, worktree_id: Optional[str] = None,
                           limit: int = 100) -> List[Dict]:
        """Get task completion records."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        if worktree_id:
            cursor.execute("""
                SELECT task_id, worktree_id, agent_id, task_description, status,
                       result_json, started_at, completed_at, duration_seconds, metadata_json
                FROM task_completions
                WHERE worktree_id = ?
                ORDER BY completed_at DESC
                LIMIT ?
            """, (worktree_id, limit))
        else:
            cursor.execute("""
                SELECT task_id, worktree_id, agent_id, task_description, status,
                       result_json, started_at, completed_at, duration_seconds, metadata_json
                FROM task_completions
                ORDER BY completed_at DESC
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "task_id": row[0],
                "worktree_id": row[1],
                "agent_id": row[2],
                "task_description": row[3],
                "status": row[4],
                "result": json.loads(row[5]) if row[5] else {},
                "started_at": row[6],
                "completed_at": row[7],
                "duration_seconds": row[8],
                "metadata": json.loads(row[9]) if row[9] else {}
            }
            for row in rows
        ]
    
    def save_ui_state(self, key: str, value: Dict, worktree_id: Optional[str] = None):
        """Save UI state."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO ui_state
            (key, worktree_id, value_json, updated_at)
            VALUES (?, ?, ?, ?)
        """, (key, worktree_id, json.dumps(value), now))
        
        conn.commit()
        conn.close()
    
    def get_ui_state(self, key: str) -> Optional[Dict]:
        """Get UI state."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT value_json FROM ui_state WHERE key = ?
        """, (key,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return json.loads(row[0])
    
    def register_skill(self, skill_name: str, skill_data: Dict, file_path: Optional[str] = None):
        """Register a skill in the database."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO skills_registry
            (skill_name, skill_json, file_path, created_at, updated_at)
            VALUES (?, ?, ?, 
                    COALESCE((SELECT created_at FROM skills_registry WHERE skill_name = ?), ?),
                    ?)
        """, (skill_name, json.dumps(skill_data), file_path,
              skill_name, now, now))
        
        conn.commit()
        conn.close()
    
    def get_skill(self, skill_name: str) -> Optional[Dict]:
        """Get skill from database."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT skill_json FROM skills_registry WHERE skill_name = ?
        """, (skill_name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return json.loads(row[0])
