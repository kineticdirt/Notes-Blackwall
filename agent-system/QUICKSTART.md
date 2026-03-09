# Quick Start: Claude Sub-Agent System

## Overview

This system enables multiple Claude instances to coordinate, communicate, and prevent race conditions through a shared ledger (AI_GROUPCHAT.json).

## Key Features

- **Shared Ledger**: File-based communication (`ledger/AI_GROUPCHAT.json`)
- **Intent Declaration**: Agents declare intents before acting
- **Resource Locking**: Prevents conflicts on shared resources
- **Task Queue**: Coordinator distributes tasks to agents
- **Specialized Agents**: Code, Research, Review agents

## Basic Usage

### 1. Initialize Coordinator and Agents

```python
from coordinator import AgentCoordinator
from agents.code_agent import CodeAgent

# Create coordinator
coordinator = AgentCoordinator()

# Create and register agents
code_agent = CodeAgent()
coordinator.register_agent(code_agent)
```

### 2. Agents Declare Intents

```python
# Agent declares what it's about to do
code_agent.declare_intent(
    "Implementing login feature",
    resources=["auth.py", "models.py"]
)

# Do the work...
code_agent.log("Implementation in progress")

# Complete the intent
code_agent.complete_intent()
```

### 3. Resource Locking

```python
# Acquire lock on a file/resource
if code_agent.acquire_resource("database.py", timeout=30):
    # Work on the resource
    # ... modify database.py ...
    
    # Release lock
    code_agent.release_resource("database.py")
```

### 4. Agent Communication

```python
# Send message to another agent
code_agent.send_message("research-001", "Need info on encryption")

# Get messages
messages = code_agent.get_messages()
```

### 5. Task Assignment

```python
# Coordinator assigns tasks
task_id = coordinator.assign_task(
    "Implement user authentication",
    agent_type="code",
    priority=8
)

# Distribute tasks to available agents
coordinator.distribute_tasks()
```

## Preventing Race Conditions

### Intent Declaration

Before modifying files, agents should declare their intent:

```python
# Agent 1
code_agent1.declare_intent(
    "Modifying auth.py",
    resources=["auth.py"]
)

# Agent 2 checks for conflicts
conflicts = code_agent2.check_for_conflicts()
if conflicts:
    # Wait or choose different files
    pass
```

### Resource Locking

For critical resources, use explicit locks:

```python
if agent.acquire_resource("critical_file.py"):
    # Safe to modify
    modify_file("critical_file.py")
    agent.release_resource("critical_file.py")
```

## Ledger Structure

The `AI_GROUPCHAT.json` ledger contains:

- **agents**: Registered agents and their status
- **messages**: Communication log
- **intents**: Active and completed intents
- **tasks**: Task queue
- **locks**: Active resource locks
- **state**: Global shared state

## Example Workflow

```python
from coordinator import AgentCoordinator
from agents.code_agent import CodeAgent
from agents.research_agent import ResearchAgent
from agents.review_agent import ReviewAgent

coordinator = AgentCoordinator()

# Create agents
code_agent = CodeAgent()
research_agent = ResearchAgent()
review_agent = ReviewAgent()

coordinator.register_agent(code_agent)
coordinator.register_agent(research_agent)
coordinator.register_agent(review_agent)

# Research phase
research_agent.research_topic("Image watermarking techniques")
research_agent.complete_intent()

# Implementation phase
code_agent.implement_feature("Add watermarking", files=["watermarking.py"])
code_agent.complete_intent()

# Review phase
review_agent.review_code("Review watermarking", files=["watermarking.py"])
review_agent.complete_intent()

# Check status
summary = coordinator.get_coordination_summary()
print(summary)
```

## Best Practices

1. **Always declare intents** before modifying files
2. **Use resource locks** for critical operations
3. **Check for conflicts** before starting work
4. **Complete intents** when done
5. **Log important actions** for other agents to see
6. **Use the coordinator** for task distribution

## Viewing the Ledger

The ledger file `ledger/AI_GROUPCHAT.json` is human-readable JSON. You can:

- View all agent communications
- See active intents and locks
- Track task progress
- Monitor agent status

## Integration with Cursor

When using multiple Claude instances in Cursor:

1. Each instance can create an agent
2. Agents communicate via the shared ledger
3. The ledger prevents race conditions
4. All agents can see what others are doing

This enables true multi-agent collaboration!
