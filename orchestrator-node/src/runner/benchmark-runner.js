/**
 * Benchmark runner with statistical analysis
 * Runs multiple iterations and analyzes performance
 * Time complexity: O(n * m) where n=iterations, m=test complexity
 */

import { spawn } from 'child_process';
import { join } from 'path';
import { profileExecution } from '../utils/profiler.js';
import { mean, stdDev, detectComplexity } from '../utils/normalize.js';

/**
 * Run benchmark for a solution
 * @param {string} solutionPath - Path to solution directory
 * @param {Object} config - Benchmark configuration
 * @returns {Promise<BenchmarkResult>} Benchmark result
 */
export async function runBenchmark(solutionPath, config) {
  const {
    benchmarkId = 'default',
    iterations = 10,
    warmupIterations = 2,
    inputSizes = null, // For complexity analysis
    command = null, // Custom benchmark command
    timeout = 60000
  } = config;
  
  const executionTimes = [];
  const resourceMetrics = [];
  
  // Warmup iterations (not measured)
  for (let i = 0; i < warmupIterations; i++) {
    await executeBenchmark(solutionPath, config, timeout);
  }
  
  // Actual benchmark iterations
  for (let i = 0; i < iterations; i++) {
    const { metrics } = await profileExecution(
      () => executeBenchmark(solutionPath, config, timeout)
    );
    
    executionTimes.push(metrics.duration);
    resourceMetrics.push(metrics);
  }
  
  // Calculate statistics
  const sortedTimes = [...executionTimes].sort((a, b) => a - b);
  const m = mean(executionTimes);
  const sd = stdDev(executionTimes, m);
  
  // Aggregate resource metrics
  const aggregateMetrics = aggregateResourceMetrics(resourceMetrics);
  
  // Detect complexity if input sizes provided
  let complexity = null;
  if (inputSizes && inputSizes.length === executionTimes.length) {
    const complexityData = inputSizes.map((size, i) => ({
      inputSize: size,
      duration: executionTimes[i]
    }));
    complexity = detectComplexity(complexityData);
  }
  
  return {
    solutionId: config.solutionId,
    benchmarkId,
    iterations,
    meanTime: m,
    medianTime: sortedTimes[Math.floor(sortedTimes.length / 2)],
    minTime: sortedTimes[0],
    maxTime: sortedTimes[sortedTimes.length - 1],
    stdDev: sd,
    metrics: aggregateMetrics,
    complexity,
    timestamp: Date.now()
  };
}

/**
 * Execute single benchmark iteration
 * @param {string} solutionPath - Path to solution
 * @param {Object} config - Benchmark config
 * @param {number} timeout - Timeout in ms
 * @returns {Promise<void>}
 */
async function executeBenchmark(solutionPath, config, timeout) {
  return new Promise((resolve, reject) => {
    // Default: run test harness, but can be customized
    const command = config.command || ['node', '--test'];
    const args = config.args || [solutionPath];
    
    const proc = spawn(command[0], args, {
      cwd: process.cwd(),
      stdio: 'ignore'
    });
    
    const timeoutId = setTimeout(() => {
      proc.kill('SIGTERM');
      reject(new Error('Benchmark timeout'));
    }, timeout);
    
    proc.on('close', (code) => {
      clearTimeout(timeoutId);
      resolve();
    });
    
    proc.on('error', (error) => {
      clearTimeout(timeoutId);
      reject(error);
    });
  });
}

/**
 * Aggregate resource metrics across iterations
 * @param {ResourceMetrics[]} metrics - Array of metrics
 * @returns {ResourceMetrics} Aggregated metrics
 */
function aggregateResourceMetrics(metrics) {
  if (metrics.length === 0) {
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
    cpuUsage: mean(metrics.map(m => m.cpuUsage)),
    memoryUsage: mean(metrics.map(m => m.memoryUsage)),
    heapUsed: mean(metrics.map(m => m.heapUsed)),
    heapTotal: mean(metrics.map(m => m.heapTotal)),
    externalMemory: mean(metrics.map(m => m.externalMemory)),
    rss: mean(metrics.map(m => m.rss)),
    duration: mean(metrics.map(m => m.duration)),
    peakMemory: Math.max(...metrics.map(m => m.peakMemory || m.heapUsed))
  };
}
