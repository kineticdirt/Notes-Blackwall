# Files Summary - Worktree Orchestration Extensions

## Concrete Files to Create/Modify

### New Files (3)

1. **`src/rpc_server.py`**
   - JSON-RPC server for critique arena
   - Unix socket: `../.shared-cache/critique-arena.sock`
   - Methods: submit_critique, get_solutions, get_critiques, ping

2. **`src/orchestrator.py`**
   - Iterative round orchestration
   - Coordinates: setup → submission → critique → testing → report
   - Integrates RPC server for critique phase

3. **`src/reporter.py`**
   - Final report generation (HTML + JSON)
   - Outputs to `../.shared-cache/round_{num}_report.{html,json}`
   - Competition summary aggregation

### Extended Files (4)

4. **`src/config.py`**
   - Add `benchmark_command` and `security_check_command` to ArenaConfig
   - Optional fields, backward-compatible

5. **`src/competitor.py`**
   - Add `archetype` field (conservative/aggressive/balanced/experimental)
   - Default: "balanced", backward-compatible

6. **`src/arena.py`**
   - Add `execute_benchmarks()` and `execute_security_checks()` methods
   - Extend test execution to include benchmarks/security

7. **`src/artifacts.py`**
   - Add `parent_cache_dir` parameter
   - Add `store_report()` method for parent directory storage

### Test Files (2)

8. **`tests/test_rpc_server.py`**
   - RPC server unit tests

9. **`tests/test_orchestrator.py`**
   - Orchestrator integration tests

### Example Files (1)

10. **`examples/archetype_config.json`**
    - Example configuration with archetypes and benchmarks

---

**Total: 10 files** (3 new, 4 extended, 2 tests, 1 example)

**Implementation Time: 1-2 hours**

**Architecture:** Conservative, backward-compatible, factory/singleton patterns
