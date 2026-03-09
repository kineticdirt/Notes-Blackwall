# Library — Open Source Tools & Resources

This folder serves as a curated library for open source tools, configurations, and reference materials used across the Notes - Blackwall workspace.

## Structure

```
library/
├── README.md                 # This file
├── open-source-tools/        # Tool-specific docs, configs, scripts
│   ├── networking/           # VPN, tunnels, remote access
│   ├── self-hosted/          # Nextcloud, Jellyfin, etc.
│   ├── devops/               # CI/CD, containers, IaC
│   ├── security/             # Pi-hole, Keycloak, etc.
│   ├── ai-ml/                # Ollama, LocalAI, Dify
│   ├── productivity/        # n8n, Supabase, etc.
│   ├── monitoring/           # Prometheus, Grafana
│   ├── databases/            # PostgreSQL, Redis, etc.
│   └── esoteric/             # copy-party, htmx, fzf, etc.
└── configs/                  # Reusable config templates (optional)
```

## Purpose

- **Reference**: Detailed documentation for each tool (see `../OPEN_SOURCE_TOOLS_REFERENCE.md`)
- **Scripts**: Installation and setup scripts for common tools
- **Configs**: Example configurations, Docker Compose snippets
- **Discovery**: Links to upstream repos, docs, and community resources

## Related

- **[OPEN_SOURCE_TOOLS_REFERENCE.md](../OPEN_SOURCE_TOOLS_REFERENCE.md)** — Expanded reference with per-tool subsections
- **[compendium/Open-Source-Tools.md](../compendium/Open-Source-Tools.md)** — Usage lore, workflows, how-to

## Conventions

- Prefer Docker/container configs for reproducibility
- No secrets in configs; use env vars or vault references
- Keep tool versions pinned where possible

---

*Part of the Notes - Blackwall workspace.*
