# Data Pipeline

ETL / streaming pipeline for collecting, transforming, and routing data across Cequence BlackWall services.

## Architecture

```
Sources                    Transforms              Sinks
─────────                  ──────────              ─────
Agent Ledger  ─┐                                ┌→ SQLite / Postgres
Overseer Logs ─┤→ Collector → Transform chain → ├→ JSON files
Competition    ─┤    (poll)    (filter, enrich,  ├→ Prometheus metrics
  Results      ─┤              aggregate)        └→ Webhook (Slack/Discord)
BlackWall      ─┘
  Events
```

## Data Sources

| Source | Location | Format | Events |
|--------|----------|--------|--------|
| Agent ledger | `ledger/AI_GROUPCHAT.json` | JSON | Agent messages, task completions |
| Overseer | `.overseer/overseer.log` | Append-only text | Goal checks, edits, violations |
| Competitions | `results/`, `worktrees/` | JSON | Scores, rankings, test results |
| BlackWall | `blackwall/` API events | JSON | Protection triggers, detections |
| Security scans | `security-toolkit/` output | JSON | Findings, vulnerabilities |

## Quick Start

```bash
pip install -r requirements.txt

# Run pipeline once (batch mode)
python -m src.pipeline --mode batch

# Run pipeline continuously (watch mode)
python -m src.pipeline --mode watch --interval 30

# Run specific collector only
python -m src.pipeline --collector agent_ledger
```

## Configuration

Pipeline config in `pipeline.yml`. Each stage (collect, transform, sink) is independently configurable.

## Transforms

- **filter**: Drop events by field value or regex
- **enrich**: Add timestamps, source labels, correlation IDs
- **aggregate**: Count, sum, avg over time windows
- **deduplicate**: Skip events already processed (by hash)
