# Cequence BlackWall — Compendium Index

Map of content for the Cequence BlackWall project. Use this as the entry point for the compendium.

**Quick reference**: [[Intent-and-Mechanism]] — one-line intent + simplified mechanism for each piece (dense, brief).

---

## 1. Agent & Subagent Systems

| Note | Description |
|------|--------------|
| [[Subagents]] | **Claude subagents**: cleanup, test, doc, code, research, review — definitions, tools, workflows, and `.claude/agents/` configs. |
| [[Agent-System]] | **Agent-system**: coordinator, ledger (AI_GROUPCHAT), task queue, base agent, scratchpad; multi-agent coordination. |
| [[Blackwall-Agents]] | **Blackwall agents**: detection, protection, MCP-aware; use [[Core-Protection]] and [[MCP-Integration]]. |
| [[Autonomous-System]] | **Autonomous layer**: orchestrator, self-coordinator, autonomous agent, autonomous protection agent. |

---

## 2. Security & Protection

| Note | Description |
|------|--------------|
| [[Prompt-Injection]] | Sacrificial low-parameter detector and remedy (block/sanitize). |
| [[Core-Protection]] | Text poisoning, text watermarking, unified processor, registry. |
| [[Nightshade-Tracker]] | Image protection: poisoning, watermarking, detector (nightshade-tracker). |

---

## 3. Integration & Services

| Note | Description |
|------|--------------|
| [[MCP-Integration]] | MCP framework, server builder, tools, prompts, resources; agent integration. |
| [[Workflow-Canvas]] | Visual workflow editor, blocks, AI gateway, execution, n8n export. |
| [[Cloud-Notifications]] | Notification service, webhooks, setup. |

---

## 4. Architecture & Assistant

| Note | Description |
|------|--------------|
| **assistant/** | **Personal assistant**: manifest-driven composition of orchestrators (prompt-injection, MCP, workflow-canvas, subagents); security boundaries + consistency; validation via shell script; no Python orchestration runtime. |
| [[Architecture-Overview]] | How agent-system, Blackwall, autonomous, MCP, protection, and workflows connect. |

---

## 5. Reference & Lore

| Note | Description |
|------|-------------|
| [[DevOps-Ops-Reference]] | **DevOps & Ops reference**: flow and terms, scripting, distributed-systems testing, mock/dev envs, AWS services, orchestrators, load balancers. |
| [[Open-Source-Tools]] | **Open source tools library**: networking, self-hosted, Ansible, n8n, Airbyte, esoteric/niche; usage patterns, how/what, typical workflows. |

---

## Quick Links (by role)

- **Subagent author** → [[Subagents]], [[Agent-System]]
- **Protection / security** → [[Prompt-Injection]], [[Core-Protection]], [[Nightshade-Tracker]]
- **MCP / tools** → [[MCP-Integration]], [[Blackwall-Agents]]
- **Autonomous behavior** → [[Autonomous-System]], [[Agent-System]]
- **Product / UX** → [[Workflow-Canvas]], [[Cloud-Notifications]]
- **Tools / DevOps** → [[DevOps-Ops-Reference]], [[Open-Source-Tools]]

---

*Compendium root. All links use `[[Page Name]]` for Obsidian-style navigation.*
