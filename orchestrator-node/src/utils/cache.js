/**
 * Content-based cache with TTL support
 * Implements LRU eviction for memory efficiency
 * Time complexity: O(1) get/set, O(n) eviction (amortized)
 */

import { hashSolution } from './hash.js';

/**
 * LRU Cache implementation for test/benchmark results
 */
export class ResultCache {
  constructor(options = {}) {
    this.maxSize = options.maxSize || 1000;
    this.ttl = options.ttl || 3600000; // 1 hour default
    this.cache = new Map(); // Map<hash, CacheEntry>
    this.accessOrder = new Map(); // Map<hash, timestamp> for LRU tracking
  }
  
  /**
   * Generate cache key from solution path and test config
   * @param {string} solutionPath - Path to solution
   * @param {Object} testConfig - Test configuration
   * @returns {string} Cache key hash
   */
  generateKey(solutionPath, testConfig) {
    return hashSolution(solutionPath, testConfig);
  }
  
  /**
   * Get cached result if valid
   * O(1) time complexity
   * @param {string} key - Cache key
   * @returns {TestResult|BenchmarkResult|null} Cached result or null
   */
  get(key) {
    const entry = this.cache.get(key);
    
    if (!entry) {
      return null;
    }
    
    // Check TTL
    const age = Date.now() - entry.timestamp;
    if (age > entry.ttl) {
      this.cache.delete(key);
      this.accessOrder.delete(key);
      return null;
    }
    
    // Update access order for LRU
    this.accessOrder.set(key, Date.now());
    
    return entry.result;
  }
  
  /**
   * Store result in cache
   * O(1) time complexity, O(n) if eviction needed (amortized)
   * @param {string} key - Cache key
   * @param {TestResult|BenchmarkResult} result - Result to cache
   * @param {number} [customTtl] - Custom TTL in ms
   */
  set(key, result, customTtl = null) {
    // Evict if at capacity
    if (this.cache.size >= this.maxSize) {
      this.evictLRU();
    }
    
    this.cache.set(key, {
      hash: key,
      result,
      timestamp: Date.now(),
      ttl: customTtl || this.ttl
    });
    
    this.accessOrder.set(key, Date.now());
  }
  
  /**
   * Evict least recently used entry
   * O(n) time complexity, but amortized to O(1) per operation
   */
  evictLRU() {
    if (this.accessOrder.size === 0) {
      return;
    }
    
    // Find oldest access
    let oldestKey = null;
    let oldestTime = Infinity;
    
    for (const [key, time] of this.accessOrder.entries()) {
      if (time < oldestTime) {
        oldestTime = time;
        oldestKey = key;
      }
    }
    
    if (oldestKey) {
      this.cache.delete(oldestKey);
      this.accessOrder.delete(oldestKey);
    }
  }
  
  /**
   * Clear expired entries
   * O(n) time complexity
   * @returns {number} Number of entries cleared
   */
  clearExpired() {
    const now = Date.now();
    let cleared = 0;
    
    for (const [key, entry] of this.cache.entries()) {
      const age = now - entry.timestamp;
      if (age > entry.ttl) {
        this.cache.delete(key);
        this.accessOrder.delete(key);
        cleared++;
      }
    }
    
    return cleared;
  }
  
  /**
   * Clear all cache entries
   */
  clear() {
    this.cache.clear();
    this.accessOrder.clear();
  }
  
  /**
   * Get cache statistics
   * @returns {Object} Cache stats
   */
  getStats() {
    const now = Date.now();
    let expired = 0;
    
    for (const entry of this.cache.values()) {
      if (now - entry.timestamp > entry.ttl) {
        expired++;
      }
    }
    
    return {
      size: this.cache.size,
      maxSize: this.maxSize,
      expired,
      hitRate: this.hits / (this.hits + this.misses) || 0
    };
  }
  
  // Track hit/miss for statistics
  hits = 0;
  misses = 0;
  
  /**
   * Get with hit/miss tracking
   * @param {string} key - Cache key
   * @returns {TestResult|BenchmarkResult|null}
   */
  getWithStats(key) {
    const result = this.get(key);
    if (result) {
      this.hits++;
    } else {
      this.misses++;
    }
    return result;
  }
}
