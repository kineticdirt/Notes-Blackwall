# RADICAL Architecture Summary

## Overview

This is a **RADICAL refactor** introducing a fully event-driven, reactive architecture for competitive AI orchestration. The system prevents solution convergence through diversity enforcement and exposes critique operations via Unix socket JSON-RPC.

## Key Innovations

1. **Event-Driven Everything**: No direct function calls, all communication via events
2. **Reactive Streams**: Components subscribe to event patterns
3. **Plugin Architecture**: Tasks, solutions, scorers, and archetypes are plugins
4. **Unix Socket JSON-RPC**: Critique arena as network service
5. **Diversity Enforcement**: Similarity thresholds prevent convergence

## Architecture Components

### 1. Event Bus (`src/core/event_bus.py`)

**Lightweight async event bus** with:
- Bounded queues (backpressure handling)
- Event replay (crash recovery)
- Type-safe subscriptions
- No heavy dependencies (pure Python asyncio)

**Usage:**
```python
event_bus = get_event_bus()
await event_bus.start()

# Subscribe
event_bus.subscribe(SolutionSubmitted.type, handler)

# Emit
await event_bus.emit(SolutionSubmitted(...))
```

### 2. Diversity Engine (`src/diversity/`)

**Prevents solution convergence** via:
- **AST-based similarity**: Code structure comparison (no ML required)
- **File structure similarity**: Directory tree comparison
- **Hash-based similarity**: Exact file matching
- **Threshold enforcement**: Reject solutions exceeding similarity threshold
- **Clustering**: Group similar solutions into clusters

**Key Classes:**
- `SimilarityAnalyzer`: Calculates similarity between solutions
- `DiversityEnforcer`: Enforces thresholds and tracks solutions per round

**Usage:**
```python
enforcer = DiversityEnforcer(DiversityConfig(
    min_similarity_threshold=0.85,  # Reject if >85% similar
    max_cluster_size=3,  # Max 3 solutions per cluster
    diversity_bonus=0.1  # 10% bonus for unique solutions
))

accepted, reason, similarity, similar_ids = enforcer.check_diversity(
    round_id=1,
    solution_id="sol_123",
    solution_path=Path("worktrees/wt_competitor_r1/solution")
)
```

### 3. Plugin System (`src/plugins/`)

**Extensible plugin interfaces:**
- `TaskPlugin`: Define competition tasks
- `SolutionPlugin`: Generate solutions (with archetype support)
- `ScorerPlugin`: Calculate scores
- `ArchetypePlugin`: Define competitor behavior (RADICAL, CONSERVATIVE, etc.)

**Example Archetype:**
```python
class RadicalArchetype(ArchetypePlugin):
    def get_behavior_profile(self):
        return BehaviorProfile(
            archetype_id="radical",
            risk_tolerance=0.9,
            innovation_level=0.95,
            convergence_avoidance=0.85
        )
```

### 4. JSON-RPC Critique Arena (`src/rpc/`)

**Unix socket JSON-RPC server** for critique operations:
- `critique.request`: Request a critique
- `critique.submit`: Submit a critique
- `solutions.list`: List solutions for a round
- `solution.get`: Get specific solution

**Protocol:** JSON-RPC 2.0 over Unix domain socket

**Usage:**
```python
server = UnixSocketRPCServer(Path(".shared-cache/arena.sock"), handler)
await server.start()
```

**Client Example:**
```python
# Python client
import socket, json
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.connect(".shared-cache/arena.sock")
sock.sendall(json.dumps({
    "jsonrpc": "2.0",
    "method": "solutions.list",
    "params": {"round_id": 1},
    "id": 1
}).encode() + b'\n')
response = json.loads(sock.recv(4096).decode())
```

## File Layout

```
worktree-orchestration/
├── RADICAL_ARCHITECTURE.md      # Full architecture document
├── ARCHITECTURE_SUMMARY.md      # This file
├── IMPLEMENTATION_GUIDE.md      # Practical guide
├── requirements.txt
│
├── src/
│   ├── core/                    # Event bus & event types
│   │   ├── event_bus.py        # Async event bus
│   │   └── event_types.py      # Event definitions
│   │
│   ├── diversity/               # Diversity enforcement
│   │   ├── similarity.py      # AST-based similarity
│   │   └── threshold.py        # Threshold enforcement
│   │
│   ├── plugins/                 # Plugin system
│   │   ├── base.py             # Base interfaces
│   │   ├── archetype/          # Archetype plugins
│   │   │   └── radical.py     # RADICAL archetype
│   │   └── scorer/             # Scorer plugins
│   │       └── weighted_scorer.py
│   │
│   └── rpc/                     # JSON-RPC server
│       ├── server.py           # Unix socket server
│       ├── protocol.py         # JSON-RPC 2.0
│       └── handlers.py         # RPC handlers
│
└── examples/
    └── basic_competition.py    # Example usage
```

## Diversity/Similarity Enforcement Flow

```
Solution Submitted
    ↓
SimilarityAnalyzer.calculate_similarity()
    ├─ AST similarity (code structure)
    ├─ File structure similarity
    └─ Hash similarity (exact matches)
    ↓
DiversityEnforcer.check_diversity()
    ├─ Compare to existing solutions
    ├─ Check similarity threshold (default: 0.85)
    ├─ Check cluster size (default: max 3)
    └─ Decision: Accept/Reject
    ↓
If Accepted:
    ├─ Register solution
    ├─ Calculate diversity score
    └─ Emit SolutionAccepted event
If Rejected:
    └─ Emit SolutionRejected event (with reason)
```

## Event Flow

```
RoundStarted
    ↓
SolutionSubmitted → SolutionValidated → SolutionAccepted/Rejected
    ↓ (if accepted)
TestStarted → TestCompleted
    ↓
ScoreCalculated → RankUpdated
    ↓
ConvergenceCalculated (if needed)
    ↓
RoundEnded
```

## Key Design Decisions

1. **No Heavy Infrastructure**: Pure Python, asyncio, no Kafka/Redis/RabbitMQ
2. **Unix Socket over TCP**: Simpler, faster, local-only
3. **AST Similarity**: Code similarity via AST (no ML, fast, deterministic)
4. **Bounded Queues**: Prevent memory bloat, backpressure handling
5. **Plugin over Inheritance**: Extensibility via plugins
6. **Event Sourcing Lite**: Events stored for replay, but not full event sourcing

## How to Enforce Diversity/Similarity Thresholds

### Configuration

```python
from src.diversity.threshold import DiversityConfig

config = DiversityConfig(
    min_similarity_threshold=0.85,  # Reject if >85% similar
    max_cluster_size=3,  # Max 3 solutions per cluster
    diversity_bonus=0.1,  # 10% bonus for unique solutions
    convergence_threshold=0.90  # Round converged if avg >90%
)
```

### Enforcement

```python
from src.diversity.threshold import DiversityEnforcer

enforcer = DiversityEnforcer(config)

# Check before accepting solution
accepted, reason, similarity, similar_ids = enforcer.check_diversity(
    round_id=1,
    solution_id="sol_new",
    solution_path=Path("worktrees/wt_new_r1/solution")
)

if accepted:
    # Register solution
    enforcer.register_solution(1, "sol_new", Path("..."))
    
    # Calculate diversity score (for bonus)
    diversity_score = enforcer.calculate_diversity_score(1, "sol_new", Path("..."))
else:
    # Reject with reason
    print(f"Rejected: {reason}")
    print(f"Similarity: {similarity:.2f}")
    print(f"Similar solutions: {similar_ids}")
```

### Convergence Detection

```python
# Calculate convergence for a round
convergence, cluster_sizes = enforcer.calculate_convergence(round_id=1)

if convergence >= config.convergence_threshold:
    print(f"Round converged! (similarity: {convergence:.2f})")
    # Emit RoundConverged event
```

## Similarity Metrics

1. **AST Similarity (60% weight)**: 
   - Parses Python files to AST
   - Compares node types and structure
   - Jaccard similarity on node signatures

2. **File Structure Similarity (30% weight)**:
   - Compares directory tree structure
   - Jaccard similarity on file paths

3. **Hash Similarity (10% weight)**:
   - SHA256 hashes of file contents
   - Counts exact matches

**Weighted combination** gives overall similarity score [0.0, 1.0].

## Integration with Existing Code

The new event-driven system can:
1. **Import existing worktree manager** (`worktree_manager.py`)
2. **Use existing test harness** (`test_harness/run_tests.sh`)
3. **Add event layer on top** without breaking existing code
4. **Gradual migration** possible

## Next Steps

1. Implement `RoundEngine` to orchestrate round lifecycle
2. Implement `SolutionManager` to handle submission flow
3. Implement `TestExecutor` for async test execution
4. Wire components together via events
5. Add CLI commands
6. Add comprehensive tests

## Example: Complete Round Flow

See `examples/basic_competition.py` for a complete working example.

## Documentation

- **RADICAL_ARCHITECTURE.md**: Full architecture details
- **IMPLEMENTATION_GUIDE.md**: Practical usage guide
- **ARCHITECTURE_SUMMARY.md**: This file (quick reference)
