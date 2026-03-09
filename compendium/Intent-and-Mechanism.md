# Intent & Mechanism — Quick Reference

One-line intent + simplified mechanism for each major piece. Information-dense.

---

## Agent & coordination

| Piece | Intent | Mechanism |
|-------|--------|-----------|
| **Agent-system (coordinator)** | Assign work to the right subagent and avoid conflicts. | Central coordinator; registers agents; assigns tasks to ledger/task queue by type; distributes pending tasks to idle agents. |
| **Ledger (AI_GROUPCHAT)** | Single source of truth for who’s doing what and what was said. | File-based JSON (thread-safe); agents register, post messages, declare/complete intents, acquire/release locks; everyone reads same file. |
| **Task queue** | Order and track work so nothing is dropped or double-assigned. | Tasks live in ledger; states: pending → assigned → completed; coordinator assigns task_id to agent_id; atomic read/write. |
| **Base agent** | Give every subagent the same coordination primitives. | Subclass gets: log to ledger, declare_intent / complete_intent, acquire/release resource locks, send_message, get_messages, check_for_conflicts. |
| **Scratchpad** | Let cleanup/test/doc agents share context without overwriting each other. | Shared JSON with sections (code_notes, test_notes, doc_notes, issues); append-only per section; agents read before writing. |
| **Cleanup subagent** | Improve code quality (dead code, lint, structure) without breaking behavior. | Claude invokes by task; tools: read/write file, search_replace, grep, codebase_search, read_lints; logs to scratchpad; declares intent before editing. |
| **Test subagent** | Add and maintain tests when code or coverage needs change. | Claude invokes by task; tools: read/write file, codebase_search, grep, read_lints; reads cleanup notes from scratchpad; writes tests, reports coverage to scratchpad. |
| **Doc subagent** | Keep docs (API, README, guides) in sync with code. | Claude invokes by task; tools: read/write file, codebase_search, grep; reads cleanup/test notes; writes docs, reports summary to scratchpad. |
| **LSP manager / setup_claude_integration** | Make Claude Code use the right language servers and subagents. | Detect project languages; check LSP binaries; output `/plugin install` commands; verify `.claude/agents/`; one script to “is everything wired?”. |

---

## Blackwall agents (protection/detection)

| Piece | Intent | Mechanism |
|-------|--------|-----------|
| **MCP-aware agent** | Let Blackwall agents call tools (files, search, etc.) in a standard way. | Wraps MCP integration: list_tools, get_tool_schema, call tool; optionally wraps agent-system BaseAgent for ledger/scratchpad. |
| **Detection agent** | Answer “is this content watermarked?” and by whom. | Uses UnifiedProcessor.detect_text/detect_image on path or text; if UUID in result, looks up registry; returns detected + optional registry match. |
| **Protection agent** | Protect text/image so it can be traced or defended. | Declares intent; reads file (MCP or direct); runs UnifiedProcessor.process_text/process_image; writes protected output; registers UUID in registry. |

---

## Autonomous layer

| Piece | Intent | Mechanism |
|-------|--------|-----------|
| **Autonomous orchestrator** | Turn high-level goals into agent work without a human assigning each step. | Stores goals (id, description, priority, status); _decide_agent_for_goal(goal) maps goal text → agent type; _autonomous_execute_goal assigns and runs; state in .blackwall/orchestrator_state.json. |
| **Self-coordinator** | Let agents find each other and team up without a central dispatcher. | File-based registry (agent_id, type, capabilities, location); register_agent() writes + triggers _autonomous_discovery(); others read registry to form coordinations. |
| **Autonomous agent** | Base for “decide for yourself” agents with persistent state. | Loads/saves state (goals, decisions) to .blackwall/agents/<id>.json; _make_decision(context) overridable; subclasses implement behavior. |
| **Autonomous protection agent** | Protect content on goals alone (e.g. “protect everything in folder”). | Extends AutonomousAgent; registers with SelfCoordinator; _make_decision picks text vs image from goal; calls UnifiedProcessor + registry. |

---

## Security & protection (core)

| Piece | Intent | Mechanism |
|-------|--------|-----------|
| **Prompt-injection gate** | Stop or neuter prompt injection before the main model sees it. | SacrificialDetector: rule match (instruction-override phrases + delimiter patterns) and optional small model score; SacrificialGate: block (return policy message) or sanitize (remove matched spans); main model only sees passed_text. |
| **Unified processor** | One API to protect or detect text and images. | Text: TextWatermarker embed + TextPoisoner poison → metadata (uuid); detect_text extracts/checks. Image: if nightshade on path, same flow via nightshade modules; else image disabled. |
| **Text poisoner / watermarker** | Text: traceable + resistant to scraping/training. | Watermarker: embed (e.g. unicode) + uuid; Poisoner: subtle perturbations; both used by UnifiedProcessor. |
| **Registry** | Map “who owns this protected asset?” by UUID. | register_content(original_path, uuid, type, …); lookup_by_uuid(uuid); used by detection/protection and autonomous protection. |
| **Nightshade-tracker** | Image: poison + watermark for traceability and robustness. | Core: poisoning, watermarking, image_processor, detector; registry; CLI. Blackwall’s UnifiedProcessor imports it when path exists; otherwise image path is no-op. |

---

## Integration & services

| Piece | Intent | Mechanism |
|-------|--------|-----------|
| **MCP server framework** | Expose tools and prompts to AI clients (Cursor, etc.) with one contract. | MCPServer: register_tool (handler + schema), register_prompt (template + resource_access), load_resources; ServerRegistry holds many servers; tools/prompts discoverable and callable. |
| **Server builder** | Create MCP servers from code or config without hand-wiring. | Fluent add_tool / add_prompt / add_resource; build(); load from YAML/JSON; export to_config(). |
| **Agent integration bridge** | Give agents one place to see and call all MCP tools/prompts. | Discovers tools and prompts across registered servers; call_tool(name, params); render_prompt(name, context); AgentContext bundles tools + prompts + resources. |
| **Workflow-canvas** | Let users build and run workflows visually and talk to an AI assistant. | Frontend: drag blocks (HTTP, MCP, prompt_llm, RAG, control, etc.); backend: workflow_engine runs DAG; blocks.py executes each type; ai_gateway turns chat into actions (add_node, run, etc.); optional MCP + n8n export. |
| **AI gateway (workflow-canvas)** | Turn natural-language commands into workflow actions and replies. | Build system prompt (block types, actions) + user prompt (command + context); call Anthropic/OpenAI or rule fallback; parse response for action (add_node, clear_canvas, execute_workflow, …); return action + message. |
| **Cloud notifications** | Notify external systems when something happens (e.g. task done). | Notification service sends to configured channels (e.g. webhook URL); env for keys/URLs; example and test scripts for validation. |
| **Workspace overseer** | Light oversight for Cursor workspaces: small monitoring + mild changes toward a known goal. | Goal from env or CLI; one cycle = monitor (file count, recent files, git) → decide (rule-based mild actions) → execute (append to .overseer log/scratchpad only); run via `python run_overseer.py` or `python -m overseer.cli run`; report for a larger AI. |
| **Personal assistant (manifest)** | Secure, consistent definition of the assistant by composing orchestrators (no new Python runtime). | Single manifest `assistant/manifest.yaml`: pipeline order (prompt_injection → mcp → workflow_canvas → subagents), boundaries per orchestrator, consistency (no secrets, audit sink); validation via `./assistant/validate.sh` (shell only); Cursor rule enforces manifest; execution = existing systems. |

---

## One-sentence map

- **Coordinator** → assigns tasks to agents via ledger/task queue.
- **Ledger** → shared messages, intents, locks in one file.
- **Scratchpad** → shared notes for cleanup/test/doc.
- **Subagents** → Claude-invoked specialists (cleanup, test, doc) using ledger + scratchpad.
- **Blackwall agents** → detection/protection using MCP tools + UnifiedProcessor + registry.
- **Autonomous** → goals → orchestrator picks agent → agent runs (e.g. protect); self-coordinator for discovery.
- **Prompt injection** → small detector + block or sanitize before main model.
- **Unified processor** → text/image protect/detect + UUID in registry; image via nightshade when present.
- **MCP** → servers expose tools/prompts; agents and workflow call them.
- **Workflow-canvas** → visual DAG + block execution + AI chat → actions.
- **Notifications** → webhooks/events for external systems.
- **Overseer** → one cycle: monitor → mild actions (append log/scratchpad) toward goal; directed by OVERSEE_GOAL or --goal.
- **Personal assistant** → manifest-driven composition of orchestrators; YAML + shell validation; pipeline + boundaries; no secrets in manifest.
