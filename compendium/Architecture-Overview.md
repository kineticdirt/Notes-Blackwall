# Architecture Overview — How It All Fits

High-level view of how Notes - Blackwall subsystems connect: agent-system, Blackwall agents, autonomous layer, MCP, protection, prompt injection, workflow-canvas, and notifications.

---

## 1. Agent & Coordination Layer

| System | Role | Location |
|--------|------|----------|
| **Agent-system** | Multi-agent coordination for Claude subagents: coordinator, ledger (AI_GROUPCHAT), task queue, scratchpad. | `agent-system/` |
| **Subagents** | Specialized Claude agents (cleanup, test, doc, code, research, review); configs in `.claude/agents/`, implementations in `agent-system/agents/`. | [[Subagents]], [[Agent-System]] |
| **Blackwall agents** | Detection and protection agents; MCP-aware; use core protection and MCP tools. | `blackwall/agents/` → [[Blackwall-Agents]] |
| **Autonomous** | Orchestrator, self-coordinator, autonomous agent, autonomous protection agent; goal-driven, file-based state. | `blackwall/autonomous/` → [[Autonomous-System]] |

- **Agent-system** is the canonical coordination layer for Claude subagents (ledger, tasks, scratchpad).
- **Blackwall agents** are protection/detection specialists; they can optionally use agent-system’s base agent and ledger when agent-system is on path.
- **Autonomous** layer can run independently with its own state; autonomous protection uses Blackwall core only (processor, registry).

---

## 2. Security & Protection

| System | Role | Location |
|--------|------|----------|
| **Prompt injection** | Sacrificial detector and remedy (block/sanitize) before main AI. | `blackwall/prompt_injection/` → [[Prompt-Injection]] |
| **Core protection** | Text/image poisoning and watermarking; unified processor and registry. | `blackwall/core/`, `blackwall/database/` → [[Core-Protection]] |
| **Nightshade-tracker** | Image poisoning and watermarking; used by Blackwall when on path. | `nightshade-tracker/` → [[Nightshade-Tracker]] |

- User input can be gated by **prompt injection** before reaching the main model (e.g. in [[Workflow-Canvas]] AI gateway).
- **Detection** and **protection** agents (and autonomous protection) use **core protection** and **registry**; image processing uses **nightshade-tracker** when available.

---

## 3. Integration & Services

| System | Role | Location |
|--------|------|----------|
| **Assistant (Pi-style)** | General-purpose assistant: gate → LLM + tools + preferences + dynamic MCP; HTTP on 8765; manifest-aligned. Run as part of the system via `scripts/run-assistant-system.sh` or docker-compose. | `assistant/` → [[PI-ASSISTANT]] |
| **Key-holder** | Holds API key and proxies LLM requests; assistant (or other callers) talk to it without ever receiving the key. Localhost/cluster-internal only. | `assistant/key_holder/` → [[KEY_HOLDER_SERVICE]] |
| **MCP** | Framework for servers, tools, prompts, resources; used by Blackwall agents and workflow blocks. | `blackwall/mcp/` → [[MCP-Integration]] |
| **Workflow-canvas** | Visual workflow editor, blocks, AI gateway, execution, n8n export; can use prompt-injection gate and MCP tools. | `workflow-canvas/` → [[Workflow-Canvas]] |
| **Cloud notifications** | Notification service and webhooks. | `cloud_agents_notifications/` → [[Cloud-Notifications]] |

---

## 4. Data and Control Flow (Simplified)

- **User → Assistant**: User message → (optional) key-holder (if used) → Assistant (gate → LLM + tools); POST `/message` returns reply; assistant can call MCP and persist preferences.
- **User → Workflow / Chat**: User input → (optional) [[Prompt-Injection]] gate → AI gateway / main model; workflow execution uses blocks, including MCP tools.
- **Protection**: Content path → Protection agent or AutonomousProtectionAgent → [[Core-Protection]] UnifiedProcessor (+ nightshade for images) → registry.
- **Detection**: Content path or text → Detection agent → UnifiedProcessor detect → optional registry lookup.
- **Subagents**: Claude Code invokes subagents by task; subagents use [[Agent-System]] ledger and scratchpad; coordinator distributes tasks.
- **Autonomous**: Goals → Orchestrator → agent type decision → AutonomousProtectionAgent (or other) → Core protection + registry; self-coordinator for discovery.

---

## 5. Compendium Map

- **Entry**: [[index]]
- **Agents & subagents**: [[Subagents]], [[Agent-System]], [[Blackwall-Agents]], [[Autonomous-System]]
- **Security & protection**: [[Prompt-Injection]], [[Core-Protection]], [[Nightshade-Tracker]]
- **Integration**: [[MCP-Integration]], [[Workflow-Canvas]], [[Cloud-Notifications]]

---

*This note is the architecture hub; each linked note has more detail and cross-links.*
