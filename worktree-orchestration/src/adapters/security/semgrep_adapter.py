"""
Semgrep security scanning adapter.
"""
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional
from ..base import SecurityAdapter


class SemgrepAdapter(SecurityAdapter):
    """
    Adapter for Semgrep security scanning tool.
    
    Requires semgrep CLI to be installed and available in PATH.
    """
    
    def __init__(self):
        """Initialize Semgrep adapter."""
        self._available = None  # Cache availability check
    
    def is_available(self) -> bool:
        """
        Check if semgrep CLI is available.
        
        Returns:
            True if semgrep is installed and accessible
        """
        if self._available is not None:
            return self._available
        
        try:
            result = subprocess.run(
                ["semgrep", "--version"],
                capture_output=True,
                timeout=5
            )
            self._available = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            self._available = False
        
        return self._available
    
    def scan(self, worktree_path: Path) -> Dict[str, Any]:
        """
        Scan worktree using Semgrep.
        
        Args:
            worktree_path: Path to worktree directory
            
        Returns:
            Dictionary with scan results
        """
        if not self.is_available():
            return {
                "vulnerability_count": 0,
                "vulnerabilities": [],
                "scan_successful": False,
                "error": "Semgrep not available",
                "adapter": "semgrep"
            }
        
        try:
            # Run semgrep scan
            # Using --json for structured output
            result = subprocess.run(
                ["semgrep", "--json", "--config", "auto", str(worktree_path)],
                capture_output=True,
                text=True,
                timeout=60,  # 60 second timeout
                cwd=str(worktree_path)
            )
            
            if result.returncode != 0 and result.returncode != 1:
                # Semgrep returns 1 when findings are found, 0 when none
                # Other codes indicate errors
                return {
                    "vulnerability_count": 0,
                    "vulnerabilities": [],
                    "scan_successful": False,
                    "error": f"Semgrep execution failed: {result.stderr}",
                    "adapter": "semgrep"
                }
            
            # Parse JSON output
            try:
                semgrep_output = json.loads(result.stdout)
                findings = semgrep_output.get("results", [])
                
                return {
                    "vulnerability_count": len(findings),
                    "vulnerabilities": findings,
                    "scan_successful": True,
                    "error": None,
                    "adapter": "semgrep"
                }
            except json.JSONDecodeError:
                return {
                    "vulnerability_count": 0,
                    "vulnerabilities": [],
                    "scan_successful": False,
                    "error": "Failed to parse Semgrep JSON output",
                    "adapter": "semgrep"
                }
        
        except subprocess.TimeoutExpired:
            return {
                "vulnerability_count": 0,
                "vulnerabilities": [],
                "scan_successful": False,
                "error": "Semgrep scan timed out",
                "adapter": "semgrep"
            }
        except Exception as e:
            return {
                "vulnerability_count": 0,
                "vulnerabilities": [],
                "scan_successful": False,
                "error": f"Semgrep scan failed: {str(e)}",
                "adapter": "semgrep"
            }
    
    def name(self) -> str:
        """Return name of this adapter."""
        return "Semgrep"
