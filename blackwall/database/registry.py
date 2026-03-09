"""
Extended registry for both text and image content.
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict
from pathlib import Path


class BlackwallRegistry:
    """
    Registry for tracking both text and image content.
    Extends the nightshade-tracker registry.
    """
    
    def __init__(self, db_path: str = "blackwall_registry.db"):
        """
        Initialize registry.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create content registry table (text + images)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_path TEXT NOT NULL,
                processed_path TEXT,
                content_type TEXT NOT NULL,
                uuid TEXT NOT NULL UNIQUE,
                phash TEXT,
                file_size INTEGER,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create index
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_uuid ON content(uuid)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_type ON content(content_type)')
        
        # Create detections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id INTEGER,
                detected_uuid TEXT,
                source_path TEXT,
                source_type TEXT,
                confidence REAL,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (content_id) REFERENCES content(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_content(self, original_path: str, uuid: str,
                        content_type: str,
                        processed_path: Optional[str] = None,
                        phash: Optional[str] = None,
                        file_size: Optional[int] = None,
                        metadata: Optional[Dict] = None):
        """
        Register content in database.
        
        Args:
            original_path: Original file path
            uuid: UUID embedded in content
            content_type: "text" or "image"
            processed_path: Processed file path
            phash: Perceptual hash (for images)
            file_size: File size in bytes
            metadata: Additional metadata
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute('''
            INSERT INTO content (
                original_path, processed_path, content_type,
                uuid, phash, file_size, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (original_path, processed_path, content_type,
              uuid, phash, file_size, metadata_json))
        
        content_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return content_id
    
    def lookup_by_uuid(self, uuid: str) -> Optional[Dict]:
        """Look up content by UUID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM content WHERE uuid = ?', (uuid,))
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return None
        
        columns = [desc[0] for desc in cursor.description]
        result = dict(zip(columns, row))
        
        if result.get('metadata'):
            result['metadata'] = json.loads(result['metadata'])
        
        return result
