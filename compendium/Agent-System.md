# Agent System — Coordinator, Ledger, Task Queue

The **agent-system** provides multi-agent coordination for Claude subagents: shared ledger, task queue, base agent, and scratchpad. See [[Subagents]] for the specialized agents; [[Blackwall-Agents]] and [[Autonomous-System]] for Blackwall’s own agents.

---

## Location

- **Path**: `agent-system/`
- **Key files**: `coordinator.py`, `agent.py`, `ledger.py`, `task_queue.py`, `scratchpad.py`, `agents/*.py`, `.claude/agents/*.md`

---

## Components

### Coordinator (`coordinator.py`)

`AgentCoordinator` manages agents and task distribution.

- **Ledger**: Uses [[#Ledger]] (AI_GROUPCHAT) for registration and messages.
- **Task queue**: Uses [[#Task Queue]] for pending/active/completed tasks.
- **Agents**: `register_agent(agent)`, `unregister_agent(agent_id)`.
- **Tasks**: `assign_task(description, agent_type=None, priority=5, metadata=None)` → task_id.
- **Distribution**: `distribute_tasks()` — assigns pending tasks to idle agents by type.
- **Status**: `get_agent_status()`, `get_coordination_summary()`.
- **Broadcast**: `broadcast_message(message, message_type)`.

---

### Ledger (`ledger.py`)

`AgentLedger` — shared communication and state (file-based, thread-safe).

- **File**: `ledger/AI_GROUPCHAT.json` (configurable path).
- **Contents**: agents, messages, intents, locks, state.
- **Operations**:
  - `register_agent(agent_id, agent_type, metadata)`
  - `post_message(agent_id, message, target_agent=None, message_type="info")`
  - `declare_intent(agent_id, intent, resources)` → intent_id
  - `complete_intent(intent_id, agent_id)`
  - `acquire_lock(agent_id, resource, timeout)`, `release_lock(agent_id, resource)`
  - `get_messages(agent_id, since=None)`
- **Concurrency**: Thread lock + atomic write (temp file then rename).

---

### Task Queue (`task_queue.py`)

`TaskQueue` — tasks stored in the same ledger file.

- **Operations**: `add_task(description, agent_type, priority, metadata)` → task_id; `get_pending_tasks()`, `get_active_tasks()`, `get_completed_tasks()`; `assign_task(task_id, agent_id)`; `complete_task(task_id, agent_id)`.
- **Task states**: pending → assigned (active) → completed.

---

### Base Agent (`agent.py`)

`BaseAgent` — base class for all Claude subagents.

- **Init**: `agent_id`, `agent_type`, `ledger_path`; registers with ledger.
- **Ledger**: `log(message, message_type)`, `declare_intent(intent, resources)`, `complete_intent()`, `send_message(target_agent, message)`, `get_messages(since=None)`.
- **Locks**: `acquire_resource(resource, timeout)`, `release_resource(resource)`.
- **Conflict**: `check_for_conflicts()` — other agents’ intents and locks.
- **State**: `update_status(status)`, `get_state()`, `cleanup()`.

---

### Scratchpad (`scratchpad.py`)

Shared scratchpad for inter-agent context (e.g. code_notes, test_notes, doc_notes, issues).

- **File**: `ledger/scratchpad.json` (configurable).
- **Usage**: Agents read/write sections so cleanup, test, and doc agents can coordinate without overwriting each other.
- **Used by**: [[Subagents]] (CleanupAgent, TestAgent, DocAgent).

---

## Claude Integration

- **LSP**: `lsp_manager.py` detects languages and reports plugin install commands; `setup_claude_integration.py` checks LSP and subagents.
- **Subagents**: Defined in `.claude/agents/*.md`; Claude Code invokes them by task; they use ledger + scratchpad. See [[Subagents]].
- **Enhanced coordinator**: `enhanced_workflow_coordinator.py` adds LSP awareness to workflow runs.

---

## Workflow Coordinators

- **workflow_coordinator.py**: Base workflow coordination.
- **enhanced_workflow_coordinator.py**: Extends base with LSP checks and subagent-aware workflow.

---

## Related

- [[Subagents]] — Cleanup, test, doc, code, research, review agents and their configs.
- [[Blackwall-Agents]] — Detection, protection, MCP-aware agents.
- [[Autonomous-System]] — Orchestrator and self-coordinator.
- [[Architecture-Overview]] — Placement of agent-system in the stack.
