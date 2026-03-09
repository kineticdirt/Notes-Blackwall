# MVP Implementation Plan - Competitive AI Orchestration

**Archetype:** PRAGMATIST  
**Approach:** Balanced, minimal time budget, medium complexity threshold  
**Patterns:** MVC/Repository/Adapter  
**Date:** 2026-01-30

## Executive Summary

This MVP plan delivers a competitive AI orchestration system that runs locally with minimal infrastructure. The design prioritizes:
- **Fast delivery**: Stub non-critical paths, implement core flows fully
- **Easy setup**: Single command install, no heavy dependencies
- **Maintainability**: Clear separation of concerns, adapter pattern for optional tools
- **Graceful degradation**: Optional security tools (semgrep/snyk) fail gracefully

## Core Requirements

### Must Have (MVP)
1. ✅ Worktree management (already implemented)
2. ✅ Round orchestration (already implemented)
3. ✅ Test execution (already implemented)
4. 🔲 **Scoring system** - Multi-criteria scoring with weights
5. 🔲 **Elimination logic** - Bottom N elimination per round
6. 🔲 **Convergence detection** - Stop when scores stabilize
7. 🔲 **Security adapters** - Semgrep/Snyk with graceful fallback
8. 🔲 **Benchmark execution** - Performance metrics collection

### Nice to Have (Stub for MVP)
- Advanced diversity metrics
- Real-time monitoring UI
- Database backend
- Parallel test execution optimization
- Git integration

## Proposed Folder Structure

```
worktree-orchestration/
├── README.md                          # Quick start guide
├── MVP_PLAN.md                        # This file
├── requirements.txt                   # Python dependencies
├── setup.py                           # Package setup
│
├── src/
│   ├── __init__.py
│   ├── cli.py                         # CLI entry point (Click)
│   │
│   ├── core/                          # Core domain logic
│   │   ├── __init__.py
│   │   ├── config.py                  # ✅ Already implemented
│   │   ├── worktree.py                # ✅ Already implemented
│   │   ├── competitor.py              # ✅ Already implemented
│   │   ├── arena.py                   # ✅ Already implemented (needs scoring)
│   │   └── artifacts.py               # ✅ Already implemented
│   │
│   ├── scoring/                       # NEW: Scoring system
│   │   ├── __init__.py
│   │   ├── scorer.py                  # Main scoring interface
│   │   ├── weighted_scorer.py         # Weighted multi-criteria scorer
│   │   ├── criteria/                  # Scoring criteria
│   │   │   ├── __init__.py
│   │   │   ├── test_score.py          # Test pass/fail scoring
│   │   │   ├── performance_score.py   # Performance metrics
│   │   │   ├── security_score.py      # Security scan results
│   │   │   └── code_quality_score.py  # Code quality metrics
│   │   └── repository.py              # Score storage/retrieval
│   │
│   ├── elimination/                   # NEW: Elimination logic
│   │   ├── __init__.py
│   │   ├── eliminator.py              # Elimination strategy interface
│   │   ├── bottom_n_eliminator.py     # Eliminate bottom N competitors
│   │   └── threshold_eliminator.py    # Eliminate below threshold
│   │
│   ├── convergence/                   # NEW: Convergence detection
│   │   ├── __init__.py
│   │   ├── detector.py                # Convergence detection interface
│   │   ├── score_stability.py         # Score variance-based detection
│   │   └── ranking_stability.py       # Ranking change detection
│   │
│   ├── adapters/                      # NEW: External tool adapters
│   │   ├── __init__.py
│   │   ├── base.py                    # Base adapter interface
│   │   ├── security/                  # Security tool adapters
│   │   │   ├── __init__.py
│   │   │   ├── semgrep_adapter.py     # Semgrep integration
│   │   │   ├── snyk_adapter.py        # Snyk integration
│   │   │   └── fallback_adapter.py    # Fallback when tools unavailable
│   │   └── benchmark/                 # Benchmark adapters
│   │       ├── __init__.py
│   │       ├── time_adapter.py        # Execution time metrics
│   │       └── memory_adapter.py      # Memory usage metrics (stub)
│   │
│   └── utils/                         # Utilities
│       ├── __init__.py
│       └── logger.py                  # Logging setup
│
├── tests/
│   ├── __init__.py
│   ├── test_scoring.py                # Scoring tests
│   ├── test_elimination.py            # Elimination tests
│   ├── test_convergence.py            # Convergence tests
│   ├── test_adapters.py               # Adapter tests
│   └── fixtures/
│       └── sample_results.json
│
└── examples/
    ├── basic_competition.json         # Example config
    └── sample_competitor.py           # Example competitor
```

## Implementation Strategy: Stub vs Full

### Fully Implement (Core MVP)

#### 1. Scoring System (`src/scoring/`)
**Priority:** HIGH  
**Complexity:** MEDIUM  
**Time:** 2-3 days

**Components:**
- `scorer.py`: Abstract base class for scoring
- `weighted_scorer.py`: Multi-criteria weighted scoring
- `criteria/test_score.py`: Test pass/fail → score (0-100)
- `criteria/performance_score.py`: Execution time → score (normalized)
- `criteria/security_score.py`: Security scan results → score (via adapter)
- `criteria/code_quality_score.py`: Basic metrics (lines, complexity) → score
- `repository.py`: Store/retrieve scores per round/competitor

**Implementation Notes:**
- Use repository pattern for score storage
- Configurable weights per criteria
- Normalize all scores to 0-100 range
- Store scores in `.shared-cache/scores/round_{n}/`

#### 2. Elimination Logic (`src/elimination/`)
**Priority:** HIGH  
**Complexity:** LOW  
**Time:** 1 day

**Components:**
- `eliminator.py`: Abstract base class
- `bottom_n_eliminator.py`: Eliminate bottom N competitors per round
- Integration with `arena.py` to remove eliminated competitors

**Implementation Notes:**
- Simple strategy: eliminate bottom 20% each round
- Store elimination status in competitor metadata
- Skip eliminated competitors in subsequent rounds

#### 3. Convergence Detection (`src/convergence/`)
**Priority:** MEDIUM  
**Complexity:** LOW  
**Time:** 1 day

**Components:**
- `detector.py`: Abstract base class
- `score_stability.py`: Check if score variance < threshold over last N rounds
- `ranking_stability.py`: Check if top N rankings unchanged over last M rounds

**Implementation Notes:**
- Simple variance-based detection
- Configurable threshold and window size
- Return boolean: converged or not

#### 4. Security Adapters (`src/adapters/security/`)
**Priority:** MEDIUM  
**Complexity:** MEDIUM  
**Time:** 2 days

**Components:**
- `base.py`: Base adapter with `scan(worktree_path) -> SecurityResult`
- `semgrep_adapter.py`: Wrapper around semgrep CLI
- `snyk_adapter.py`: Wrapper around snyk CLI (stub if no API key)
- `fallback_adapter.py`: Returns neutral score when tools unavailable

**Implementation Notes:**
- Use adapter pattern: try semgrep → try snyk → fallback
- Check tool availability at startup
- Graceful degradation: missing tools = neutral security score
- Cache scan results per worktree

### Stub Implementation (Future Enhancement)

#### 1. Advanced Benchmarking (`src/adapters/benchmark/memory_adapter.py`)
**Stub:** Return mock memory usage data  
**Reason:** Memory profiling requires platform-specific tools, adds complexity

#### 2. Diversity Metrics (`src/diversity/`)
**Stub:** Basic similarity check (already exists, keep as-is)  
**Reason:** Advanced diversity requires embeddings/clustering, out of scope for MVP

#### 3. Parallel Test Execution
**Stub:** Sequential execution (already implemented)  
**Reason:** Parallel adds complexity, sequential is fine for MVP

#### 4. Real-time Monitoring
**Stub:** CLI output only  
**Reason:** Web UI requires additional infrastructure

## Detailed Implementation Plan

### Phase 1: Scoring System (Days 1-3)

**Day 1: Core Scoring Infrastructure**
```python
# src/scoring/scorer.py
class Scorer(ABC):
    @abstractmethod
    def score(self, competitor_id: str, round_num: int, test_results: dict) -> float:
        """Calculate score 0-100"""
        pass

# src/scoring/weighted_scorer.py
class WeightedScorer(Scorer):
    def __init__(self, criteria: List[Scorer], weights: List[float]):
        self.criteria = criteria
        self.weights = weights
    
    def score(self, competitor_id, round_num, test_results):
        scores = [c.score(competitor_id, round_num, test_results) for c in self.criteria]
        return sum(s * w for s, w in zip(scores, self.weights))
```

**Day 2: Scoring Criteria**
- Test score: `100 if passed else 0`
- Performance score: Normalize execution time (faster = higher)
- Security score: Via adapter (count vulnerabilities)
- Code quality: Basic metrics (lines, complexity)

**Day 3: Score Repository**
- Store scores in JSON files
- Retrieve historical scores for convergence detection

### Phase 2: Elimination & Convergence (Days 4-5)

**Day 4: Elimination**
```python
# src/elimination/bottom_n_eliminator.py
class BottomNEliminator:
    def eliminate(self, scores: Dict[str, float], n: int) -> List[str]:
        sorted_competitors = sorted(scores.items(), key=lambda x: x[1])
        return [c[0] for c in sorted_competitors[:n]]
```

**Day 5: Convergence**
```python
# src/convergence/score_stability.py
class ScoreStabilityDetector:
    def is_converged(self, round_scores: List[Dict[str, float]], threshold: float = 0.05) -> bool:
        if len(round_scores) < 3:
            return False
        variances = [np.var(list(scores.values())) for scores in round_scores[-3:]]
        return max(variances) < threshold
```

### Phase 3: Security Adapters (Days 6-7)

**Day 6: Adapter Infrastructure**
```python
# src/adapters/base.py
class SecurityAdapter(ABC):
    @abstractmethod
    def scan(self, worktree_path: Path) -> SecurityResult:
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass

# src/adapters/security/fallback_adapter.py
class FallbackSecurityAdapter(SecurityAdapter):
    def scan(self, worktree_path: Path) -> SecurityResult:
        return SecurityResult(vulnerabilities=[], score=50)  # Neutral
```

**Day 7: Semgrep/Snyk Integration**
- Check if `semgrep` CLI available
- Check if `snyk` CLI available + API key configured
- Try semgrep → try snyk → fallback
- Parse output, extract vulnerability count

### Phase 4: Integration & Testing (Day 8)

**Integration Points:**
1. Update `arena.py` to call scoring after tests
2. Update `arena.py` to call elimination after scoring
3. Update `arena.py` to check convergence before next round
4. Add security scanning to test execution flow

**Testing:**
- Unit tests for each component
- Integration test: full round with scoring/elimination/convergence
- Adapter tests: verify graceful fallback

## Configuration Schema Updates

```json
{
  "version": "2.0.0",
  "competition": {
    "name": "string",
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
  "worktree": { ... },
  "arena": { ... }
}
```

## Maintainability Patterns

### 1. Repository Pattern
- `ScoreRepository`: Abstract score storage
- `CompetitorRepository`: Already exists (via CompetitorRegistry)
- `ArtifactRepository`: Already exists (via ArtifactStore)

### 2. Adapter Pattern
- `SecurityAdapter`: Abstract security scanning
- `BenchmarkAdapter`: Abstract benchmark execution
- Graceful fallback when adapters unavailable

### 3. Strategy Pattern
- `EliminationStrategy`: Pluggable elimination logic
- `ConvergenceStrategy`: Pluggable convergence detection
- `ScoringStrategy`: Pluggable scoring algorithms

### 4. Dependency Injection
- Pass dependencies via constructor
- No global state
- Easy to test with mocks

## Code Organization Principles

1. **Single Responsibility**: Each module has one clear purpose
2. **Open/Closed**: Extend via adapters/strategies, don't modify core
3. **Dependency Inversion**: Depend on abstractions (interfaces), not concretions
4. **Interface Segregation**: Small, focused interfaces
5. **DRY**: Reuse adapters, repositories, utilities

## Error Handling Strategy

1. **Validation Errors**: Fail fast with clear messages
2. **Adapter Failures**: Log warning, use fallback, continue
3. **Test Failures**: Record failure, continue with other competitors
4. **Scoring Failures**: Use default score (0), log error
5. **Elimination Edge Cases**: Handle ties, minimum competitors

## Performance Considerations

1. **Score Caching**: Cache scores per round, avoid recalculation
2. **Security Scan Caching**: Cache scan results per worktree hash
3. **Lazy Loading**: Load competitor data only when needed
4. **Batch Operations**: Score/eliminate in batches, not one-by-one

## Testing Strategy

1. **Unit Tests**: Each component tested in isolation
2. **Integration Tests**: Full round flow with scoring/elimination
3. **Adapter Tests**: Test with/without optional tools
4. **Edge Case Tests**: Ties, empty rounds, single competitor

## Quick Start (Post-Implementation)

```bash
# Install dependencies
pip install -r requirements.txt

# Optional: Install security tools (will fallback if missing)
pip install semgrep
# snyk requires: npm install -g snyk && snyk auth

# Initialize competition
python -m src.cli init examples/basic_competition.json

# Register competitors
python -m src.cli competitor register "AgentA" examples/sample_competitor.py

# Run competition (handles rounds, scoring, elimination, convergence)
python -m src.cli arena run-all
```

## Success Criteria

✅ **MVP Complete When:**
1. Scoring system calculates multi-criteria scores
2. Elimination removes bottom N competitors per round
3. Convergence detection stops competition when stable
4. Security adapters work with graceful fallback
5. All tests pass
6. Can run end-to-end competition locally
7. Code follows MVC/repository/adapter patterns

## Future Enhancements (Post-MVP)

1. **Advanced Benchmarking**: Memory profiling, CPU usage
2. **Diversity Metrics**: Embedding-based similarity
3. **Parallel Execution**: Concurrent test runs
4. **Web UI**: Real-time monitoring dashboard
5. **Database Backend**: Replace JSON files with SQLite/Postgres
6. **Git Integration**: Optional git worktree support

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Security tools unavailable | Fallback adapter returns neutral score |
| Scoring too complex | Start simple, iterate |
| Performance issues | Cache aggressively, optimize hot paths |
| Integration complexity | Test integration early, mock dependencies |
| Time overrun | Prioritize core features, stub rest |

## Timeline Summary

- **Days 1-3**: Scoring system
- **Days 4-5**: Elimination & convergence
- **Days 6-7**: Security adapters
- **Day 8**: Integration & testing
- **Total**: ~8 days for MVP

## Next Steps

1. Review and approve this plan
2. Create folder structure
3. Implement Phase 1 (Scoring)
4. Iterate based on feedback
