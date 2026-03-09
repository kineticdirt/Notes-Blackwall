# Open Source & Free Technologies — Quick Reference

A curated reference of open source and free software across categories. For **usage lore, how/what, and typical workflows**, see the compendium: [Open-Source-Tools](compendium/Open-Source-Tools.md).

All listed tools are open source and free to use (some offer paid tiers for hosted/managed options).

**Library folder**: Tool-specific configs, scripts, and reference materials live in [`library/open-source-tools/`](library/open-source-tools/).

---

## Networking, VPN & Remote Access

| Tool | Description | Notes |
|------|-------------|-------|
| **Tailscale** | Zero-config mesh VPN built on WireGuard | Easy setup, MagicDNS, works behind NAT |
| **ZeroTier** | Software-defined mesh networking | Self-host controller option, global networks |
| **WireGuard** | Modern, fast VPN protocol | Kernel-level, minimal config, very performant |
| **Cloudflare Tunnel** (cloudflared) | Expose local services without opening ports | No firewall changes, routes through Cloudflare |
| **OpenVPN** | Mature VPN solution | Widely supported, more config than WireGuard |
| **frp** | Fast reverse proxy | Expose local services, written in Go |
| **ngrok** (community) | Secure tunnels to localhost | Quick dev sharing; paid for production features |

### Tailscale

| Attribute | Details |
|-----------|---------|
| **License** | BSD-3-Clause |
| **Repo** | [tailscale/tailscale](https://github.com/tailscale/tailscale) |
| **Library** | `library/open-source-tools/networking/` |

Zero-config mesh VPN built on WireGuard. Devices get Tailscale IPs and can reach each other from anywhere. MagicDNS provides hostname resolution; works behind NAT without port forwarding.

**Install**: `brew install tailscale` (macOS) or [tailscale.com/download](https://tailscale.com/download)

**Key features**: No VPN server to maintain, ACLs for access control, subnet routing, exit nodes.

---

### ZeroTier

| Attribute | Details |
|-----------|---------|
| **License** | BSL 1.1 (source-available) |
| **Repo** | [zerotier/ZeroTier](https://github.com/zerotier/ZeroTier) |
| **Library** | `library/open-source-tools/networking/` |

Software-defined mesh networking. Create a network, join from devices; traffic is encrypted end-to-end. Optional self-hosted controller (Moon) for lower latency.

**Install**: `brew install zerotier-one` or [zerotier.com/download](https://www.zerotier.com/download/)

**Key features**: Global networks, SDN, self-host controller, cross-platform.

---

### WireGuard

| Attribute | Details |
|-----------|---------|
| **License** | GPL-2.0 |
| **Repo** | [WireGuard/wireguard-go](https://github.com/WireGuard/wireguard-go) |
| **Library** | `library/open-source-tools/networking/` |

Modern, fast VPN protocol. Kernel-level on Linux; minimal config; very performant. Manual key exchange required.

**Install**: Kernel module on Linux; `brew install wireguard-tools` on macOS.

**Key features**: ~4K lines of code, ChaCha20-Poly1305, no handshake overhead.

---

### Cloudflare Tunnel (cloudflared)

| Attribute | Details |
|-----------|---------|
| **License** | Apache-2.0 |
| **Repo** | [cloudflare/cloudflared](https://github.com/cloudflare/cloudflared) |
| **Library** | `library/open-source-tools/networking/` |

Expose local services without opening firewall ports. Traffic routes through Cloudflare; no inbound ports needed.

**Install**: `brew install cloudflared` or download from [developers.cloudflare.com](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/)

**Key features**: Zero Trust access, quick tunnels for dev, named tunnels for production.

---

### OpenVPN

| Attribute | Details |
|-----------|---------|
| **License** | GPL-2.0 |
| **Repo** | [OpenVPN/openvpn](https://github.com/OpenVPN/openvpn) |
| **Library** | `library/open-source-tools/networking/` |

Mature VPN solution. Widely supported; more configuration than WireGuard; good for legacy environments.

**Install**: `brew install openvpn` or package manager on Linux.

**Key features**: TLS-based, flexible config, cross-platform.

---

### frp

| Attribute | Details |
|-----------|---------|
| **License** | Apache-2.0 |
| **Repo** | [fatedier/frp](https://github.com/fatedier/frp) |
| **Library** | `library/open-source-tools/networking/` |

Fast reverse proxy in Go. Client on local machine, server on public host; expose ports via HTTP/TCP/HTTPS.

**Install**: Download binaries from [GitHub releases](https://github.com/fatedier/frp/releases).

**Key features**: TCP/HTTP/HTTPS reverse proxy, P2P mode, dashboard.

---

### ngrok (community)

| Attribute | Details |
|-----------|---------|
| **License** | Apache-2.0 |
| **Repo** | [ngrok/ngrok](https://github.com/ngrok/ngrok) |
| **Library** | `library/open-source-tools/networking/` |

Secure tunnels to localhost. Quick dev sharing; community tier has limits; paid for production features.

**Install**: `brew install ngrok` or [ngrok.com/download](https://ngrok.com/download)

**Key features**: Instant HTTPS, inspect traffic, webhooks.

---

## Self-Hosted Applications

| Tool | Description | Replaces |
|------|-------------|----------|
| **Nextcloud** | File sync, calendar, contacts, collaboration | Dropbox, Google Drive |
| **Jellyfin** | Media server for movies, TV, music | Plex (free tier) |
| **Immich** | Photo and video management | Google Photos |
| **Vaultwarden** | Password manager (Bitwarden-compatible) | Bitwarden (self-hosted, lighter) |
| **Paperless-ngx** | Document scanning, indexing, archival | Physical filing, Evernote |
| **Home Assistant** | Home automation platform | Smart home hubs |
| **Calibre-Web** | E-book library and reader | Kindle Cloud |
| **Stirling-PDF** | PDF toolkit (merge, split, convert) | Adobe Acrobat |

### Nextcloud

| Attribute | Details |
|-----------|---------|
| **License** | AGPL-3.0 |
| **Repo** | [nextcloud/server](https://github.com/nextcloud/server) |
| **Library** | `library/open-source-tools/self-hosted/` |

File sync, calendar, contacts, collaboration. Full Dropbox/Google Drive replacement with apps ecosystem.

**Install**: Docker, Snap, or manual PHP setup. [docs.nextcloud.com](https://docs.nextcloud.com/)

**Key features**: WebDAV, CalDAV, CardDAV, end-to-end encryption, federation.

---

### Jellyfin

| Attribute | Details |
|-----------|---------|
| **License** | GPL-2.0 |
| **Repo** | [jellyfin/jellyfin](https://github.com/jellyfin/jellyfin) |
| **Library** | `library/open-source-tools/self-hosted/` |

Media server for movies, TV, music. No tracking, no paywall; Plex alternative.

**Install**: Docker, package managers, or [jellyfin.org/downloads](https://jellyfin.org/downloads)

**Key features**: Transcoding, live TV, DVR, clients for all platforms.

---

### Immich

| Attribute | Details |
|-----------|---------|
| **License** | MIT |
| **Repo** | [immich-app/immich](https://github.com/immich-app/immich) |
| **Library** | `library/open-source-tools/self-hosted/` |

Photo and video management with face recognition, albums, timeline. Google Photos replacement.

**Install**: Docker Compose recommended. [immich.app/docs](https://immich.app/docs)

**Key features**: ML face detection, mobile app, backup from devices.

---

### Vaultwarden

| Attribute | Details |
|-----------|---------|
| **License** | GPL-3.0 |
| **Repo** | [dani-garcia/vaultwarden](https://github.com/dani-garcia/vaultwarden) |
| **Library** | `library/open-source-tools/self-hosted/` |

Lightweight Bitwarden-compatible password manager. Rust-based; much lighter than official server.

**Install**: Docker; single binary available. [github.com/dani-garcia/vaultwarden](https://github.com/dani-garcia/vaultwarden)

**Key features**: Bitwarden clients work as-is, 2FA, minimal resource use.

---

### Paperless-ngx

| Attribute | Details |
|-----------|---------|
| **License** | GPL-3.0 |
| **Repo** | [paperless-ngx/paperless-ngx](https://github.com/paperless-ngx/paperless-ngx) |
| **Library** | `library/open-source-tools/self-hosted/` |

Document scanning, OCR, indexing, archival. Tag, search, and retrieve documents.

**Install**: Docker Compose. [docs.paperless-ngx.com](https://docs.paperless-ngx.com/)

**Key features**: OCR (Tesseract), tags, correspondent matching, full-text search.

---

### Home Assistant

| Attribute | Details |
|-----------|---------|
| **License** | Apache-2.0 |
| **Repo** | [home-assistant/core](https://github.com/home-assistant/core) |
| **Library** | `library/open-source-tools/self-hosted/` |

Home automation platform. Integrates 1000+ devices; local-first; no cloud required.

**Install**: Docker, HA OS, or Supervised. [home-assistant.io/installation](https://www.home-assistant.io/installation/)

**Key features**: Automations, dashboards, integrations, local control.

---

### Calibre-Web

| Attribute | Details |
|-----------|---------|
| **License** | GPL-3.0 |
| **Repo** | [janeczku/calibre-web](https://github.com/janeczku/calibre-web) |
| **Library** | `library/open-source-tools/self-hosted/` |

Web UI for Calibre e-book library. Browse, read, and manage e-books.

**Install**: Docker or Python. Requires Calibre library.

**Key features**: OPDS, e-reader sync, user management.

---

### Stirling-PDF

| Attribute | Details |
|-----------|---------|
| **License** | MIT |
| **Repo** | [Stirling-Tools/Stirling-PDF](https://github.com/Stirling-Tools/Stirling-PDF) |
| **Library** | `library/open-source-tools/self-hosted/` |

PDF toolkit: merge, split, convert, compress, OCR. Runs locally; no data leaves your server.

**Install**: Docker. [stirlingpdf.com](https://www.stirlingpdf.com/)

**Key features**: 80+ tools, no upload limits, privacy-focused.

---

## Development & DevOps

| Tool | Description | Replaces |
|------|-------------|----------|
| **Gitea** / **Forgejo** | Lightweight Git hosting | GitHub (self-hosted) |
| **GitLab CE** | Full DevOps platform | GitHub, Azure DevOps |
| **Drone** | CI/CD platform | Jenkins, GitHub Actions |
| **Woodpecker CI** | Simple CI engine | GitHub Actions |
| **Docker** | Containerization | — |
| **Podman** | Daemonless containers | Docker (rootless alternative) |
| **K3s** / **K0s** | Lightweight Kubernetes | Full K8s |
| **MinIO** | S3-compatible object storage | AWS S3 |
| **Caddy** | Web server with auto-HTTPS | Nginx, Apache |
| **Traefik** | Reverse proxy & load balancer | Nginx, HAProxy |
| **Nginx** | Web server, reverse proxy | — |

### Gitea / Forgejo

| Attribute | Details |
|-----------|---------|
| **License** | MIT |
| **Repo** | [go-gitea/gitea](https://github.com/go-gitea/gitea), [forgejo/forgejo](https://github.com/forgejo/forgejo) |
| **Library** | `library/open-source-tools/devops/` |

Lightweight Git hosting. Forgejo is a community fork of Gitea. Single binary; low resource use.

**Install**: Docker, binary, or package manager. [docs.gitea.com](https://docs.gitea.com/)

**Key features**: Issues, PRs, Actions (CI), wiki, minimal footprint.

---

### GitLab CE

| Attribute | Details |
|-----------|---------|
| **License** | MIT |
| **Repo** | [gitlab-org/gitlab](https://github.com/gitlab-org/gitlab) |
| **Library** | `library/open-source-tools/devops/` |

Full DevOps platform: Git, CI/CD, container registry, security scanning.

**Install**: Docker, Omnibus, or Helm. [docs.gitlab.com](https://docs.gitlab.com/)

**Key features**: Built-in CI/CD, container registry, SAST/DAST, requires more resources.

---

### Drone

| Attribute | Details |
|-----------|---------|
| **License** | Apache-2.0 |
| **Repo** | [harness/drone](https://github.com/harness/drone) |
| **Library** | `library/open-source-tools/devops/` |

CI/CD platform. Pipeline-as-code; integrates with Gitea, GitHub, GitLab.

**Install**: Docker. [docs.drone.io](https://docs.drone.io/)

**Key features**: YAML pipelines, Docker runners, secrets management.

---

### Woodpecker CI

| Attribute | Details |
|-----------|---------|
| **License** | Apache-2.0 |
| **Repo** | [woodpecker-ci/woodpecker](https://github.com/woodpecker-ci/woodpecker) |
| **Library** | `library/open-source-tools/devops/` |

Simple CI engine. Forgejo/Gitea native; Drone-compatible pipeline format.

**Install**: Docker. [woodpecker-ci.org](https://woodpecker-ci.org/)

**Key features**: Lightweight, Forgejo integration, pipeline reuse.

---

### Docker

| Attribute | Details |
|-----------|---------|
| **License** | Apache-2.0 |
| **Repo** | [moby/moby](https://github.com/moby/moby) |
| **Library** | `library/open-source-tools/devops/` |

Containerization platform. Build, ship, run applications in containers.

**Install**: [docs.docker.com/get-docker](https://docs.docker.com/get-docker/)

**Key features**: Images, Compose, daemon-based, industry standard.

---

### Podman

| Attribute | Details |
|-----------|---------|
| **License** | Apache-2.0 |
| **Repo** | [containers/podman](https://github.com/containers/podman) |
| **Library** | `library/open-source-tools/devops/` |

Daemonless containers. Rootless by default; Docker-compatible CLI.

**Install**: `brew install podman` or [podman.io](https://podman.io/)

**Key features**: No daemon, rootless, systemd integration, Docker-compatible.

---

### K3s / K0s

| Attribute | Details |
|-----------|---------|
| **License** | Apache-2.0 |
| **Repo** | [k3s-io/k3s](https://github.com/k3s-io/k3s), [k0sproject/k0s](https://github.com/k0sproject/k0s) |
| **Library** | `library/open-source-tools/devops/` |

Lightweight Kubernetes. K3s: single binary, SQLite; K0s: single binary, no host deps.

**Install**: Single binary; [k3s.io](https://k3s.io/), [k0sproject.io](https://k0sproject.io/)

**Key features**: Edge/IoT, minimal footprint, full K8s API.

---

### MinIO

| Attribute | Details |
|-----------|---------|
| **License** | AGPL-3.0 |
| **Repo** | [minio/minio](https://github.com/minio/minio) |
| **Library** | `library/open-source-tools/devops/` |

S3-compatible object storage. Self-hosted; drop-in for AWS S3.

**Install**: Docker, binary, or Kubernetes. [min.io/docs](https://min.io/docs/)

**Key features**: S3 API, encryption, replication, distributed mode.

---

### Caddy

| Attribute | Details |
|-----------|---------|
| **License** | Apache-2.0 |
| **Repo** | [caddyserver/caddy](https://github.com/caddyserver/caddy) |
| **Library** | `library/open-source-tools/devops/` |

Web server with automatic HTTPS. Caddyfile config; automatic cert renewal.

**Install**: `brew install caddy` or [caddyserver.com](https://caddyserver.com/)

**Key features**: Auto-HTTPS, HTTP/3, reverse proxy, minimal config.

---

### Traefik

| Attribute | Details |
|-----------|---------|
| **License** | MIT |
| **Repo** | [traefik/traefik](https://github.com/traefik/traefik) |
| **Library** | `library/open-source-tools/devops/` |

Reverse proxy and load balancer. Dynamic config from Docker, K8s, Consul.

**Install**: Docker, binary. [doc.traefik.io](https://doc.traefik.io/traefik/)

**Key features**: Auto-discovery, Let's Encrypt, dashboard, middleware.

---

### Nginx

| Attribute | Details |
|-----------|---------|
| **License** | BSD-2-Clause |
| **Repo** | [nginx/nginx](https://github.com/nginx/nginx) |
| **Library** | `library/open-source-tools/devops/` |

Web server and reverse proxy. Industry standard; highly configurable.

**Install**: Package manager or [nginx.org](https://nginx.org/)

**Key features**: High performance, load balancing, static files, proxy.

---

## Security & Privacy

| Tool | Description | Use Case |
|------|-------------|----------|
| **Pi-hole** | Network-wide ad & tracker blocking | DNS-level blocking |
| **AdGuard Home** | DNS-level ad/tracker blocking | Pi-hole alternative |
| **Authentik** | Identity provider, SSO | Okta, Auth0 |
| **Keycloak** | Identity and access management | Okta, Auth0 |
| **Vault** (HashiCorp) | Secrets management | — |
| **Fail2ban** | Intrusion prevention | Block brute-force |
| **OWASP ZAP** | Web app security testing | Burp Suite |
| **CrowdSec** | Collaborative intrusion prevention | Fail2ban successor |

### Pi-hole

| Attribute | Details |
|-----------|---------|
| **License** | EUPL-1.2 |
| **Repo** | [pi-hole/pi-hole](https://github.com/pi-hole/pi-hole) |
| **Library** | `library/open-source-tools/security/` |

Network-wide ad and tracker blocking via DNS. Point router DNS to Pi-hole; blocks at network level.

**Install**: [pi-hole.net](https://pi-hole.net/) — one-line installer or Docker.

**Key features**: Blocklists, query log, dashboard, DHCP optional.

---

### AdGuard Home

| Attribute | Details |
|-----------|---------|
| **License** | GPL-3.0 |
| **Repo** | [AdguardTeam/AdGuardHome](https://github.com/AdguardTeam/AdGuardHome) |
| **Library** | `library/open-source-tools/security/` |

DNS-level ad/tracker blocking. Pi-hole alternative with modern UI.

**Install**: Binary or Docker. [adguard.com/adguard-home](https://adguard.com/adguard-home/overview.html)

**Key features**: DoH/DoT, parental control, stats, blocklists.

---

### Authentik

| Attribute | Details |
|-----------|---------|
| **License** | MIT |
| **Repo** | [goauthentik/authentik](https://github.com/goauthentik/authentik) |
| **Library** | `library/open-source-tools/security/` |

Identity provider and SSO. OIDC, SAML, LDAP; user-friendly admin UI.

**Install**: Docker Compose. [goauthentik.io](https://goauthentik.io/)

**Key features**: Flows, MFA, directory sync, SCIM.

---

### Keycloak

| Attribute | Details |
|-----------|---------|
| **License** | Apache-2.0 |
| **Repo** | [keycloak/keycloak](https://github.com/keycloak/keycloak) |
| **Library** | `library/open-source-tools/security/` |

Identity and access management. OIDC, SAML, LDAP; enterprise-grade.

**Install**: Docker, Kubernetes, or standalone. [keycloak.org](https://www.keycloak.org/)

**Key features**: Realms, federation, adapters, admin REST API.

---

### Vault (HashiCorp)

| Attribute | Details |
|-----------|---------|
| **License** | BSL 1.1 (source-available) |
| **Repo** | [hashicorp/vault](https://github.com/hashicorp/vault) |
| **Library** | `library/open-source-tools/security/` |

Secrets management. Store, lease, rotate secrets; dynamic credentials.

**Install**: Binary or Docker. [developer.hashicorp.com/vault](https://developer.hashicorp.com/vault)

**Key features**: Dynamic secrets, encryption as a service, audit logging.

---

### Fail2ban

| Attribute | Details |
|-----------|---------|
| **License** | GPL-2.0 |
| **Repo** | [fail2ban/fail2ban](https://github.com/fail2ban/fail2ban) |
| **Library** | `library/open-source-tools/security/` |

Intrusion prevention. Monitors logs, bans IPs after failed attempts.

**Install**: `apt install fail2ban` or `brew install fail2ban`

**Key features**: Jails, filters, actions, ban/unban.

---

### OWASP ZAP

| Attribute | Details |
|-----------|---------|
| **License** | Apache-2.0 |
| **Repo** | [zaproxy/zaproxy](https://github.com/zaproxy/zaproxy) |
| **Library** | `library/open-source-tools/security/` |

Web application security testing. DAST, passive scanning, API testing.

**Install**: [zaproxy.org](https://www.zaproxy.org/download/) — GUI or headless.

**Key features**: Automated scans, API, CI integration, plugins.

---

### CrowdSec

| Attribute | Details |
|-----------|---------|
| **License** | MIT |
| **Repo** | [crowdsecurity/crowdsec](https://github.com/crowdsecurity/crowdsec) |
| **Library** | `library/open-source-tools/security/` |

Collaborative intrusion prevention. Behavior-based blocking; blocklists shared across users.

**Install**: [crowdsec.net](https://crowdsec.net/) — one-liner or package manager.

**Key features**: Scenario-based detection, remediation (bouncers), blocklist sharing.

---

## AI & Machine Learning

| Tool | Description | Use Case |
|------|-------------|----------|
| **Ollama** | Run LLMs locally (CLI + API) | Local ChatGPT alternative |
| **LocalAI** | OpenAI-compatible local inference | Drop-in API replacement |
| **LM Studio** | Desktop app for local LLMs | No-code local AI |
| **GPT4All** | Local LLM runner | Privacy-focused chat |
| **Open WebUI** | Web UI for Ollama/LocalAI | Chat interface |
| **Dify** | LLM app development platform | Build AI workflows |
| **Langflow** | Visual LLM workflow builder | No-code AI pipelines |
| **MLflow** | ML experiment tracking | MLOps |
| **Airbyte** | Data integration (ETL) | Fivetran, Stitch |

### Ollama

| Attribute | Details |
|-----------|---------|
| **License** | MIT |
| **Repo** | [ollama/ollama](https://github.com/ollama/ollama) |
| **Library** | `library/open-source-tools/ai-ml/` |

Run LLMs locally. CLI + API at `localhost:11434`; OpenAI-compatible.

**Install**: [ollama.com](https://ollama.com/) — `ollama run llama3`

**Key features**: Model library, GPU support, no cloud, simple API.

---

### LocalAI

| Attribute | Details |
|-----------|---------|
| **License** | MIT |
| **Repo** | [mudler/LocalAI](https://github.com/mudler/LocalAI) |
| **Library** | `library/open-source-tools/ai-ml/` |

OpenAI-compatible local inference. Drop-in replacement for OpenAI API.

**Install**: Docker or binary. [localai.io](https://localai.io/)

**Key features**: OpenAI API, embeddings, image gen, multiple backends.

---

### LM Studio

| Attribute | Details |
|-----------|---------|
| **License** | Proprietary (free for personal use) |
| **Site** | [lmstudio.ai](https://lmstudio.ai/) |
| **Library** | `library/open-source-tools/ai-ml/` |

Desktop app for local LLMs. No-code; download models, chat, use local server.

**Install**: Download from [lmstudio.ai](https://lmstudio.ai/)

**Key features**: Model browser, chat UI, local server, GPU.

---

### GPT4All

| Attribute | Details |
|-----------|---------|
| **License** | Apache-2.0 |
| **Repo** | [nomic-ai/gpt4all](https://github.com/nomic-ai/gpt4all) |
| **Library** | `library/open-source-tools/ai-ml/` |

Local LLM runner. Privacy-focused; runs fully offline.

**Install**: [gpt4all.io](https://gpt4all.io/) — desktop or CLI.

**Key features**: Offline, multiple models, chat UI.

---

### Open WebUI

| Attribute | Details |
|-----------|---------|
| **License** | MIT |
| **Repo** | [open-webui/open-webui](https://github.com/open-webui/open-webui) |
| **Library** | `library/open-source-tools/ai-ml/` |

Web UI for Ollama/LocalAI. Chat interface, model management.

**Install**: Docker. [openwebui.com](https://openwebui.com/)

**Key features**: Chat, RAG, plugins, multi-user.

---

### Dify

| Attribute | Details |
|-----------|---------|
| **License** | Apache-2.0 |
| **Repo** | [langgenius/dify](https://github.com/langgenius/dify) |
| **Library** | `library/open-source-tools/ai-ml/` |

LLM app development platform. Build chatbots, agents, RAG workflows.

**Install**: Docker Compose. [dify.ai](https://dify.ai/)

**Key features**: Visual workflow, RAG, agents, API, plugins.

---

### Langflow

| Attribute | Details |
|-----------|---------|
| **License** | MIT |
| **Repo** | [langflow-ai/langflow](https://github.com/langflow-ai/langflow) |
| **Library** | `library/open-source-tools/ai-ml/` |

Visual LLM workflow builder. Drag-and-drop; no-code AI pipelines.

**Install**: `pip install langflow` or Docker. [langflow.org](https://www.langflow.org/)

**Key features**: Components, flows, API export, integrations.

---

### MLflow

| Attribute | Details |
|-----------|---------|
| **License** | Apache-2.0 |
| **Repo** | [mlflow/mlflow](https://github.com/mlflow/mlflow) |
| **Library** | `library/open-source-tools/ai-ml/` |

ML experiment tracking. Log params, metrics, artifacts; model registry.

**Install**: `pip install mlflow`. [mlflow.org](https://mlflow.org/)

**Key features**: Tracking, projects, models, registry.

---

### Airbyte

| Attribute | Details |
|-----------|---------|
| **License** | MIT |
| **Repo** | [airbytehq/airbyte](https://github.com/airbytehq/airbyte) |
| **Library** | `library/open-source-tools/ai-ml/` |

Data integration (ETL). 300+ connectors; sync DBs, APIs, files to warehouses.

**Install**: Docker Compose. [airbyte.com](https://airbyte.com/)

**Key features**: Connectors, normalization, incremental sync, API.

---

## Productivity & Workflow

| Tool | Description | Replaces |
|------|-------------|----------|
| **n8n** | Workflow automation (self-hosted) | Zapier, Make |
| **Supabase** | Firebase alternative (PostgreSQL) | Firebase |
| **Appsmith** | Low-code internal tools | Retool |
| **Budibase** | Low-code app builder | Internal tools |
| **Excalidraw** | Collaborative whiteboard | Miro, FigJam |
| **Outline** | Team wiki and knowledge base | Notion |
| **BookStack** | Simple wiki platform | Confluence |
| **Plausible** | Privacy-focused analytics | Google Analytics |

### n8n

| Attribute | Details |
|-----------|---------|
| **License** | Fair-code (source-available) |
| **Repo** | [n8n-io/n8n](https://github.com/n8n-io/n8n) |
| **Library** | `library/open-source-tools/productivity/` |

Workflow automation. Nodes for HTTP, DB, AI, webhooks; visual editor; self-hosted Zapier/Make.

**Install**: `npx n8n` or Docker. [docs.n8n.io](https://docs.n8n.io/)

**Key features**: 400+ nodes, webhooks, AI nodes, export/import.

---

### Supabase

| Attribute | Details |
|-----------|---------|
| **License** | Apache-2.0 |
| **Repo** | [supabase/supabase](https://github.com/supabase/supabase) |
| **Library** | `library/open-source-tools/productivity/` |

Firebase alternative. PostgreSQL, auth, storage, realtime, Edge Functions.

**Install**: Docker or [supabase.com](https://supabase.com/) cloud.

**Key features**: Postgres, Row Level Security, auth, storage, realtime.

---

### Appsmith

| Attribute | Details |
|-----------|---------|
| **License** | Apache-2.0 |
| **Repo** | [appsmithorg/appsmith](https://github.com/appsmithorg/appsmith) |
| **Library** | `library/open-source-tools/productivity/` |

Low-code internal tools. Connect to DBs, APIs; build admin panels, dashboards.

**Install**: Docker. [appsmith.com](https://www.appsmith.com/)

**Key features**: Drag-and-drop, JS, DB/API connectors, Git sync.

---

### Budibase

| Attribute | Details |
|-----------|---------|
| **License** | GPL-3.0 |
| **Repo** | [Budibase/budibase](https://github.com/Budibase/budibase) |
| **Library** | `library/open-source-tools/productivity/` |

Low-code app builder. Internal tools, forms, workflows.

**Install**: Docker. [budibase.com](https://budibase.com/)

**Key features**: DB connectors, automations, self-host or cloud.

---

### Excalidraw

| Attribute | Details |
|-----------|---------|
| **License** | MIT |
| **Repo** | [excalidraw/excalidraw](https://github.com/excalidraw/excalidraw) |
| **Library** | `library/open-source-tools/productivity/` |

Collaborative whiteboard. Hand-drawn style; real-time collab; Miro/FigJam alternative.

**Install**: [excalidraw.com](https://excalidraw.com/) or self-host static files.

**Key features**: Hand-drawn look, export SVG/PNG, end-to-end encrypted rooms.

---

### Outline

| Attribute | Details |
|-----------|---------|
| **License** | BSD-2-Clause |
| **Repo** | [outline/outline](https://github.com/outline/outline) |
| **Library** | `library/open-source-tools/productivity/` |

Team wiki and knowledge base. Notion-like; Markdown, collab, search.

**Install**: Docker. [getoutline.com](https://www.getoutline.com/)

**Key features**: Collections, Slack integration, SSO, full-text search.

---

### BookStack

| Attribute | Details |
|-----------|---------|
| **License** | MIT |
| **Repo** | [BookStackApp/BookStack](https://github.com/BookStackApp/BookStack) |
| **Library** | `library/open-source-tools/productivity/` |

Simple wiki platform. Books, chapters, pages; WYSIWYG editor.

**Install**: Docker or manual. [bookstackapp.com](https://www.bookstackapp.com/)

**Key features**: Hierarchical structure, roles, export PDF, LDAP.

---

### Plausible

| Attribute | Details |
|-----------|---------|
| **License** | AGPL-3.0 |
| **Repo** | [plausible/analytics](https://github.com/plausible/analytics) |
| **Library** | `library/open-source-tools/productivity/` |

Privacy-focused analytics. No cookies; lightweight script; GDPR-friendly.

**Install**: Self-host or [plausible.io](https://plausible.io/) cloud.

**Key features**: No cookies, lightweight, goals, revenue tracking.

---

## Monitoring & Observability

| Tool | Description | Use Case |
|------|-------------|----------|
| **Prometheus** | Metrics collection & alerting | — |
| **Grafana** | Dashboards & visualization | — |
| **Loki** | Log aggregation (like Prometheus for logs) | ELK alternative |
| **VictoriaMetrics** | Prometheus-compatible, faster | Prometheus scaling |
| **Netdata** | Real-time performance monitoring | Low-overhead metrics |
| **Uptime Kuma** | Uptime monitoring & status page | UptimeRobot |
| **Grafana Tempo** | Distributed tracing | Jaeger alternative |
| **Jaeger** | Distributed tracing | — |

### Prometheus

| Attribute | Details |
|-----------|---------|
| **License** | Apache-2.0 |
| **Repo** | [prometheus/prometheus](https://github.com/prometheus/prometheus) |
| **Library** | `library/open-source-tools/monitoring/` |

Metrics collection and alerting. Pull model; time-series DB; PromQL.

**Install**: Binary or Docker. [prometheus.io](https://prometheus.io/)

**Key features**: Scraping, alerting, service discovery, federation.

---

### Grafana

| Attribute | Details |
|-----------|---------|
| **License** | AGPL-3.0 |
| **Repo** | [grafana/grafana](https://github.com/grafana/grafana) |
| **Library** | `library/open-source-tools/monitoring/` |

Dashboards and visualization. Connect to Prometheus, Loki, InfluxDB, etc.

**Install**: Docker or package manager. [grafana.com](https://grafana.com/)

**Key features**: Panels, alerts, plugins, Loki/Tempo integration.

---

### Loki

| Attribute | Details |
|-----------|---------|
| **License** | AGPL-3.0 |
| **Repo** | [grafana/loki](https://github.com/grafana/loki) |
| **Library** | `library/open-source-tools/monitoring/` |

Log aggregation. Like Prometheus for logs; indexes labels, not content.

**Install**: Docker or Helm. [grafana.com/oss/loki](https://grafana.com/oss/loki/)

**Key features**: LogQL, Prometheus-style, Grafana integration.

---

### VictoriaMetrics

| Attribute | Details |
|-----------|---------|
| **License** | Apache-2.0 |
| **Repo** | [VictoriaMetrics/VictoriaMetrics](https://github.com/VictoriaMetrics/VictoriaMetrics) |
| **Library** | `library/open-source-tools/monitoring/` |

Prometheus-compatible, faster and more storage-efficient. Drop-in replacement.

**Install**: Binary or Docker. [victoriametrics.com](https://victoriametrics.com/)

**Key features**: PromQL, long-term storage, clustering.

---

### Netdata

| Attribute | Details |
|-----------|---------|
| **License** | GPL-3.0 |
| **Repo** | [netdata/netdata](https://github.com/netdata/netdata) |
| **Library** | `library/open-source-tools/monitoring/` |

Real-time performance monitoring. Per-second metrics; zero config.

**Install**: One-liner. [netdata.cloud](https://www.netdata.cloud/)

**Key features**: Per-second, zero config, anomaly detection.

---

### Uptime Kuma

| Attribute | Details |
|-----------|---------|
| **License** | MIT |
| **Repo** | [louislam/uptime-kuma](https://github.com/louislam/uptime-kuma) |
| **Library** | `library/open-source-tools/monitoring/` |

Uptime monitoring and status page. HTTP, TCP, ping; status page for incidents.

**Install**: Docker. [uptime.kuma.pet](https://uptime.kuma.pet/)

**Key features**: 90+ monitor types, status page, notifications.

---

### Grafana Tempo

| Attribute | Details |
|-----------|---------|
| **License** | AGPL-3.0 |
| **Repo** | [grafana/tempo](https://github.com/grafana/tempo) |
| **Library** | `library/open-source-tools/monitoring/` |

Distributed tracing. OpenTelemetry; Grafana integration; Jaeger-compatible.

**Install**: Docker or Helm. [grafana.com/oss/tempo](https://grafana.com/oss/tempo/)

**Key features**: Trace-to-metrics, exemplars, multi-tenant.

---

### Jaeger

| Attribute | Details |
|-----------|---------|
| **License** | Apache-2.0 |
| **Repo** | [jaegertracing/jaeger](https://github.com/jaegertracing/jaeger) |
| **Library** | `library/open-source-tools/monitoring/` |

Distributed tracing. OpenTracing/OpenTelemetry; trace collection and UI.

**Install**: Docker or binary. [jaegertracing.io](https://www.jaegertracing.io/)

**Key features**: Sampling, storage backends, service graph.

---

## Databases & Data

| Tool | Description | Use Case |
|------|-------------|----------|
| **PostgreSQL** | Relational database | MySQL, SQL Server |
| **SQLite** | Embedded database | File-based storage |
| **Redis** | In-memory data store | Caching, queues |
| **ClickHouse** | Columnar analytics DB | BigQuery, Snowflake |
| **TimescaleDB** | Time-series on PostgreSQL | InfluxDB |
| **Meilisearch** | Fast typo-tolerant search | Elasticsearch (simpler) |
| **Typesense** | Fast search engine | Algolia |
| **Qdrant** | Vector database for AI | Pinecone, Weaviate |

### PostgreSQL

| Attribute | Details |
|-----------|---------|
| **License** | PostgreSQL License |
| **Repo** | [postgres/postgres](https://github.com/postgres/postgres) |
| **Library** | `library/open-source-tools/databases/` |

Relational database. ACID; JSON, full-text search; extensions (PostGIS, pgvector).

**Install**: Package manager or [postgresql.org](https://www.postgresql.org/)

**Key features**: Extensible, JSONB, partitioning, replication.

---

### SQLite

| Attribute | Details |
|-----------|---------|
| **License** | Public domain |
| **Site** | [sqlite.org](https://www.sqlite.org/) |
| **Library** | `library/open-source-tools/databases/` |

Embedded database. Single file; no server; ubiquitous.

**Install**: Usually pre-installed; or [sqlite.org/download](https://www.sqlite.org/download.html)

**Key features**: Zero config, serverless, WAL mode, FTS5.

---

### Redis

| Attribute | Details |
|-----------|---------|
| **License** | BSD-3-Clause |
| **Repo** | [redis/redis](https://github.com/redis/redis) |
| **Library** | `library/open-source-tools/databases/` |

In-memory data store. Strings, hashes, lists, sets; pub/sub; Lua scripting.

**Install**: `brew install redis` or [redis.io](https://redis.io/)

**Key features**: Caching, sessions, queues, real-time.

---

### ClickHouse

| Attribute | Details |
|-----------|---------|
| **License** | Apache-2.0 |
| **Repo** | [ClickHouse/ClickHouse](https://github.com/ClickHouse/ClickHouse) |
| **Library** | `library/open-source-tools/databases/` |

Columnar analytics DB. OLAP; SQL; very fast aggregations.

**Install**: Package manager or Docker. [clickhouse.com](https://clickhouse.com/)

**Key features**: Columnar, compression, distributed, SQL.

---

### TimescaleDB

| Attribute | Details |
|-----------|---------|
| **License** | Apache-2.0 (Timescale License for cloud) |
| **Repo** | [timescale/timescaledb](https://github.com/timescale/timescaledb) |
| **Library** | `library/open-source-tools/databases/` |

Time-series extension for PostgreSQL. Hypertables, compression, continuous aggregates.

**Install**: Extension for Postgres. [timescale.com](https://www.timescale.com/)

**Key features**: Postgres-native, compression, retention policies.

---

### Meilisearch

| Attribute | Details |
|-----------|---------|
| **License** | MIT |
| **Repo** | [meilisearch/meilisearch](https://github.com/meilisearch/meilisearch) |
| **Library** | `library/open-source-tools/databases/` |

Fast typo-tolerant search. REST API; instant search; typo tolerance.

**Install**: `curl -L https://install.meilisearch.com | sh` or Docker.

**Key features**: Typo tolerance, facets, instant, REST.

---

### Typesense

| Attribute | Details |
|-----------|---------|
| **License** | GPL-3.0 |
| **Repo** | [typesense/typesense](https://github.com/typesense/typesense) |
| **Library** | `library/open-source-tools/databases/` |

Fast search engine. Typo-tolerant; instant; Algolia alternative.

**Install**: Binary or Docker. [typesense.org](https://typesense.org/)

**Key features**: Typo tolerance, faceting, geo-search, API.

---

### Qdrant

| Attribute | Details |
|-----------|---------|
| **License** | Apache-2.0 |
| **Repo** | [qdrant/qdrant](https://github.com/qdrant/qdrant) |
| **Library** | `library/open-source-tools/databases/` |

Vector database for AI. Embeddings, similarity search; RAG, recommendations.

**Install**: Docker or binary. [qdrant.tech](https://qdrant.tech/)

**Key features**: HNSW, filtering, payload, gRPC/REST.

---

## Infrastructure & IaC

| Tool | Description | Replaces |
|------|-------------|----------|
| **Terraform** | Infrastructure as Code | CloudFormation |
| **Pulumi** | IaC with real languages (Python, Go, TypeScript) | Terraform |
| **Ansible** | Configuration management | Chef, Puppet |
| **Packer** | Machine image builder | — |
| **Vagrant** | Dev environment provisioning | — |

### Terraform

| Attribute | Details |
|-----------|---------|
| **License** | BSL 1.1 (source-available) |
| **Repo** | [hashicorp/terraform](https://github.com/hashicorp/terraform) |
| **Library** | `library/open-source-tools/devops/` |

Infrastructure as Code. Declarative HCL; 3000+ providers; plan/apply workflow.

**Install**: [terraform.io](https://www.terraform.io/) — binary or `brew install terraform`

**Key features**: State, modules, providers, plan before apply.

---

### Pulumi

| Attribute | Details |
|-----------|---------|
| **License** | Apache-2.0 |
| **Repo** | [pulumi/pulumi](https://github.com/pulumi/pulumi) |
| **Library** | `library/open-source-tools/devops/` |

IaC with real languages. Python, Go, TypeScript; same providers as Terraform.

**Install**: [pulumi.com](https://www.pulumi.com/) — `brew install pulumi`

**Key features**: Real languages, state backend, preview, secrets.

---

### Ansible

| Attribute | Details |
|-----------|---------|
| **License** | GPL-3.0 |
| **Repo** | [ansible/ansible](https://github.com/ansible/ansible) |
| **Library** | `library/open-source-tools/devops/` |

Configuration management. Agentless (SSH); YAML playbooks; idempotent.

**Install**: `pip install ansible` or `brew install ansible`

**Key features**: Playbooks, roles, vault, inventory, modules.

---

### Packer

| Attribute | Details |
|-----------|---------|
| **License** | MPL-2.0 |
| **Repo** | [hashicorp/packer](https://github.com/hashicorp/packer) |
| **Library** | `library/open-source-tools/devops/` |

Machine image builder. AMI, VM, Docker; provisioners; multi-cloud.

**Install**: [packer.io](https://www.packer.io/) — binary or `brew install packer`

**Key features**: Builders, provisioners, post-processors.

---

### Vagrant

| Attribute | Details |
|-----------|---------|
| **License** | MIT |
| **Repo** | [hashicorp/vagrant](https://github.com/hashicorp/vagrant) |
| **Library** | `library/open-source-tools/devops/` |

Dev environment provisioning. VM lifecycle; providers (VirtualBox, VMware, etc.).

**Install**: [vagrantup.com](https://www.vagrantup.com/) — `brew install vagrant`

**Key features**: Boxes, providers, provisioning, plugins.

---

## Communication & Collaboration

| Tool | Description | Replaces |
|------|-------------|----------|
| **Mattermost** | Team messaging | Slack |
| **Rocket.Chat** | Team chat & collaboration | Slack, Teams |
| **Matrix** / **Element** | Decentralized messaging | — |
| **Zulip** | Threaded team chat | Slack |
| **Jitsi** | Video conferencing | Zoom |
| **BigBlueButton** | Web conferencing for education | Zoom |
| **Mailcow** | Email server (Docker) | Gmail (self-hosted) |
| **iRedMail** | Full email server stack | — |

### Mattermost

| Attribute | Details |
|-----------|---------|
| **License** | AGPL-3.0 / Enterprise |
| **Repo** | [mattermost/mattermost](https://github.com/mattermost/mattermost) |
| **Library** | `library/open-source-tools/productivity/` |

Team messaging. Slack-compatible; self-hosted; channels, threads, integrations.

**Install**: Docker or binary. [mattermost.com](https://mattermost.com/)

**Key features**: Channels, threads, integrations, LDAP, SSO.

---

### Rocket.Chat

| Attribute | Details |
|-----------|---------|
| **License** | MIT |
| **Repo** | [RocketChat/Rocket.Chat](https://github.com/RocketChat/Rocket.Chat) |
| **Library** | `library/open-source-tools/productivity/` |

Team chat and collaboration. Channels, DMs, video; Slack/Teams alternative.

**Install**: Docker or Snap. [rocket.chat](https://www.rocket.chat/)

**Key features**: Channels, threads, video, omnichannel, apps.

---

### Matrix / Element

| Attribute | Details |
|-----------|---------|
| **License** | Apache-2.0 |
| **Repo** | [matrix-org/synapse](https://github.com/matrix-org/synapse), [element-hq/element-web](https://github.com/element-hq/element-web) |
| **Library** | `library/open-source-tools/productivity/` |

Decentralized messaging. Federated; E2E encryption; Element is the reference client.

**Install**: Synapse + Element; [matrix.org](https://matrix.org/)

**Key features**: Federation, E2E, bridges, spaces.

---

### Zulip

| Attribute | Details |
|-----------|---------|
| **License** | Apache-2.0 |
| **Repo** | [zulip/zulip](https://github.com/zulip/zulip) |
| **Library** | `library/open-source-tools/productivity/` |

Threaded team chat. Topic-based threads; better for async.

**Install**: Docker or manual. [zulip.com](https://zulip.com/)

**Key features**: Threads, topics, integrations, search.

---

### Jitsi

| Attribute | Details |
|-----------|---------|
| **License** | Apache-2.0 |
| **Repo** | [jitsi/jitsi-meet](https://github.com/jitsi/jitsi-meet) |
| **Library** | `library/open-source-tools/productivity/` |

Video conferencing. WebRTC; no account required; self-hosted Zoom alternative.

**Install**: Docker or Debian packages. [jitsi.org](https://jitsi.org/)

**Key features**: WebRTC, recording, livestreaming, E2E.

---

### BigBlueButton

| Attribute | Details |
|-----------|---------|
| **License** | LGPL-3.0 |
| **Repo** | [bigbluebutton/bigbluebutton](https://github.com/bigbluebutton/bigbluebutton) |
| **Library** | `library/open-source-tools/productivity/` |

Web conferencing for education. Polls, breakout rooms, whiteboard.

**Install**: [bigbluebutton.org](https://bigbluebutton.org/) — Ubuntu install script.

**Key features**: Education-focused, breakout rooms, polls, recordings.

---

### Mailcow

| Attribute | Details |
|-----------|---------|
| **License** | GPL-3.0 |
| **Repo** | [mailcow/mailcow-dockerized](https://github.com/mailcow/mailcow-dockerized) |
| **Library** | `library/open-source-tools/productivity/` |

Email server (Docker). Postfix, Dovecot, SOGo; web UI; full stack.

**Install**: Docker Compose. [mailcow.email](https://mailcow.email/)

**Key features**: IMAP/SMTP, webmail, antivirus, DKIM.

---

### iRedMail

| Attribute | Details |
|-----------|---------|
| **License** | GPL-3.0 |
| **Site** | [iredmail.org](https://www.iredmail.org/) |
| **Library** | `library/open-source-tools/productivity/` |

Full email server stack. One-installer; Postfix, Dovecot, roundcube.

**Install**: [iredmail.org/download](https://www.iredmail.org/download.html) — install script.

**Key features**: Full stack, LDAP/MySQL, webmail, antispam.

---

## Documentation & Knowledge

| Tool | Description | Replaces |
|------|-------------|----------|
| **Docusaurus** | Documentation sites | — |
| **MkDocs** | Static site from Markdown | — |
| **Obsidian** | Local-first note-taking | Notion (local) |
| **Logseq** | Outliner + knowledge graph | Roam Research |
| **Trilium** | Hierarchical note-taking | Evernote |
| **Wiki.js** | Modern wiki platform | MediaWiki |

### Docusaurus

| Attribute | Details |
|-----------|---------|
| **License** | MIT |
| **Repo** | [facebook/docusaurus](https://github.com/facebook/docusaurus) |
| **Library** | `library/open-source-tools/productivity/` |

Documentation sites. React-based; MDX; versioning, search.

**Install**: `npx create-docusaurus@latest`. [docusaurus.io](https://docusaurus.io/)

**Key features**: MDX, versioning, i18n, search, themes.

---

### MkDocs

| Attribute | Details |
|-----------|---------|
| **License** | BSD-2-Clause |
| **Repo** | [mkdocs/mkdocs](https://github.com/mkdocs/mkdocs) |
| **Library** | `library/open-source-tools/productivity/` |

Static site from Markdown. Python; themes (Material); plugins.

**Install**: `pip install mkdocs`. [mkdocs.org](https://www.mkdocs.org/)

**Key features**: Markdown, themes, plugins, search.

---

### Obsidian

| Attribute | Details |
|-----------|---------|
| **License** | Proprietary (free for personal use) |
| **Site** | [obsidian.md](https://obsidian.md/) |
| **Library** | `library/open-source-tools/productivity/` |

Local-first note-taking. Markdown; graph view; plugins; sync optional.

**Install**: [obsidian.md](https://obsidian.md/) — desktop app.

**Key features**: Local-first, graph, backlinks, plugins, vaults.

---

### Logseq

| Attribute | Details |
|-----------|---------|
| **License** | AGPL-3.0 |
| **Repo** | [logseq/logseq](https://github.com/logseq/logseq) |
| **Library** | `library/open-source-tools/productivity/` |

Outliner + knowledge graph. Block-based; Roam-like; local-first.

**Install**: [logseq.com](https://logseq.com/) — desktop or web.

**Key features**: Outliner, graph, queries, plugins.

---

### Trilium

| Attribute | Details |
|-----------|---------|
| **License** | AGPL-3.0 |
| **Repo** | [zadam/trilium](https://github.com/zadam/trilium) |
| **Library** | `library/open-source-tools/productivity/` |

Hierarchical note-taking. Self-hosted; rich editor; scripts.

**Install**: Node.js or Docker. [github.com/zadam/trilium](https://github.com/zadam/trilium)

**Key features**: Hierarchy, attributes, scripts, sync.

---

### Wiki.js

| Attribute | Details |
|-----------|---------|
| **License** | AGPL-3.0 |
| **Repo** | [requarks/wiki](https://github.com/requarks/wiki) |
| **Library** | `library/open-source-tools/productivity/` |

Modern wiki platform. Git sync; Markdown; auth; search.

**Install**: Docker. [js.wiki](https://js.wiki/)

**Key features**: Git sync, auth, editor, search.

---

## Backup & Sync

| Tool | Description | Use Case |
|------|-------------|----------|
| **Restic** | Fast, encrypted backups | Borg alternative |
| **BorgBackup** | Deduplicating backups | — |
| **Duplicati** | Backup with encryption | — |

### Restic

| Attribute | Details |
|-----------|---------|
| **License** | BSD-2-Clause |
| **Repo** | [restic/restic](https://github.com/restic/restic) |
| **Library** | `library/open-source-tools/` |

Fast, encrypted backups. Deduplication; multiple backends (S3, SFTP, local).

**Install**: `brew install restic` or [restic.net](https://restic.net/)

**Key features**: Encryption, dedup, snapshots, prune.

---

### BorgBackup

| Attribute | Details |
|-----------|---------|
| **License** | BSD-3-Clause |
| **Repo** | [borgbackup/borg](https://github.com/borgbackup/borg) |
| **Library** | `library/open-source-tools/` |

Deduplicating backups. Compression; encryption; mountable archives.

**Install**: `brew install borgbackup` or package manager.

**Key features**: Dedup, compression, encryption, mount.

---

### Duplicati

| Attribute | Details |
|-----------|---------|
| **License** | LGPL |
| **Repo** | [duplicati/duplicati](https://github.com/duplicati/duplicati) |
| **Library** | `library/open-source-tools/` |

Backup with encryption. Web UI; cloud backends; scheduling.

**Install**: [duplicati.com](https://www.duplicati.com/) — Windows/Linux/macOS.

**Key features**: Web UI, encryption, cloud backends, scheduling.

---

## Developer Tools

| Tool | Description | Use Case |
|------|-------------|----------|
| **Codeberg** | Git hosting (non-profit) | GitHub |
| **SourceHut** | Minimalist dev platform | GitHub |
| **Sentry** (self-hosted) | Error tracking | — |
| **Grafana Loki** | Log aggregation | — |
| **SvelteKit** | Full-stack framework | Next.js |
| **FastAPI** | Python API framework | Flask, Django REST |

### Codeberg

| Attribute | Details |
|-----------|---------|
| **License** | Non-profit hosting |
| **Site** | [codeberg.org](https://codeberg.org/) |
| **Library** | `library/open-source-tools/devops/` |

Git hosting (non-profit). Gitea-based; EU-based; no tracking.

**Use**: Host repos at [codeberg.org](https://codeberg.org/)

**Key features**: Gitea, issues, CI, non-profit.

---

### SourceHut

| Attribute | Details |
|-----------|---------|
| **License** | AGPL-3.0 (self-hosted) |
| **Repo** | [sr.ht](https://sr.ht/) |
| **Library** | `library/open-source-tools/devops/` |

Minimalist dev platform. Git, CI, lists, paste; no JavaScript by default.

**Use**: [sr.ht](https://sr.ht/) or self-host.

**Key features**: Minimal, email-centric, builds, lists.

---

### Sentry (self-hosted)

| Attribute | Details |
|-----------|---------|
| **License** | BSL (source-available) |
| **Repo** | [getsentry/sentry](https://github.com/getsentry/sentry) |
| **Library** | `library/open-source-tools/devops/` |

Error tracking. Stack traces, release tracking, performance.

**Install**: Docker or [sentry.io](https://sentry.io/) cloud.

**Key features**: Errors, performance, releases, integrations.

---

### SvelteKit

| Attribute | Details |
|-----------|---------|
| **License** | MIT |
| **Repo** | [sveltejs/kit](https://github.com/sveltejs/kit) |
| **Library** | `library/open-source-tools/devops/` |

Full-stack framework. Svelte; SSR; adapters for Vercel, Node, etc.

**Install**: `npm create svelte@latest`. [kit.svelte.dev](https://kit.svelte.dev/)

**Key features**: SSR, adapters, forms, load functions.

---

### FastAPI

| Attribute | Details |
|-----------|---------|
| **License** | MIT |
| **Repo** | [tiangolo/fastapi](https://github.com/tiangolo/fastapi) |
| **Library** | `library/open-source-tools/devops/` |

Python API framework. Async; automatic OpenAPI; Pydantic validation.

**Install**: `pip install fastapi uvicorn`. [fastapi.tiangolo.com](https://fastapi.tiangolo.com/)

**Key features**: Async, OpenAPI, validation, dependency injection.

---

## Esoteric & Niche

*The copy-party tier: single-file servers, odd protocols, local-first sync engines, and tools that do one weird thing brilliantly.*

### Single-File / Portable Servers

| Tool | Description | Why It's Niche |
|------|-------------|---------------|
| **copy-party** | Portable file server in a single Python file | Zero deps, WebDAV + FTP + TFTP, media indexer, zeroconf. Drop `copyparty-sfx.py` and run. |
| **redbean** | Single zip-executable web server | Cosmopolitan Libc—one binary runs on Linux, macOS, Windows, BSD, ARM64. Embeds Lua, SQLite, MbedTLS. 2MB. |
| **Algernon** | Pure-Go web server, single binary | Lua, Teal, Markdown, HTTP/2, QUIC, Redis, SQLite, PostgreSQL. Docker image &lt;12MB. |
| **Kawipiko** | Blazingly fast static HTTP server | Go + fasthttp + embedded CDB. Minimal, high concurrency. |

#### copy-party

| Attribute | Details |
|-----------|---------|
| **License** | MIT |
| **Repo** | [9001/copyparty](https://github.com/9001/copyparty) |
| **Library** | `library/open-source-tools/esoteric/` |

Portable file server in a single Python file. Zero deps; WebDAV, FTP, TFTP; media indexer; zeroconf. Drop `copyparty-sfx.py` and run.

**Install**: Download `copyparty-sfx.py` from [GitHub](https://github.com/9001/copyparty). `python copyparty-sfx.py -d /path`

---

#### redbean

| Attribute | Details |
|-----------|---------|
| **License** | ISC |
| **Site** | [redbean.dev](https://redbean.dev/) |
| **Library** | `library/open-source-tools/esoteric/` |

Single zip-executable web server. Cosmopolitan Libc—one binary runs on Linux, macOS, Windows, BSD, ARM64. Embeds Lua, SQLite, MbedTLS. ~2MB.

**Install**: Download `redbean.com` from [redbean.dev](https://redbean.dev/). Add HTML/Lua, run.

---

#### Algernon

| Attribute | Details |
|-----------|---------|
| **License** | MIT |
| **Repo** | [xyproto/algernon](https://github.com/xyproto/algernon) |
| **Library** | `library/open-source-tools/esoteric/` |

Pure-Go web server, single binary. Lua, Teal, Markdown, HTTP/2, QUIC, Redis, SQLite, PostgreSQL. Docker image &lt;12MB.

**Install**: `go install github.com/xyproto/algernon@latest` or Docker.

---

### File Transfer & LAN

| Tool | Description | Why It's Niche |
|------|-------------|---------------|
| **croc** | Encrypted file transfer with a code phrase | PAKE auth (3 random words). LAN relay when on same network. Resumable. No server setup. |
| **e2ecp** (Schollz) | E2E encrypted file transfer | Web + CLI. Same author as croc. |

#### croc

| Attribute | Details |
|-----------|---------|
| **License** | MIT |
| **Repo** | [schollz/croc](https://github.com/schollz/croc) |
| **Library** | `library/open-source-tools/esoteric/` |

Encrypted file transfer with a code phrase. PAKE auth (3 random words). LAN relay when on same network. Resumable. No server setup.

**Install**: `brew install croc` or [github.com/schollz/croc](https://github.com/schollz/croc). Sender: `croc send file.zip` → get 3 words. Receiver: `croc [words]`.

---

### HTML Over the Wire (No-JS-First)

| Tool | Description | Why It's Niche |
|------|-------------|---------------|
| **htmx** | Dynamic UIs via HTML attributes | `hx-post`, `hx-swap`, `hx-target`. No build step. Idiomorph for morphing. |
| **Unpoly** | Progressive enhancement for HTML | Fragment updates, overlays, response caching. Graceful degradation. |
| **Turbo** (Hotwire) | Drive, Frames, Streams | 37 Signals. Replace body, sections, or stream actions. |

#### htmx

| Attribute | Details |
|-----------|---------|
| **License** | BSD-2-Clause |
| **Repo** | [bigskysoftware/htmx](https://github.com/bigskysoftware/htmx) |
| **Library** | `library/open-source-tools/esoteric/` |

Dynamic UIs via HTML attributes. `hx-post`, `hx-swap`, `hx-target`. No build step. Idiomorph for morphing. HTML-over-the-wire.

**Install**: CDN or npm. [htmx.org](https://htmx.org/)

---

### Local-First & CRDTs

| Tool | Description | Why It's Niche |
|------|-------------|---------------|
| **Automerge** | CRDT-based sync engine | Conflict-free replicated data. Offline-first, multi-language. Martin Kleppmann. |
| **Concordant** | Local-first datastore with CRDTs | Edge/mobile, E2E encryption, auto-sync. |
| **Litestream** | SQLite replication to S3 | Continuous backup, point-in-time recovery. Single binary. |
| **LiteFS** | Distributed SQLite (Fly.io) | FUSE passthrough, replicates across nodes. Primary/replica. |

### Terminal & CLI (Modern Replacements)

| Tool | Description | Why It's Niche |
|------|-------------|---------------|
| **fzf** | Fuzzy finder for anything | Pipes, history, files, processes. Vim/Bash/Zsh integration. |
| **ripgrep** (rg) | grep, but 5–10× faster | Respects .gitignore, skips binaries, syntax highlight. |
| **fd** | find, but intuitive | `fd "\.tsx$"` vs `find . -name "*.tsx"`. |
| **bat** | cat with syntax highlighting | Git integration, pager mode. |
| **eza** | ls with git status, tree view | Color-coded, exa successor. |
| **zoxide** | Smarter `cd` | Learns dirs, `z foo` jumps. |
| **atuin** | Magical shell history | Encrypted sync, search, stats. |
| **zellij** | Terminal multiplexer | Panes, plugins (WASM), multiplayer. tmux alternative. |
| **Gum** (Charm) | TUI components for shell scripts | `gum choose`, `gum input`, `gum confirm`. No Go required. |
| **Just** | Task runner, not a build system | `justfile` instead of Makefile. Cross-platform, better errors. |

#### fzf

| Attribute | Details |
|-----------|---------|
| **License** | MIT |
| **Repo** | [junegunn/fzf](https://github.com/junegunn/fzf) |
| **Library** | `library/open-source-tools/esoteric/` |

Fuzzy finder for anything. Pipes, history, files, processes. Vim/Bash/Zsh integration.

**Install**: `brew install fzf`. [github.com/junegunn/fzf](https://github.com/junegunn/fzf)

---

#### ripgrep (rg)

| Attribute | Details |
|-----------|---------|
| **License** | MIT |
| **Repo** | [BurntSushi/ripgrep](https://github.com/BurntSushi/ripgrep) |
| **Library** | `library/open-source-tools/esoteric/` |

grep, but 5–10× faster. Respects .gitignore, skips binaries, syntax highlight.

**Install**: `brew install ripgrep`. `rg "pattern"` — [github.com/BurntSushi/ripgrep](https://github.com/BurntSushi/ripgrep)

---

#### fd

| Attribute | Details |
|-----------|---------|
| **License** | MIT/Apache-2.0 |
| **Repo** | [sharkdp/fd](https://github.com/sharkdp/fd) |
| **Library** | `library/open-source-tools/esoteric/` |

find, but intuitive. `fd "\.tsx$"` vs `find . -name "*.tsx"`. Color, .gitignore by default.

**Install**: `brew install fd`. [github.com/sharkdp/fd](https://github.com/sharkdp/fd)

---

#### bat

| Attribute | Details |
|-----------|---------|
| **License** | MIT/Apache-2.0 |
| **Repo** | [sharkdp/bat](https://github.com/sharkdp/bat) |
| **Library** | `library/open-source-tools/esoteric/` |

cat with syntax highlighting. Git integration, pager mode.

**Install**: `brew install bat`. [github.com/sharkdp/bat](https://github.com/sharkdp/bat)

---

#### Just

| Attribute | Details |
|-----------|---------|
| **License** | MIT |
| **Repo** | [casey/just](https://github.com/casey/just) |
| **Library** | `library/open-source-tools/esoteric/` |

Task runner, not a build system. `justfile` instead of Makefile. Cross-platform, better errors.

**Install**: `brew install just`. [just.systems](https://just.systems/)

---

### Typesetting & Documents

| Tool | Description | Why It's Niche |
|------|-------------|---------------|
| **Typst** | Markup-based typesetting | LaTeX alternative. Millisecond compile. Single binary. Math, tables, bib. |
| **SILE** | Simon's Improved Layout Engine | Lua-scriptable typesetter. Different paradigm than TeX. |
| **OTranscribe** | Transcribe audio interviews | Keyboard shortcuts, timestamps, no cloud. |
| **QPDF** | CLI PDF transformations | Encrypt, merge, split, convert. No GUI. |

### Transcription & Speech

| Tool | Description | Why It's Niche |
|------|-------------|---------------|
| **whisper.cpp** | Whisper model, C++ port | Single binary, CPU-only, no Python. Offline, private. |
| **OTranscribe** | Manual transcription helper | Play/pause with foot pedal, timestamps. |

### Database Oddities

| Tool | Description | Why It's Niche |
|------|-------------|---------------|
| **wddbfs** | Mount SQLite as a filesystem | WebDAV mount. Tables → CSV/TSV/JSON/JSONL. `grep` your DB. |
| **sqlfs** | SQLite FUSE filesystem | True FUSE mount with sqlcipher. |

### Other Curiosities

| Tool | Description | Why It's Niche |
|------|-------------|---------------|
| **Xonsh** | Python-powered shell | Unix commands + Python in one REPL. |
| **Pagefind** | Static search, runs in browser | No server. Hugo, Eleventy, Astro, etc. |
| **CryptPad** | E2E encrypted office suite | Real-time collab. Admins can't read content. |
| **SiYuan** | Privacy-first knowledge management | TypeScript + Go. Block-based, local-first. |
| **Flameshot** | Screenshot + OCR + barcode decode | Composable with other tools. |
| **Infisical** | Secret management, dev-friendly | Vault alternative, simpler onboarding. |
| **River** | Online machine learning (Python) | Streaming ML. |
| **Open Chaos** / **GitConsensus** | Democratic PR voting | "Twitch Plays GitHub"—community controls project. |

---

## Quick Links & Resources

- **[library/open-source-tools/](library/open-source-tools/)** — Local library folder for tool configs, scripts, and reference materials
- **[awesome-selfhosted](https://awesome-selfhosted.net/)** — Curated list of self-hosted software
- **[AlternativeTo](https://alternativeto.net/)** — Find alternatives to any software
- **[AlternativeOSS](https://alternativeoss.com/)** — Open source alternatives directory (500+)
- **[Self-Hosted Survey](https://selfhosted-survey.deployn.de/)** — Community-voted favorites
- **[Hacker News](https://news.ycombinator.com/)** — "Show HN" and "Ask HN" surface obscure tools
- **[Lobste.rs](https://lobste.rs/)** — Tech links with tagging; good for niche discoveries
- **[Star History](https://www.star-history.com/)** — Underrated OSS projects, monthly picks

---

## How to Choose

1. **Start small** — Pick one or two tools per category.
2. **Docker first** — Many tools have official images; try before committing.
3. **Check resource needs** — Light options: Gitea, Caddy, Uptime Kuma. Heavier: GitLab, Nextcloud.
4. **Community & docs** — Prefer projects with active maintenance and clear documentation.

---

*Last updated: February 2025. Library folder: [library/](library/).*
