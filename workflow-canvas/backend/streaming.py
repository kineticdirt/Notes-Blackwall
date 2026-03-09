"""
HTTP streaming manager for workflow execution.
Manages Server-Sent Events (SSE) streams.
"""

from typing import Dict, Optional, List
from datetime import datetime
import uuid


class StreamManager:
    """Manages active streaming connections."""
    
    def __init__(self):
        self.streams: Dict[str, Dict] = {}
    
    def create_stream(self, workflow_id: str) -> str:
        """Create a new stream and return stream ID."""
        stream_id = str(uuid.uuid4())
        self.streams[stream_id] = {
            "id": stream_id,
            "workflow_id": workflow_id,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "events": []
        }
        return stream_id
    
    def add_event(self, stream_id: str, event: Dict):
        """Add an event to a stream."""
        if stream_id in self.streams:
            self.streams[stream_id]["events"].append({
                **event,
                "timestamp": datetime.now().isoformat()
            })
    
    def close_stream(self, stream_id: str):
        """Close a stream."""
        if stream_id in self.streams:
            self.streams[stream_id]["status"] = "closed"
            self.streams[stream_id]["closed_at"] = datetime.now().isoformat()
    
    def get_stream_status(self, stream_id: str) -> Optional[Dict]:
        """Get status of a stream."""
        return self.streams.get(stream_id)
    
    def get_active_streams(self) -> List[Dict]:
        """Get all active streams."""
        return [
            stream for stream in self.streams.values()
            if stream["status"] == "active"
        ]
