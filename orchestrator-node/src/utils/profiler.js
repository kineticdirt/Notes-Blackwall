/**
 * Resource profiler for CPU and memory metrics
 * Uses Node.js native APIs for low-overhead monitoring
 */

import { performance } from 'perf_hooks';
import process from 'process';

/**
 * Start resource profiling for a solution execution
 * @returns {Object} Profiler instance with start/stop methods
 */
export function createProfiler() {
  const startCpuUsage = process.cpuUsage();
  const startMemory = process.memoryUsage();
  const startTime = performance.now();
  
  let peakMemory = startMemory.heapUsed;
  let lastCheck = startTime;
  const memorySamples = [startMemory.heapUsed];
  
  // Monitor memory periodically (every 10ms) to catch peaks
  const memoryMonitor = setInterval(() => {
    const current = process.memoryUsage();
    memorySamples.push(current.heapUsed);
    if (current.heapUsed > peakMemory) {
      peakMemory = current.heapUsed;
    }
    lastCheck = performance.now();
  }, 10);
  
  return {
    /**
     * Stop profiling and return metrics
     * @returns {ResourceMetrics} Resource usage metrics
     */
    stop() {
      clearInterval(memoryMonitor);
      
      const endTime = performance.now();
      const endCpuUsage = process.cpuUsage(startCpuUsage);
      const endMemory = process.memoryUsage();
      
      const duration = endTime - startTime;
      
      // Calculate CPU usage percentage
      // cpuUsage returns { user, system } in microseconds
      const totalCpuTime = (endCpuUsage.user + endCpuUsage.system) / 1000; // Convert to ms
      const cpuUsagePercent = duration > 0 
        ? Math.min(100, (totalCpuTime / duration) * 100)
        : 0;
      
      // Calculate memory statistics
      const memoryDelta = endMemory.heapUsed - startMemory.heapUsed;
      const avgMemory = memorySamples.reduce((a, b) => a + b, 0) / memorySamples.length;
      
      return {
        cpuUsage: cpuUsagePercent,
        memoryUsage: endMemory.heapUsed,
        heapUsed: endMemory.heapUsed,
        heapTotal: endMemory.heapTotal,
        externalMemory: endMemory.external,
        rss: endMemory.rss,
        duration,
        peakMemory,
        memoryDelta,
        avgMemory,
        memorySamples: memorySamples.length
      };
    }
  };
}

/**
 * Profile an async function execution
 * @param {Function} fn - Async function to profile
 * @param {...any} args - Arguments to pass to function
 * @returns {Promise<{result: any, metrics: ResourceMetrics}>}
 */
export async function profileExecution(fn, ...args) {
  const profiler = createProfiler();
  try {
    const result = await fn(...args);
    const metrics = profiler.stop();
    return { result, metrics };
  } catch (error) {
    const metrics = profiler.stop();
    throw { error, metrics };
  }
}

/**
 * Get current system resource usage snapshot
 * @returns {ResourceMetrics} Current resource metrics
 */
export function getResourceSnapshot() {
  const memory = process.memoryUsage();
  const cpuUsage = process.cpuUsage();
  
  return {
    cpuUsage: 0, // Requires delta calculation
    memoryUsage: memory.heapUsed,
    heapUsed: memory.heapUsed,
    heapTotal: memory.heapTotal,
    externalMemory: memory.external,
    rss: memory.rss,
    duration: 0,
    timestamp: Date.now()
  };
}
