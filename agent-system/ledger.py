"""
Communication ledger for Claude sub-agents (AI_GROUPCHAT).
Prevents race conditions by providing a shared state and communication channel.
"""

import json
import os
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import hashlib


class AgentLedger:
    """
    Shared ledger for agent communication and coordination.
    Uses file-based locking to prevent race conditions.
    """
    
    def __init__(self, ledger_path: str = "ledger/AI_GROUPCHAT.json"):
        """
        Initialize the ledger.
        
        Args:
            ledger_path: Path to the ledger JSON file
        """
        self.ledger_path = Path(ledger_path)
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self._ensure_ledger_exists()
    
    def _ensure_ledger_exists(self):
        """Create ledger file if it doesn't exist."""
        if not self.ledger_path.exists():
            initial_data = {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "agents": {},
                "messages": [],
                "tasks": [],
                "locks": {},
                "state": {}
            }
            self._write_ledger(initial_data)
    
    def _read_ledger(self) -> Dict:
        """Read ledger with locking."""
        with self.lock:
            try:
                with open(self.ledger_path, 'r') as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                # Return default structure if file is corrupted
                return {
                    "version": "1.0",
                    "created_at": datetime.now().isoformat(),
                    "agents": {},
                    "messages": [],
                    "tasks": [],
                    "locks": {},
                    "state": {}
                }
    
    def _write_ledger(self, data: Dict):
        """Write ledger with locking."""
        with self.lock:
            # Atomic write: write to temp file, then rename
            temp_path = self.ledger_path.with_suffix('.tmp')
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2)
            temp_path.replace(self.ledger_path)
    
    def register_agent(self, agent_id: str, agent_type: str, 
                       metadata: Optional[Dict] = None) -> bool:
        """
        Register an agent in the ledger.
        
        Args:
            agent_id: Unique agent identifier
            agent_type: Type of agent (code, research, review, etc.)
            metadata: Additional agent metadata
            
        Returns:
            True if registration successful
        """
        ledger = self._read_ledger()
        
        if agent_id in ledger["agents"]:
            return False  # Agent already registered
        
        ledger["agents"][agent_id] = {
            "agent_id": agent_id,
            "agent_type": agent_type,
            "registered_at": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "status": "active",
            "metadata": metadata or {}
        }
        
        self._write_ledger(ledger)
        self.post_message(agent_id, f"Agent {agent_id} ({agent_type}) registered")
        return True
    
    def update_agent_status(self, agent_id: str, status: str):
        """Update agent status (active, idle, working, error)."""
        ledger = self._read_ledger()
        
        if agent_id in ledger["agents"]:
            ledger["agents"][agent_id]["status"] = status
            ledger["agents"][agent_id]["last_seen"] = datetime.now().isoformat()
            self._write_ledger(ledger)
    
    def post_message(self, agent_id: str, message: str, 
                    message_type: str = "info",
                    target_agent: Optional[str] = None) -> str:
        """
        Post a message to the ledger.
        
        Args:
            agent_id: Agent posting the message
            message: Message content
            message_type: Type of message (info, intent, task, error, warning)
            target_agent: Optional target agent ID for direct messages
            
        Returns:
            Message ID
        """
        ledger = self._read_ledger()
        
        message_id = hashlib.md5(
            f"{agent_id}{message}{time.time()}".encode()
        ).hexdigest()[:12]
        
        message_entry = {
            "id": message_id,
            "agent_id": agent_id,
            "target_agent": target_agent,
            "message": message,
            "type": message_type,
            "timestamp": datetime.now().isoformat()
        }
        
        ledger["messages"].append(message_entry)
        
        # Keep only last 1000 messages
        if len(ledger["messages"]) > 1000:
            ledger["messages"] = ledger["messages"][-1000:]
        
        self._write_ledger(ledger)
        return message_id
    
    def declare_intent(self, agent_id: str, intent: str, 
                      resources: Optional[List[str]] = None) -> str:
        """
        Declare an intent to prevent race conditions.
        
        Args:
            agent_id: Agent declaring intent
            intent: Description of intended action
            resources: List of resources that will be used
            
        Returns:
            Intent ID
        """
        ledger = self._read_ledger()
        
        intent_id = hashlib.md5(
            f"{agent_id}{intent}{time.time()}".encode()
        ).hexdigest()[:12]
        
        intent_entry = {
            "id": intent_id,
            "agent_id": agent_id,
            "intent": intent,
            "resources": resources or [],
            "status": "declared",
            "timestamp": datetime.now().isoformat()
        }
        
        # Check for conflicts
        conflicts = []
        for existing_intent in ledger.get("intents", []):
            if existing_intent["status"] == "active":
                # Check resource overlap
                if resources and existing_intent.get("resources"):
                    overlap = set(resources) & set(existing_intent["resources"])
                    if overlap:
                        conflicts.append(existing_intent)
        
        if conflicts:
            self.post_message(
                agent_id,
                f"Intent conflicts detected: {[c['id'] for c in conflicts]}",
                message_type="warning"
            )
        
        if "intents" not in ledger:
            ledger["intents"] = []
        ledger["intents"].append(intent_entry)
        
        self._write_ledger(ledger)
        self.post_message(
            agent_id,
            f"Declared intent: {intent}",
            message_type="intent"
        )
        return intent_id
    
    def complete_intent(self, intent_id: str, agent_id: str):
        """Mark an intent as completed."""
        ledger = self._read_ledger()
        
        if "intents" not in ledger:
            return
        
        for intent in ledger["intents"]:
            if intent["id"] == intent_id and intent["agent_id"] == agent_id:
                intent["status"] = "completed"
                intent["completed_at"] = datetime.now().isoformat()
                self._write_ledger(ledger)
                self.post_message(
                    agent_id,
                    f"Completed intent: {intent['intent']}",
                    message_type="info"
                )
                break
    
    def acquire_lock(self, agent_id: str, resource: str, 
                    timeout: int = 30) -> bool:
        """
        Acquire a lock on a resource.
        
        Args:
            agent_id: Agent requesting lock
            resource: Resource identifier
            timeout: Lock timeout in seconds
            
        Returns:
            True if lock acquired
        """
        ledger = self._read_ledger()
        
        if "locks" not in ledger:
            ledger["locks"] = {}
        
        current_time = time.time()
        
        # Check if resource is locked
        if resource in ledger["locks"]:
            lock_info = ledger["locks"][resource]
            lock_time = datetime.fromisoformat(lock_info["acquired_at"]).timestamp()
            
            # Check if lock expired
            if current_time - lock_time > timeout:
                # Lock expired, release it
                del ledger["locks"][resource]
            else:
                # Lock still active
                if lock_info["agent_id"] != agent_id:
                    return False
        
        # Acquire lock
        ledger["locks"][resource] = {
            "agent_id": agent_id,
            "acquired_at": datetime.now().isoformat(),
            "timeout": timeout
        }
        
        self._write_ledger(ledger)
        return True
    
    def release_lock(self, agent_id: str, resource: str):
        """Release a lock on a resource."""
        ledger = self._read_ledger()
        
        if "locks" not in ledger:
            return
        
        if resource in ledger["locks"]:
            if ledger["locks"][resource]["agent_id"] == agent_id:
                del ledger["locks"][resource]
                self._write_ledger(ledger)
    
    def get_messages(self, agent_id: Optional[str] = None,
                    since: Optional[str] = None,
                    message_type: Optional[str] = None) -> List[Dict]:
        """
        Get messages from the ledger.
        
        Args:
            agent_id: Filter by agent ID
            since: ISO timestamp to get messages since
            message_type: Filter by message type
            
        Returns:
            List of messages
        """
        ledger = self._read_ledger()
        messages = ledger.get("messages", [])
        
        # Apply filters
        if agent_id:
            messages = [m for m in messages if m.get("agent_id") == agent_id or 
                       m.get("target_agent") == agent_id]
        
        if since:
            since_time = datetime.fromisoformat(since)
            messages = [m for m in messages if 
                       datetime.fromisoformat(m["timestamp"]) > since_time]
        
        if message_type:
            messages = [m for m in messages if m.get("type") == message_type]
        
        return messages
    
    def get_agent_state(self, agent_id: str) -> Optional[Dict]:
        """Get current state of an agent."""
        ledger = self._read_ledger()
        return ledger.get("agents", {}).get(agent_id)
    
    def get_all_agents(self) -> Dict[str, Dict]:
        """Get all registered agents."""
        ledger = self._read_ledger()
        return ledger.get("agents", {})
    
    def set_state(self, key: str, value: any):
        """Set global state value."""
        ledger = self._read_ledger()
        if "state" not in ledger:
            ledger["state"] = {}
        ledger["state"][key] = value
        self._write_ledger(ledger)
    
    def get_state(self, key: str, default: any = None) -> any:
        """Get global state value."""
        ledger = self._read_ledger()
        return ledger.get("state", {}).get(key, default)
