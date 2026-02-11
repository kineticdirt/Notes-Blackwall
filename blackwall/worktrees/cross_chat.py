"""
Cross-Chat Communication System
Enables disparate Cursor chat sessions to share findings and collaborate
without formal registration or knowledge of each other.

Design Principles:
1. Discovery: Any chat can discover other chats' findings
2. Broadcasting: Chats can broadcast findings without knowing recipients
3. Verification: Chats can verify others are "listening" via heartbeat
4. Persistence: Findings persist across sessions
"""

import json
import sqlite3
import hashlib
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import threading


@dataclass
class Finding:
    """A finding or discovery from a chat session."""
    finding_id: str
    chat_session_id: str
    title: str
    content: str
    category: str = "general"  # general, code, bug, solution, research, etc.
    tags: List[str] = None
    related_files: List[str] = None
    related_code: Optional[str] = None
    confidence: float = 1.0  # 0.0 to 1.0
    created_at: str = ""
    updated_at: str = ""
    metadata: Dict = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.related_files is None:
            self.related_files = []
        if self.metadata is None:
            self.metadata = {}
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()


@dataclass
class ChatSession:
    """Represents an active or past chat session."""
    session_id: str
    session_name: Optional[str] = None
    last_seen: str = ""
    status: str = "active"  # active, idle, inactive
    findings_count: int = 0
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if not self.last_seen:
            self.last_seen = datetime.now().isoformat()


class CrossChatRegistry:
    """
    Registry for cross-chat communication.
    Provides discovery, broadcasting, and verification mechanisms.
    """
    
    def __init__(self, registry_path: Optional[Path] = None):
        """
        Initialize cross-chat registry.
        
        Args:
            registry_path: Path to registry database (defaults to .crosschat/registry.db)
        """
        if registry_path is None:
            registry_path = Path(".crosschat") / "registry.db"
        
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        conn = sqlite3.connect(str(self.registry_path))
        cursor = conn.cursor()
        
        # Chat sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                session_id TEXT PRIMARY KEY,
                session_name TEXT,
                last_seen TEXT NOT NULL,
                status TEXT NOT NULL,
                findings_count INTEGER DEFAULT 0,
                metadata_json TEXT
            )
        """)
        
        # Findings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS findings (
                finding_id TEXT PRIMARY KEY,
                chat_session_id TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                tags_json TEXT,
                related_files_json TEXT,
                related_code TEXT,
                confidence REAL DEFAULT 1.0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata_json TEXT,
                FOREIGN KEY (chat_session_id) REFERENCES chat_sessions(session_id)
            )
        """)
        
        # Heartbeats table (for verification)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS heartbeats (
                heartbeat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata_json TEXT,
                FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
            )
        """)
        
        # Subscriptions table (optional: chats can subscribe to topics)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                subscription_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_findings_session 
            ON findings(chat_session_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_findings_category 
            ON findings(category)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_findings_created 
            ON findings(created_at DESC)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_heartbeats_session 
            ON heartbeats(session_id, timestamp DESC)
        """)
        
        conn.commit()
        conn.close()
    
    def register_session(self, session_id: Optional[str] = None,
                        session_name: Optional[str] = None,
                        metadata: Optional[Dict] = None) -> str:
        """
        Register a chat session.
        
        Args:
            session_id: Unique session ID (auto-generated if None)
            session_name: Human-readable session name
            metadata: Additional metadata
            
        Returns:
            Session ID
        """
        if session_id is None:
            session_id = f"chat-{uuid.uuid4().hex[:12]}"
        
        conn = sqlite3.connect(str(self.registry_path))
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO chat_sessions
            (session_id, session_name, last_seen, status, findings_count, metadata_json)
            VALUES (?, ?, ?, 'active', 
                    COALESCE((SELECT findings_count FROM chat_sessions WHERE session_id = ?), 0),
                    ?)
        """, (session_id, session_name, now, session_id, json.dumps(metadata or {})))
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def heartbeat(self, session_id: str, metadata: Optional[Dict] = None):
        """
        Send a heartbeat to indicate this session is active.
        Other sessions can check heartbeats to verify others are "listening".
        
        Args:
            session_id: Session ID
            metadata: Optional metadata
        """
        conn = sqlite3.connect(str(self.registry_path))
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        # Update session last_seen
        cursor.execute("""
            UPDATE chat_sessions 
            SET last_seen = ?, status = 'active'
            WHERE session_id = ?
        """, (now, session_id))
        
        # Record heartbeat
        cursor.execute("""
            INSERT INTO heartbeats (session_id, timestamp, metadata_json)
            VALUES (?, ?, ?)
        """, (session_id, now, json.dumps(metadata or {})))
        
        # Clean old heartbeats (keep last 1000)
        cursor.execute("""
            DELETE FROM heartbeats 
            WHERE heartbeat_id NOT IN (
                SELECT heartbeat_id FROM heartbeats 
                ORDER BY timestamp DESC LIMIT 1000
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_active_sessions(self, max_age_minutes: int = 30) -> List[Dict]:
        """
        Get active chat sessions (those with recent heartbeats).
        
        Args:
            max_age_minutes: Maximum age of heartbeat in minutes
            
        Returns:
            List of active session info
        """
        conn = sqlite3.connect(str(self.registry_path))
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(minutes=max_age_minutes)).isoformat()
        
        cursor.execute("""
            SELECT DISTINCT s.session_id, s.session_name, s.last_seen, 
                   s.findings_count, s.metadata_json
            FROM chat_sessions s
            INNER JOIN heartbeats h ON s.session_id = h.session_id
            WHERE h.timestamp > ?
            ORDER BY h.timestamp DESC
        """, (cutoff,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "session_id": row[0],
                "session_name": row[1],
                "last_seen": row[2],
                "findings_count": row[3],
                "metadata": json.loads(row[4]) if row[4] else {}
            }
            for row in rows
        ]
    
    def publish_finding(self, finding: Finding) -> str:
        """
        Publish a finding that other chats can discover.
        
        Args:
            finding: Finding to publish
            
        Returns:
            Finding ID
        """
        conn = sqlite3.connect(str(self.registry_path))
        cursor = conn.cursor()
        
        # Ensure session exists
        cursor.execute("""
            INSERT OR IGNORE INTO chat_sessions (session_id, last_seen, status)
            VALUES (?, ?, 'active')
        """, (finding.chat_session_id, datetime.now().isoformat()))
        
        # Insert finding
        cursor.execute("""
            INSERT OR REPLACE INTO findings
            (finding_id, chat_session_id, title, content, category,
             tags_json, related_files_json, related_code, confidence,
             created_at, updated_at, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            finding.finding_id,
            finding.chat_session_id,
            finding.title,
            finding.content,
            finding.category,
            json.dumps(finding.tags),
            json.dumps(finding.related_files),
            finding.related_code,
            finding.confidence,
            finding.created_at,
            finding.updated_at,
            json.dumps(finding.metadata)
        ))
        
        # Update session findings count
        cursor.execute("""
            UPDATE chat_sessions 
            SET findings_count = findings_count + 1,
                last_seen = ?
            WHERE session_id = ?
        """, (datetime.now().isoformat(), finding.chat_session_id))
        
        conn.commit()
        conn.close()
        
        return finding.finding_id
    
    def discover_findings(self, 
                        category: Optional[str] = None,
                        tags: Optional[List[str]] = None,
                        session_id: Optional[str] = None,
                        limit: int = 50,
                        since: Optional[str] = None) -> List[Finding]:
        """
        Discover findings from other chat sessions.
        
        Args:
            category: Filter by category
            tags: Filter by tags (any match)
            session_id: Filter by session ID
            limit: Maximum number of findings
            since: ISO timestamp to get findings since
            
        Returns:
            List of findings
        """
        conn = sqlite3.connect(str(self.registry_path))
        cursor = conn.cursor()
        
        query = "SELECT * FROM findings WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if session_id:
            query += " AND chat_session_id = ?"
            params.append(session_id)
        
        if since:
            query += " AND created_at > ?"
            params.append(since)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        findings = []
        for row in rows:
            # Filter by tags if specified
            row_tags = json.loads(row[4] or "[]")
            if tags:
                if not any(tag in row_tags for tag in tags):
                    continue
            
            finding = Finding(
                finding_id=row[0],
                chat_session_id=row[1],
                title=row[2],
                content=row[3],
                category=row[4] or "general",
                tags=row_tags,
                related_files=json.loads(row[5] or "[]"),
                related_code=row[6],
                confidence=row[7] or 1.0,
                created_at=row[8],
                updated_at=row[9],
                metadata=json.loads(row[10] or "{}")
            )
            findings.append(finding)
        
        return findings
    
    def search_findings(self, query: str, limit: int = 20) -> List[Finding]:
        """
        Search findings by text content.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching findings
        """
        conn = sqlite3.connect(str(self.registry_path))
        cursor = conn.cursor()
        
        # Simple text search (SQLite FTS could be added)
        cursor.execute("""
            SELECT * FROM findings
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        findings = []
        for row in rows:
            finding = Finding(
                finding_id=row[0],
                chat_session_id=row[1],
                title=row[2],
                content=row[3],
                category=row[4] or "general",
                tags=json.loads(row[5] or "[]"),
                related_files=json.loads(row[6] or "[]"),
                related_code=row[7],
                confidence=row[8] or 1.0,
                created_at=row[9],
                updated_at=row[10],
                metadata=json.loads(row[11] or "{}")
            )
            findings.append(finding)
        
        return findings
    
    def verify_listeners(self, session_id: str) -> Dict:
        """
        Verify that other sessions are "listening" (have recent heartbeats).
        
        Args:
            session_id: Session ID to check (excludes self)
            
        Returns:
            Dict with listener count and details
        """
        active_sessions = self.get_active_sessions(max_age_minutes=30)
        
        # Exclude self
        listeners = [s for s in active_sessions if s["session_id"] != session_id]
        
        return {
            "listener_count": len(listeners),
            "listeners": listeners,
            "verified_at": datetime.now().isoformat()
        }
    
    def get_session_stats(self, session_id: str) -> Dict:
        """Get statistics for a session."""
        conn = sqlite3.connect(str(self.registry_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT session_id, session_name, last_seen, findings_count, metadata_json
            FROM chat_sessions
            WHERE session_id = ?
        """, (session_id,))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return {}
        
        cursor.execute("""
            SELECT COUNT(*) FROM findings WHERE chat_session_id = ?
        """, (session_id,))
        
        findings_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "session_id": row[0],
            "session_name": row[1],
            "last_seen": row[2],
            "findings_count": findings_count,
            "metadata": json.loads(row[4]) if row[4] else {}
        }


class CrossChatBridge:
    """
    Bridge for Cursor chat sessions to use cross-chat communication.
    Provides simple API for publishing and discovering findings.
    """
    
    def __init__(self, session_id: Optional[str] = None,
                session_name: Optional[str] = None):
        """
        Initialize cross-chat bridge.
        
        Args:
            session_id: Session ID (auto-generated if None)
            session_name: Human-readable session name
        """
        self.registry = CrossChatRegistry()
        self.session_id = self.registry.register_session(
            session_id=session_id,
            session_name=session_name
        )
        self.session_name = session_name
    
    def publish(self, title: str, content: str,
               category: str = "general",
               tags: Optional[List[str]] = None,
               related_files: Optional[List[str]] = None,
               related_code: Optional[str] = None,
               confidence: float = 1.0,
               metadata: Optional[Dict] = None) -> str:
        """
        Publish a finding that other chats can discover.
        
        Args:
            title: Finding title
            content: Finding content
            category: Category (general, code, bug, solution, etc.)
            tags: Tags for discovery
            related_files: Related file paths
            related_code: Related code snippet
            confidence: Confidence level (0.0 to 1.0)
            metadata: Additional metadata
            
        Returns:
            Finding ID
        """
        finding_id = f"finding-{uuid.uuid4().hex[:12]}"
        
        finding = Finding(
            finding_id=finding_id,
            chat_session_id=self.session_id,
            title=title,
            content=content,
            category=category,
            tags=tags or [],
            related_files=related_files or [],
            related_code=related_code,
            confidence=confidence,
            metadata=metadata or {}
        )
        
        return self.registry.publish_finding(finding)
    
    def discover(self, category: Optional[str] = None,
                tags: Optional[List[str]] = None,
                limit: int = 20) -> List[Finding]:
        """
        Discover findings from other chat sessions.
        
        Args:
            category: Filter by category
            tags: Filter by tags
            limit: Maximum results
            
        Returns:
            List of findings
        """
        return self.registry.discover_findings(
            category=category,
            tags=tags,
            limit=limit
        )
    
    def search(self, query: str, limit: int = 20) -> List[Finding]:
        """
        Search findings by text.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching findings
        """
        return self.registry.search_findings(query, limit=limit)
    
    def heartbeat(self):
        """Send heartbeat to indicate this session is active."""
        self.registry.heartbeat(self.session_id)
    
    def verify_listeners(self) -> Dict:
        """
        Verify that other sessions are "listening".
        
        Returns:
            Dict with listener count and details
        """
        return self.registry.verify_listeners(self.session_id)
    
    def get_stats(self) -> Dict:
        """Get statistics for this session."""
        return self.registry.get_session_stats(self.session_id)
