# Tradeoffs and Edge Cases

## Design Tradeoffs

### 1. Directory Isolation vs. Git Worktrees

**Decision:** Directory-based isolation  
**Rationale:** No git dependency, works in non-git repos, simpler implementation

**Pros:**
- ✅ No git dependency
- ✅ Works in non-git repositories
- ✅ Simpler implementation
- ✅ No git config changes required
- ✅ Cross-platform compatibility

**Cons:**
- ❌ No automatic branch tracking
- ❌ Manual cleanup required
- ❌ Larger disk usage (full directory copies)
- ❌ No git history benefits
- ❌ No easy way to see diffs between rounds

**Mitigation Strategies:**
- Add cleanup commands (`cleanup` CLI command)
- Use hardlinks if OS supports (future enhancement)
- Provide disk usage monitoring
- Document manual diff tools

### 2. Config Validation Strictness

**Decision:** Strict validation with clear error messages  
**Rationale:** Fail fast, prevent misconfiguration

**Pros:**
- ✅ Prevents misconfiguration early
- ✅ Clear error messages guide users
- ✅ Type safety with Pydantic
- ✅ Better user experience

**Cons:**
- ❌ May reject valid but unusual configs
- ❌ Requires schema updates for new features
- ❌ Less flexible for advanced users

**Mitigation Strategies:**
- Versioned schema (v2.0.0)
- Allow schema extensions via `additionalProperties`
- Provide migration tools for schema changes
- Document all validation rules

### 3. Artifact Storage Format

**Decision:** JSON files in directory structure  
**Rationale:** Human-readable, easy to inspect, no database dependency

**Pros:**
- ✅ Human-readable format
- ✅ Easy to inspect/debug
- ✅ No database dependency
- ✅ Version control friendly
- ✅ Simple backup/restore

**Cons:**
- ❌ Slower for large datasets
- ❌ No query capabilities
- ❌ Manual cleanup needed
- ❌ No concurrent write protection
- ❌ Limited scalability

**Mitigation Strategies:**
- Add indexing if needed (future enhancement)
- Provide cleanup tools
- Use atomic writes (temp file + rename)
- Consider database backend as optional feature

### 4. Test Execution Strategy

**Decision:** Subprocess execution with timeout  
**Rationale:** Isolated execution, cross-platform, timeout protection

**Pros:**
- ✅ Isolated execution per competitor
- ✅ Timeout protection
- ✅ Cross-platform (subprocess)
- ✅ Captures stdout/stderr
- ✅ Simple implementation

**Cons:**
- ❌ Overhead per test execution
- ❌ Limited parallelization (by default)
- ❌ Resource limits harder to enforce
- ❌ No fine-grained resource monitoring

**Mitigation Strategies:**
- Add parallel execution option (`parallel_tests: true`)
- Monitor subprocess resource usage (future)
- Provide resource limit configuration
- Add test result caching

## Edge Cases

### 1. Path Traversal Attacks

**Risk:** Competitor scripts could escape worktree directories  
**Scenario:** Script uses `../../` to access parent directories

**Mitigation:**
- ✅ Validate all paths before use
- ✅ Use `os.path.join()` and `pathlib.Path` (no manual concatenation)
- ✅ Set read-only permissions on parent directories where possible
- ✅ Reject absolute paths in config
- ✅ Validate competitor script paths

**Remaining Risk:** Medium - OS-level sandboxing would be better but adds complexity

### 2. Concurrent Round Execution

**Risk:** Multiple rounds running simultaneously could conflict  
**Scenario:** User starts round 2 while round 1 is still active

**Mitigation:**
- ✅ Lock file per round (`.lock` file in round directory)
- ✅ Check round state before starting
- ✅ Clear error messages if round already active
- ✅ State tracking in `Arena.round_states`

**Remaining Risk:** Low - handled by state checks

### 3. Disk Space Exhaustion

**Risk:** Many worktrees consume disk space  
**Scenario:** 50 competitors × 100 rounds = 5000 worktrees

**Mitigation:**
- ✅ Configurable cleanup (`cleanup_after_round`)
- ✅ Disk space checks before worktree creation (future)
- ✅ Warnings when disk space is low
- ✅ Manual cleanup command

**Remaining Risk:** Medium - depends on template size and disk capacity

### 4. Test Timeout Failures

**Risk:** Tests hang indefinitely  
**Scenario:** Competitor's test has infinite loop

**Mitigation:**
- ✅ Configurable timeout (`timeout_seconds`)
- ✅ `subprocess.run()` with `timeout` parameter
- ✅ Kill subprocess on timeout
- ✅ Clear error messages

**Remaining Risk:** Low - timeout enforced at OS level

### 5. Invalid Competitor Scripts

**Risk:** Competitor scripts crash or misbehave  
**Scenario:** Script has syntax errors or crashes immediately

**Mitigation:**
- ✅ Validate scripts exist before registration
- ✅ Basic syntax check (future: try importing/executing)
- ✅ Sandbox execution (tests run in isolated worktree)
- ✅ Capture and report errors

**Remaining Risk:** Medium - script validation is basic

### 6. Artifact Corruption

**Risk:** JSON files corrupted or incomplete  
**Scenario:** Process killed during write, disk full, etc.

**Mitigation:**
- ✅ Atomic writes (write to `.tmp`, then rename)
- ✅ JSON validation on read
- ✅ Error handling with clear messages
- ✅ Backup artifacts before overwriting (future)

**Remaining Risk:** Low - atomic writes prevent most issues

### 7. Worktree Cleanup Failures

**Risk:** Worktrees not cleaned up, disk space issues  
**Scenario:** Permission errors, files in use, etc.

**Mitigation:**
- ✅ Idempotent cleanup (safe to run multiple times)
- ✅ Force flag (`--force`) to skip confirmation
- ✅ Manual cleanup command
- ✅ Clear error messages

**Remaining Risk:** Low - cleanup is best-effort, manual fallback available

### 8. Config Schema Evolution

**Risk:** Breaking changes in future versions  
**Scenario:** v2.1.0 adds required field, breaks v2.0.0 configs

**Mitigation:**
- ✅ Versioned schema (`version: "2.0.0"`)
- ✅ Strict version matching
- ✅ Migration tools (future)
- ✅ Backward compatibility checks
- ✅ Clear upgrade path documentation

**Remaining Risk:** Low - version pinning prevents accidental breakage

### 9. Large Template Directories

**Risk:** Copying large templates is slow  
**Scenario:** Template is 1GB, copying to 50 worktrees takes hours

**Mitigation:**
- ✅ Optional templates (not required)
- ✅ Use hardlinks if OS supports (future)
- ✅ Progress indicators (future)
- ✅ Parallel worktree creation (future)

**Remaining Risk:** Medium - depends on template size

### 10. Invalid Test Commands

**Risk:** Test command fails or is malicious  
**Scenario:** User configures `test_command: "rm -rf /"`

**Mitigation:**
- ✅ No shell execution (`shell=False` in subprocess)
- ✅ Explicit command + args parsing
- ✅ Run in isolated worktree directory
- ✅ Timeout protection
- ✅ Document security considerations

**Remaining Risk:** Low - subprocess isolation prevents most issues

## Performance Considerations

### Worktree Creation
- **Bottleneck:** Template copying for large templates
- **Impact:** O(n) where n = template size
- **Optimization:** Use hardlinks (future), parallel creation (future)

### Test Execution
- **Bottleneck:** Sequential test execution
- **Impact:** O(m) where m = number of competitors
- **Optimization:** Parallel execution option (`parallel_tests: true`)

### Artifact Storage
- **Bottleneck:** JSON file I/O
- **Impact:** Negligible for < 1000 artifacts
- **Optimization:** Database backend (optional, future)

## Security Considerations

1. **No shell injection**: Use `subprocess.run()` with explicit args, `shell=False`
2. **Path validation**: All paths validated, no absolute paths, no traversal
3. **Read-only isolation**: Parent directories set read-only where possible
4. **Resource limits**: Configurable timeouts, disk space checks (future)
5. **Sandboxing**: Worktrees isolated, tests run in worktree directory

## Limitations

1. **No Git Integration**: Cannot leverage git features (branches, history, etc.)
2. **Disk Usage**: Full directory copies, no deduplication (hardlinks future)
3. **Concurrency**: Limited concurrent round support (lock-based)
4. **Scalability**: Designed for < 50 competitors, < 100 rounds
5. **Platform**: Unix-like systems (Linux, macOS), Windows support limited

## Future Enhancements

1. **Hardlink Support**: Reduce disk usage for template copying
2. **Parallel Test Execution**: With resource monitoring
3. **Database Backend**: Optional database for artifact storage
4. **Web UI**: Competition monitoring dashboard
5. **Git Integration**: Optional git worktree support (opt-in)
6. **Resource Monitoring**: CPU/memory limits per test
7. **Artifact Indexing**: Fast search across artifacts
8. **Migration Tools**: Config schema migration utilities
