# Performance-Focused Orchestrator

High-performance Node.js orchestrator for running tests and benchmarks across multiple solutions with resource profiling, caching, and statistical normalization.

## Features

### 🚀 Performance Optimizations

- **Parallel Execution**: Runs tests/benchmarks in parallel batches (configurable concurrency)
- **Content-Based Caching**: SHA-256 hash-based cache to avoid repeated work
- **LRU Cache Eviction**: Memory-efficient cache with TTL support
- **Resource Profiling**: Low-overhead CPU/memory monitoring using Node.js native APIs
- **Time Complexity**: O(n log n) max complexity for normalization, O(n) for execution

### 📊 Metrics & Analysis

- **CPU/Memory Profiling**: Real-time resource usage tracking
- **Statistical Normalization**: Z-score normalization and percentile ranking
- **Bottleneck Detection**: Automatic identification of performance issues
- **Complexity Analysis**: Detects time complexity from benchmark data

### 🎯 What Gets Measured

1. **Execution Metrics**:
   - Duration (wall-clock time)
   - CPU usage percentage
   - Memory usage (heap, RSS, external)
   - Peak memory consumption
   - Memory delta (leak detection)

2. **Benchmark Metrics**:
   - Mean, median, min, max execution times
   - Standard deviation (variance analysis)
   - Time complexity detection (O(1), O(n), O(n log n), etc.)

3. **Normalized Metrics**:
   - Z-scores for all metrics
   - Percentile rankings
   - Normalized scores (0-100 scale)

## Installation

```bash
cd orchestrator-node
npm install
```

## Usage

### Basic Usage

```bash
node src/index.js
```

Uses `worktree-spec.json` by default.

### Configuration

Create or modify `worktree-spec.json`:

```json
{
  "solutions": [
    {
      "id": "solution-1",
      "name": "Solution 1",
      "path": "worktrees/solution-1"
    }
  ],
  "testHarness": {
    "path": "test_harness",
    "runner": "run_tests.sh",
    "timeout": 30000
  },
  "benchmarking": {
    "iterations": 10,
    "warmupIterations": 2
  },
  "caching": {
    "maxSize": 1000,
    "ttl": 3600000
  },
  "scoring": {
    "weights": {
      "correctness": 0.5,
      "performance": 0.2,
      "code_quality": 0.2,
      "documentation": 0.1
    }
  },
  "maxConcurrency": 4,
  "report": {
    "output": "performance-report.html"
  }
}
```

## Architecture

### Core Components

1. **Orchestrator** (`src/orchestrator.js`)
   - Coordinates parallel execution
   - Manages caching
   - Aggregates results
   - Calculates scores

2. **Test Runner** (`src/runner/test-runner.js`)
   - Executes test harness
   - Captures resource metrics
   - Parses results

3. **Benchmark Runner** (`src/runner/benchmark-runner.js`)
   - Runs multiple iterations
   - Statistical analysis
   - Complexity detection

4. **Profiler** (`src/utils/profiler.js`)
   - CPU/memory monitoring
   - Low-overhead sampling
   - Peak detection

5. **Cache** (`src/utils/cache.js`)
   - Content-based hashing
   - LRU eviction
   - TTL support

6. **Normalizer** (`src/utils/normalize.js`)
   - Z-score calculation
   - Percentile ranking
   - Statistical analysis

## Performance Characteristics

### Time Complexity

- **Test Execution**: O(n) with parallel execution (n = number of solutions)
- **Benchmark Execution**: O(n * m) where m = iterations
- **Normalization**: O(n log n) due to sorting for percentile calculation
- **Cache Operations**: O(1) get/set, O(n) eviction (amortized)

### Memory Complexity

- **Cache**: O(k) where k = max cache size
- **Profiling**: O(1) per execution (samples stored temporarily)
- **Results**: O(n) where n = number of solutions

### Optimizations

1. **Parallel Batching**: Limits concurrent executions to prevent resource exhaustion
2. **Content Hashing**: Only re-runs tests when solution code changes
3. **LRU Eviction**: Prevents unbounded memory growth
4. **Efficient Sampling**: Memory monitoring uses minimal overhead
5. **Early Termination**: Timeout handling prevents hanging processes

## Bottleneck Detection

The orchestrator automatically identifies:

- **Memory Leaks**: >50MB memory increase during execution
- **High CPU Usage**: >80% CPU utilization
- **High Memory Usage**: >500MB peak memory
- **Slow Execution**: >10s execution time
- **Unstable Performance**: >20% coefficient of variation in benchmarks

## Z-Score Normalization

Metrics are normalized using z-scores:

```
z = (x - μ) / σ
```

Where:
- `x` = metric value
- `μ` = mean across all solutions
- `σ` = standard deviation

Z-scores are then converted to normalized scores (0-100) using a sigmoid-like function:

```
normalized_score = 50 + (50 * tanh(z / 2))
```

This ensures:
- Values near the mean → ~50
- Values above mean → 50-100
- Values below mean → 0-50

## Example Output

```
🚀 Starting evaluation of 3 solutions
📊 Max concurrency: 4

📦 Evaluating: Solution 1 (solution-1)
  ⚡ Cache hit - skipping execution

📦 Evaluating: Solution 2 (solution-2)
  Running tests...
  Running benchmarks...

✅ Evaluation complete in 1234ms
📈 Cache hit rate: 33.3%

📊 Summary:
  1. Solution 1: 85.50/100
  2. Solution 2: 72.30/100
     ⚠️  2 bottleneck(s) detected
  3. Solution 3: 68.90/100
```

## Report

Generates detailed HTML report with:
- Score breakdowns
- Resource metrics with z-scores
- Bottleneck analysis
- Comparison tables
- Visual indicators

## API

### Programmatic Usage

```javascript
import { PerformanceOrchestrator } from './src/orchestrator.js';

const config = {
  solutions: [...],
  testHarness: {...},
  benchmarking: {...},
  caching: {...},
  scoring: {...}
};

const orchestrator = new PerformanceOrchestrator(config);
const results = await orchestrator.evaluateAll();
```

## Benchmarking

To benchmark the orchestrator itself:

```bash
npm run bench
```

## License

MIT
