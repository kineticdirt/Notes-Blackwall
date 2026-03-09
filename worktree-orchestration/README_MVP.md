# Competitive AI Orchestration - MVP Implementation

## Overview

This MVP implements a competitive AI orchestration system with:
- ✅ **Worktrees** - Isolated directories per competitor/round
- ✅ **Rounds** - Multi-round competition structure
- ✅ **Tests** - Test execution with timeout handling
- 🔲 **Scoring** - Multi-criteria weighted scoring (structure created, needs integration)
- 🔲 **Elimination** - Bottom N elimination per round (structure created, needs integration)
- 🔲 **Convergence** - Score stability detection (structure created, needs integration)
- 🔲 **Security Checks** - Semgrep/Snyk adapters with graceful fallback (structure created, needs integration)
- ✅ **Artifacts** - Solution/critique storage

## Quick Start

### Prerequisites
```bash
# Core dependencies
pip install -r requirements.txt

# Optional: Security tools (will fallback gracefully if missing)
pip install semgrep
# OR
npm install -g snyk && snyk auth
```

### Run Competition
```bash
# Initialize
python -m src.cli init examples/basic_competition.json

# Register competitors
python -m src.cli competitor register "AgentA" examples/sample_competitor.py

# Run competition (after integration)
python -m src.cli arena run-all
```

## Folder Structure

```
worktree-orchestration/
├── MVP_PLAN.md                    # Complete implementation plan
├── IMPLEMENTATION_QUICK_REF.md    # Quick reference guide
├── MVP_STATUS.md                  # Current status and integration checklist
├── README_MVP.md                  # This file
│
├── src/
│   ├── core/                      # ✅ Existing core modules
│   │   ├── config.py
│   │   ├── worktree.py
│   │   ├── competitor.py
│   │   ├── arena.py               # Needs integration
│   │   └── artifacts.py
│   │
│   ├── scoring/                   # ⭐ NEW - Scoring system
│   │   ├── scorer.py              # Abstract base
│   │   ├── weighted_scorer.py     # Multi-criteria scorer
│   │   ├── repository.py          # Score storage
│   │   └── criteria/
│   │       ├── test_score.py      # Test pass/fail → score
│   │       ├── performance_score.py  # Time → score
│   │       ├── security_score.py  # Security scan → score
│   │       └── code_quality_score.py  # Quality metrics → score
│   │
│   ├── elimination/               # ⭐ NEW - Elimination logic
│   │   ├── eliminator.py          # Abstract base
│   │   └── bottom_n_eliminator.py # Bottom N strategy
│   │
│   ├── convergence/               # ⭐ NEW - Convergence detection
│   │   ├── detector.py           # Abstract base
│   │   └── score_stability.py     # Variance-based detection
│   │
│   └── adapters/                  # ⭐ NEW - External tool adapters
│       ├── base.py                # Abstract adapter interface
│       └── security/
│           ├── semgrep_adapter.py # Semgrep integration
│           ├── snyk_adapter.py    # Snyk integration
│           ├── fallback_adapter.py # Neutral fallback
│           └── factory.py         # Adapter factory
│
└── tests/                         # Test suite (to be created)
```

## What's Implemented vs What's Stubbed

### ✅ Fully Implemented (Structure Created)
- Scoring system architecture
- Elimination logic architecture
- Convergence detection architecture
- Security adapter architecture with graceful fallback

### 🔲 Needs Integration
- Wire scoring into `arena.py` test execution
- Wire elimination into `arena.py` round completion
- Wire convergence check into `arena.py` round loop
- Update `config.py` with new configuration sections
- Update `cli.py` with new commands

### 📝 Stubbed (Future Enhancement)
- Advanced memory profiling (returns mock data)
- Parallel test execution (sequential for MVP)
- Web UI monitoring (CLI only for MVP)
- Database backend (JSON files for MVP)

## Design Patterns Used

### 1. Repository Pattern
- `ScoreRepository` - Abstract score storage
- `CompetitorRegistry` - Competitor storage (existing)
- `ArtifactStore` - Artifact storage (existing)

### 2. Adapter Pattern
- `SecurityAdapter` - Abstract security scanning
- `SemgrepAdapter` / `SnykAdapter` - Concrete implementations
- `FallbackSecurityAdapter` - Graceful degradation

### 3. Strategy Pattern
- `Eliminator` - Pluggable elimination strategies
- `ConvergenceDetector` - Pluggable convergence detection
- `Scorer` - Pluggable scoring criteria

### 4. Factory Pattern
- `SecurityAdapterFactory` - Creates adapters with fallback

## Key Features

### Scoring System
- **Multi-criteria**: Test, performance, security, code quality
- **Weighted**: Configurable weights per criterion
- **Extensible**: Add new criteria via `Scorer` interface
- **Normalized**: All scores in 0-100 range

### Elimination Logic
- **Bottom N**: Eliminate lowest-scoring competitors
- **Configurable**: Per-round elimination count
- **Safe**: Respects minimum competitor threshold

### Convergence Detection
- **Score Stability**: Variance-based detection
- **Configurable**: Threshold and window size
- **Extensible**: Add new detection methods

### Security Adapters
- **Graceful Fallback**: Works without security tools
- **Multiple Tools**: Tries Semgrep → Snyk → Fallback
- **Cached**: Results cached per worktree
- **Non-blocking**: Missing tools don't stop competition

## Configuration Example

```json
{
  "version": "2.0.0",
  "competition": {
    "name": "AI Competition",
    "rounds": 10,
    "max_competitors": 20,
    "elimination": {
      "strategy": "bottom_n",
      "eliminate_per_round": 2,
      "min_competitors": 3
    },
    "convergence": {
      "enabled": true,
      "method": "score_stability",
      "threshold": 0.05,
      "window_size": 3
    }
  },
  "scoring": {
    "weights": {
      "test_score": 0.4,
      "performance_score": 0.3,
      "security_score": 0.2,
      "code_quality_score": 0.1
    }
  },
  "security": {
    "adapters": ["semgrep", "snyk"],
    "fallback_on_missing": true
  },
  "worktree": {
    "base_path": ".worktrees",
    "cleanup_after_round": false
  },
  "arena": {
    "test_command": "python -m pytest tests/",
    "timeout_seconds": 300
  }
}
```

## Integration Steps

See `MVP_STATUS.md` for detailed integration checklist.

**Quick Integration:**
1. Update `config.py` with new config classes
2. Update `arena.py` to initialize new components
3. Wire scoring into test execution
4. Wire elimination into round completion
5. Wire convergence check into round loop
6. Add tests

## Testing Strategy

### Unit Tests
- Each scorer criterion tested independently
- Adapters tested with/without tools available
- Elimination logic tested with various score distributions
- Convergence detection tested with different score patterns

### Integration Tests
- Full round: test → score → eliminate → check convergence
- Multiple rounds: verify elimination persists
- Convergence: verify competition stops when stable

## Performance Considerations

1. **Score Caching**: Scores stored in repository, avoid recalculation
2. **Security Scan Caching**: Results cached per worktree hash
3. **Lazy Loading**: Competitor data loaded only when needed
4. **Batch Operations**: Score/eliminate all competitors at once

## Error Handling

- **Adapter Failures**: Log warning, use fallback, continue
- **Scoring Failures**: Use default score (0), log error
- **Elimination Edge Cases**: Handle ties, minimum competitors
- **Convergence Edge Cases**: Handle insufficient rounds

## Maintainability

- **Single Responsibility**: Each module has one clear purpose
- **Open/Closed**: Extend via adapters/strategies, don't modify core
- **Dependency Inversion**: Depend on abstractions, not concretions
- **Interface Segregation**: Small, focused interfaces
- **DRY**: Reuse adapters, repositories, utilities

## Timeline

- **Days 1-3**: Scoring system ✅ (structure created)
- **Days 4-5**: Elimination & convergence ✅ (structure created)
- **Days 6-7**: Security adapters ✅ (structure created)
- **Day 8**: Integration & testing 🔲 (pending)

## Success Criteria

✅ **MVP Structure Complete When:**
1. All modules created with proper interfaces
2. Adapters implement graceful fallback
3. Scoring system is extensible
4. Code follows MVC/repository/adapter patterns

🔲 **MVP Integration Complete When:**
1. Scoring integrated into arena
2. Elimination integrated into arena
3. Convergence integrated into arena
4. All tests pass
5. Can run end-to-end competition

## Next Steps

1. Review `MVP_PLAN.md` for detailed implementation plan
2. Review `MVP_STATUS.md` for integration checklist
3. Review `IMPLEMENTATION_QUICK_REF.md` for quick reference
4. Integrate components into `arena.py`
5. Add tests
6. Update CLI commands

## Support

- **Architecture Questions**: See `MVP_PLAN.md`
- **Integration Help**: See `MVP_STATUS.md`
- **Quick Reference**: See `IMPLEMENTATION_QUICK_REF.md`
- **Original Spec**: See `SPEC.md`
