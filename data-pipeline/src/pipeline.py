import time
import yaml
import click
import structlog
from pathlib import Path

from .collectors.json_file import JsonFileCollector
from .collectors.tail_file import TailFileCollector
from .transforms.core import EnrichTransform, FilterTransform, DeduplicateTransform
from .sinks.sqlite_sink import SQLiteSink
from .sinks.jsonl_sink import JSONLSink

log = structlog.get_logger()

COLLECTOR_TYPES = {
    "json_file": JsonFileCollector,
    "tail_file": TailFileCollector,
}


def load_config(path: str = "pipeline.yml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def build_collectors(config: dict) -> list:
    collectors = []
    for name, cfg in config.get("collectors", {}).items():
        ctype = cfg["type"]
        if ctype == "json_file":
            collectors.append(JsonFileCollector(name=name, path=Path(cfg["path"])))
        elif ctype == "tail_file":
            collectors.append(TailFileCollector(name=name, path=Path(cfg["path"])))
    return collectors


def build_transforms(config: dict) -> list:
    transforms = []
    for t in config.get("transforms", []):
        if t["type"] == "enrich":
            transforms.append(EnrichTransform(fields=t.get("fields", {})))
        elif t["type"] == "filter":
            transforms.append(FilterTransform(exclude=t.get("exclude")))
        elif t["type"] == "deduplicate":
            transforms.append(DeduplicateTransform(key_fields=t.get("key_fields", [])))
    return transforms


def build_sinks(config: dict) -> list:
    sinks = []
    for name, cfg in config.get("sinks", {}).items():
        if cfg["type"] == "sqlite":
            sinks.append(SQLiteSink(db_path=cfg["path"], table=cfg.get("table", "events")))
        elif cfg["type"] == "json_file":
            sinks.append(JSONLSink(file_path=cfg["path"]))
    return sinks


def run_once(collectors, transforms, sinks):
    total = 0
    for collector in collectors:
        events = collector.collect()
        if not events:
            continue
        for transform in transforms:
            events = transform.apply(events)
        for sink in sinks:
            sink.write(events)
        total += len(events)
    return total


@click.command()
@click.option("--config", default="pipeline.yml", help="Pipeline config file")
@click.option("--mode", type=click.Choice(["batch", "watch"]), default="batch")
@click.option("--interval", default=30, help="Poll interval in seconds (watch mode)")
@click.option("--collector", default=None, help="Run only this collector")
def main(config, mode, interval, collector):
    """Cequence BlackWall Data Pipeline"""
    cfg = load_config(config)
    collectors = build_collectors(cfg)
    transforms = build_transforms(cfg)
    sinks = build_sinks(cfg)

    if collector:
        collectors = [c for c in collectors if c.name == collector]

    log.info("pipeline.start", mode=mode, collectors=len(collectors), sinks=len(sinks))

    if mode == "batch":
        count = run_once(collectors, transforms, sinks)
        log.info("pipeline.batch_complete", events_processed=count)
    else:
        log.info("pipeline.watch_start", interval=interval)
        while True:
            count = run_once(collectors, transforms, sinks)
            if count > 0:
                log.info("pipeline.cycle", events_processed=count)
            time.sleep(interval)


if __name__ == "__main__":
    main()
