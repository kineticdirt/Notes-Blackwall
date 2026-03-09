# Agent Coordination Solution

## Problem Statement

When coordinating multiple AI agents/LLMs:
- **Race conditions**: Agents waiting for each other indefinitely
- **Hanging processes**: Agents that stop responding
- **Time estimation**: Need to know how long operations will take
- **Action tracking**: Track what agents are doing

## Solution: Agent Coordination System

The coordination system provides:

1. ✅ **Health Monitoring**: Detect hanging agents/processes
2. ✅ **Timeout Handling**: Automatic timeout for operations
3. ✅ **Time Estimation**: Request and provide time estimates
4. ✅ **Action Tracking**: Track agent actions and completion
5. ✅ **Deadlock Detection**: Detect when agents are waiting for each other

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│           Agent Coordination System                     │
│                                                         │
│  - AgentHealthMonitor: Monitors agent health            │
│  - AgentCoordinator: Coordinates agents                │
│  - CoordinatedCrossChatBridge: Enhanced bridge        │
└─────────────────────────────────────────────────────────┘
         ▲                    ▲                    ▲
         │                    │                    │
    ┌────┴────┐         ┌────┴────┐         ┌────┴────┐
    │ Agent 1 │         │ Agent 2 │         │ Agent 3 │
    │         │         │         │         │         │
    │ Waits   │         │ Waits   │         │ Monitors│
    │ for 2   │         │ for 1   │         │ Health  │
    └─────────┘         └─────────┘         └─────────┘
```

## Key Features

### 1. Health Monitoring

Automatically monitors:
- **Heartbeats**: Last time agent sent heartbeat
- **Action duration**: How long actions have been running
- **Process status**: If monitoring system processes
- **Timeout detection**: Automatic detection of hanging agents

```python
from blackwall.worktrees import CoordinatedCrossChatBridge

agent = CoordinatedCrossChatBridge(session_name="Agent 1")

# Send heartbeat regularly
agent.send_heartbeat()

# Check health
status = agent.get_coordination_status()
print(f"Status: {status['status']}")
print(f"Is hanging: {status.get('is_hanging', False)}")
```

### 2. Timeout Handling

Prevents indefinite waiting:

```python
# Wait for another agent (with timeout)
success = agent.wait_for_other_session(
    session_id="other-agent",
    timeout_seconds=300.0  # 5 minutes max
)

if not success:
    print("Timeout - agent may be hanging")
```

### 3. Time Estimation

Request and provide time estimates:

```python
# Provide time estimate
agent.coordinator.provide_time_estimate(
    operation_id="op-123",
    agent_id=agent.session_id,
    estimated_seconds=180.0,  # 3 minutes
    confidence=0.8
)

# Request time estimate
estimate = agent.request_time_estimate("op-123")
if estimate:
    print(f"Estimated: {estimate.estimated_seconds} seconds")
```

### 4. Action Tracking

Track what agents are doing:

```python
# Start operation
operation_id = agent.start_operation(
    operation_description="Analyze codebase",
    expected_duration_seconds=120.0
)

# Do work...
# ...

# Complete operation
agent.complete_operation(operation_id, success=True)
```

### 5. Hanging Process Detection

Automatically detects hanging agents:

```python
# Check for hanging agents
hanging = agent.check_hanging_sessions()

for h in hanging:
    print(f"Hanging: {h['agent_id']}")
    print(f"Status: {h['status']}")
    print(f"Last heartbeat: {h['last_heartbeat']}")
```

## Usage Examples

### Example 1: Coordinating Two Agents

```python
from blackwall.worktrees.coordination_integration import create_coordinated_bridge

# Agent 1
agent1 = create_coordinated_bridge("Agent 1")
op_id = agent1.start_operation("Task 1", expected_duration_seconds=120)
agent1.coordinator.provide_time_estimate(op_id, agent1.session_id, 120.0, 0.8)

# Agent 2 waits for Agent 1
agent2 = create_coordinated_bridge("Agent 2")
estimate = agent2.request_time_estimate(op_id)
success = agent2.wait_for_other_session(agent1.session_id, timeout_seconds=180)

if success:
    print("Agent 1 completed!")
else:
    print("Timeout - Agent 1 may be hanging")
```

### Example 2: Detecting Hanging Processes

```python
agent = create_coordinated_bridge("Test Agent")

# Start operation
op_id = agent.start_operation("Long task", expected_duration_seconds=10)

# Simulate hang (don't complete)
time.sleep(15)

# Check for hanging
hanging = agent.check_hanging_sessions()
if hanging:
    print(f"Detected {len(hanging)} hanging agent(s)")
```

### Example 3: Publishing with Time Estimates

```python
agent = create_coordinated_bridge("Agent 1")

# Publish finding with time estimate
finding_id = agent.publish_with_time_estimate(
    title="Code analysis complete",
    content="Found 5 issues",
    estimated_seconds=60.0,  # Takes 1 minute to process
    category="code"
)

# Other agents can see the time estimate
estimate = agent.request_time_estimate(finding_id)
```

## Integration with Cross-Chat

The coordination system integrates with cross-chat:

```python
from blackwall.worktrees import CoordinatedCrossChatBridge

# Create coordinated bridge
bridge = CoordinatedCrossChatBridge(session_name="My Session")

# Publish finding
finding_id = bridge.publish("Found bug", "Token issue", category="bug")

# Start operation
op_id = bridge.start_operation("Fix bug", expected_duration_seconds=180)

# Other sessions can:
# - Discover the finding
# - See the operation status
# - Wait for completion
# - Detect if hanging
```

## Best Practices

1. **Send Heartbeats Regularly**: Every 30-60 seconds
   ```python
   import time
   while True:
       agent.send_heartbeat()
       time.sleep(30)
   ```

2. **Always Use Timeouts**: Don't wait indefinitely
   ```python
   success = agent.wait_for_other_session(
       session_id="other",
       timeout_seconds=300.0  # Always set timeout
   )
   ```

3. **Provide Time Estimates**: Help other agents plan
   ```python
   agent.coordinator.provide_time_estimate(
       operation_id="op-123",
       agent_id=agent.session_id,
       estimated_seconds=estimated_time,
       confidence=0.8
   )
   ```

4. **Track Operations**: Always start/complete operations
   ```python
   op_id = agent.start_operation("Doing work")
   try:
       # Do work
       pass
   finally:
       agent.complete_operation(op_id, success=True)
   ```

5. **Check for Hanging**: Periodically check for hanging agents
   ```python
   hanging = agent.check_hanging_sessions()
   if hanging:
       # Handle hanging agents
       pass
   ```

## Database Schema

The coordination system uses SQLite with tables:
- `agent_actions`: Tracks agent actions
- `time_estimates`: Stores time estimates
- `agent_health`: Tracks agent health status

## Files

- `blackwall/worktrees/agent_coordination.py`: Core coordination system
- `blackwall/worktrees/coordination_integration.py`: Integration with cross-chat
- `blackwall/worktrees/coordination_example.py`: Example usage
- `blackwall/worktrees/COORDINATION_GUIDE.md`: Full documentation

## Summary

The coordination system solves:
- ✅ **Race conditions**: Timeout handling prevents indefinite waiting
- ✅ **Hanging processes**: Automatic detection via health monitoring
- ✅ **Time estimation**: Request/provide estimates for planning
- ✅ **Action tracking**: Track what agents are doing
- ✅ **Deadlock detection**: Detect circular dependencies

Use `CoordinatedCrossChatBridge` for enhanced coordination capabilities!
