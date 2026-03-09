# RADICAL Event-Driven Competitive AI Orchestration

## 🚀 Quick Start

```bash
cd worktree-orchestration
pip install -r requirements.txt
python examples/basic_competition.py
```

## 📋 What This Is

A **RADICAL refactor** introducing a fully event-driven, reactive architecture for competitive AI orchestration with:

- ✅ **Event-driven everything**: All communication via events, no direct function calls
- ✅ **Diversity enforcement**: Similarity thresholds prevent solution convergence
- ✅ **Plugin architecture**: Tasks, solutions, scorers, and archetypes are plugins
- ✅ **Unix socket JSON-RPC**: Critique arena exposed as network service
- ✅ **No heavy infrastructure**: Pure Python, asyncio, pragmatic implementation

## 🏗️ Architecture

### Event Bus (Core)

Lightweight async event bus with bounded queues and backpressure:

```python
from src.core.event_bus import get_event_bus
from src.core.event_types import SolutionSubmitted

event_bus = get_event_bus()
await event_bus.start()

event_bus.subscribe(SolutionSubmitted.type, lambda e: print(f"Solution: {e.solution_id}"))
await event_bus.emit(SolutionSubmitted(...))
```

### Diversity Enforcement

Prevents solution convergence via AST-based similarity analysis:

```python
from src.diversity.threshold import DiversityEnforcer, DiversityConfig

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

### JSON-RPC Critique Arena

Unix socket JSON-RPC server for critique operations:

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

### Plugin System

Extensible plugins for tasks, solutions, scorers, and archetypes:

```python
from src.plugins.base import TaskPlugin, SolutionPlugin, ScorerPlugin, ArchetypePlugin

# Implement plugin interfaces
class MyTaskPlugin(TaskPlugin):
    def get_task_spec(self) -> TaskSpec:
        return TaskSpec(...)
    
    def validate_solution(self, solution_path: Path) -> ValidationResult:
        return ValidationResult(...)
    
    def get_test_command(self, solution_path: Path) -> List[str]:
        return ["python", "-m", "pytest", "tests/test.py"]
```

## 📁 File Layout

```
worktree-orchestration/
├── README_RADICAL.md              # This file
├── RADICAL_ARCHITECTURE.md         # Full architecture document
├── ARCHITECTURE_SUMMARY.md         # Quick reference
├── IMPLEMENTATION_GUIDE.md         # Practical guide
├── requirements.txt
│
├── src/
│   ├── core/                       # Event bus & event types
│   │   ├── event_bus.py           # Async event bus
│   │   └── event_types.py         # Event definitions
│   │
│   ├── diversity/                  # Diversity enforcement
│   │   ├── similarity.py          # AST-based similarity
│   │   └── threshold.py           # Threshold enforcement
│   │
│   ├── plugins/                     # Plugin system
│   │   ├── base.py                # Base interfaces
│   │   ├── archetype/              # Archetype plugins
│   │   │   └── radical.py         # RADICAL archetype
│   │   └── scorer/                 # Scorer plugins
│   │       └── weighted_scorer.py
│   │
│   └── rpc/                         # JSON-RPC server
│       ├── server.py               # Unix socket server
│       ├── protocol.py             # JSON-RPC 2.0
│       └── handlers.py             # RPC handlers
│
└── examples/
    └── basic_competition.py        # Example usage
```

## 🔧 How Diversity/Similarity Thresholds Work

### Similarity Metrics

1. **AST Similarity (60% weight)**: Code structure comparison via AST
2. **File Structure Similarity (30% weight)**: Directory tree comparison
3. **Hash Similarity (10% weight)**: Exact file matching

### Enforcement Flow

```
Solution Submitted
    ↓
SimilarityAnalyzer.calculate_similarity()
    ├─ Compare AST structures
    ├─ Compare file trees
    └─ Compare file hashes
    ↓
DiversityEnforcer.check_diversity()
    ├─ Compare to existing solutions
    ├─ Check threshold (default: 0.85)
    ├─ Check cluster size (default: max 3)
    └─ Accept/Reject decision
```

### Configuration

```python
config = DiversityConfig(
    min_similarity_threshold=0.85,  # Reject if >85% similar
    max_cluster_size=3,  # Max 3 solutions per cluster
    diversity_bonus=0.1,  # 10% bonus for unique solutions
    convergence_threshold=0.90  # Round converged if avg >90%
)
```

## 📚 Documentation

- **RADICAL_ARCHITECTURE.md**: Full architecture details, design decisions, event types
- **ARCHITECTURE_SUMMARY.md**: Quick reference guide
- **IMPLEMENTATION_GUIDE.md**: Practical usage examples, plugin development
- **README_RADICAL.md**: This file (overview)

## 🎯 Key Features

1. **Event-Driven**: All communication via events, reactive patterns
2. **Diversity Enforcement**: Prevents solution convergence
3. **Plugin Architecture**: Extensible via plugins
4. **Unix Socket JSON-RPC**: Network service for critiques
5. **Pragmatic**: No heavy infrastructure, pure Python

## 🔄 Event Flow

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

## 🚦 Status

✅ **Implemented:**
- Event bus (async, bounded queues, replay)
- Event types (all competition events)
- Diversity engine (similarity analysis, threshold enforcement)
- Plugin interfaces (task, solution, scorer, archetype)
- JSON-RPC server (Unix socket, JSON-RPC 2.0)
- Example plugins (RADICAL archetype, weighted scorer)
- Example competition flow

⏳ **Next Steps:**
- Round engine (orchestrate round lifecycle)
- Solution manager (handle submission flow)
- Test executor (async test execution)
- CLI commands
- Integration tests

## 💡 Example Usage

See `examples/basic_competition.py` for a complete working example.

## 🔗 Integration

This system integrates with existing code:
- Can import `worktree_manager.py`
- Can use existing `test_harness/run_tests.sh`
- Adds event layer on top
- Gradual migration possible

## 📝 License

Same as parent project.
