# Usage Examples

## Basic Usage

```bash
# Install dependencies
npm install

# Run orchestrator
node src/index.js
```

## Programmatic Usage

```javascript
import { PerformanceOrchestrator } from './src/orchestrator.js';

const config = {
  solutions: [
    {
      id: 'sol-1',
      name: 'Solution 1',
      path: './worktrees/solution-1'
    }
  ],
  testHarness: {
    path: './test_harness',
    runner: 'run_tests.sh',
    timeout: 30000
  },
  benchmarking: {
    iterations: 10,
    warmupIterations: 2
  },
  caching: {
    maxSize: 1000,
    ttl: 3600000 // 1 hour
  },
  scoring: {
    weights: {
      correctness: 0.5,
      performance: 0.2,
      code_quality: 0.2,
      documentation: 0.1
    }
  },
  maxConcurrency: 4
};

const orchestrator = new PerformanceOrchestrator(config);
const results = await orchestrator.evaluateAll();

// Access results
results.forEach(result => {
  console.log(`${result.solutionName}: ${result.finalScore}/100`);
  console.log(`  Bottlenecks: ${result.bottlenecks.length}`);
  console.log(`  Duration: ${result.aggregateMetrics.duration}ms`);
  console.log(`  Memory: ${result.aggregateMetrics.memoryUsage / 1024 / 1024}MB`);
});

// Generate report
await orchestrator.generateReport('my-report.html');
```

## Custom Test Configuration

```json
{
  "testHarness": {
    "path": "./test_harness",
    "runner": "run_tests.sh",
    "timeout": 30000,
    "tests": [
      {
        "testId": "unit-tests",
        "args": ["--test", "unit"]
      },
      {
        "testId": "integration-tests",
        "args": ["--test", "integration"]
      }
    ]
  }
}
```

## Custom Benchmark Configuration

```json
{
  "benchmarking": {
    "iterations": 20,
    "warmupIterations": 5,
    "benchmarks": [
      {
        "benchmarkId": "small-input",
        "inputSizes": [10, 100, 1000]
      },
      {
        "benchmarkId": "large-input",
        "inputSizes": [10000, 100000, 1000000]
      }
    ]
  }
}
```

## Cache Management

```javascript
const orchestrator = new PerformanceOrchestrator(config);

// Check cache stats
const stats = orchestrator.cache.getStats();
console.log(`Cache size: ${stats.size}/${stats.maxSize}`);
console.log(`Hit rate: ${stats.hitRate * 100}%`);

// Clear expired entries
const cleared = orchestrator.cache.clearExpired();
console.log(`Cleared ${cleared} expired entries`);

// Clear all cache
orchestrator.cache.clear();
```

## Accessing Normalized Metrics

```javascript
const results = await orchestrator.evaluateAll();

results.forEach(result => {
  const normalized = result.normalizedMetrics;
  
  // Duration metrics
  const duration = normalized.duration;
  console.log(`Duration z-score: ${duration.zScore}`);
  console.log(`Duration percentile: ${duration.percentile}`);
  console.log(`Normalized score: ${duration.normalizedScore}`);
  
  // Memory metrics
  const memory = normalized.memoryUsage;
  console.log(`Memory z-score: ${memory.zScore}`);
  
  // Raw statistics
  console.log(`Mean: ${duration.raw.mean}`);
  console.log(`Std Dev: ${duration.raw.stdDev}`);
  console.log(`Min: ${duration.raw.min}`);
  console.log(`Max: ${duration.raw.max}`);
});
```

## Bottleneck Analysis

```javascript
const results = await orchestrator.evaluateAll();

results.forEach(result => {
  if (result.bottlenecks.length > 0) {
    console.log(`${result.solutionName} has bottlenecks:`);
    result.bottlenecks.forEach(bottleneck => {
      console.log(`  - ${bottleneck}`);
    });
  }
});
```

## Performance Tuning

### Increase Concurrency

```json
{
  "maxConcurrency": 8
}
```

### Adjust Cache Settings

```json
{
  "caching": {
    "maxSize": 5000,
    "ttl": 7200000
  }
}
```

### Custom Scoring Weights

```json
{
  "scoring": {
    "weights": {
      "correctness": 0.6,
      "performance": 0.3,
      "code_quality": 0.05,
      "documentation": 0.05
    }
  }
}
```

## Error Handling

```javascript
try {
  const results = await orchestrator.evaluateAll();
} catch (error) {
  if (error.error) {
    // Profiling error
    console.error('Execution failed:', error.error);
    console.error('Metrics captured:', error.metrics);
  } else {
    // General error
    console.error('Orchestration failed:', error);
  }
}
```

## Monitoring Progress

The orchestrator logs progress automatically:

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
```
