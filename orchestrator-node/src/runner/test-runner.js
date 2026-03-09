/**
 * Test runner with resource profiling
 * Executes tests and captures metrics
 */

import { spawn } from 'child_process';
import { join } from 'path';
import { readFileSync, existsSync } from 'fs';
import { profileExecution } from '../utils/profiler.js';

/**
 * Run test harness for a solution
 * @param {string} solutionPath - Path to solution directory
 * @param {Object} config - Test configuration
 * @returns {Promise<TestResult>} Test result with metrics
 */
export async function runTest(solutionPath, config) {
  const { testHarness, timeout = 30000 } = config;
  const harnessPath = join(testHarness.path, testHarness.runner);
  
  if (!existsSync(harnessPath)) {
    throw new Error(`Test harness not found: ${harnessPath}`);
  }
  
  // Profile the test execution
  const { result: testOutput, metrics } = await profileExecution(async () => {
    return new Promise((resolve, reject) => {
      const proc = spawn(harnessPath, [solutionPath], {
        cwd: process.cwd(),
        stdio: ['ignore', 'pipe', 'pipe']
      });
      
      let stdout = '';
      let stderr = '';
      
      proc.stdout.on('data', (data) => {
        stdout += data.toString();
      });
      
      proc.stderr.on('data', (data) => {
        stderr += data.toString();
      });
      
      const timeoutId = setTimeout(() => {
        proc.kill('SIGTERM');
        reject(new Error('Test timeout'));
      }, timeout);
      
      proc.on('close', (code) => {
        clearTimeout(timeoutId);
        resolve({ code, stdout, stderr });
      });
      
      proc.on('error', (error) => {
        clearTimeout(timeoutId);
        reject(error);
      });
    });
  });
  
  // Parse test result JSON
  const resultFile = join(solutionPath, 'test_result.json');
  let testResult = null;
  
  if (existsSync(resultFile)) {
    try {
      testResult = JSON.parse(readFileSync(resultFile, 'utf-8'));
    } catch (error) {
      // Invalid JSON, continue with defaults
    }
  }
  
  return {
    solutionId: config.solutionId,
    testId: config.testId || 'default',
    passed: testOutput.code === 0 && testResult !== null,
    score: testResult?.score || 0,
    maxScore: testResult?.max_score || 100,
    metrics: {
      ...metrics,
      exitCode: testOutput.code
    },
    output: {
      stdout: testOutput.stdout,
      stderr: testOutput.stderr,
      testResult
    },
    timestamp: Date.now()
  };
}
