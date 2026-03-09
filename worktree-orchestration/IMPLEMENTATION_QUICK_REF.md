# Implementation Quick Reference

## Folder Structure (Visual)

```
worktree-orchestration/
├── src/
│   ├── scoring/              ⭐ NEW - Scoring system
│   │   ├── scorer.py         [Abstract base]
│   │   ├── weighted_scorer.py [Main scorer]
│   │   ├── criteria/         [Individual criteria]
│   │   └── repository.py     [Score storage]
│   │
│   ├── elimination/          ⭐ NEW - Elimination logic
│   │   ├── eliminator.py     [Abstract base]
│   │   └── bottom_n_eliminator.py [Implementation]
│   │
│   ├── convergence/          ⭐ NEW - Convergence detection
│   │   ├── detector.py       [Abstract base]
│   │   └── score_stability.py [Implementation]
│   │
│   └── adapters/             ⭐ NEW - External tool adapters
│       ├── base.py           [Abstract base]
│       └── security/         [Security tool adapters]
│           ├── semgrep_adapter.py
│           ├── snyk_adapter.py
│           └── fallback_adapter.py
```

## Implementation Checklist

### Phase 1: Scoring (Days 1-3)
- [ ] `src/scoring/scorer.py` - Abstract base class
- [ ] `src/scoring/weighted_scorer.py` - Weighted multi-criteria scorer
- [ ] `src/scoring/criteria/test_score.py` - Test pass/fail → score
- [ ] `src/scoring/criteria/performance_score.py` - Time → score
- [ ] `src/scoring/criteria/security_score.py` - Security scan → score
- [ ] `src/scoring/criteria/code_quality_score.py` - Quality metrics → score
- [ ] `src/scoring/repository.py` - Score storage/retrieval
- [ ] `tests/test_scoring.py` - Unit tests

### Phase 2: Elimination & Convergence (Days 4-5)
- [ ] `src/elimination/eliminator.py` - Abstract base
- [ ] `src/elimination/bottom_n_eliminator.py` - Bottom N elimination
- [ ] `src/convergence/detector.py` - Abstract base
- [ ] `src/convergence/score_stability.py` - Variance-based detection
- [ ] `tests/test_elimination.py` - Unit tests
- [ ] `tests/test_convergence.py` - Unit tests

### Phase 3: Security Adapters (Days 6-7)
- [ ] `src/adapters/base.py` - Abstract adapter interface
- [ ] `src/adapters/security/semgrep_adapter.py` - Semgrep wrapper
- [ ] `src/adapters/security/snyk_adapter.py` - Snyk wrapper
- [ ] `src/adapters/security/fallback_adapter.py` - Fallback when tools missing
- [ ] `tests/test_adapters.py` - Adapter tests

### Phase 4: Integration (Day 8)
- [ ] Update `arena.py` to integrate scoring
- [ ] Update `arena.py` to integrate elimination
- [ ] Update `arena.py` to integrate convergence
- [ ] Update `config.py` to support new config schema
- [ ] Integration tests

## Key Interfaces

### Scorer Interface
```python
class Scorer(ABC):
    @abstractmethod
    def score(self, competitor_id: str, round_num: int, 
              test_results: dict) -> float:
        """Returns score 0-100"""
        pass
```

### Security Adapter Interface
```python
class SecurityAdapter(ABC):
    @abstractmethod
    def scan(self, worktree_path: Path) -> SecurityResult:
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass
```

### Eliminator Interface
```python
class Eliminator(ABC):
    @abstractmethod
    def eliminate(self, scores: Dict[str, float]) -> List[str]:
        """Returns list of competitor IDs to eliminate"""
        pass
```

### Convergence Detector Interface
```python
class ConvergenceDetector(ABC):
    @abstractmethod
    def is_converged(self, round_scores: List[Dict[str, float]]) -> bool:
        """Returns True if competition has converged"""
        pass
```

## Integration Points

### Arena Integration
```python
# In arena.py, after test_round():
test_results = self.test_round(round_num)
scores = self.scorer.score_all(test_results)
eliminated = self.eliminator.eliminate(scores)
if self.convergence_detector.is_converged(historical_scores):
    return "CONVERGED"
```

### Security Integration
```python
# In arena.py, during test execution:
security_result = self.security_adapter.scan(worktree.path)
# Pass to scoring system
```

## Configuration Updates

Add to `config.py`:
```python
class ScoringConfig(BaseModel):
    weights: Dict[str, float]

class EliminationConfig(BaseModel):
    strategy: str
    eliminate_per_round: int
    min_competitors: int

class ConvergenceConfig(BaseModel):
    enabled: bool
    method: str
    threshold: float
    window_size: int
```

## Testing Strategy

### Unit Tests
- Each scorer criterion tested independently
- Adapters tested with/without tools available
- Elimination logic tested with various score distributions

### Integration Tests
- Full round: test → score → eliminate → check convergence
- Multiple rounds: verify elimination persists
- Convergence: verify competition stops when stable

### Mock Strategy
- Mock security adapters for tests
- Mock test execution for scoring tests
- Use fixtures for consistent test data

## Error Handling Patterns

```python
# Adapter pattern: graceful fallback
try:
    result = semgrep_adapter.scan(path)
except ToolNotFoundError:
    result = fallback_adapter.scan(path)

# Scoring: default to 0 on error
try:
    score = scorer.score(...)
except Exception as e:
    logger.warning(f"Scoring failed: {e}")
    score = 0.0

# Elimination: handle edge cases
if len(competitors) <= min_competitors:
    return []  # Don't eliminate if too few remain
```

## Performance Optimizations

1. **Cache scores**: Store in repository, avoid recalculation
2. **Cache security scans**: Key by worktree hash
3. **Lazy load**: Load competitor data only when needed
4. **Batch operations**: Score all competitors at once

## Common Patterns

### Repository Pattern
```python
class ScoreRepository:
    def save(self, round_num: int, competitor_id: str, score: float):
        # Save to .shared-cache/scores/round_{n}/{competitor_id}.json
    
    def get(self, round_num: int, competitor_id: str) -> Optional[float]:
        # Load from cache
```

### Adapter Pattern
```python
class SecurityAdapterFactory:
    @staticmethod
    def create() -> SecurityAdapter:
        if SemgrepAdapter.is_available():
            return SemgrepAdapter()
        elif SnykAdapter.is_available():
            return SnykAdapter()
        else:
            return FallbackSecurityAdapter()
```

### Strategy Pattern
```python
class EliminationStrategyFactory:
    @staticmethod
    def create(strategy: str) -> Eliminator:
        if strategy == "bottom_n":
            return BottomNEliminator()
        elif strategy == "threshold":
            return ThresholdEliminator()
```
