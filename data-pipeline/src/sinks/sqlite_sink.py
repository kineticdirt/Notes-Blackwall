import json
import sqlite3
from pathlib import Path
from dataclasses import asdict

from ..collectors.json_file import Event


class SQLiteSink:
    def __init__(self, db_path: str, table: str = "pipeline_events"):
        self.db_path = Path(db_path)
        self.table = table
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE,
                    source TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    data TEXT NOT NULL,
                    ingested_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.table}_source ON {self.table}(source)")
            conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.table}_type ON {self.table}(event_type)")

    def write(self, events: list[Event]):
        if not events:
            return
        with sqlite3.connect(str(self.db_path)) as conn:
            for event in events:
                try:
                    conn.execute(
                        f"INSERT OR IGNORE INTO {self.table} (event_id, source, event_type, timestamp, data) VALUES (?, ?, ?, ?, ?)",
                        (event.event_id, event.source, event.event_type, event.timestamp, json.dumps(event.data)),
                    )
                except sqlite3.Error:
                    continue
