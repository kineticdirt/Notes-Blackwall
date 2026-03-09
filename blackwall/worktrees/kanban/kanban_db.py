"""
Kanban Database: Database layer for UI and Task Completion tracking.
Based on whiteboard: "Resources -> Points to the nested markdown + DB for UI and Task Comp"
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from .kanban_board import KanbanCard, CardStatus


class KanbanDatabase:
    """
    Database for tracking Kanban board state, task completion, and UI data.
    Complements the markdown-based board with persistent state.
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize Kanban database.
        
        Args:
            db_path: Path to SQLite database (defaults to .kanban/kanban.db)
        """
        if db_path is None:
            db_path = Path(".kanban") / "kanban.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Boards table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS boards (
                board_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                config_json TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        # Cards table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cards (
                card_id TEXT PRIMARY KEY,
                board_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL,
                assignee TEXT,
                priority INTEGER DEFAULT 5,
                tags_json TEXT,
                created_at TEXT,
                updated_at TEXT,
                due_date TEXT,
                metadata_json TEXT,
                FOREIGN KEY (board_id) REFERENCES boards(board_id)
            )
        """)
        
        # Task completions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_completions (
                completion_id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id TEXT NOT NULL,
                board_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                status TEXT NOT NULL,
                completed_at TEXT NOT NULL,
                duration_seconds REAL,
                result_json TEXT,
                FOREIGN KEY (card_id) REFERENCES cards(card_id),
                FOREIGN KEY (board_id) REFERENCES boards(board_id)
            )
        """)
        
        # UI state table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ui_state (
                key TEXT PRIMARY KEY,
                board_id TEXT,
                value_json TEXT,
                updated_at TEXT,
                FOREIGN KEY (board_id) REFERENCES boards(board_id)
            )
        """)
        
        # Resources table (links to markdown files)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                resource_id TEXT PRIMARY KEY,
                board_id TEXT,
                card_id TEXT,
                resource_path TEXT NOT NULL,
                resource_type TEXT,
                metadata_json TEXT,
                created_at TEXT,
                FOREIGN KEY (board_id) REFERENCES boards(board_id),
                FOREIGN KEY (card_id) REFERENCES cards(card_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_board(self, board_id: str, name: str, config: Optional[Dict] = None):
        """Save board to database."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO boards
            (board_id, name, config_json, created_at, updated_at)
            VALUES (?, ?, ?, 
                    COALESCE((SELECT created_at FROM boards WHERE board_id = ?), ?),
                    ?)
        """, (board_id, name, json.dumps(config or {}), board_id, now, now))
        
        conn.commit()
        conn.close()
    
    def save_card(self, card: KanbanCard, board_id: str):
        """Save card to database."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO cards
            (card_id, board_id, title, description, status, assignee,
             priority, tags_json, created_at, updated_at, due_date, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            card.card_id, board_id, card.title, card.description,
            card.status, card.assignee, card.priority,
            json.dumps(card.tags), card.created_at, card.updated_at,
            card.due_date, json.dumps(card.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    def record_completion(self, card_id: str, board_id: str, agent_id: str,
                         status: str, duration_seconds: Optional[float] = None,
                         result: Optional[Dict] = None):
        """Record task completion."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO task_completions
            (card_id, board_id, agent_id, status, completed_at, duration_seconds, result_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            card_id, board_id, agent_id, status,
            datetime.now().isoformat(), duration_seconds,
            json.dumps(result or {})
        ))
        
        conn.commit()
        conn.close()
    
    def save_ui_state(self, key: str, value: Dict, board_id: Optional[str] = None):
        """Save UI state."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO ui_state
            (key, board_id, value_json, updated_at)
            VALUES (?, ?, ?, ?)
        """, (key, board_id, json.dumps(value), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def register_resource(self, resource_id: str, resource_path: str,
                         board_id: Optional[str] = None,
                         card_id: Optional[str] = None,
                         resource_type: Optional[str] = None,
                         metadata: Optional[Dict] = None):
        """Register a resource (markdown file)."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO resources
            (resource_id, board_id, card_id, resource_path, resource_type,
             metadata_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            resource_id, board_id, card_id, resource_path,
            resource_type, json.dumps(metadata or {}),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_resources(self, board_id: Optional[str] = None,
                     card_id: Optional[str] = None) -> List[Dict]:
        """Get resources (markdown files)."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        if card_id:
            cursor.execute("""
                SELECT resource_id, resource_path, resource_type, metadata_json
                FROM resources
                WHERE card_id = ?
            """, (card_id,))
        elif board_id:
            cursor.execute("""
                SELECT resource_id, resource_path, resource_type, metadata_json
                FROM resources
                WHERE board_id = ?
            """, (board_id,))
        else:
            cursor.execute("""
                SELECT resource_id, resource_path, resource_type, metadata_json
                FROM resources
            """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "resource_id": row[0],
                "resource_path": row[1],
                "resource_type": row[2],
                "metadata": json.loads(row[3]) if row[3] else {}
            }
            for row in rows
        ]
