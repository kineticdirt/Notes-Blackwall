from datetime import datetime, timezone
from ..collectors.json_file import Event


class EnrichTransform:
    def __init__(self, fields: dict):
        self.fields = fields

    def apply(self, events: list[Event]) -> list[Event]:
        for event in events:
            event.data.update(self.fields)
            event.data.setdefault("processed_at", datetime.now(timezone.utc).isoformat())
        return events


class FilterTransform:
    def __init__(self, exclude: dict[str, list[str]] | None = None, include: dict[str, list[str]] | None = None):
        self.exclude = exclude or {}
        self.include = include or {}

    def apply(self, events: list[Event]) -> list[Event]:
        result = []
        for event in events:
            excluded = False
            for field, values in self.exclude.items():
                if getattr(event, field, None) in values:
                    excluded = True
                    break
                if event.data.get(field) in values:
                    excluded = True
                    break
            if excluded:
                continue

            if self.include:
                included = False
                for field, values in self.include.items():
                    if getattr(event, field, None) in values or event.data.get(field) in values:
                        included = True
                        break
                if not included:
                    continue

            result.append(event)
        return result


class DeduplicateTransform:
    def __init__(self, key_fields: list[str]):
        self.key_fields = key_fields
        self._seen: set[str] = set()

    def apply(self, events: list[Event]) -> list[Event]:
        result = []
        for event in events:
            key_parts = []
            for f in self.key_fields:
                key_parts.append(str(getattr(event, f, event.data.get(f, ""))))
            key = "|".join(key_parts)
            if key not in self._seen:
                self._seen.add(key)
                result.append(event)
        return result
