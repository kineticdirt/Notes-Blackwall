# Worktree Orchestration v2.0.0 - Implementation Plan

**Status:** Proposal  
**Approach:** Conservative, incremental, self-contained  
**Date:** 2026-01-30

## Overview

A directory-based multi-agent competition system that simulates git worktrees without requiring git. Agents compete in rounds by submitting solutions and critiques in isolated directory workspaces.

## Design Principles

1. **Self-contained**: All code lives in `worktree-orchestration/` subfolder
2. **No git dependencies**: Pure directory-based isolation
3. **No git config changes**: Zero git configuration modifications
4. **Tests-first**: Test suite before implementation
5. **Minimal changes**: Only new files, no modifications to existing workspace
6. **Backward compatible**: Existing scripts remain untouched

## File Tree Structure

```
worktree-orchestration/
├── README.md                          # User-facing documentation
├── IMPLEMENTATION_PLAN.md             # This file
├── SPEC.md                            # Detailed specification
├── requirements.txt                   # Python dependencies
├── setup.py                           # Package setup (optional)
│
├── src/
│   ├── __init__.py
│   ├── cli.py                         # Main CLI entry point
│   ├── config.py                      # Configuration validation
│   ├── worktree.py                    # Directory-based worktree manager
│   ├── arena.py                       # Competition arena logic
│   ├── competitor.py                  # Competitor registration/management
│   └── artifacts.py                   # Artifact storage/retrieval
│
├── tests/
│   ├── __init__.py
│   ├── test_config.py                 # Config validation tests
│   ├── test_worktree.py               # Worktree creation/isolation tests
│   ├── test_arena.py                  # Arena round execution tests
│   ├── test_competitor.py             # Competitor registration tests
│   ├── test_artifacts.py              # Artifact storage tests
│   └── fixtures/                      # Test fixtures
│       ├── sample_config.json
│       └── sample_solution.py
│
├── .shared-cache/                     # Shared artifact storage (gitignored)
│   ├── rounds/                        # Per-round artifacts
│   │   └── round_001/
│   │       ├── solutions/
│   │       ├── critiques/
│   │       └── results.json
│   └── competitors/                   # Competitor metadata
│
└── examples/
    ├── basic_competition.json         # Example config
    └── sample_competitor.py           # Example competitor script
```

## Core Modules

### 1. `config.py` - Configuration Validation

**Purpose:** Validate competition configuration JSON

**Key Classes:**
- `ConfigValidator`: Validates JSON schema
- `CompetitionConfig`: Typed config object

**Schema Requirements:**
```json
{
  "version": "2.0.0",
  "competition": {
    "name": "string",
    "rounds": "integer > 0",
    "max_competitors": "integer > 0"
  },
  "worktree": {
    "base_path": "string (relative path)",
    "template_path": "string (optional)"
  },
  "arena": {
    "test_command": "string",
    "timeout_seconds": "integer > 0"
  }
}
```

**Validation Rules:**
- Version must be exactly "2.0.0"
- Paths must be relative (no absolute paths)
- Commands must be safe (no shell injection vectors)
- Timeouts must be reasonable (< 3600s)

### 2. `worktree.py` - Directory-Based Worktrees

**Purpose:** Create/isolate/manage directory workspaces

**Key Classes:**
- `WorktreeManager`: Creates and manages worktree directories
- `Worktree`: Represents a single worktree instance

**Methods:**
- `create_worktree(competitor_id, round_num) -> Worktree`
- `cleanup_worktree(worktree_id) -> None`
- `list_worktrees() -> List[Worktree]`
- `get_worktree_path(competitor_id, round_num) -> Path`

**Isolation Strategy:**
- Each worktree: `{base_path}/wt_{competitor_id}_r{round_num}/`
- Copy template if provided, else empty directory
- Set read-only permissions on parent to prevent escapes
- Use `os.path.join()` and `pathlib.Path` (no symlinks)

### 3. `competitor.py` - Competitor Management

**Purpose:** Register and track competitors

**Key Classes:**
- `CompetitorRegistry`: Manages competitor registration
- `Competitor`: Represents a single competitor

**Methods:**
- `register_competitor(name, script_path) -> Competitor`
- `list_competitors() -> List[Competitor]`
- `get_competitor(competitor_id) -> Competitor`
- `validate_competitor_script(path) -> bool`

**Storage:**
- Metadata in `.shared-cache/competitors/{competitor_id}.json`
- Scripts referenced by path (not copied)

### 4. `arena.py` - Competition Arena

**Purpose:** Execute competition rounds

**Key Classes:**
- `Arena`: Main competition orchestrator
- `Round`: Represents a single competition round
- `Submission`: Solution or critique submission

**Methods:**
- `start_round(round_num) -> Round`
- `submit_solution(competitor_id, worktree_path, solution_data) -> Submission`
- `submit_critique(competitor_id, target_solution_id, critique_data) -> Submission`
- `execute_tests(round_num) -> TestResults`
- `end_round(round_num) -> RoundResults`

**Round Flow:**
1. Create worktrees for all registered competitors
2. Competitors submit solutions (copy files to worktree)
3. Competitors submit critiques (reference other solutions)
4. Execute test suite on all solutions
5. Collect results and store artifacts
6. Cleanup worktrees (optional, configurable)

### 5. `artifacts.py` - Artifact Storage

**Purpose:** Store and retrieve competition artifacts

**Key Classes:**
- `ArtifactStore`: Manages artifact storage
- `Artifact`: Represents stored artifact

**Methods:**
- `store_solution(round_num, competitor_id, solution_data) -> Artifact`
- `store_critique(round_num, competitor_id, target_id, critique_data) -> Artifact`
- `store_results(round_num, results) -> None`
- `retrieve_artifact(artifact_id) -> Artifact`
- `list_artifacts(round_num) -> List[Artifact]`

**Storage Layout:**
```
.shared-cache/rounds/{round_num}/
  ├── solutions/
  │   └── {competitor_id}_{timestamp}.json
  ├── critiques/
  │   └── {competitor_id}_{target_id}_{timestamp}.json
  └── results.json
```

### 6. `cli.py` - Command-Line Interface

**Purpose:** User-facing CLI commands

**Commands:**
- `init <config.json>` - Initialize competition from config
- `worktree create <competitor_id> <round_num>` - Create worktree
- `competitor register <name> <script_path>` - Register competitor
- `arena start-round <round_num>` - Start a competition round
- `arena submit-solution <competitor_id> <round_num> <solution_path>` - Submit solution
- `arena submit-critique <competitor_id> <round_num> <target_id> <critique_path>` - Submit critique
- `arena test <round_num>` - Run tests on round solutions
- `arena end-round <round_num>` - End round and collect results
- `artifacts list <round_num>` - List artifacts for a round
- `artifacts show <artifact_id>` - Show artifact contents
- `cleanup` - Remove all worktrees (with confirmation)

## Step-by-Step CLI Workflow

### Phase 1: Setup

```bash
# 1. Navigate to workspace
cd "/Users/abhinav/Desktop/Cequence Goose"

# 2. Initialize competition from config
python -m worktree_orchestration.cli init examples/basic_competition.json

# 3. Register competitors
python -m worktree_orchestration.cli competitor register "AgentA" examples/sample_competitor.py
python -m worktree_orchestration.cli competitor register "AgentB" examples/sample_competitor.py
python -m worktree_orchestration.cli competitor register "AgentC" examples/sample_competitor.py

# 4. Verify setup
python -m worktree_orchestration.cli competitor list
```

### Phase 2: Round Execution

```bash
# 1. Start round 1
python -m worktree_orchestration.cli arena start-round 1

# 2. Create worktrees for all competitors (automatic or manual)
python -m worktree_orchestration.cli worktree create AgentA 1
python -m worktree_orchestration.cli worktree create AgentB 1
python -m worktree_orchestration.cli worktree create AgentC 1

# 3. Competitors submit solutions (via their scripts or manually)
python -m worktree_orchestration.cli arena submit-solution AgentA 1 ./solutions/agent_a_solution.py
python -m worktree_orchestration.cli arena submit-solution AgentB 1 ./solutions/agent_b_solution.py
python -m worktree_orchestration.cli arena submit-solution AgentC 1 ./solutions/agent_c_solution.py

# 4. Competitors submit critiques
python -m worktree_orchestration.cli arena submit-critique AgentA 1 AgentB ./critiques/agent_a_on_b.txt
python -m worktree_orchestration.cli arena submit-critique AgentB 1 AgentC ./critiques/agent_b_on_c.txt

# 5. Run tests on all solutions
python -m worktree_orchestration.cli arena test 1

# 6. End round and collect results
python -m worktree_orchestration.cli arena end-round 1

# 7. View results
python -m worktree_orchestration.cli artifacts list 1
python -m worktree_orchestration.cli artifacts show <artifact_id>
```

### Phase 3: Cleanup

```bash
# Remove all worktrees (with confirmation prompt)
python -m worktree_orchestration.cli cleanup
```

## Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Create directory structure
- [ ] Implement `config.py` with validation
- [ ] Write tests for config validation
- [ ] Implement `worktree.py` basic operations
- [ ] Write tests for worktree creation/isolation

### Phase 2: Core Logic (Week 2)
- [ ] Implement `competitor.py` registration
- [ ] Write tests for competitor management
- [ ] Implement `artifacts.py` storage
- [ ] Write tests for artifact storage

### Phase 3: Arena (Week 3)
- [ ] Implement `arena.py` round execution
- [ ] Write tests for arena operations
- [ ] Implement test execution with timeout
- [ ] Write integration tests

### Phase 4: CLI (Week 4)
- [ ] Implement `cli.py` with all commands
- [ ] Add error handling and user feedback
- [ ] Write CLI tests
- [ ] Create example configs and competitors

### Phase 5: Polish (Week 5)
- [ ] Documentation (README.md)
- [ ] Edge case handling
- [ ] Performance optimization
- [ ] Security audit

## Tradeoffs

### 1. Directory Isolation vs. Git Worktrees

**Chosen:** Directory-based isolation  
**Pros:**
- No git dependency
- Works in non-git repos
- Simpler implementation
- No git config changes

**Cons:**
- No automatic branch tracking
- Manual cleanup required
- Larger disk usage (full copies)
- No git history benefits

**Mitigation:** Add cleanup commands, use hardlinks if OS supports

### 2. Config Validation Strictness

**Chosen:** Strict validation with clear errors  
**Pros:**
- Prevents misconfiguration
- Early failure detection
- Better user experience

**Cons:**
- May reject valid but unusual configs
- Requires schema updates for new features

**Mitigation:** Versioned schema, allow schema extensions

### 3. Artifact Storage Format

**Chosen:** JSON files in directory structure  
**Pros:**
- Human-readable
- Easy to inspect/debug
- No database dependency
- Version control friendly

**Cons:**
- Slower for large datasets
- No query capabilities
- Manual cleanup needed

**Mitigation:** Add indexing if needed, provide cleanup tools

### 4. Test Execution Strategy

**Chosen:** Subprocess execution with timeout  
**Pros:**
- Isolated execution
- Timeout protection
- Cross-platform

**Cons:**
- Overhead per test
- Limited parallelization
- Resource limits harder to enforce

**Mitigation:** Add parallel execution option, resource monitoring

## Edge Cases & Considerations

### 1. Path Traversal Attacks
- **Risk:** Competitor scripts could escape worktree directories
- **Mitigation:** Validate all paths, use `os.path.join()`, set read-only parent dirs

### 2. Concurrent Round Execution
- **Risk:** Multiple rounds running simultaneously
- **Mitigation:** Lock file per round, check before starting

### 3. Disk Space Exhaustion
- **Risk:** Many worktrees consume disk space
- **Mitigation:** Configurable cleanup, disk space checks, warnings

### 4. Test Timeout Failures
- **Risk:** Tests hang indefinitely
- **Mitigation:** Configurable timeout, kill subprocess on timeout

### 5. Invalid Competitor Scripts
- **Risk:** Competitor scripts crash or misbehave
- **Mitigation:** Validate scripts before registration, sandbox execution

### 6. Artifact Corruption
- **Risk:** JSON files corrupted or incomplete
- **Mitigation:** Atomic writes (write to temp, then rename), validation on read

### 7. Worktree Cleanup Failures
- **Risk:** Worktrees not cleaned up, disk space issues
- **Mitigation:** Idempotent cleanup, force flag, manual cleanup command

### 8. Config Schema Evolution
- **Risk:** Breaking changes in future versions
- **Mitigation:** Versioned schema, migration tools, backward compatibility checks

## Security Considerations

1. **No shell injection**: Use subprocess with explicit args, not shell=True
2. **Path validation**: All paths validated, no absolute paths allowed
3. **Read-only isolation**: Parent directories set read-only where possible
4. **Resource limits**: Configurable timeouts and memory limits
5. **Sandboxing**: Consider chroot/jail if available (future enhancement)

## Testing Strategy

1. **Unit tests**: Each module tested independently
2. **Integration tests**: Full workflow tests
3. **Edge case tests**: Path traversal, concurrent access, failures
4. **Performance tests**: Large numbers of competitors/rounds
5. **Security tests**: Injection attempts, path escapes

## Success Criteria

1. ✅ All tests pass
2. ✅ CLI commands work end-to-end
3. ✅ No modifications to existing workspace files
4. ✅ Self-contained in `worktree-orchestration/` folder
5. ✅ Documentation complete
6. ✅ Handles edge cases gracefully
7. ✅ No git dependencies or config changes

## Next Steps

1. Review and approve this plan
2. Create initial directory structure
3. Implement Phase 1 (Foundation)
4. Iterate based on feedback
