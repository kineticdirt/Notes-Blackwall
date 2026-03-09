/**
 * High-performance orchestrator
 * Coordinates parallel test/benchmark execution with caching and resource monitoring
 * Time complexity: O(n log n) for normalization, O(n) for execution (parallel)
 */

import { runTest } from './runner/test-runner.js';
import { runBenchmark } from './runner/benchmark-runner.js';
import { ResultCache } from './utils/cache.js';
import { normalizeMetrics, mean } from './utils/normalize.js';
import { getResourceSnapshot } from './utils/profiler.js';
import { cpus } from 'os';

/**
 * Performance-focused orchestrator
 */
export class PerformanceOrchestrator {
  constructor(config) {
    this.config = config;
    this.cache = new ResultCache(config.caching || {});
    this.results = [];
    this.maxConcurrency = config.maxConcurrency || Math.min(4, cpus().length);
  }
  
  /**
   * Run full evaluation: tests + benchmarks for all solutions
   * @returns {Promise<SolutionEvaluation[]>} Evaluation results
   */
  async evaluateAll() {
    const startTime = Date.now();
    const solutions = this.config.solutions || [];
    
    console.log(`🚀 Starting evaluation of ${solutions.length} solutions`);
    console.log(`📊 Max concurrency: ${this.maxConcurrency}`);
    
    // Clear expired cache entries
    const cleared = this.cache.clearExpired();
    if (cleared > 0) {
      console.log(`🗑️  Cleared ${cleared} expired cache entries`);
    }
    
    // Run evaluations in parallel batches
    const evaluations = await this.runParallelBatches(solutions);
    
    // Normalize metrics across all solutions
    const normalized = this.normalizeAllMetrics(evaluations);
    
    // Calculate final scores
    const scored = this.calculateScores(evaluations, normalized);
    
    // Identify bottlenecks
    const withBottlenecks = scored.map(eval => ({
      ...eval,
      bottlenecks: this.identifyBottlenecks(eval)
    }));
    
    const duration = Date.now() - startTime;
    console.log(`✅ Evaluation complete in ${duration}ms`);
    console.log(`📈 Cache hit rate: ${(this.cache.hits / (this.cache.hits + this.cache.misses) * 100).toFixed(1)}%`);
    
    this.results = withBottlenecks;
    return withBottlenecks;
  }
  
  /**
   * Run evaluations in parallel batches
   * Time complexity: O(n) with parallel execution
   * @param {SolutionConfig[]} solutions - Solutions to evaluate
   * @returns {Promise<SolutionEvaluation[]>} Evaluations
   */
  async runParallelBatches(solutions) {
    const batches = [];
    
    // Create batches for parallel execution
    for (let i = 0; i < solutions.length; i += this.maxConcurrency) {
      batches.push(solutions.slice(i, i + this.maxConcurrency));
    }
    
    const allEvaluations = [];
    
    for (const batch of batches) {
      const batchPromises = batch.map(solution => this.evaluateSolution(solution));
      const batchResults = await Promise.all(batchPromises);
      allEvaluations.push(...batchResults);
    }
    
    return allEvaluations;
  }
  
  /**
   * Evaluate a single solution (tests + benchmarks)
   * @param {SolutionConfig} solution - Solution configuration
   * @returns {Promise<SolutionEvaluation>} Evaluation result
   */
  async evaluateSolution(solution) {
    const solutionPath = solution.path;
    const solutionId = solution.id;
    
    console.log(`\n📦 Evaluating: ${solution.name} (${solutionId})`);
    
    // Check cache first
    const cacheKey = this.cache.generateKey(solutionPath, {
      testHarness: this.config.testHarness,
      benchmarking: this.config.benchmarking
    });
    
    const cached = this.cache.getWithStats(cacheKey);
    if (cached) {
      console.log(`  ⚡ Cache hit - skipping execution`);
      return cached;
    }
    
    const startSnapshot = getResourceSnapshot();
    
    // Run tests
    const testResults = await this.runTests(solution);
    
    // Run benchmarks
    const benchmarkResults = await this.runBenchmarks(solution);
    
    // Aggregate resource metrics
    const aggregateMetrics = this.aggregateSolutionMetrics(testResults, benchmarkResults);
    
    const evaluation = {
      solutionId,
      solutionName: solution.name,
      testResults,
      benchmarkResults,
      aggregateMetrics,
      timestamp: Date.now()
    };
    
    // Cache result
    this.cache.set(cacheKey, evaluation);
    
    return evaluation;
  }
  
  /**
   * Run tests for a solution
   * @param {SolutionConfig} solution - Solution config
   * @returns {Promise<TestResult[]>} Test results
   */
  async runTests(solution) {
    const tests = this.config.testHarness?.tests || [{ testId: 'default' }];
    const results = [];
    
    for (const testConfig of tests) {
      try {
        const result = await runTest(solution.path, {
          ...this.config.testHarness,
          solutionId: solution.id,
          ...testConfig
        });
        results.push(result);
      } catch (error) {
        results.push({
          solutionId: solution.id,
          testId: testConfig.testId || 'default',
          passed: false,
          score: 0,
          metrics: {},
          error: error.message,
          timestamp: Date.now()
        });
      }
    }
    
    return results;
  }
  
  /**
   * Run benchmarks for a solution
   * @param {SolutionConfig} solution - Solution config
   * @returns {Promise<BenchmarkResult[]>} Benchmark results
   */
  async runBenchmarks(solution) {
    const benchmarks = this.config.benchmarking?.benchmarks || [{ benchmarkId: 'default' }];
    const results = [];
    
    for (const benchmarkConfig of benchmarks) {
      try {
        const result = await runBenchmark(solution.path, {
          ...this.config.benchmarking,
          solutionId: solution.id,
          ...benchmarkConfig
        });
        results.push(result);
      } catch (error) {
        console.error(`  ❌ Benchmark failed: ${error.message}`);
        // Continue with other benchmarks
      }
    }
    
    return results;
  }
  
  /**
   * Normalize metrics across all solutions
   * Time complexity: O(n log n) due to sorting
   * @param {SolutionEvaluation[]} evaluations - Evaluations
   * @returns {Map<string, Object>} Normalized metrics
   */
  normalizeAllMetrics(evaluations) {
    // Extract metrics to normalize
    const metricKeys = [
      'duration',
      'memoryUsage',
      'cpuUsage',
      'peakMemory',
      'meanTime', // From benchmarks
      'stdDev'    // From benchmarks
    ];
    
    // Prepare data structure for normalization
    const solutionsWithMetrics = evaluations.map(eval => ({
      solutionId: eval.solutionId,
      metrics: {
        ...eval.aggregateMetrics,
        // Add benchmark metrics
        meanTime: eval.benchmarkResults.length > 0 
          ? mean(eval.benchmarkResults.map(b => b.meanTime))
          : null,
        stdDev: eval.benchmarkResults.length > 0
          ? mean(eval.benchmarkResults.map(b => b.stdDev))
          : null
      }
    }));
    
    return normalizeMetrics(solutionsWithMetrics, metricKeys);
  }
  
  /**
   * Calculate final scores with weights
   * @param {SolutionEvaluation[]} evaluations - Evaluations
   * @param {Map<string, Object>} normalized - Normalized metrics
   * @returns {SolutionEvaluation[]} Evaluations with scores
   */
  calculateScores(evaluations, normalized) {
    const weights = this.config.scoring?.weights || {
      correctness: 0.5,
      performance: 0.2,
      code_quality: 0.2,
      documentation: 0.1
    };
    
    return evaluations.map(eval => {
      const normalizedMetrics = normalized.get(eval.solutionId) || {};
      
      // Calculate category scores
      const correctness = this.calculateCorrectnessScore(eval.testResults);
      const performance = this.calculatePerformanceScore(normalizedMetrics);
      const codeQuality = this.calculateCodeQualityScore(eval.testResults);
      const documentation = this.calculateDocumentationScore(eval.testResults);
      
      // Weighted final score
      const finalScore = 
        correctness * weights.correctness +
        performance * weights.performance +
        codeQuality * weights.code_quality +
        documentation * weights.documentation;
      
      return {
        ...eval,
        normalizedMetrics,
        finalScore: Math.round(finalScore * 100) / 100,
        breakdown: {
          correctness: Math.round(correctness * 100),
          performance: Math.round(performance * 100),
          codeQuality: Math.round(codeQuality * 100),
          documentation: Math.round(documentation * 100)
        }
      };
    });
  }
  
  /**
   * Calculate correctness score from test results
   * @param {TestResult[]} testResults - Test results
   * @returns {number} Score 0-1
   */
  calculateCorrectnessScore(testResults) {
    if (testResults.length === 0) return 0;
    const totalScore = testResults.reduce((sum, t) => sum + (t.score || 0), 0);
    const maxScore = testResults.reduce((sum, t) => sum + (t.maxScore || 100), 0);
    return maxScore > 0 ? totalScore / maxScore : 0;
  }
  
  /**
   * Calculate performance score from normalized metrics
   * @param {Object} normalizedMetrics - Normalized metrics
   * @returns {number} Score 0-1
   */
  calculatePerformanceScore(normalizedMetrics) {
    // Higher normalized scores for duration/meanTime = better (lower is better, so invert)
    const durationScore = normalizedMetrics.duration?.normalizedScore || 50;
    const meanTimeScore = normalizedMetrics.meanTime?.normalizedScore || 50;
    
    // Invert: lower duration = higher score
    return (100 - (durationScore + meanTimeScore) / 2) / 100;
  }
  
  /**
   * Calculate code quality score
   * @param {TestResult[]} testResults - Test results
   * @returns {number} Score 0-1
   */
  calculateCodeQualityScore(testResults) {
    // Based on syntax validity, error rates, etc.
    const validTests = testResults.filter(t => t.passed && !t.error).length;
    return testResults.length > 0 ? validTests / testResults.length : 0;
  }
  
  /**
   * Calculate documentation score
   * @param {TestResult[]} testResults - Test results
   * @returns {number} Score 0-1
   */
  calculateDocumentationScore(testResults) {
    // Check if README exists (from test output)
    const hasReadme = testResults.some(t => 
      t.output?.testResult?.has_readme === true
    );
    return hasReadme ? 1 : 0;
  }
  
  /**
   * Identify performance bottlenecks
   * @param {SolutionEvaluation} evaluation - Evaluation
   * @returns {string[]} Bottleneck descriptions
   */
  identifyBottlenecks(evaluation) {
    const bottlenecks = [];
    const metrics = evaluation.aggregateMetrics;
    
    // Memory leaks: increasing memory over time
    if (metrics.memoryDelta > 50 * 1024 * 1024) { // > 50MB increase
      bottlenecks.push(`Memory leak detected: ${(metrics.memoryDelta / 1024 / 1024).toFixed(2)}MB increase`);
    }
    
    // High CPU usage
    if (metrics.cpuUsage > 80) {
      bottlenecks.push(`High CPU usage: ${metrics.cpuUsage.toFixed(1)}%`);
    }
    
    // High memory usage
    if (metrics.peakMemory > 500 * 1024 * 1024) { // > 500MB
      bottlenecks.push(`High memory usage: ${(metrics.peakMemory / 1024 / 1024).toFixed(2)}MB peak`);
    }
    
    // Slow execution
    if (metrics.duration > 10000) { // > 10s
      bottlenecks.push(`Slow execution: ${metrics.duration.toFixed(0)}ms`);
    }
    
    // High variance in benchmark times (unstable)
    if (evaluation.benchmarkResults.length > 0) {
      const avgStdDev = mean(evaluation.benchmarkResults.map(b => b.stdDev));
      const avgMean = mean(evaluation.benchmarkResults.map(b => b.meanTime));
      if (avgStdDev / avgMean > 0.2) { // > 20% coefficient of variation
        bottlenecks.push(`Unstable performance: ${(avgStdDev / avgMean * 100).toFixed(1)}% variance`);
      }
    }
    
    return bottlenecks;
  }
  
  /**
   * Aggregate resource metrics from tests and benchmarks
   * @param {TestResult[]} testResults - Test results
   * @param {BenchmarkResult[]} benchmarkResults - Benchmark results
   * @returns {ResourceMetrics} Aggregated metrics
   */
  aggregateSolutionMetrics(testResults, benchmarkResults) {
    const allMetrics = [
      ...testResults.map(t => t.metrics),
      ...benchmarkResults.map(b => b.metrics)
    ].filter(m => m && m.duration);
    
    if (allMetrics.length === 0) {
      return {
        cpuUsage: 0,
        memoryUsage: 0,
        heapUsed: 0,
        heapTotal: 0,
        externalMemory: 0,
        rss: 0,
        duration: 0,
        peakMemory: 0
      };
    }
    
    return {
      cpuUsage: mean(allMetrics.map(m => m.cpuUsage || 0)),
      memoryUsage: mean(allMetrics.map(m => m.memoryUsage || 0)),
      heapUsed: mean(allMetrics.map(m => m.heapUsed || 0)),
      heapTotal: mean(allMetrics.map(m => m.heapTotal || 0)),
      externalMemory: mean(allMetrics.map(m => m.externalMemory || 0)),
      rss: mean(allMetrics.map(m => m.rss || 0)),
      duration: allMetrics.reduce((sum, m) => sum + (m.duration || 0), 0),
      peakMemory: Math.max(...allMetrics.map(m => m.peakMemory || m.heapUsed || 0)),
      memoryDelta: allMetrics.length > 1 
        ? (allMetrics[allMetrics.length - 1].heapUsed || 0) - (allMetrics[0].heapUsed || 0)
        : 0
    };
  }
  
  /**
   * Generate performance report
   * @param {string} [outputPath] - Output file path
   * @returns {Promise<string>} Report HTML
   */
  async generateReport(outputPath = 'performance-report.html') {
    // Implementation in separate file for clarity
    const { generateReport: genReport } = await import('./report-generator.js');
    return genReport(this.results, outputPath);
  }
}
