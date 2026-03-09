# Claude Sub-Agent System

A multi-agent coordination system for Claude instances to work together, communicate, and prevent race conditions.

## Overview

This system enables multiple Claude agents to:
- Coordinate tasks without conflicts
- Communicate via a shared ledger (AI_GROUPCHAT)
- Track agent states and intents
- Prevent race conditions through file-based locking
- Delegate tasks to specialized sub-agents

## Architecture

```
agent-system/
├── coordinator.py          # Main coordinator for managing agents
├── agent.py                # Base agent class
├── ledger.py               # Communication ledger (AI_GROUPCHAT)
├── task_queue.py           # Task queue management
├── agents/
│   ├── __init__.py
│   ├── code_agent.py       # Specialized code agent
│   ├── research_agent.py   # Research and analysis agent
│   └── review_agent.py     # Code review agent
└── ledger/
    └── AI_GROUPCHAT.json   # Shared communication ledger
```

## Features

- **Shared Ledger**: File-based communication system (AI_GROUPCHAT.json)
- **Task Queue**: Prevents race conditions with atomic operations
- **Agent Registry**: Tracks active agents and their states
- **Intent System**: Agents declare intents before acting
- **Locking Mechanism**: File-based locks prevent concurrent conflicts

## Usage

```python
from coordinator import AgentCoordinator
from agents.code_agent import CodeAgent

# Initialize coordinator
coordinator = AgentCoordinator()

# Create and register agents
code_agent = CodeAgent(agent_id="code-001")
coordinator.register_agent(code_agent)

# Agents communicate via ledger
code_agent.declare_intent("Implementing feature X")
code_agent.complete_task("Feature X implemented")

# Coordinator manages task distribution
coordinator.assign_task("Implement login system", agent_type="code")
```
