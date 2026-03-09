# Agent Coordination Guide

## Problem: Race Conditions and Hanging Processes

When coordinating multiple AI agents/LLMs:
- **Race conditions**: Agents waiting for each other indefinitely
- **Hanging processes**: Agents that stop responding
- **Time estimation**: Need to know how long operations will take
- **Action tracking**: Track what agents are doing

## Solution: Agent Coordination System

The coordination system provides:
1. **Health monitoring**: Detect hanging agents/processes
2. **Timeout handling**: Automatic timeout for operations
3. **Time estimation**: Request and provide time estimates
4. **Action tracking**: Track agent actions and completion
5. **Deadlock detection**: Detect when agents are waiting for each other

## Usage

### Basic Coordination

```python
from blackwall.worktrees.coordination_integration import CoordinatedCrossChatBridge

# Create coordinated bridge
bridge = CoordinatedCrossChatBridge(session_name="Agent 1")

# Start an operation with time estimate
operation_id = bridge.start_operation(
    operation_description="Analyze codebase",
    expected_duration_seconds=120.0  # 2 minutes
)

# Do work...
# ...

# Complete operation
bridge.complete_operation(operation_id, success=True)

# Send heartbeat regularly
bridge.send_heartbeat()
```

### Waiting for Other Agents

```python
# Wait for another session to become idle
success = bridge.wait_for_other_session(
    session_id="chat-abc123",
    timeout_seconds=300.0  # 5 minutes
)

if success:
    print("Other session is ready")
else:
    print("Timeout - other session may be hanging")
```

### Time Estimation

```python
# Provide time estimate for an operation
bridge.coordinator.provide_time_estimate(
    operation_id="op-123",
    agent_id=bridge.session_id,
    estimated_seconds=180.0,  # 3 minutes
    confidence=0.8
)

# Request time estimate
estimate = bridge.request_time_estimate("op-123")
if estimate:
    print(f"Estimated time: {estimate.estimated_seconds} seconds")
    print(f"Confidence: {estimate.confidence}")
```

### Hanging Process Detection

```python
# Check for hanging sessions
hanging = bridge.check_hanging_sessions()

for agent in hanging:
    print(f"Hanging agent: {agent['agent_id']}")
    print(f"Status: {agent['status']}")
    print(f"Last heartbeat: {agent['last_heartbeat']}")
```

### Publishing with Time Estimates

```python
# Publish finding with time estimate
finding_id = bridge.publish_with_time_estimate(
    title="Code analysis complete",
    content="Found 5 issues",
    estimated_seconds=60.0,  # Takes 1 minute to process
    category="code"
)
```

## Health Monitoring

The system automatically monitors:
- **Heartbeats**: Last time agent sent heartbeat
- **Action duration**: How long actions have been running
- **Process status**: If monitoring system processes
- **Timeout detection**: Automatic detection of hanging agents

### Agent Status

```python
status = bridge.get_coordination_status()

print(f"Status: {status['status']}")
print(f"Last heartbeat: {status['last_heartbeat']}")
print(f"Active actions: {status['active_action_count']}")
print(f"Cross-chat listeners: {status['cross_chat_listeners']}")
```

## Timeout Handling

### Operation Timeouts

```python
# Start operation with timeout
operation_id = bridge.start_operation(
    operation_description="Long-running task",
    expected_duration_seconds=300.0
)

# Wait for completion (with timeout)
completed = bridge.coordinator.wait_for_action(
    operation_id,
    timeout_seconds=600.0  # 10 minutes max
)

if not completed:
    print("Operation timed out - may be hanging")
```

### Agent Timeouts

```python
# Register agent with timeout
bridge.coordinator.register_agent(
    agent_id="agent-123",
    timeout_seconds=300.0  # 5 minutes
)

# Check if agent is hanging
health = bridge.coordinator.health_monitor.check_health("agent-123")
if health["is_hanging"]:
    print("Agent is hanging!")
```

## Deadlock Detection

The system can detect when agents are waiting for each other:

```python
# Agent 1 waits for Agent 2
bridge1.wait_for_other_session("agent-2", timeout_seconds=300)

# Agent 2 waits for Agent 1
bridge2.wait_for_other_session("agent-1", timeout_seconds=300)

# System detects deadlock when both timeouts occur
hanging = bridge1.check_hanging_sessions()
# Both agents will appear as hanging
```

## Best Practices

1. **Send Heartbeats Regularly**: Every 30-60 seconds
   ```python
   import time
   while True:
       bridge.send_heartbeat()
       time.sleep(30)
   ```

2. **Provide Time Estimates**: Help other agents plan
   ```python
   bridge.coordinator.provide_time_estimate(
       operation_id="op-123",
       agent_id=bridge.session_id,
       estimated_seconds=estimated_time,
       confidence=0.8
   )
   ```

3. **Use Timeouts**: Always set reasonable timeouts
   ```python
   success = bridge.wait_for_other_session(
       session_id="other",
       timeout_seconds=300.0  # Don't wait forever
   )
   ```

4. **Check for Hanging**: Periodically check for hanging agents
   ```python
   hanging = bridge.check_hanging_sessions()
   if hanging:
       # Handle hanging agents
       pass
   ```

5. **Track Operations**: Always start/complete operations
   ```python
   op_id = bridge.start_operation("Doing work")
   try:
       # Do work
       pass
   finally:
       bridge.complete_operation(op_id, success=True)
   ```

## Integration with Worktrees

```python
from blackwall.worktrees import UnifiedWorktreeManager
from blackwall.worktrees.coordination_integration import CoordinatedCrossChatBridge

# Worktree for agent coordination
manager = UnifiedWorktreeManager()
worktree = manager.create_worktree(name="Dev Team")

# Coordinated cross-chat
bridge = CoordinatedCrossChatBridge(session_name="Dev Team Chat")

# Agents can coordinate through bridge
operation_id = bridge.start_operation("Code review", expected_duration_seconds=180)
# ... do work ...
bridge.complete_operation(operation_id)

# Other agents can see status
status = bridge.get_coordination_status()
```

## Database Schema

The coordination system uses SQLite with tables:
- `agent_actions`: Tracks agent actions
- `time_estimates`: Stores time estimates
- `agent_health`: Tracks agent health status

## Summary

The coordination system solves:
- ✅ **Race conditions**: Timeout handling prevents indefinite waiting
- ✅ **Hanging processes**: Automatic detection via health monitoring
- ✅ **Time estimation**: Request/provide estimates for planning
- ✅ **Action tracking**: Track what agents are doing
- ✅ **Deadlock detection**: Detect circular dependencies

Use `CoordinatedCrossChatBridge` for enhanced coordination capabilities!
