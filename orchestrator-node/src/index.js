#!/usr/bin/env node
/**
 * Performance-focused orchestrator CLI
 * Main entry point
 */

import { readFileSync, writeFileSync } from 'fs';
import { cpus } from 'os';
import { PerformanceOrchestrator } from './orchestrator.js';
import { generateReport } from './report-generator.js';

/**
 * Load configuration from file
 */
function loadConfig(configPath = 'worktree-spec.json') {
  try {
    const content = readFileSync(configPath, 'utf-8');
    return JSON.parse(content);
  } catch (error) {
    console.error(`Failed to load config from ${configPath}:`, error.message);
    process.exit(1);
  }
}

/**
 * Main execution
 */
async function main() {
  const config = loadConfig();
  
  // Enhance config with performance settings
  const enhancedConfig = {
    ...config,
    maxConcurrency: config.maxConcurrency || Math.min(4, cpus().length),
    caching: {
      maxSize: 1000,
      ttl: 3600000, // 1 hour
      ...config.caching
    },
    benchmarking: {
      iterations: 10,
      warmupIterations: 2,
      ...config.benchmarking
    },
    performance: {
      maxMemoryMB: 1024,
      maxDurationMS: 60000,
      ...config.performance
    }
  };
  
  console.log('🎯 Performance-Focused Orchestrator');
  console.log('=====================================\n');
  
  const orchestrator = new PerformanceOrchestrator(enhancedConfig);
  
  try {
    const results = await orchestrator.evaluateAll();
    
    // Generate report
    const reportPath = config.report?.output || 'performance-report.html';
    const html = generateReport(results, reportPath);
    
    console.log(`\n📄 Report generated: ${reportPath}`);
    
    // Print summary
    console.log('\n📊 Summary:');
    results
      .sort((a, b) => b.finalScore - a.finalScore)
      .forEach((result, idx) => {
        console.log(`  ${idx + 1}. ${result.solutionName}: ${result.finalScore.toFixed(2)}/100`);
        if (result.bottlenecks && result.bottlenecks.length > 0) {
          console.log(`     ⚠️  ${result.bottlenecks.length} bottleneck(s) detected`);
        }
      });
    
  } catch (error) {
    console.error('❌ Orchestration failed:', error);
    process.exit(1);
  }
}

// Run if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}

export { PerformanceOrchestrator };
