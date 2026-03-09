# Cequence BlackWall Compendium

An **Obsidian-style** compendium of the project: linked notes, maps of content, and expanded documentation for agents, subagents, and core systems.

## How to Use

- **In Obsidian**: Open the project folder (or copy `compendium/` into a vault) and use **Graph view**, **Backlinks**, and **[[WikiLinks]]** for navigation.
- **As Markdown**: All links use `[[Page Name]]`; open `index.md` as the entry point and follow links. Any markdown viewer will work; backlinks are manual.

## Entry Point

- **Quick digest**: **[[Intent-and-Mechanism]]** — intent + mechanism for every major piece (information-dense).
- **Full map**: **[[index]]** for the full map of content.

In Obsidian, open this folder as a vault (or add `compendium/` to an existing vault) to get backlinks and graph view for all `[[links]]`.

## Structure

| Section | Description |
|--------|--------------|
| [[index]] | Map of content — all nodes and links |
| [[Subagents]] | Claude subagents (cleanup, test, doc, code, research, review) |
| [[Agent-System]] | Coordinator, ledger, task queue, base agent |
| [[Blackwall-Agents]] | Detection, protection, MCP-aware agents |
| [[Autonomous-System]] | Orchestrator, self-coordinator, autonomous agents |
| [[MCP-Integration]] | MCP framework, servers, tools, resources |
| [[Prompt-Injection]] | Sacrificial detector and remedy |
| [[Core-Protection]] | Text/image poisoning, watermarking, unified processor |
| [[Nightshade-Tracker]] | Image protection (nightshade-tracker) |
| [[Workflow-Canvas]] | Visual workflow, AI gateway, blocks |
| [[Cloud-Notifications]] | Notification service and webhooks |
| [[Architecture-Overview]] | How subsystems connect |
| [[DevOps-Ops-Reference]] | DevOps & Ops reference — flow, scripting, testing, AWS, orchestrators, load balancers |
| [[Open-Source-Tools]] | Open source tools library — Ansible, n8n, Airbyte, esoteric; usage lore |

## Conventions

- **[[Link]]** — link to another compendium note (Obsidian will resolve these).
- **#tag** — optional tags for filtering (e.g. `#agent`, `#security`).
- **Backlinks** — each note lists "Linked from" where relevant; in Obsidian these appear automatically.
