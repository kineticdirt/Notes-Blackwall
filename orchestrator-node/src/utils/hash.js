/**
 * Content-based hashing utilities for cache invalidation
 * Uses SHA-256 for deterministic hashing
 */

import { createHash } from 'crypto';
import { readFileSync, readdirSync } from 'fs';
import { join } from 'path';

/**
 * Generate hash for a file
 * @param {string} filePath - Path to file
 * @returns {string} SHA-256 hash
 */
export function hashFile(filePath) {
  try {
    const content = readFileSync(filePath);
    return createHash('sha256').update(content).digest('hex');
  } catch (error) {
    return null;
  }
}

/**
 * Generate hash for directory contents (recursive)
 * Efficiently hashes all files in directory tree
 * Time complexity: O(n) where n is total file size
 * @param {string} dirPath - Path to directory
 * @param {string[]} [ignorePatterns] - Patterns to ignore
 * @returns {string} Combined hash of all files
 */
export function hashDirectory(dirPath, ignorePatterns = ['.git', 'node_modules', '__pycache__', '.cache']) {
  const hashes = [];
  
  function walkDir(currentPath) {
    try {
      const entries = readdirSync(currentPath, { withFileTypes: true });
      
      for (const entry of entries) {
        const fullPath = join(currentPath, entry.name);
        
        // Skip ignored patterns
        if (ignorePatterns.some(pattern => entry.name.includes(pattern))) {
          continue;
        }
        
        if (entry.isDirectory()) {
          walkDir(fullPath);
        } else if (entry.isFile()) {
          const hash = hashFile(fullPath);
          if (hash) {
            hashes.push(`${entry.name}:${hash}`);
          }
        }
      }
    } catch (error) {
      // Skip inaccessible directories
    }
  }
  
  try {
    walkDir(dirPath);
  } catch (error) {
    return null;
  }
  
  // Sort for deterministic ordering, then hash combined result
  hashes.sort();
  return createHash('sha256').update(hashes.join('|')).digest('hex');
}

/**
 * Generate hash for solution (files + metadata)
 * @param {string} solutionPath - Path to solution
 * @param {Object} metadata - Additional metadata
 * @returns {string} Combined hash
 */
export function hashSolution(solutionPath, metadata = {}) {
  const fileHash = hashDirectory(solutionPath);
  const metaHash = createHash('sha256')
    .update(JSON.stringify(metadata))
    .digest('hex');
  
  return createHash('sha256')
    .update(`${fileHash}:${metaHash}`)
    .digest('hex');
}
