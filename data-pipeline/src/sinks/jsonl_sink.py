import json
from pathlib import Path
from dataclasses import asdict

from ..collectors.json_file import Event


class JSONLSink:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, events: list[Event]):
        if not events:
            return
        with open(self.file_path, "a") as f:
            for event in events:
                record = {
                    "event_id": event.event_id,
                    "source": event.source,
                    "event_type": event.event_type,
                    "timestamp": event.timestamp,
                    "data": event.data,
                }
                f.write(json.dumps(record) + "\n")
