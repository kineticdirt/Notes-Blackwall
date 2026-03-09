# API Gateway

Lightweight API gateway for Cequence BlackWall services. Provides a single entry point with routing, authentication, rate limiting, and request validation.

## Architecture

```
Client → API Gateway (:9000)
            ├── /api/blackwall/*   → BlackWall Service (:8000)
            ├── /api/workflow/*    → Workflow Canvas (:8080)
            ├── /api/agents/*     → Agent System
            └── /api/nightshade/* → Nightshade Tracker
```

## Features

- **Reverse proxy** with service discovery via config
- **JWT authentication** with role-based access control
- **Rate limiting** per client (token bucket)
- **Request validation** against OpenAPI schemas
- **Circuit breaker** for downstream service failures
- **Structured logging** with correlation IDs
- **Health aggregation** from all downstream services

## Quick Start

```bash
pip install -r requirements.txt
python -m src.gateway
```

## Configuration

Copy `.env.example` to `.env` and set values. Service routes are defined in `src/config.py`.

## Endpoints

| Path | Upstream | Description |
|------|----------|-------------|
| `GET /health` | — | Aggregated health of all services |
| `/api/blackwall/**` | blackwall:8000 | AI protection API |
| `/api/workflow/**` | workflow-canvas:8080 | Workflow editor API |
| `/api/agents/**` | agent-system | Agent coordination |
| `/api/nightshade/**` | nightshade-tracker | Image/text poisoning |
