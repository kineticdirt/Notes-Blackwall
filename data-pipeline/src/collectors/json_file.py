import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field


@dataclass
class Event:
    source: str
    event_type: str
    timestamp: str
    data: dict
    event_id: str = ""

    def __post_init__(self):
        if not self.event_id:
            raw = f"{self.source}:{self.timestamp}:{json.dumps(self.data, sort_keys=True)}"
            self.event_id = hashlib.sha256(raw.encode()).hexdigest()[:16]


@dataclass
class JsonFileCollector:
    name: str
    path: Path
    _last_hash: str = field(default="", init=False)

    def collect(self) -> list[Event]:
        if not self.path.exists():
            return []

        content = self.path.read_text(errors="replace")
        content_hash = hashlib.md5(content.encode()).hexdigest()
        if content_hash == self._last_hash:
            return []
        self._last_hash = content_hash

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return []

        events: list[Event] = []
        now = datetime.now(timezone.utc).isoformat()

        if isinstance(data, list):
            for item in data:
                events.append(Event(
                    source=self.name,
                    event_type=item.get("type", "unknown"),
                    timestamp=item.get("timestamp", now),
                    data=item,
                ))
        elif isinstance(data, dict):
            events.append(Event(
                source=self.name,
                event_type=data.get("type", "state_snapshot"),
                timestamp=now,
                data=data,
            ))

        return events
