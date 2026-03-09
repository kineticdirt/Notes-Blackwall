/**
 * Type definitions for the performance orchestrator
 */

/**
 * @typedef {Object} SolutionConfig
 * @property {string} id - Unique solution identifier
 * @property {string} name - Human-readable solution name
 * @property {string} path - Path to solution directory
 * @property {Object} [metadata] - Additional metadata
 */

/**
 * @typedef {Object} ResourceMetrics
 * @property {number} cpuUsage - CPU usage percentage (0-100)
 * @property {number} memoryUsage - Memory usage in bytes
 * @property {number} heapUsed - Heap used in bytes
 * @property {number} heapTotal - Total heap in bytes
 * @property {number} externalMemory - External memory in bytes
 * @property {number} rss - Resident Set Size in bytes
 * @property {number} duration - Execution duration in milliseconds
 * @property {number} [peakMemory] - Peak memory usage during execution
 */

/**
 * @typedef {Object} TestResult
 * @property {string} solutionId - Solution identifier
 * @property {string} testId - Test identifier
 * @property {boolean} passed - Whether test passed
 * @property {number} score - Test score (0-100)
 * @property {ResourceMetrics} metrics - Resource usage metrics
 * @property {string} [error] - Error message if failed
 * @property {Object} [output] - Test output data
 * @property {number} timestamp - Execution timestamp
 */

/**
 * @typedef {Object} BenchmarkResult
 * @property {string} solutionId - Solution identifier
 * @property {string} benchmarkId - Benchmark identifier
 * @property {number} iterations - Number of iterations run
 * @property {number} meanTime - Mean execution time in ms
 * @property {number} medianTime - Median execution time in ms
 * @property {number} minTime - Minimum execution time in ms
 * @property {number} maxTime - Maximum execution time in ms
 * @property {number} stdDev - Standard deviation of execution times
 * @property {ResourceMetrics} metrics - Resource usage metrics
 * @property {string} [complexity] - Detected time complexity (O(n), O(n log n), etc.)
 * @property {number} timestamp - Execution timestamp
 */

/**
 * @typedef {Object} NormalizedMetrics
 * @property {number} zScore - Z-score normalized value
 * @property {number} percentile - Percentile rank (0-100)
 * @property {number} normalizedScore - Normalized score (0-100)
 * @property {Object} raw - Raw metric values
 */

/**
 * @typedef {Object} SolutionEvaluation
 * @property {string} solutionId - Solution identifier
 * @property {string} solutionName - Solution name
 * @property {TestResult[]} testResults - Test results
 * @property {BenchmarkResult[]} benchmarkResults - Benchmark results
 * @property {Object<string, NormalizedMetrics>} normalizedMetrics - Normalized metrics by type
 * @property {number} finalScore - Final weighted score
 * @property {Object} breakdown - Score breakdown by category
 * @property {ResourceMetrics} aggregateMetrics - Aggregate resource usage
 * @property {string[]} bottlenecks - Identified performance bottlenecks
 * @property {number} timestamp - Evaluation timestamp
 */

/**
 * @typedef {Object} CacheEntry
 * @property {string} hash - Content hash
 * @property {TestResult|BenchmarkResult} result - Cached result
 * @property {number} timestamp - Cache timestamp
 * @property {number} ttl - Time-to-live in milliseconds
 */

/**
 * @typedef {Object} OrchestratorConfig
 * @property {SolutionConfig[]} solutions - Solutions to evaluate
 * @property {Object} testHarness - Test harness configuration
 * @property {Object} benchmarking - Benchmarking configuration
 * @property {Object} caching - Caching configuration
 * @property {Object} scoring - Scoring weights
 * @property {Object} performance - Performance limits
 * @property {number} [maxConcurrency] - Maximum parallel executions
 */
