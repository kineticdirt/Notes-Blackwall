# Worktree Orchestration v2.0.0

A directory-based multi-agent competition system that enables agents to compete in isolated workspaces without requiring git worktrees or git configuration changes.

## Features

- ✅ **Directory-based isolation**: No git dependencies
- ✅ **Multi-agent competition**: Support for multiple competitors and rounds
- ✅ **Solution & critique submission**: Agents can submit solutions and critique others
- ✅ **Test execution**: Automated test execution with timeout protection
- ✅ **Artifact storage**: Organized storage of solutions, critiques, and results
- ✅ **Self-contained**: All code in `worktree-orchestration/` folder
- ✅ **No git config changes**: Zero modifications to git configuration

## Quick Start

### 1. Install Dependencies

```bash
cd worktree-orchestration
pip install -r requirements.txt
```

### 2. Initialize Competition

```bash
python -m src.cli init examples/basic_competition.json
```

### 3. Register Competitors

```bash
python -m src.cli competitor register "AgentA" examples/sample_competitor.py
python -m src.cli competitor register "AgentB" examples/sample_competitor.py
```

### 4. Run a Competition Round

```bash
# Start round
python -m src.cli arena start-round 1

# Submit solutions
python -m src.cli arena submit-solution AgentA 1 ./solutions/agent_a.py
python -m src.cli arena submit-solution AgentB 1 ./solutions/agent_b.py

# Run tests
python -m src.cli arena test 1

# End round
python -m src.cli arena end-round 1
```

## Documentation

- [Implementation Plan](IMPLEMENTATION_PLAN.md) - Detailed implementation plan
- [Specification](SPEC.md) - Complete specification and API reference
- [Examples](examples/) - Example configurations and competitor scripts

## Architecture

See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for detailed architecture and design decisions.

## Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test suite
python -m pytest tests/test_config.py
```

## License

Internal use only.
