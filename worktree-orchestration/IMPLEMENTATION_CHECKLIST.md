# Implementation Checklist - Worktree Orchestration Extensions

**Conservative Approach:** Minimal, stable, backward-compatible  
**Time Estimate:** 1-2 hours  
**Max Files:** 10 conceptual changes

## Files to Create/Modify

### New Files (3)

#### 1. `src/rpc_server.py`
**Responsibility:** JSON-RPC server for critique arena over unix socket  
**Key Components:**
- `CritiqueArenaServer` class
- Unix socket listener at `../.shared-cache/critique-arena.sock`
- RPC methods: `submit_critique`, `get_solutions`, `get_critiques`, `ping`
- Thread-safe artifact access
- Graceful shutdown

**Dependencies:** `jsonrpcserver` library

#### 2. `src/orchestrator.py`
**Responsibility:** Iterative round orchestration with cross-review  
**Key Components:**
- `RoundOrchestrator` class
- Round state management (setup → submission → critique → testing → completed)
- Integration with RPC server for critique phase
- Coordination of tests, benchmarks, security checks
- Timeout handling for submissions/critiques

**Dependencies:** Uses `arena.py`, `rpc_server.py`, `artifacts.py`

#### 3. `src/reporter.py`
**Responsibility:** Generate final reports in parent `.shared-cache/` directory  
**Key Components:**
- `ReportGenerator` class
- HTML report generation (round results, critiques, rankings)
- JSON report generation (machine-readable)
- Competition summary aggregation
- Output to `../.shared-cache/round_{num}_report.{html,json}`

**Dependencies:** Uses `artifacts.py` for data retrieval

### Extended Files (4)

#### 4. `src/config.py`
**Changes:**
- Add `benchmark_command: Optional[str]` to `ArenaConfig`
- Add `security_check_command: Optional[str]` to `ArenaConfig`
- Validation for command safety (no shell injection)

**Impact:** Minimal, backward-compatible (optional fields)

#### 5. `src/competitor.py`
**Changes:**
- Add `archetype: str` field to `Competitor` model
- Default: `"balanced"`
- Validation: pattern `^(conservative|aggressive|balanced|experimental)$`
- Update `register_competitor()` to accept archetype parameter

**Impact:** Minimal, backward-compatible (default value)

#### 6. `src/arena.py`
**Changes:**
- Add `execute_benchmarks(worktree)` method
- Add `execute_security_checks(worktree)` method
- Extend `_execute_tests()` to call benchmarks/security after tests
- Aggregate results in test results dictionary

**Impact:** Extends existing test execution, non-breaking

#### 7. `src/artifacts.py`
**Changes:**
- Add `parent_cache_dir: Optional[Path]` parameter to `ArtifactStore.__init__`
- Add `store_report(round_num, report_data, report_type)` method
- Store reports in `parent_cache_dir` if provided, else local cache
- Ensure parent directory exists

**Impact:** Minimal, backward-compatible (optional parameter)

### Test Files (2)

#### 8. `tests/test_rpc_server.py`
**Responsibility:** Test RPC server functionality  
**Tests:**
- RPC method calls (submit_critique, get_solutions)
- Unix socket communication
- Error handling (invalid params, missing artifacts)
- Concurrent request handling

#### 9. `tests/test_orchestrator.py`
**Responsibility:** Test orchestrator round flow  
**Tests:**
- Round state transitions
- Submission waiting logic
- Critique phase coordination
- Validation execution (tests + benchmarks + security)
- Report generation trigger

### Example Files (1)

#### 10. `examples/archetype_config.json`
**Responsibility:** Example configuration with archetypes and benchmarks  
**Contents:**
- Competitor registration with archetypes
- Benchmark and security check commands
- Full round configuration example

## Implementation Order

1. **Extend existing models** (config.py, competitor.py) - 15 min
2. **Implement RPC server** (rpc_server.py) - 30 min
3. **Extend arena** (arena.py) - 20 min
4. **Implement orchestrator** (orchestrator.py) - 30 min
5. **Implement reporter** (reporter.py) - 20 min
6. **Extend artifacts** (artifacts.py) - 10 min
7. **Write tests** (test_rpc_server.py, test_orchestrator.py) - 30 min
8. **Create examples** (archetype_config.json) - 5 min

**Total:** ~2 hours

## Key Integration Points

1. **RPC Server ↔ Artifacts:** RPC server reads/writes critiques via `ArtifactStore`
2. **Orchestrator ↔ Arena:** Orchestrator uses `Arena` for round operations
3. **Orchestrator ↔ RPC Server:** Orchestrator starts/stops RPC server for critique phase
4. **Reporter ↔ Artifacts:** Reporter reads artifacts to generate reports
5. **Arena ↔ Config:** Arena reads benchmark/security commands from config

## Dependencies to Add

```txt
jsonrpcserver>=5.0.0
```

Update `requirements.txt` accordingly.

## Directory Structure After Implementation

```
worktree-orchestration/
├── src/
│   ├── config.py              # [EXTENDED]
│   ├── competitor.py          # [EXTENDED]
│   ├── arena.py               # [EXTENDED]
│   ├── artifacts.py           # [EXTENDED]
│   ├── rpc_server.py          # [NEW]
│   ├── orchestrator.py        # [NEW]
│   └── reporter.py            # [NEW]
├── tests/
│   ├── test_rpc_server.py     # [NEW]
│   └── test_orchestrator.py   # [NEW]
└── examples/
    └── archetype_config.json  # [NEW]
```

## Validation Checklist

- [ ] All existing tests still pass
- [ ] RPC server accepts critiques over unix socket
- [ ] Benchmarks execute after tests
- [ ] Security checks execute after benchmarks
- [ ] Orchestrator runs complete round flow
- [ ] Reports generated in `../.shared-cache/`
- [ ] Archetypes stored and retrievable
- [ ] Backward compatibility maintained (default values work)

## Notes

- **Conservative approach:** All extensions are backward-compatible
- **Factory pattern:** Use factory methods for creating orchestrator instances
- **Singleton pattern:** RPC server should be singleton per process
- **Observer pattern:** Consider event-based notifications for round state changes (future)
- **Fast commands:** Use subprocess with explicit args, avoid shell=True
- **Enterprise practices:** Error handling, logging, atomic writes, validation
