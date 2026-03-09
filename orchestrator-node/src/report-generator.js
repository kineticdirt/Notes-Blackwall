/**
 * Performance report generator
 * Creates detailed HTML reports with metrics, bottlenecks, and visualizations
 */

import { writeFileSync } from 'fs';

/**
 * Generate HTML performance report
 * @param {SolutionEvaluation[]} results - Evaluation results
 * @param {string} outputPath - Output file path
 * @returns {string} Generated HTML
 */
export function generateReport(results, outputPath) {
  const sortedResults = [...results].sort((a, b) => b.finalScore - a.finalScore);
  const timestamp = new Date().toISOString();
  
  const html = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Performance Evaluation Report</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f5f7fa;
            color: #2c3e50;
            line-height: 1.6;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h1 { font-size: 2.5em; margin-bottom: 10px; }
        .timestamp { opacity: 0.9; font-size: 0.9em; }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .summary-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .summary-card h3 {
            font-size: 0.9em;
            color: #7f8c8d;
            text-transform: uppercase;
            margin-bottom: 10px;
        }
        .summary-card .value {
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
        }
        .solution-card {
            background: white;
            border-radius: 8px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .solution-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .solution-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #ecf0f1;
        }
        .solution-name {
            font-size: 1.5em;
            font-weight: bold;
            color: #2c3e50;
        }
        .score-badge {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            font-size: 1.2em;
            font-weight: bold;
        }
        .breakdown {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .breakdown-item {
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 6px;
        }
        .breakdown-label {
            font-size: 0.85em;
            color: #7f8c8d;
            margin-bottom: 5px;
        }
        .breakdown-value {
            font-size: 1.3em;
            font-weight: bold;
            color: #2c3e50;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .metric {
            padding: 15px;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 4px solid #667eea;
        }
        .metric-label {
            font-size: 0.85em;
            color: #7f8c8d;
            margin-bottom: 5px;
        }
        .metric-value {
            font-size: 1.1em;
            font-weight: bold;
            color: #2c3e50;
        }
        .bottlenecks {
            margin-top: 20px;
            padding: 15px;
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            border-radius: 6px;
        }
        .bottlenecks h4 {
            color: #856404;
            margin-bottom: 10px;
        }
        .bottleneck-item {
            color: #856404;
            margin: 5px 0;
            padding-left: 20px;
        }
        .bottleneck-item::before {
            content: "⚠ ";
            font-weight: bold;
        }
        .no-bottlenecks {
            color: #28a745;
            font-weight: bold;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
            border-radius: 8px;
            overflow: hidden;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ecf0f1;
        }
        th {
            background: #34495e;
            color: white;
            font-weight: 600;
        }
        tr:hover {
            background: #f8f9fa;
        }
        .z-score {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: bold;
        }
        .z-score.positive {
            background: #d4edda;
            color: #155724;
        }
        .z-score.negative {
            background: #f8d7da;
            color: #721c24;
        }
        .z-score.neutral {
            background: #e2e3e5;
            color: #383d41;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 Performance Evaluation Report</h1>
            <div class="timestamp">Generated: ${timestamp}</div>
        </header>
        
        <div class="summary">
            <div class="summary-card">
                <h3>Solutions Evaluated</h3>
                <div class="value">${results.length}</div>
            </div>
            <div class="summary-card">
                <h3>Average Score</h3>
                <div class="value">${(results.reduce((sum, r) => sum + r.finalScore, 0) / results.length).toFixed(1)}</div>
            </div>
            <div class="summary-card">
                <h3>Top Performer</h3>
                <div class="value">${sortedResults[0]?.solutionName || 'N/A'}</div>
            </div>
            <div class="summary-card">
                <h3>Cache Hit Rate</h3>
                <div class="value">${((results.filter(r => r.cached).length / results.length) * 100).toFixed(1)}%</div>
            </div>
        </div>
        
        <h2 style="margin: 30px 0 20px 0;">📊 Detailed Results</h2>
        
        ${sortedResults.map(result => generateSolutionCard(result)).join('\n')}
        
        <h2 style="margin: 40px 0 20px 0;">📈 Comparison Table</h2>
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Solution</th>
                    <th>Final Score</th>
                    <th>Correctness</th>
                    <th>Performance</th>
                    <th>Code Quality</th>
                    <th>Documentation</th>
                    <th>Duration (ms)</th>
                    <th>Memory (MB)</th>
                    <th>CPU %</th>
                </tr>
            </thead>
            <tbody>
                ${sortedResults.map((result, idx) => generateTableRow(result, idx + 1)).join('\n')}
            </tbody>
        </table>
    </div>
</body>
</html>`;
  
  if (outputPath) {
    writeFileSync(outputPath, html, 'utf-8');
  }
  
  return html;
}

/**
 * Generate solution card HTML
 */
function generateSolutionCard(result) {
  const bottlenecksHtml = result.bottlenecks && result.bottlenecks.length > 0
    ? `<div class="bottlenecks">
         <h4>⚠️ Performance Bottlenecks</h4>
         ${result.bottlenecks.map(b => `<div class="bottleneck-item">${b}</div>`).join('')}
       </div>`
    : `<div class="bottlenecks no-bottlenecks">✓ No bottlenecks detected</div>`;
  
  const normalized = result.normalizedMetrics || {};
  const durationNorm = normalized.duration || {};
  const memoryNorm = normalized.memoryUsage || {};
  
  return `
        <div class="solution-card">
            <div class="solution-header">
                <div class="solution-name">${result.solutionName}</div>
                <div class="score-badge">${result.finalScore.toFixed(2)} / 100</div>
            </div>
            
            <div class="breakdown">
                <div class="breakdown-item">
                    <div class="breakdown-label">Correctness</div>
                    <div class="breakdown-value">${result.breakdown.correctness}%</div>
                </div>
                <div class="breakdown-item">
                    <div class="breakdown-label">Performance</div>
                    <div class="breakdown-value">${result.breakdown.performance}%</div>
                </div>
                <div class="breakdown-item">
                    <div class="breakdown-label">Code Quality</div>
                    <div class="breakdown-value">${result.breakdown.codeQuality}%</div>
                </div>
                <div class="breakdown-item">
                    <div class="breakdown-label">Documentation</div>
                    <div class="breakdown-value">${result.breakdown.documentation}%</div>
                </div>
            </div>
            
            <div class="metrics-grid">
                <div class="metric">
                    <div class="metric-label">Duration</div>
                    <div class="metric-value">${(result.aggregateMetrics.duration || 0).toFixed(0)} ms</div>
                    ${durationNorm.zScore !== undefined ? `<div class="z-score ${getZScoreClass(durationNorm.zScore)}">Z: ${durationNorm.zScore.toFixed(2)}</div>` : ''}
                </div>
                <div class="metric">
                    <div class="metric-label">Memory Usage</div>
                    <div class="metric-value">${((result.aggregateMetrics.memoryUsage || 0) / 1024 / 1024).toFixed(2)} MB</div>
                    ${memoryNorm.zScore !== undefined ? `<div class="z-score ${getZScoreClass(memoryNorm.zScore)}">Z: ${memoryNorm.zScore.toFixed(2)}</div>` : ''}
                </div>
                <div class="metric">
                    <div class="metric-label">CPU Usage</div>
                    <div class="metric-value">${(result.aggregateMetrics.cpuUsage || 0).toFixed(1)}%</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Peak Memory</div>
                    <div class="metric-value">${((result.aggregateMetrics.peakMemory || 0) / 1024 / 1024).toFixed(2)} MB</div>
                </div>
            </div>
            
            ${bottlenecksHtml}
        </div>`;
}

/**
 * Generate table row HTML
 */
function generateTableRow(result, rank) {
  return `
                <tr>
                    <td>${rank}</td>
                    <td><strong>${result.solutionName}</strong></td>
                    <td><strong>${result.finalScore.toFixed(2)}</strong></td>
                    <td>${result.breakdown.correctness}%</td>
                    <td>${result.breakdown.performance}%</td>
                    <td>${result.breakdown.codeQuality}%</td>
                    <td>${result.breakdown.documentation}%</td>
                    <td>${(result.aggregateMetrics.duration || 0).toFixed(0)}</td>
                    <td>${((result.aggregateMetrics.memoryUsage || 0) / 1024 / 1024).toFixed(2)}</td>
                    <td>${(result.aggregateMetrics.cpuUsage || 0).toFixed(1)}</td>
                </tr>`;
}

/**
 * Get CSS class for z-score
 */
function getZScoreClass(zScore) {
  if (zScore > 1) return 'positive';
  if (zScore < -1) return 'negative';
  return 'neutral';
}
