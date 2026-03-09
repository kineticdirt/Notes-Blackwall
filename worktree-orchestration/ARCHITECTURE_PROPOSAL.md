# Worktree Orchestration - Minimal Stable Architecture Proposal

**Archetype:** CONSERVATIVE  
**Goal:** Extend existing implementation with archetypes, JSON-RPC critique arena, benchmarks/security checks, and iterative rounds  
**Constraint:** Max 10 files changed (conceptually), implementable in 1-2 hours  
**Date:** 2026-01-30

## Overview

Minimal extensions to existing `worktree-orchestration/` to support:
- **Multiple archetypes** per competitor (conservative, aggressive, balanced, etc.)
- **JSON-RPC server** over unix socket (`../.shared-cache/critique-arena.sock`) for cross-review
- **Benchmarks & security checks** in addition to tests
- **Iterative rounds** with orchestration
- **Final reports** in parent `.shared-cache/` directory

## Directory Layout

```
worktree-orchestration/
├── src/
│   ├── config.py              # [EXTEND] Add archetype config
│   ├── competitor.py          # [EXTEND] Add archetype field
│   ├── arena.py               # [EXTEND] Add benchmark/security hooks
│   ├── artifacts.py            # [EXTEND] Support parent .shared-cache/
│   ├── rpc_server.py           # [NEW] JSON-RPC server for critique arena
│   ├── orchestrator.py        # [NEW] Iterative round orchestration
│   └── reporter.py            # [NEW] Final report generation
├── tests/
│   ├── test_rpc_server.py     # [NEW] RPC server tests
│   └── test_orchestrator.py   # [NEW] Orchestrator tests
└── examples/
    └── archetype_config.json  # [NEW] Example with archetypes
```

**Total:** 3 new files, 4 extensions = 7 conceptual changes (under 10 limit)

## Core Extensions

### 1. Archetype Support

**File:** `src/config.py` + `src/competitor.py`

- Add `archetype` field to competitor registration (conservative, aggressive, balanced, experimental)
- Store archetype in competitor metadata
- Use archetype for strategy selection in critiques

**Changes:**
```python
# competitor.py
class Competitor(BaseModel):
    archetype: str = Field(default="balanced", pattern="^(conservative|aggressive|balanced|experimental)$")
```

### 2. JSON-RPC Critique Arena Server

**File:** `src/rpc_server.py` (NEW)

**Purpose:** Enable cross-review via JSON-RPC over unix socket

**Key Classes:**
- `CritiqueArenaServer`: JSON-RPC server listening on `../.shared-cache/critique-arena.sock`
- Methods: `submit_critique`, `get_solutions`, `get_critiques`, `ping`

**Implementation:**
- Use `jsonrpcserver` library (lightweight, async-capable)
- Unix domain socket server
- Thread-safe artifact access
- Graceful shutdown handling

**RPC Methods:**
```python
{
  "method": "submit_critique",
  "params": {
    "competitor_id": "agent_a",
    "round_num": 1,
    "target_solution_id": "agent_b_1234567890",
    "critique_text": "...",
    "scores": {"clarity": 8, "correctness": 7}
  }
}
```

### 3. Benchmark & Security Checks

**File:** `src/arena.py` (EXTEND)

**Purpose:** Add benchmark and security check hooks to test execution

**Changes:**
- Add `benchmark_command` and `security_check_command` to `ArenaConfig`
- Execute benchmarks after tests (performance metrics)
- Execute security checks (static analysis, vulnerability scanning)
- Store results in test results artifact

**Flow:**
1. Execute tests → test results
2. Execute benchmarks → benchmark results (timing, memory, etc.)
3. Execute security checks → security report (vulnerabilities, code quality)
4. Aggregate all results

### 4. Iterative Round Orchestration

**File:** `src/orchestrator.py` (NEW)

**Purpose:** Coordinate iterative rounds with cross-review

**Key Classes:**
- `RoundOrchestrator`: Manages round lifecycle
- `RoundState`: Tracks round state (setup, submission, critique, testing, completed)

**Flow:**
1. **Setup:** Create worktrees for all competitors
2. **Submission:** Competitors submit solutions
3. **Critique Phase:** Competitors review others via RPC server
4. **Testing:** Execute tests, benchmarks, security checks
5. **Results:** Collect and store artifacts
6. **Report:** Generate final report

**Methods:**
- `run_round(round_num, config)` - Execute full round
- `wait_for_submissions(round_num, timeout)` - Wait for all submissions
- `wait_for_critiques(round_num, timeout)` - Wait for critiques
- `execute_validation(round_num)` - Run tests/benchmarks/security

### 5. Final Report Generation

**File:** `src/reporter.py` (NEW)

**Purpose:** Generate final report artifacts in `../.shared-cache/`

**Key Classes:**
- `ReportGenerator`: Creates HTML/JSON reports

**Outputs:**
- `../.shared-cache/round_{num}_report.html` - Human-readable HTML report
- `../.shared-cache/round_{num}_report.json` - Machine-readable JSON report
- `../.shared-cache/competition_summary.json` - Overall competition summary

**Report Contents:**
- Round results (test scores, benchmarks, security)
- Critique summaries
- Competitor rankings
- Archetype performance analysis

### 6. Parent Directory Artifact Storage

**File:** `src/artifacts.py` (EXTEND)

**Purpose:** Support storing artifacts in parent `.shared-cache/` directory

**Changes:**
- Add `parent_cache_dir` parameter to `ArtifactStore.__init__`
- Use parent directory for final reports
- Keep round artifacts in local cache, reports in parent

## Implementation Strategy

### Phase 1: Foundation (30 min)
1. Extend `competitor.py` with archetype field
2. Extend `config.py` with benchmark/security commands
3. Update `artifacts.py` to support parent cache directory

### Phase 2: RPC Server (30 min)
1. Implement `rpc_server.py` with JSON-RPC server
2. Add unix socket handling
3. Integrate with artifact store for critique submission

### Phase 3: Orchestration (30 min)
1. Implement `orchestrator.py` with round flow
2. Extend `arena.py` with benchmark/security execution
3. Add orchestration methods

### Phase 4: Reporting (30 min)
1. Implement `reporter.py` with report generation
2. Generate HTML and JSON reports
3. Store in parent `.shared-cache/` directory

## Key Design Decisions

### 1. Unix Socket Location
- **Path:** `../.shared-cache/critique-arena.sock` (relative to worktree-orchestration/)
- **Rationale:** Shared cache directory accessible to all competitors
- **Security:** Unix sockets provide process isolation

### 2. Archetype Implementation
- **Storage:** Field in competitor metadata
- **Usage:** Strategy selection for critiques, not solution generation
- **Extensibility:** Pattern-based validation allows easy addition

### 3. Benchmark/Security Hooks
- **Execution:** Sequential after tests (tests → benchmarks → security)
- **Failure Handling:** Non-blocking (failures logged, don't stop round)
- **Results:** Stored in test results artifact

### 4. Report Location
- **Local:** Round artifacts in `worktree-orchestration/.shared-cache/`
- **Parent:** Final reports in `../.shared-cache/` (workspace root)
- **Rationale:** Reports are final artifacts, should be at workspace level

## Testing Strategy

### Unit Tests
- `test_rpc_server.py`: RPC method testing, socket handling
- `test_orchestrator.py`: Round flow, state transitions
- Extend existing tests for new fields

### Integration Tests
- Full round execution with RPC server
- Report generation end-to-end
- Multi-competitor critique submission

### Test Fixtures
- Mock competitors with different archetypes
- Sample solutions and critiques
- Test configs with benchmark/security commands

## Dependencies

**New Dependencies:**
- `jsonrpcserver` - JSON-RPC server implementation
- `aiofiles` (optional) - Async file operations for RPC server

**Update:** `requirements.txt` with new dependencies

## Security Considerations

1. **Unix Socket Permissions:** Restrict socket file permissions (600)
2. **RPC Input Validation:** Validate all RPC parameters
3. **Path Traversal:** Ensure critique submissions don't escape worktrees
4. **Resource Limits:** Timeout RPC calls, limit concurrent connections

## Performance Considerations

1. **RPC Server:** Use async/threading for concurrent requests
2. **Benchmark Execution:** Parallel execution option (configurable)
3. **Report Generation:** Lazy evaluation, cache intermediate results
4. **Socket Communication:** Keep payloads small, use compression if needed

## Success Criteria

1. ✅ Competitors can register with archetypes
2. ✅ RPC server accepts critique submissions over unix socket
3. ✅ Benchmarks and security checks execute after tests
4. ✅ Orchestrator runs complete round flow
5. ✅ Reports generated in parent `.shared-cache/` directory
6. ✅ All tests pass
7. ✅ No breaking changes to existing API

## File Responsibilities Summary

| File | Responsibility | Changes |
|------|---------------|---------|
| `config.py` | Configuration validation | EXTEND: Add benchmark/security config |
| `competitor.py` | Competitor management | EXTEND: Add archetype field |
| `arena.py` | Arena operations | EXTEND: Add benchmark/security execution |
| `artifacts.py` | Artifact storage | EXTEND: Support parent cache directory |
| `rpc_server.py` | JSON-RPC critique server | NEW: Unix socket server for critiques |
| `orchestrator.py` | Round orchestration | NEW: Iterative round coordination |
| `reporter.py` | Report generation | NEW: HTML/JSON report creation |

**Total:** 7 conceptual files (3 new, 4 extensions)
