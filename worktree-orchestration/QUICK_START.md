# Quick Start Guide

## Overview

This is a **conservative, incremental implementation plan** for worktree-orchestration v2.0.0. The system is **self-contained** in the `worktree-orchestration/` folder and requires **no git dependencies** or **git config changes**.

## File Structure

```
worktree-orchestration/
├── README.md                    # User documentation
├── IMPLEMENTATION_PLAN.md       # Detailed implementation plan
├── SPEC.md                      # Complete specification
├── TRADEOFFS.md                 # Tradeoffs and edge cases
├── QUICK_START.md               # This file
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
│
├── src/                         # Source code
│   ├── __init__.py
│   ├── cli.py                   # CLI entry point
│   ├── config.py                # Config validation
│   ├── worktree.py              # Worktree management
│   ├── competitor.py            # Competitor registration
│   ├── arena.py                 # Arena orchestration
│   └── artifacts.py             # Artifact storage
│
├── tests/                       # Test suite
│   ├── test_config.py
│   ├── test_worktree.py
│   └── fixtures/
│
├── examples/                    # Examples
│   ├── basic_competition.json
│   ├── sample_competitor.py
│   └── template/
│
└── .shared-cache/               # Generated (gitignored)
    ├── rounds/
    └── competitors/
```

## Key Modules

### 1. `config.py` - Configuration Validation
- Validates JSON configuration files
- Ensures version is exactly "2.0.0"
- Validates paths are relative (no absolute paths)
- Uses Pydantic for type safety

### 2. `worktree.py` - Directory-Based Worktrees
- Creates isolated directories: `wt_{competitor_id}_r{round_num}/`
- Copies templates if provided
- Manages worktree lifecycle (create, list, cleanup)

### 3. `competitor.py` - Competitor Management
- Registers competitors with unique IDs
- Stores competitor metadata in `.shared-cache/competitors/`
- Validates competitor scripts exist

### 4. `arena.py` - Competition Arena
- Orchestrates competition rounds
- Manages round states (pending, active, testing, completed)
- Executes tests with timeout protection
- Collects results

### 5. `artifacts.py` - Artifact Storage
- Stores solutions and critiques as JSON
- Organizes artifacts by round
- Provides artifact retrieval

### 6. `cli.py` - Command-Line Interface
- Click-based CLI
- All commands documented
- Error handling and user feedback

## Step-by-Step Workflow

### 1. Setup

```bash
# Install dependencies
cd worktree-orchestration
pip install -r requirements.txt

# Initialize competition
python -m src.cli init examples/basic_competition.json
```

### 2. Register Competitors

```bash
python -m src.cli competitor register "AgentA" examples/sample_competitor.py
python -m src.cli competitor register "AgentB" examples/sample_competitor.py
python -m src.cli competitor list
```

### 3. Run Competition Round

```bash
# Start round
python -m src.cli arena start-round 1 --config examples/basic_competition.json

# Submit solutions
python -m src.cli arena submit-solution AgentA 1 ./solutions/agent_a.py \
  --config examples/basic_competition.json
python -m src.cli arena submit-solution AgentB 1 ./solutions/agent_b.py \
  --config examples/basic_competition.json

# Run tests
python -m src.cli arena test 1 --config examples/basic_competition.json

# End round
python -m src.cli arena end-round 1 --config examples/basic_competition.json
```

### 4. View Results

```bash
python -m src.cli artifacts list 1
```

### 5. Cleanup

```bash
python -m src.cli cleanup --config examples/basic_competition.json
```

## Configuration Example

```json
{
  "version": "2.0.0",
  "competition": {
    "name": "Basic Python Challenge",
    "rounds": 3,
    "max_competitors": 5
  },
  "worktree": {
    "base_path": "worktrees",
    "template_path": "examples/template",
    "cleanup_after_round": false
  },
  "arena": {
    "test_command": "python -m pytest tests/ -v",
    "timeout_seconds": 300,
    "parallel_tests": false
  }
}
```

## Key Design Decisions

1. **Self-contained**: All code in `worktree-orchestration/` folder
2. **No git dependencies**: Pure directory-based isolation
3. **No git config changes**: Zero modifications to git
4. **Tests-first**: Test suite included
5. **Minimal changes**: Only new files, no modifications to existing workspace
6. **Conservative**: Strict validation, clear error messages

## Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_config.py -v
```

## Tradeoffs

See [TRADEOFFS.md](TRADEOFFS.md) for detailed tradeoff analysis including:
- Directory isolation vs. git worktrees
- Config validation strictness
- Artifact storage format
- Test execution strategy
- Edge cases and mitigations

## Edge Cases Handled

1. ✅ Path traversal attacks (path validation)
2. ✅ Concurrent round execution (state checks)
3. ✅ Disk space exhaustion (cleanup commands)
4. ✅ Test timeout failures (subprocess timeout)
5. ✅ Invalid competitor scripts (validation)
6. ✅ Artifact corruption (atomic writes)
7. ✅ Worktree cleanup failures (idempotent cleanup)
8. ✅ Config schema evolution (versioned schema)

## Next Steps

1. Review implementation plan
2. Run tests to verify setup
3. Try example workflow
4. Customize for your use case

## Support

- **Specification**: See [SPEC.md](SPEC.md)
- **Implementation Plan**: See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)
- **Tradeoffs**: See [TRADEOFFS.md](TRADEOFFS.md)
