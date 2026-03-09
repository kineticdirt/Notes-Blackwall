from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timezone

from .json_file import Event


@dataclass
class TailFileCollector:
    """Collects new lines appended to a file since last poll."""

    name: str
    path: Path
    _last_pos: int = field(default=0, init=False)

    def collect(self) -> list[Event]:
        if not self.path.exists():
            return []

        size = self.path.stat().st_size
        if size <= self._last_pos:
            return []

        events: list[Event] = []
        now = datetime.now(timezone.utc).isoformat()

        with open(self.path, "r", errors="replace") as f:
            f.seek(self._last_pos)
            for line in f:
                stripped = line.strip()
                if stripped:
                    events.append(Event(
                        source=self.name,
                        event_type="log_line",
                        timestamp=now,
                        data={"line": stripped},
                    ))
            self._last_pos = f.tell()

        return events
