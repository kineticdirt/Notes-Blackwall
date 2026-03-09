# Observability Stack

Monitoring, logging, and tracing for Cequence BlackWall services.

## Components

| Component | Port | Role |
|-----------|------|------|
| **Prometheus** | 9090 | Metrics collection and alerting |
| **Grafana** | 3000 | Dashboards and visualization |
| **Loki** | 3100 | Log aggregation (Grafana-native) |
| **Promtail** | — | Log shipper (sends to Loki) |

## Quick Start

```bash
docker compose up -d
```

Open Grafana at `http://localhost:3000` (default: admin/admin).

## Dashboards

Pre-built dashboards in `grafana/dashboards/`:

- **Service Health** — Request rates, error rates, latency percentiles per service
- **Agent Activity** — Agent task throughput, competition scores, coordination events
- **Infrastructure** — CPU, memory, disk, network per container

## Metrics Convention

Services expose metrics at `/metrics` (Prometheus format). Standard labels:

```
service="blackwall"
environment="dev"
instance="blackwall:8000"
```

## Alerting

Alert rules in `prometheus/alerts.yml`. Defaults:

- Service down > 1 min
- Error rate > 5% over 5 min
- P99 latency > 2s
- Disk usage > 80%
