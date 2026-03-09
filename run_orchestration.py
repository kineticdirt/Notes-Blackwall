#!/usr/bin/env python3
"""
Main orchestration script - coordinates worktrees, tests, scoring, and reporting
"""
import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from worktree_manager import WorktreeManager


class Orchestrator:
    def __init__(self, spec_file="worktree-spec.json"):
        self.manager = WorktreeManager(spec_file)
        with open(spec_file, 'r') as f:
            self.spec = json.load(f)
        self.results = []
        
    def setup(self):
        """Create worktrees and directories"""
        print("=== Setting up worktrees ===\n")
        self.manager.create_worktrees()
        print()
        
    def run_tests(self):
        """Run test harness on all worktrees"""
        print("=== Running test harness ===\n")
        worktrees = self.manager.list_worktrees()
        test_harness = self.spec.get("test_harness", {})
        harness_path = Path(test_harness.get("path", "test_harness"))
        runner = harness_path / test_harness.get("runner", "run_tests.sh")
        
        if not runner.exists():
            print(f"❌ Test harness not found: {runner}")
            return []
        
        # Make runner executable
        os.chmod(runner, 0o755)
        
        results = []
        for wt in worktrees:
            wt_path = self.manager.get_worktree_path(wt["id"])
            print(f"Testing {wt['name']}...")
            
            try:
                # Run test harness
                result = subprocess.run(
                    [str(runner), str(wt_path)],
                    capture_output=True,
                    text=True,
                    timeout=test_harness.get("timeout", 30)
                )
                
                print(result.stdout)
                if result.stderr:
                    print(result.stderr, file=sys.stderr)
                
                # Load test result JSON
                result_file = wt_path / "test_result.json"
                if result_file.exists():
                    with open(result_file, 'r') as f:
                        test_result = json.load(f)
                        test_result["worktree_id"] = wt["id"]
                        test_result["worktree_name"] = wt["name"]
                        results.append(test_result)
                        print(f"✓ {wt['name']}: Score {test_result.get('score', 0)}/{test_result.get('max_score', 100)}\n")
                else:
                    print(f"⚠ {wt['name']}: No result file generated\n")
                    
            except subprocess.TimeoutExpired:
                print(f"❌ {wt['name']}: Test timed out\n")
            except Exception as e:
                print(f"❌ {wt['name']}: Error - {e}\n")
        
        self.results = results
        return results
    
    def compute_scores(self):
        """Compute final scores based on spec weights"""
        print("=== Computing scores ===\n")
        scoring = self.spec.get("scoring", {})
        weights = scoring.get("weights", {})
        
        for result in self.results:
            # Map test results to scoring categories
            base_score = result.get("score", 0)
            max_score = result.get("max_score", 100)
            
            # Normalize to 0-1
            normalized = base_score / max_score if max_score > 0 else 0
            
            # Apply weights (simplified - in real system, compute per category)
            correctness = normalized * weights.get("correctness", 0.5)
            code_quality = (1 if result.get("syntax_valid", False) else 0) * weights.get("code_quality", 0.2)
            documentation = (1 if result.get("has_readme", False) else 0) * weights.get("documentation", 0.1)
            performance = 0.0  # Placeholder
            
            final_score = (correctness + code_quality + documentation + performance) * scoring.get("max_score", 100)
            
            result["final_score"] = round(final_score, 2)
            result["breakdown"] = {
                "correctness": round(correctness * 100, 2),
                "code_quality": round(code_quality * 100, 2),
                "documentation": round(documentation * 100, 2),
                "performance": round(performance * 100, 2)
            }
            
            print(f"{result['worktree_name']}: {result['final_score']:.2f}/100")
            print(f"  Breakdown: {result['breakdown']}\n")
        
        return self.results
    
    def generate_report(self):
        """Generate HTML report"""
        print("=== Generating report ===\n")
        report_config = self.spec.get("report", {})
        output_file = report_config.get("output", "report.html")
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Worktree Evaluation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
        h1 {{ color: #333; }}
        .worktree {{ border: 1px solid #ddd; margin: 15px 0; padding: 15px; border-radius: 5px; }}
        .score {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
        .breakdown {{ margin-top: 10px; }}
        .metric {{ display: inline-block; margin: 5px 10px; padding: 5px 10px; background: #ecf0f1; border-radius: 3px; }}
        .timestamp {{ color: #7f8c8d; font-size: 12px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #34495e; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Worktree Evaluation Report</h1>
        <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <table>
            <thead>
                <tr>
                    <th>Worktree</th>
                    <th>Final Score</th>
                    <th>Files</th>
                    <th>Python Files</th>
                    <th>Has README</th>
                    <th>Syntax Valid</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for result in sorted(self.results, key=lambda x: x.get("final_score", 0), reverse=True):
            html += f"""
                <tr>
                    <td><strong>{result['worktree_name']}</strong></td>
                    <td class="score">{result.get('final_score', 0):.2f}</td>
                    <td>{result.get('file_count', 0)}</td>
                    <td>{result.get('python_files', 0)}</td>
                    <td>{'✓' if result.get('has_readme') else '✗'}</td>
                    <td>{'✓' if result.get('syntax_valid') else '✗'}</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
        
        <h2>Detailed Results</h2>
"""
        
        for result in sorted(self.results, key=lambda x: x.get("final_score", 0), reverse=True):
            breakdown = result.get("breakdown", {})
            html += f"""
        <div class="worktree">
            <h3>{result['worktree_name']} (ID: {result['worktree_id']})</h3>
            <div class="score">Score: {result.get('final_score', 0):.2f}/100</div>
            <div class="breakdown">
                <span class="metric">Correctness: {breakdown.get('correctness', 0):.1f}%</span>
                <span class="metric">Code Quality: {breakdown.get('code_quality', 0):.1f}%</span>
                <span class="metric">Documentation: {breakdown.get('documentation', 0):.1f}%</span>
                <span class="metric">Performance: {breakdown.get('performance', 0):.1f}%</span>
            </div>
            <p><strong>Path:</strong> {result.get('worktree', 'N/A')}</p>
        </div>
"""
        
        html += """
    </div>
</body>
</html>
"""
        
        with open(output_file, 'w') as f:
            f.write(html)
        
        print(f"✓ Report generated: {output_file}")
        return output_file
    
    def run(self):
        """Run full orchestration"""
        self.setup()
        self.run_tests()
        if self.results:
            self.compute_scores()
            self.generate_report()
            print("\n=== Orchestration complete ===")
        else:
            print("\n⚠ No results to process")


if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.run()
