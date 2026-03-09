# Implementation Guide: RADICAL Event-Driven Architecture

## Quick Start

### 1. Install Dependencies

```bash
cd worktree-orchestration
pip install -r requirements.txt
```

### 2. Basic Usage

```python
import asyncio
from src.core.event_bus import get_event_bus, EventBus
from src.core.event_types import RoundStarted, SolutionSubmitted
from src.diversity.threshold import DiversityEnforcer, DiversityConfig
from src.rpc.server import UnixSocketRPCServer
from src.rpc.handlers import CritiqueArenaHandlers
from src.rpc.protocol import JSONRPCHandler

async def main():
    # Initialize event bus
    event_bus = get_event_bus()
    await event_bus.start()
    
    # Subscribe to events
    def on_solution_submitted(event: SolutionSubmitted):
        print(f"Solution submitted: {event.solution_id}")
    
    event_bus.subscribe(SolutionSubmitted.type, on_solution_submitted)
    
    # Initialize diversity enforcer
    diversity_config = DiversityConfig(
        min_similarity_threshold=0.85,
        max_cluster_size=3,
        diversity_bonus=0.1
    )
    enforcer = DiversityEnforcer(diversity_config)
    
    # Start JSON-RPC server
    handlers = CritiqueArenaHandlers()
    rpc_handler = JSONRPCHandler()
    rpc_handler.register_method("critique.request", handlers.critique_request)
    rpc_handler.register_method("critique.submit", handlers.critique_submit)
    rpc_handler.register_method("solutions.list", handlers.solutions_list)
    
    server = UnixSocketRPCServer(
        Path(".shared-cache/critique-arena.sock"),
        rpc_handler
    )
    await server.start()
    
    # Emit a test event
    event = RoundStarted(
        round_id=1,
        task_spec={"name": "Test Task", "description": "..."},
        competitor_ids=["radical_1", "conservative_1"]
    )
    await event_bus.emit(event)
    
    # Keep running
    try:
        await asyncio.sleep(3600)  # Run for 1 hour
    finally:
        await server.stop()
        await event_bus.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

## Architecture Components

### Event Bus

The event bus is the core of the system. All components communicate via events.

```python
from src.core.event_bus import get_event_bus
from src.core.event_types import SolutionSubmitted

event_bus = get_event_bus()
await event_bus.start()

# Subscribe
unsubscribe = event_bus.subscribe(
    SolutionSubmitted.type,
    lambda event: print(f"Solution: {event.solution_id}")
)

# Emit
await event_bus.emit(SolutionSubmitted(
    competitor_id="radical_1",
    round_id=1,
    solution_id="sol_123",
    files=[],
    worktree_path=Path("worktrees/wt_radical_1_r1")
))
```

### Diversity Enforcement

Enforce similarity thresholds to prevent solution convergence.

```python
from src.diversity.threshold import DiversityEnforcer, DiversityConfig
from pathlib import Path

config = DiversityConfig(
    min_similarity_threshold=0.85,  # Reject if >85% similar
    max_cluster_size=3,  # Max 3 solutions per cluster
    diversity_bonus=0.1  # 10% bonus for unique solutions
)

enforcer = DiversityEnforcer(config)

# Check diversity
accepted, reason, similarity, similar_ids = enforcer.check_diversity(
    round_id=1,
    solution_id="sol_new",
    solution_path=Path("worktrees/wt_new_r1/solution")
)

if accepted:
    enforcer.register_solution(1, "sol_new", Path("worktrees/wt_new_r1/solution"))
    diversity_score = enforcer.calculate_diversity_score(1, "sol_new", Path("..."))
else:
    print(f"Rejected: {reason}")
```

### JSON-RPC Critique Arena

Expose critique operations via Unix socket JSON-RPC.

**Server Side:**

```python
from src.rpc.server import UnixSocketRPCServer
from src.rpc.handlers import CritiqueArenaHandlers
from src.rpc.protocol import JSONRPCHandler

handlers = CritiqueArenaHandlers()
rpc_handler = JSONRPCHandler()
rpc_handler.register_method("critique.request", handlers.critique_request)
rpc_handler.register_method("critique.submit", handlers.critique_submit)
rpc_handler.register_method("solutions.list", handlers.solutions_list)

server = UnixSocketRPCServer(Path(".shared-cache/arena.sock"), rpc_handler)
await server.start()
```

**Client Side (Python):**

```python
import socket
import json

def rpc_call(socket_path: str, method: str, params: dict) -> dict:
    """Call JSON-RPC method."""
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(socket_path)
    
    request = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    
    sock.sendall(json.dumps(request).encode() + b'\n')
    response_str = sock.recv(4096).decode()
    sock.close()
    
    return json.loads(response_str)

# Example: Request critique
result = rpc_call(
    ".shared-cache/arena.sock",
    "critique.request",
    {
        "competitor_id": "radical_1",
        "round_id": 1,
        "target_solution_id": "sol_abc123"
    }
)
print(result)
```

**Client Side (Command Line):**

```bash
# Using socat or nc
echo '{"jsonrpc":"2.0","method":"solutions.list","params":{"round_id":1},"id":1}' | \
  socat - UNIX-CONNECT:.shared-cache/arena.sock
```

## Plugin Development

### Creating a Task Plugin

```python
from src.plugins.base import TaskPlugin, TaskSpec, ValidationResult
from pathlib import Path
from typing import List

class MyTaskPlugin(TaskPlugin):
    def get_task_spec(self) -> TaskSpec:
        return TaskSpec(
            name="My Task",
            description="Solve problem X",
            constraints=["Must use Python", "No external deps"],
            test_suite="tests/test_solution.py",
            metadata={"difficulty": "medium"}
        )
    
    def validate_solution(self, solution_path: Path) -> ValidationResult:
        # Check solution structure
        main_file = solution_path / "main.py"
        if not main_file.exists():
            return ValidationResult(
                valid=False,
                errors=["main.py not found"]
            )
        return ValidationResult(valid=True, errors=[])
    
    def get_test_command(self, solution_path: Path) -> List[str]:
        return ["python", "-m", "pytest", "tests/test_solution.py"]
```

### Creating a Solution Plugin

```python
from src.plugins.base import SolutionPlugin, Solution, SolutionContext, TaskSpec
from pathlib import Path
import shutil

class MySolutionPlugin(SolutionPlugin):
    async def generate_solution(
        self,
        competitor_id: str,
        round_id: int,
        task_spec: TaskSpec,
        context: SolutionContext
    ) -> Solution:
        # Generate solution files
        worktree_path = Path(f"worktrees/wt_{competitor_id}_r{round_id}")
        solution_dir = worktree_path / "solution"
        solution_dir.mkdir(parents=True, exist_ok=True)
        
        # Write solution
        (solution_dir / "main.py").write_text("# My solution")
        
        return Solution(
            solution_id=f"sol_{competitor_id}_{round_id}",
            competitor_id=competitor_id,
            round_id=round_id,
            files=[{"path": "main.py", "size": 100, "hash": "abc123"}],
            worktree_path=worktree_path
        )
    
    def get_archetype(self) -> str:
        return "radical"
```

### Creating an Archetype Plugin

```python
from src.plugins.base import ArchetypePlugin, BehaviorProfile, Strategy

class MyArchetype(ArchetypePlugin):
    def get_behavior_profile(self) -> BehaviorProfile:
        return BehaviorProfile(
            archetype_id="my_archetype",
            risk_tolerance=0.7,
            innovation_level=0.8,
            convergence_avoidance=0.6,
            metadata={}
        )
    
    async def adapt_strategy(self, competitor_id, round_history, rankings):
        return Strategy(
            competitor_id=competitor_id,
            approach="custom",
            parameters={"param1": "value1"}
        )
```

## Event Flow Example

Complete round flow with events:

```python
# 1. Start round
await event_bus.emit(RoundStarted(
    round_id=1,
    task_spec={"name": "Task 1"},
    competitor_ids=["radical_1"]
))

# 2. Submit solution
await event_bus.emit(SolutionSubmitted(
    competitor_id="radical_1",
    round_id=1,
    solution_id="sol_1",
    files=[],
    worktree_path=Path("worktrees/wt_radical_1_r1")
))

# 3. Validate (diversity check)
accepted, reason, sim, similar = enforcer.check_diversity(1, "sol_1", Path("..."))
if accepted:
    await event_bus.emit(SolutionAccepted(
        solution_id="sol_1",
        diversity_score=0.9
    ))
else:
    await event_bus.emit(SolutionRejected(
        solution_id="sol_1",
        reason=reason,
        similarity_to_existing=sim
    ))

# 4. Run tests
await event_bus.emit(TestStarted(solution_id="sol_1", test_suite="tests/test.py"))
# ... test execution ...
await event_bus.emit(TestCompleted(
    solution_id="sol_1",
    passed=True,
    output="All tests passed",
    duration_ms=1500
))

# 5. Calculate score
score = scorer.calculate_score(solution, test_results, critiques)
await event_bus.emit(ScoreCalculated(
    solution_id="sol_1",
    scores=score.breakdown,
    test_results={}
))

# 6. End round
await event_bus.emit(RoundEnded(round_id=1, results={}))
```

## File Layout Summary

```
worktree-orchestration/
├── src/
│   ├── core/              # Event bus, event types
│   ├── diversity/          # Similarity, threshold enforcement
│   ├── plugins/            # Plugin interfaces and examples
│   ├── rpc/                # JSON-RPC server
│   └── ...
├── plugins/                # User plugins (optional)
├── configs/                # Configuration files
└── examples/               # Example scripts
```

## Next Steps

1. **Implement Round Engine**: Orchestrate round lifecycle
2. **Implement Solution Manager**: Handle solution submission flow
3. **Implement Test Executor**: Async test execution
4. **Integrate Components**: Wire everything together via events
5. **Add CLI**: Command-line interface for operations
6. **Add Tests**: Unit and integration tests

See `RADICAL_ARCHITECTURE.md` for full architecture details.
