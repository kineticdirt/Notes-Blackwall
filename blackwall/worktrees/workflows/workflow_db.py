"""
Workflow Database: Database for workflow execution tracking.
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import json


class WorkflowDatabase:
    """Database for tracking workflow executions."""
    
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = Path(".workflows") / "workflows.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflow_executions (
                execution_id TEXT PRIMARY KEY,
                dag_id TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                metadata_json TEXT
            )
        """)
        
        conn.commit()
        conn.close()
