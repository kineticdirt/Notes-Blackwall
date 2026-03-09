"""
Agent Coordination System
Handles race conditions, timeouts, hanging processes, and time estimation
for coordinating multiple AI agents/LLMs.

Key Features:
1. Health monitoring for agents/processes
2. Timeout handling for operations
3. Time estimation requests/responses
4. Hanging process detection
5. Deadlock detection
6. Action tracking and coordination
"""

import json
import sqlite3
import time
import threading
import signal
import psutil
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum


class AgentStatus(Enum):
    """Agent status enumeration."""
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    HANGING = "hanging"
    TIMEOUT = "timeout"
    ERROR = "error"
    COMPLETED = "completed"


@dataclass
class TimeEstimate:
    """Time estimate for an operation."""
    operation_id: str
    agent_id: str
    estimated_seconds: float
    confidence: float = 0.5  # 0.0 to 1.0
    created_at: str = ""
    expires_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.expires_at:
            # Default: estimate expires in 2x the estimated time
            expires_dt = datetime.now() + timedelta(seconds=self.estimated_seconds * 2)
            self.expires_at = expires_dt.isoformat()
    
    def is_expired(self) -> bool:
        """Check if estimate has expired."""
        if not self.expires_at:
            return False
        return datetime.now() > datetime.fromisoformat(self.expires_at)


@dataclass
class AgentAction:
    """Tracks an agent's action."""
    action_id: str
    agent_id: str
    action_type: str  # operation, wait, request_time, etc.
    description: str
    started_at: str
    expected_completion: Optional[str] = None
    actual_completion: Optional[str] = None
    status: str = "active"  # active, completed, timeout, error
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if not self.started_at:
            self.started_at = datetime.now().isoformat()
    
    def is_timed_out(self, timeout_seconds: float) -> bool:
        """Check if action has timed out."""
        started = datetime.fromisoformat(self.started_at)
        elapsed = (datetime.now() - started).total_seconds()
        return elapsed > timeout_seconds
    
    def get_elapsed_seconds(self) -> float:
        """Get elapsed time in seconds."""
        started = datetime.fromisoformat(self.started_at)
        return (datetime.now() - started).total_seconds()


class AgentHealthMonitor:
    """
    Monitors agent health and detects hanging processes.
    """
    
    def __init__(self, check_interval: float = 5.0):
        """
        Initialize health monitor.
        
        Args:
            check_interval: Seconds between health checks
        """
        self.check_interval = check_interval
        self.monitored_agents: Dict[str, Dict] = {}
        self.lock = threading.Lock()
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
    
    def register_agent(self, agent_id: str, process_id: Optional[int] = None,
                      timeout_seconds: float = 300.0):
        """
        Register an agent for monitoring.
        
        Args:
            agent_id: Agent identifier
            process_id: Process ID (if monitoring system process)
            timeout_seconds: Timeout threshold
        """
        with self.lock:
            self.monitored_agents[agent_id] = {
                "agent_id": agent_id,
                "process_id": process_id,
                "timeout_seconds": timeout_seconds,
                "last_heartbeat": datetime.now().isoformat(),
                "status": AgentStatus.IDLE.value,
                "action_started": None,
                "hang_detected": False
            }
    
    def update_heartbeat(self, agent_id: str):
        """Update agent heartbeat."""
        with self.lock:
            if agent_id in self.monitored_agents:
                self.monitored_agents[agent_id]["last_heartbeat"] = datetime.now().isoformat()
                self.monitored_agents[agent_id]["hang_detected"] = False
    
    def start_action(self, agent_id: str, action_description: str,
                    expected_duration_seconds: Optional[float] = None):
        """Mark agent as starting an action."""
        with self.lock:
            if agent_id in self.monitored_agents:
                self.monitored_agents[agent_id]["status"] = AgentStatus.WORKING.value
                self.monitored_agents[agent_id]["action_started"] = datetime.now().isoformat()
                self.monitored_agents[agent_id]["action_description"] = action_description
                if expected_duration_seconds:
                    expected_completion = datetime.now() + timedelta(seconds=expected_duration_seconds)
                    self.monitored_agents[agent_id]["expected_completion"] = expected_completion.isoformat()
    
    def complete_action(self, agent_id: str):
        """Mark agent action as completed."""
        with self.lock:
            if agent_id in self.monitored_agents:
                self.monitored_agents[agent_id]["status"] = AgentStatus.IDLE.value
                self.monitored_agents[agent_id]["action_started"] = None
                self.monitored_agents[agent_id]["hang_detected"] = False
    
    def check_health(self, agent_id: str) -> Dict:
        """
        Check agent health.
        
        Returns:
            Dict with health status
        """
        with self.lock:
            if agent_id not in self.monitored_agents:
                return {"status": "not_monitored"}
            
            agent = self.monitored_agents[agent_id]
            last_heartbeat = datetime.fromisoformat(agent["last_heartbeat"])
            elapsed = (datetime.now() - last_heartbeat).total_seconds()
            timeout = agent["timeout_seconds"]
            
            # Check if hanging
            is_hanging = False
            if agent["status"] == AgentStatus.WORKING.value:
                if agent["action_started"]:
                    action_started = datetime.fromisoformat(agent["action_started"])
                    action_elapsed = (datetime.now() - action_started).total_seconds()
                    if action_elapsed > timeout:
                        is_hanging = True
                        agent["hang_detected"] = True
                        agent["status"] = AgentStatus.HANGING.value
                elif elapsed > timeout:
                    is_hanging = True
                    agent["hang_detected"] = True
                    agent["status"] = AgentStatus.HANGING.value
            
            # Check process if PID available
            process_alive = True
            if agent["process_id"]:
                try:
                    process = psutil.Process(agent["process_id"])
                    process_alive = process.is_running()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    process_alive = False
            
            return {
                "agent_id": agent_id,
                "status": agent["status"],
                "last_heartbeat": agent["last_heartbeat"],
                "elapsed_since_heartbeat": elapsed,
                "is_hanging": is_hanging,
                "process_alive": process_alive,
                "action_started": agent.get("action_started"),
                "action_description": agent.get("action_description")
            }
    
    def get_hanging_agents(self) -> List[str]:
        """Get list of hanging agent IDs."""
        with self.lock:
            return [
                agent_id for agent_id, agent in self.monitored_agents.items()
                if agent["hang_detected"] or agent["status"] == AgentStatus.HANGING.value
            ]
    
    def start_monitoring(self):
        """Start background monitoring thread."""
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop background monitoring."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
    
    def _monitor_loop(self):
        """Background monitoring loop."""
        while self.running:
            time.sleep(self.check_interval)
            with self.lock:
                for agent_id in list(self.monitored_agents.keys()):
                    self.check_health(agent_id)


class AgentCoordinator:
    """
    Coordinates multiple agents with timeout handling, time estimation,
    and hanging process detection.
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize agent coordinator.
        
        Args:
            db_path: Path to coordination database
        """
        if db_path is None:
            db_path = Path(".worktrees") / "coordination.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.health_monitor = AgentHealthMonitor()
        self.health_monitor.start_monitoring()
        
        self.actions: Dict[str, AgentAction] = {}
        self.time_estimates: Dict[str, TimeEstimate] = {}
        self.lock = threading.Lock()
        
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Agent actions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_actions (
                action_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                action_type TEXT NOT NULL,
                description TEXT NOT NULL,
                started_at TEXT NOT NULL,
                expected_completion TEXT,
                actual_completion TEXT,
                status TEXT NOT NULL,
                metadata_json TEXT
            )
        """)
        
        # Time estimates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS time_estimates (
                operation_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                estimated_seconds REAL NOT NULL,
                confidence REAL DEFAULT 0.5,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            )
        """)
        
        # Agent health table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_health (
                agent_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                last_heartbeat TEXT NOT NULL,
                hang_detected INTEGER DEFAULT 0,
                last_check TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def register_agent(self, agent_id: str, process_id: Optional[int] = None,
                     timeout_seconds: float = 300.0):
        """Register an agent for coordination."""
        self.health_monitor.register_agent(agent_id, process_id, timeout_seconds)
        self.health_monitor.update_heartbeat(agent_id)
    
    def request_time_estimate(self, operation_id: str, agent_id: str,
                            operation_description: str) -> Optional[TimeEstimate]:
        """
        Request a time estimate from an agent.
        
        Args:
            operation_id: Unique operation identifier
            agent_id: Agent to request estimate from
            operation_description: Description of operation
            
        Returns:
            TimeEstimate if available, None otherwise
        """
        # Check if agent has provided an estimate
        estimate = self.time_estimates.get(operation_id)
        if estimate and not estimate.is_expired():
            return estimate
        
        # Store request (agent can respond later)
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR IGNORE INTO time_estimates
            (operation_id, agent_id, estimated_seconds, confidence, created_at, expires_at)
            VALUES (?, ?, 0, 0, ?, ?)
        """, (operation_id, agent_id, datetime.now().isoformat(),
              (datetime.now() + timedelta(hours=1)).isoformat()))
        
        conn.commit()
        conn.close()
        
        return None
    
    def provide_time_estimate(self, operation_id: str, agent_id: str,
                             estimated_seconds: float, confidence: float = 0.5):
        """
        Provide a time estimate for an operation.
        
        Args:
            operation_id: Operation identifier
            agent_id: Agent providing estimate
            estimated_seconds: Estimated duration in seconds
            confidence: Confidence level (0.0 to 1.0)
        """
        estimate = TimeEstimate(
            operation_id=operation_id,
            agent_id=agent_id,
            estimated_seconds=estimated_seconds,
            confidence=confidence
        )
        
        with self.lock:
            self.time_estimates[operation_id] = estimate
        
        # Store in database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO time_estimates
            (operation_id, agent_id, estimated_seconds, confidence, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            operation_id, agent_id, estimated_seconds, confidence,
            estimate.created_at, estimate.expires_at
        ))
        
        conn.commit()
        conn.close()
    
    def start_action(self, action_id: str, agent_id: str, action_type: str,
                    description: str, expected_duration_seconds: Optional[float] = None):
        """
        Start tracking an agent action.
        
        Args:
            action_id: Unique action identifier
            agent_id: Agent performing action
            action_type: Type of action
            description: Action description
            expected_duration_seconds: Expected duration (for timeout detection)
        """
        action = AgentAction(
            action_id=action_id,
            agent_id=agent_id,
            action_type=action_type,
            description=description
        )
        
        if expected_duration_seconds:
            expected_completion = datetime.now() + timedelta(seconds=expected_duration_seconds)
            action.expected_completion = expected_completion.isoformat()
        
        with self.lock:
            self.actions[action_id] = action
        
        # Update health monitor
        self.health_monitor.start_action(agent_id, description, expected_duration_seconds)
        self.health_monitor.update_heartbeat(agent_id)
        
        # Store in database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO agent_actions
            (action_id, agent_id, action_type, description, started_at,
             expected_completion, actual_completion, status, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            action_id, agent_id, action_type, description, action.started_at,
            action.expected_completion, action.actual_completion,
            action.status, json.dumps(action.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    def complete_action(self, action_id: str, success: bool = True):
        """Mark an action as completed."""
        with self.lock:
            if action_id not in self.actions:
                return
            
            action = self.actions[action_id]
            action.actual_completion = datetime.now().isoformat()
            action.status = "completed" if success else "error"
            
            # Update health monitor
            self.health_monitor.complete_action(action.agent_id)
            self.health_monitor.update_heartbeat(action.agent_id)
        
        # Update database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE agent_actions
            SET actual_completion = ?, status = ?
            WHERE action_id = ?
        """, (action.actual_completion, action.status, action_id))
        
        conn.commit()
        conn.close()
    
    def wait_for_agent(self, agent_id: str, timeout_seconds: float = 300.0,
                      check_interval: float = 1.0) -> bool:
        """
        Wait for an agent to become idle.
        
        Args:
            agent_id: Agent to wait for
            timeout_seconds: Maximum wait time
            check_interval: Seconds between checks
            
        Returns:
            True if agent became idle, False if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            health = self.health_monitor.check_health(agent_id)
            
            if health["status"] == AgentStatus.IDLE.value:
                return True
            
            if health["is_hanging"]:
                return False
            
            time.sleep(check_interval)
        
        return False
    
    def wait_for_action(self, action_id: str, timeout_seconds: float = 300.0,
                       check_interval: float = 1.0) -> bool:
        """
        Wait for an action to complete.
        
        Args:
            action_id: Action to wait for
            timeout_seconds: Maximum wait time
            check_interval: Seconds between checks
            
        Returns:
            True if action completed, False if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            with self.lock:
                if action_id not in self.actions:
                    return False
                
                action = self.actions[action_id]
                if action.status in ("completed", "error"):
                    return True
                
                if action.is_timed_out(timeout_seconds):
                    action.status = "timeout"
                    return False
            
            time.sleep(check_interval)
        
        return False
    
    def get_hanging_agents(self) -> List[Dict]:
        """Get list of hanging agents with details."""
        hanging_ids = self.health_monitor.get_hanging_agents()
        
        result = []
        for agent_id in hanging_ids:
            health = self.health_monitor.check_health(agent_id)
            result.append(health)
        
        return result
    
    def get_agent_status(self, agent_id: str) -> Dict:
        """Get comprehensive status for an agent."""
        health = self.health_monitor.check_health(agent_id)
        
        # Get active actions
        with self.lock:
            active_actions = [
                asdict(action) for action in self.actions.values()
                if action.agent_id == agent_id and action.status == "active"
            ]
        
        return {
            **health,
            "active_actions": active_actions,
            "active_action_count": len(active_actions)
        }
    
    def heartbeat(self, agent_id: str):
        """Send heartbeat from an agent."""
        self.health_monitor.update_heartbeat(agent_id)
        
        # Update database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO agent_health
            (agent_id, status, last_heartbeat, hang_detected, last_check)
            VALUES (?, ?, ?, ?, ?)
        """, (
            agent_id,
            self.health_monitor.monitored_agents.get(agent_id, {}).get("status", "unknown"),
            datetime.now().isoformat(),
            0,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
