# Autonomous System — Orchestrator, Self-Coordinator, Autonomous Agents

The **autonomous** layer in `blackwall/autonomous/` coordinates agents that operate with minimal human intervention: goal-driven orchestration, self-coordination, and autonomous protection. See [[Agent-System]] and [[Blackwall-Agents]] for the non-autonomous agents.

---

## Location

- **Path**: `blackwall/autonomous/`
- **Files**: `orchestrator.py`, `self_coordinator.py`, `autonomous_agent.py`, `autonomous_protection_agent.py`

---

## Components

### Autonomous Orchestrator (`orchestrator.py`)

`AutonomousOrchestrator` — sets goals and assigns them to agents autonomously.

- **State**: `project_path`, `goals`, `active_agents`, `decision_history`; persisted in `.blackwall/orchestrator_state.json`.
- **Goals**: `set_goal(goal_description, priority=5)` → goal_id; goal has id, description, priority, status (pending/active/completed), assigned_agent, progress.
- **Processing**: `_autonomous_goal_processing()` — for each pending goal, decides agent type via `_decide_agent_for_goal(goal)`, then `_autonomous_execute_goal(goal, agent_type)`.
- **Decision logic**: Heuristic mapping from goal text to agent type (e.g. “protect” → protection agent); can be extended.

---

### Self-Coordinator (`self_coordinator.py`)

`SelfCoordinator` — agents register and discover each other for ad-hoc coordination.

- **State**: `coordination_file` (default `.blackwall/coordination.json`); `agent_registry`, `active_coordinations`.
- **Registration**: `register_agent(agent_id, agent_type, capabilities, location="local")` — stores agent in registry and triggers `_autonomous_discovery()`.
- **Discovery**: Agents discover each other via the shared registry (in a full setup this could be network or shared store).
- **Coordination**: Methods to form and track active coordinations between agents.

---

### Autonomous Agent (`autonomous_agent.py`)

`AutonomousAgent` — base for agents that make their own decisions.

- **State**: `agent_id`, `agent_type`, `status`, `current_goals`, `decision_log`; persisted in `.blackwall/agents/<agent_id>.json`.
- **Goals**: Accept and pursue goals; log decisions.
- **Decision**: Subclasses override `_make_decision(context)` to implement autonomous behavior.
- **Persistence**: Load/save state on init and after significant actions.

---

### Autonomous Protection Agent (`autonomous_protection_agent.py`)

`AutonomousProtectionAgent` — protects content autonomously using [[Core-Protection]].

- **Extends**: `AutonomousAgent` (agent_type=`"autonomous_protection"`).
- **Dependencies**: `UnifiedProcessor`, `BlackwallRegistry`.
- **Registration**: Registers with `SelfCoordinator` on init (capabilities: protection, watermarking, poisoning, text, image).
- **Decision**: `_make_decision(context)` — e.g. choose text vs image protection from goal text.
- **Execution**: `autonomous_protect(content_path)` — decide strategy, run processor, register in registry; returns protection result.

---

## Data Flow

1. **Orchestrator**: User or system calls `set_goal(...)` → goal stored → `_autonomous_goal_processing()` picks agent type → executes via appropriate agent (e.g. AutonomousProtectionAgent).
2. **Self-coordinator**: Agents call `register_agent(...)` → registry updated → discovery can form coordinations.
3. **Autonomous agents**: Load state, receive goals, call `_make_decision()`, perform work, save state and optionally report back.

---

## Relation to Agent-System

- **Agent-system** ([[Agent-System]]): Coordinator + ledger + task queue; explicit task assignment and ledger-based communication.
- **Autonomous**: Goal-driven, heuristic assignment, file-based state; can run without the agent-system ledger. Autonomous protection agent uses Blackwall core only (processor, registry), not the agent-system ledger.

---

## Related

- [[Blackwall-Agents]] — Detection and protection agents (non-autonomous).
- [[Agent-System]] — Coordinator, ledger, task queue.
- [[Core-Protection]] — UnifiedProcessor and registry used by autonomous protection.
- [[Architecture-Overview]] — Where the autonomous layer sits.
