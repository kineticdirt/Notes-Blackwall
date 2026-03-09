# Open Source Tools — Library & Usage Lore

A compendium of open source and free technologies: what they do, how to use them, and when they fit. Reference documentation, not a checklist—use what serves the task.

**Related**: [[Workflow-Canvas]] (n8n export), [[MCP-Integration]] (tool integration), [[index]].

---

## How to Use This Document

- **Lookup**: Use the tables to find a tool by category; follow links to usage sections.
- **Usage**: Each section includes *what it does*, *how to run it*, and *typical workflow*.
- **Not exhaustive**: Prefer depth on tools you'll actually use (Ansible, n8n, Airbyte, etc.) over breadth.
- **Obsidian**: Open `compendium/` as a vault for [[WikiLinks]] and graph view.

---

## 1. Networking, VPN & Remote Access

| Tool | What It Does | Usage Summary |
|------|--------------|---------------|
| **Tailscale** | Zero-config mesh VPN on WireGuard | Install → sign in → devices see each other. MagicDNS, works behind NAT. |
| **ZeroTier** | Software-defined mesh network | Create network → join from devices. Self-host controller optional. |
| **WireGuard** | Modern VPN protocol | Kernel-level, minimal config. Manual key exchange. |
| **Cloudflare Tunnel** (cloudflared) | Expose local services without opening ports | Run `cloudflared tunnel`; traffic routes through Cloudflare. |
| **frp** | Fast reverse proxy | Client on local machine, server on public host. Expose ports. |

### Usage: Tailscale

**What**: Private network overlay. Devices get Tailscale IPs and can reach each other from anywhere.

**How**:
```bash
# Install (macOS)
brew install tailscale
tailscale up

# Or download from tailscale.com
```

**Typical workflow**: Install on laptop + server → both appear in admin console → `ssh user@server-hostname` works from anywhere. No port forwarding, no VPN server to maintain.

---

## 2. Self-Hosted Applications

| Tool | What It Does | Replaces |
|------|--------------|----------|
| **Nextcloud** | File sync, calendar, contacts | Dropbox, Google Drive |
| **Jellyfin** | Media server | Plex |
| **Immich** | Photo/video management | Google Photos |
| **Vaultwarden** | Password manager (Bitwarden API) | Bitwarden (lighter) |
| **Paperless-ngx** | Document scanning, indexing | Physical filing |
| **Home Assistant** | Home automation | Smart hubs |

---

## 3. Development & DevOps

| Tool | What It Does | Replaces |
|------|--------------|----------|
| **Gitea** / **Forgejo** | Lightweight Git hosting | GitHub (self-hosted) |
| **GitLab CE** | Full DevOps platform | GitHub, Azure DevOps |
| **Drone** / **Woodpecker CI** | CI/CD | Jenkins, GitHub Actions |
| **Docker** / **Podman** | Containers | — |
| **Caddy** / **Traefik** | Web server, reverse proxy | Nginx |

---

## 4. Ansible — Configuration Management

**What**: Declarative configuration and orchestration. You describe desired state in YAML; Ansible applies it. Agentless (SSH), idempotent.

**How**:
```bash
# Install
pip install ansible
# or: brew install ansible

# Directory layout
inventory/
  hosts.yml          # or hosts.ini
playbooks/
  deploy.yml
  provision.yml
roles/
  common/
  nginx/
```

**Typical workflow**:
1. **Inventory**: Define hosts (or groups) in `hosts.yml`.
2. **Playbook**: Write tasks (install packages, copy files, run commands).
3. **Run**: `ansible-playbook -i inventory/hosts.yml playbooks/deploy.yml`.

**Example playbook**:
```yaml
# playbooks/deploy.yml
- hosts: webservers
  become: yes
  tasks:
    - name: Install nginx
      apt:
        name: nginx
        state: present
    - name: Copy config
      copy:
        src: nginx.conf
        dest: /etc/nginx/sites-available/default
      notify: Restart nginx
  handlers:
    - name: Restart nginx
      service:
        name: nginx
        state: restarted
```

**Usage patterns**:
- **Ad-hoc**: `ansible webservers -m ping` or `ansible webservers -a "apt update"`.
- **Roles**: Reusable units; `ansible-galaxy init role_name`.
- **Vault**: Encrypt secrets with `ansible-vault encrypt file.yml`.

---

## 5. n8n — Workflow Automation

**What**: Self-hosted workflow automation. Nodes for HTTP, databases, AI, webhooks, etc. Visual editor, JSON export. Replaces Zapier/Make for self-hosted use.

**How**:
```bash
# Docker
docker run -it --rm \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  n8nio/n8n

# npm
npx n8n
```

**Typical workflow**:
1. Open UI at `http://localhost:5678`.
2. Add nodes: Trigger (webhook, schedule, manual) → Action (HTTP, DB, AI, etc.) → Output.
3. Connect nodes; test with "Execute workflow".
4. Activate for production.

**Usage patterns**:
- **Webhooks**: Trigger on HTTP POST; process payload; respond or forward.
- **Scheduled**: Cron-style triggers for periodic tasks.
- **AI nodes**: Call OpenAI/Anthropic from workflows.
- **Export**: Workflow-canvas can export to n8n format (see [[Workflow-Canvas]]).

**Node types**: HTTP Request, Webhook, Schedule, Set, Code (JavaScript), AI (OpenAI, etc.), Database, Slack, etc.

---

## 6. Airbyte — Data Integration (ETL)

**What**: Sync data between sources and destinations. Connectors for databases, APIs, files, data warehouses. Self-hosted or cloud.

**How**:
```bash
# Docker Compose
curl -sL https://raw.githubusercontent.com/airbytehq/airbyte/master/docker-compose.yaml -o docker-compose.yaml
docker-compose up -d
```

**Typical workflow**:
1. Define **Source** (Postgres, API, S3, etc.) and **Destination** (Postgres, BigQuery, Snowflake, etc.).
2. Configure connection (credentials, schema, sync mode).
3. Run sync (full or incremental).
4. Schedule or trigger via API.

**Usage patterns**:
- **Replication**: DB → Data warehouse for analytics.
- **API ingestion**: REST API → Database.
- **Normalization**: Optional step to transform data before loading.
- **Incremental**: Only sync changed records (where supported).

---

## 7. Security & Privacy

| Tool | What It Does | Usage |
|------|--------------|-------|
| **Pi-hole** / **AdGuard Home** | DNS-level ad/tracker blocking | Point router DNS to Pi-hole; blocks at network level. |
| **Authentik** / **Keycloak** | Identity provider, SSO | Central auth for apps; OIDC/SAML. |
| **Vault** | Secrets management | Store, lease, rotate secrets. API-driven. |
| **CrowdSec** | Collaborative intrusion prevention | Fail2ban successor; block IPs based on behavior. |

---

## 8. AI & Machine Learning

| Tool | What It Does | Usage |
|------|--------------|-------|
| **Ollama** | Run LLMs locally | `ollama run llama3`; API at `localhost:11434`. |
| **LocalAI** | OpenAI-compatible local inference | Drop-in for OpenAI API. |
| **Dify** / **Langflow** | LLM app builders | Visual workflows, RAG, agents. |
| **Airbyte** | Data integration | See §6. |

---

## 9. Esoteric & Niche

*Single-file servers, odd protocols, local-first—the copy-party tier.*

### Single-File Servers

| Tool | What It Does | Usage |
|------|--------------|-------|
| **copy-party** | Portable file server, single Python file | `python copyparty-sfx.py -d /path`; WebDAV, FTP, zeroconf. |
| **redbean** | Single zip-executable web server | Download `redbean.com`, add HTML/Lua, run. Cosmopolitan Libc. |
| **Algernon** | Pure-Go web server | Single binary; Lua, SQLite, HTTP/2, QUIC. |

### File Transfer

| Tool | What It Does | Usage |
|------|--------------|-------|
| **croc** | Encrypted transfer with code phrase | Sender: `croc send file.zip` → get 3 words. Receiver: `croc [words]`. LAN relay when on same network. |

### HTML Over the Wire

| Tool | What It Does | Usage |
|------|--------------|-------|
| **htmx** | Dynamic UIs via HTML attributes | `hx-post`, `hx-swap`, `hx-target`. No build step. |
| **Unpoly** | Progressive enhancement | Fragment updates, overlays. |
| **Turbo** | Drive, Frames, Streams | 37 Signals; replace body/sections. |

### Terminal & CLI

| Tool | What It Does | Usage |
|------|--------------|-------|
| **fzf** | Fuzzy finder | Pipe any list; interactive filter. |
| **ripgrep** (rg) | grep, faster | `rg "pattern"`; respects .gitignore. |
| **fd** | find, intuitive | `fd "\.tsx$"` instead of find. |
| **bat** | cat with syntax highlight | `bat file.py`. |
| **Just** | Task runner | `justfile` instead of Makefile; `just build`. |
| **Gum** | TUI for shell scripts | `gum choose`, `gum input`, `gum confirm`. |

### Local-First & CRDTs

| Tool | What It Does | Usage |
|------|--------------|-------|
| **Automerge** | CRDT sync engine | Offline-first apps; conflict-free merge. |
| **Litestream** | SQLite → S3 replication | Continuous backup; point-in-time recovery. |

### Database Oddities

| Tool | What It Does | Usage |
|------|--------------|-------|
| **wddbfs** | Mount SQLite as filesystem | WebDAV mount; tables as CSV/JSON. `grep` your DB. |

---

## 10. Quick Reference Tables

### By Role

| Need | Tools |
|------|-------|
| Config management | Ansible |
| Workflow automation | n8n |
| Data pipelines | Airbyte |
| Remote access | Tailscale, ZeroTier |
| Local LLMs | Ollama, LocalAI |
| Single-file server | copy-party, redbean |
| Modern CLI | fzf, ripgrep, fd, bat, Just |

### Discovery

- **[awesome-selfhosted](https://awesome-selfhosted.net/)** — Curated self-hosted list
- **[AlternativeOSS](https://alternativeoss.com/)** — 500+ alternatives
- **Hacker News** "Show HN" — Obscure tools
- **[Star History](https://www.star-history.com/)** — Underrated OSS picks

---

## Conventions

- **Start small**: One or two tools per category.
- **Docker first**: Try before committing; many have official images.
- **Check resources**: Gitea/Caddy are light; GitLab/Nextcloud are heavy.

---

*Linked from [[index]]. Part of the Cequence BlackWall compendium.*
