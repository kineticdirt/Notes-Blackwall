# RADICAL Architecture: Event-Driven Competitive AI Orchestration

## Philosophy

**RADICAL**: Bold refactor, new patterns, functional/reactive/event-driven, scalability/innovation/tech debt focus.

This architecture breaks from imperative/procedural patterns into a fully event-driven, reactive system where:
- **Everything is an event**: No direct function calls, only event emissions
- **Reactive streams**: Components subscribe to event patterns, not direct dependencies
- **Plugin architecture**: Tasks, solutions, scorers, and archetypes are plugins
- **Unix socket JSON-RPC**: Critique arena exposed as network service
- **Diversity enforcement**: Similarity thresholds prevent solution convergence

## Core Principles

1. **Event Sourcing**: All state changes flow through events
2. **CQRS-lite**: Separate command (events) from query (snapshots)
3. **Actor Model**: Competitors, rounds, and arena are independent actors
4. **Backpressure**: Event bus handles backpressure via bounded queues
5. **Idempotency**: All handlers are idempotent (safe to replay)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Event Bus (Core)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Round    │  │ Solution │  │ Critique │  │ Test     │   │
│  │ Events   │  │ Events   │  │ Events   │  │ Events   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Round Engine │ │ Solution     │ │ Critique     │ │ Test         │
│              │ │ Manager      │ │ Arena        │ │ Executor     │
│              │ │              │ │ (JSON-RPC)   │ │              │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│              Plugin System                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Task     │  │ Solution │  │ Scorer   │  │ Archetype│   │
│  │ Plugins  │  │ Plugins  │  │ Plugins  │  │ Plugins  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│              Diversity Engine                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │ Similarity│ │ Threshold │ │ Clustering│                 │
│  │ Analyzer │ │ Enforcer   │ │ Engine    │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

## Event Bus Design

### Event Types

```python
# Core event hierarchy
Event (base)
├── RoundEvent
│   ├── RoundStarted(round_id, task_spec)
│   ├── RoundEnded(round_id, results)
│   └── RoundConverged(round_id, convergence_score)
├── SolutionEvent
│   ├── SolutionSubmitted(competitor_id, round_id, solution_id, files)
│   ├── SolutionValidated(solution_id, valid, errors)
│   ├── SolutionRejected(solution_id, reason, similarity_to_existing)
│   └── SolutionAccepted(solution_id, diversity_score)
├── CritiqueEvent
│   ├── CritiqueRequested(competitor_id, target_solution_id)
│   ├── CritiqueSubmitted(critique_id, competitor_id, target_id, critique)
│   └── CritiqueEvaluated(critique_id, score)
├── TestEvent
│   ├── TestStarted(solution_id, test_suite)
│   ├── TestCompleted(solution_id, passed, output, duration)
│   └── TestFailed(solution_id, error, timeout)
└── ScoringEvent
    ├── ScoreCalculated(solution_id, scores)
    ├── RankUpdated(round_id, rankings)
    └── ConvergenceCalculated(round_id, convergence_metric)
```

### Event Bus Implementation

**Python-based, async-first, with backpressure:**

```python
# Lightweight event bus using asyncio.Queue
# No heavy dependencies (no RxJS, no Kafka, no Redis)
# Bounded queues prevent memory bloat
# Event replay for crash recovery
```

## Plugin System

### Task Plugin Interface

```python
class TaskPlugin(ABC):
    """Plugin for defining competition tasks."""
    
    @abstractmethod
    def get_task_spec(self) -> TaskSpec:
        """Return task specification (description, constraints, test suite)."""
        pass
    
    @abstractmethod
    def validate_solution(self, solution_path: Path) -> ValidationResult:
        """Validate solution structure before acceptance."""
        pass
    
    @abstractmethod
    def get_test_command(self, solution_path: Path) -> List[str]:
        """Return test command for this task."""
        pass
```

### Solution Plugin Interface

```python
class SolutionPlugin(ABC):
    """Plugin for solution generation strategies."""
    
    @abstractmethod
    async def generate_solution(
        self, 
        competitor_id: str,
        round_id: int,
        task_spec: TaskSpec,
        context: SolutionContext  # Includes other solutions, critiques
    ) -> Solution:
        """Generate a solution given task and context."""
        pass
    
    @abstractmethod
    def get_archetype(self) -> str:
        """Return archetype identifier (RADICAL, CONSERVATIVE, etc.)."""
        pass
```

### Scorer Plugin Interface

```python
class ScorerPlugin(ABC):
    """Plugin for scoring solutions."""
    
    @abstractmethod
    def calculate_score(
        self,
        solution: Solution,
        test_results: TestResults,
        critiques: List[Critique]
    ) -> Score:
        """Calculate composite score."""
        pass
```

### Archetype Plugin Interface

```python
class ArchetypePlugin(ABC):
    """Plugin defining competitor archetype behavior."""
    
    @abstractmethod
    def get_behavior_profile(self) -> BehaviorProfile:
        """Return behavior profile (risk tolerance, innovation level, etc.)."""
        pass
    
    @abstractmethod
    async def adapt_strategy(
        self,
        competitor_id: str,
        round_history: List[Round],
        current_rankings: Rankings
    ) -> Strategy:
        """Adapt strategy based on history."""
        pass
```

## Diversity & Similarity Enforcement

### Similarity Metrics

1. **Code Similarity**: AST-based comparison (using `ast` module)
2. **Semantic Similarity**: Embedding-based (optional, lightweight model)
3. **File Structure Similarity**: Directory tree comparison
4. **Test Output Similarity**: Test result comparison

### Threshold System

```python
class DiversityConfig:
    min_similarity_threshold: float = 0.85  # Reject if >85% similar
    max_cluster_size: int = 3  # Max solutions per cluster
    diversity_bonus: float = 0.1  # Bonus score for unique solutions
    convergence_threshold: float = 0.90  # Round converged if avg similarity >90%
```

### Enforcement Flow

```
SolutionSubmitted → SimilarityAnalyzer → DiversityEngine
                                      ├─> SimilarityScore
                                      ├─> ClusterAssignment
                                      └─> Accept/Reject Decision
```

## Unix Socket JSON-RPC Critique Arena

### Protocol

**Transport**: Unix domain socket (AF_UNIX)
**Protocol**: JSON-RPC 2.0
**Location**: `{cache_dir}/critique-arena.sock`

### Methods

```json
{
  "jsonrpc": "2.0",
  "method": "critique.request",
  "params": {
    "competitor_id": "radical_1",
    "round_id": 1,
    "target_solution_id": "sol_abc123"
  },
  "id": 1
}

{
  "jsonrpc": "2.0",
  "method": "critique.submit",
  "params": {
    "competitor_id": "radical_1",
    "critique_id": "crit_xyz789",
    "critique": {
      "text": "This solution lacks error handling...",
      "scores": {
        "clarity": 7,
        "correctness": 6,
        "efficiency": 8
      }
    }
  },
  "id": 2
}

{
  "jsonrpc": "2.0",
  "method": "solutions.list",
  "params": {
    "round_id": 1,
    "competitor_id": "radical_1"  // optional filter
  },
  "id": 3
}
```

### Server Implementation

- Async server using `asyncio` + Unix socket
- Event bus integration: RPC calls emit events
- Thread-safe: Multiple concurrent clients
- Graceful shutdown: Drain connections

## File Layout

```
worktree-orchestration/
├── README.md
├── RADICAL_ARCHITECTURE.md          # This file
├── requirements.txt
├── pyproject.toml
│
├── src/
│   ├── __init__.py
│   │
│   ├── core/                         # Core event-driven infrastructure
│   │   ├── __init__.py
│   │   ├── event_bus.py             # Event bus implementation
│   │   ├── event_types.py           # Event type definitions
│   │   ├── event_store.py           # Event persistence (optional)
│   │   └── snapshot.py              # State snapshots for queries
│   │
│   ├── engine/                       # Orchestration engines
│   │   ├── __init__.py
│   │   ├── round_engine.py          # Round lifecycle management
│   │   ├── solution_manager.py      # Solution submission & validation
│   │   ├── test_executor.py         # Test execution (async)
│   │   └── scoring_engine.py        # Score calculation
│   │
│   ├── diversity/                    # Diversity enforcement
│   │   ├── __init__.py
│   │   ├── similarity.py            # Similarity analysis
│   │   ├── clustering.py            # Solution clustering
│   │   ├── threshold.py             # Threshold enforcement
│   │   └── metrics.py                # Diversity metrics
│   │
│   ├── plugins/                      # Plugin system
│   │   ├── __init__.py
│   │   ├── base.py                   # Base plugin interfaces
│   │   ├── task/                     # Task plugins
│   │   │   ├── __init__.py
│   │   │   └── example_task.py
│   │   ├── solution/                 # Solution plugins
│   │   │   ├── __init__.py
│   │   │   └── archetype_*.py        # Archetype-specific generators
│   │   ├── scorer/                   # Scorer plugins
│   │   │   ├── __init__.py
│   │   │   └── weighted_scorer.py
│   │   └── archetype/                # Archetype plugins
│   │       ├── __init__.py
│   │       ├── radical.py
│   │       ├── conservative.py
│   │       └── balanced.py
│   │
│   ├── rpc/                          # JSON-RPC critique arena
│   │   ├── __init__.py
│   │   ├── server.py                 # Unix socket server
│   │   ├── handlers.py               # RPC method handlers
│   │   ├── protocol.py               # JSON-RPC 2.0 protocol
│   │   └── client.py                 # Client library (optional)
│   │
│   ├── worktree/                     # Worktree management
│   │   ├── __init__.py
│   │   ├── manager.py                # Worktree lifecycle
│   │   └── isolation.py              # Isolation enforcement
│   │
│   ├── artifacts/                    # Artifact storage
│   │   ├── __init__.py
│   │   ├── store.py                  # Artifact storage
│   │   └── formats.py                # Artifact schemas
│   │
│   └── cli/                          # CLI interface
│       ├── __init__.py
│       ├── main.py                   # CLI entry point
│       └── commands/                 # Command implementations
│           ├── __init__.py
│           ├── round.py
│           ├── competitor.py
│           ├── plugin.py
│           └── arena.py
│
├── plugins/                          # User-defined plugins (optional)
│   ├── tasks/
│   ├── solutions/
│   └── scorers/
│
├── configs/                          # Configuration files
│   ├── default.yaml
│   └── examples/
│
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_event_bus.py
│   │   ├── test_diversity.py
│   │   └── test_plugins.py
│   ├── integration/
│   │   ├── test_round_flow.py
│   │   └── test_rpc_arena.py
│   └── fixtures/
│
└── examples/
    ├── basic_competition.py
    ├── custom_plugin.py
    └── rpc_client_example.py
```

## Implementation Strategy

### Phase 1: Event Bus Foundation
- Async event bus with bounded queues
- Event type system with Pydantic models
- Basic subscription/unsubscription
- Event replay mechanism

### Phase 2: Core Engines
- Round engine (event-driven)
- Solution manager with validation
- Test executor (async subprocess)
- Scoring engine

### Phase 3: Diversity System
- AST-based similarity analyzer
- Clustering engine
- Threshold enforcement
- Integration with solution manager

### Phase 4: Plugin System
- Plugin registry and loader
- Base plugin interfaces
- Example plugins (task, solution, scorer)
- Plugin discovery

### Phase 5: JSON-RPC Arena
- Unix socket server
- JSON-RPC 2.0 protocol
- Event bus integration
- Client library

### Phase 6: CLI & Polish
- CLI commands
- Configuration management
- Error handling
- Documentation

## Key Design Decisions

1. **No Heavy Infrastructure**: Pure Python, asyncio, no Kafka/Redis/RabbitMQ
2. **Unix Socket over TCP**: Simpler, faster, local-only (fits use case)
3. **Event Sourcing Lite**: Events stored for replay, but not full event sourcing
4. **Plugin over Inheritance**: Extensibility via plugins, not class hierarchies
5. **AST Similarity**: Code similarity via AST (no ML required, fast)
6. **Bounded Queues**: Prevent memory bloat, backpressure handling
7. **Idempotent Handlers**: Safe replay, crash recovery

## Scalability Considerations

- **Horizontal**: Multiple arena servers (load balance via socket paths)
- **Vertical**: Async I/O handles concurrency efficiently
- **Memory**: Bounded queues, event replay buffer limits
- **Disk**: Event log rotation, artifact cleanup policies

## Tech Debt & Innovation Tradeoffs

**Innovation**:
- Event-driven architecture enables future distributed deployment
- Plugin system allows experimentation without core changes
- Diversity enforcement prevents premature convergence

**Tech Debt**:
- Event replay adds complexity (but enables debugging)
- Plugin discovery overhead (mitigated by caching)
- Similarity analysis CPU cost (mitigated by caching)

## Migration Path

Existing `worktree-orchestration/` scripts remain intact. New system:
1. Can import existing worktree manager
2. Can use existing test harness
3. Adds event layer on top
4. Gradual migration possible
