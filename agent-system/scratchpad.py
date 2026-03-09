"""
Scratchpad system for agents to share notes and context.
Agents append to the scratchpad to help coordinate work.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import threading


class Scratchpad:
    """
    Shared scratchpad for agents to append notes and context.
    Helps coordinate multi-agent workflows.
    """
    
    def __init__(self, scratchpad_path: str = "ledger/scratchpad.json"):
        """
        Initialize scratchpad.
        
        Args:
            scratchpad_path: Path to scratchpad JSON file
        """
        self.scratchpad_path = Path(scratchpad_path)
        self.scratchpad_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self._ensure_scratchpad_exists()
    
    def _ensure_scratchpad_exists(self):
        """Create scratchpad file if it doesn't exist."""
        if not self.scratchpad_path.exists():
            initial_data = {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "sections": {
                    "overview": [],
                    "code_notes": [],
                    "test_notes": [],
                    "doc_notes": [],
                    "issues": [],
                    "todo": []
                },
                "metadata": {}
            }
            self._write_scratchpad(initial_data)
    
    def _read_scratchpad(self) -> Dict:
        """Read scratchpad with locking."""
        with self.lock:
            try:
                with open(self.scratchpad_path, 'r') as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                return {
                    "version": "1.0",
                    "created_at": datetime.now().isoformat(),
                    "sections": {
                        "overview": [],
                        "code_notes": [],
                        "test_notes": [],
                        "doc_notes": [],
                        "issues": [],
                        "todo": []
                    },
                    "metadata": {}
                }
    
    def _write_scratchpad(self, data: Dict):
        """Write scratchpad with locking."""
        with self.lock:
            temp_path = self.scratchpad_path.with_suffix('.tmp')
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2)
            temp_path.replace(self.scratchpad_path)
    
    def append(self, section: str, content: str, agent_id: str, 
              metadata: Optional[Dict] = None):
        """
        Append content to a scratchpad section.
        
        Args:
            section: Section name (overview, code_notes, test_notes, doc_notes, issues, todo)
            content: Content to append
            agent_id: Agent adding the content
            metadata: Additional metadata
        """
        scratchpad = self._read_scratchpad()
        
        if "sections" not in scratchpad:
            scratchpad["sections"] = {}
        
        if section not in scratchpad["sections"]:
            scratchpad["sections"][section] = []
        
        entry = {
            "content": content,
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        scratchpad["sections"][section].append(entry)
        
        # Keep last 1000 entries per section
        if len(scratchpad["sections"][section]) > 1000:
            scratchpad["sections"][section] = scratchpad["sections"][section][-1000:]
        
        self._write_scratchpad(scratchpad)
    
    def read_section(self, section: str) -> List[Dict]:
        """
        Read all entries from a section.
        
        Args:
            section: Section name
            
        Returns:
            List of entries
        """
        scratchpad = self._read_scratchpad()
        return scratchpad.get("sections", {}).get(section, [])
    
    def read_all(self) -> Dict:
        """Read entire scratchpad."""
        return self._read_scratchpad()
    
    def get_latest(self, section: str, count: int = 10) -> List[Dict]:
        """
        Get latest entries from a section.
        
        Args:
            section: Section name
            count: Number of latest entries to return
            
        Returns:
            List of latest entries
        """
        entries = self.read_section(section)
        return entries[-count:] if len(entries) > count else entries
    
    def clear_section(self, section: str):
        """Clear all entries from a section."""
        scratchpad = self._read_scratchpad()
        if "sections" in scratchpad and section in scratchpad["sections"]:
            scratchpad["sections"][section] = []
            self._write_scratchpad(scratchpad)
    
    def set_metadata(self, key: str, value: any):
        """Set metadata value."""
        scratchpad = self._read_scratchpad()
        if "metadata" not in scratchpad:
            scratchpad["metadata"] = {}
        scratchpad["metadata"][key] = value
        self._write_scratchpad(scratchpad)
    
    def get_metadata(self, key: str, default: any = None) -> any:
        """Get metadata value."""
        scratchpad = self._read_scratchpad()
        return scratchpad.get("metadata", {}).get(key, default)
