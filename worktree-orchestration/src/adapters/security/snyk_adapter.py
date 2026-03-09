"""
Snyk security scanning adapter.
"""
import subprocess
import json
from pathlib import Path
from typing import Dict, Any
from ..base import SecurityAdapter


class SnykAdapter(SecurityAdapter):
    """
    Adapter for Snyk security scanning tool.
    
    Requires snyk CLI to be installed and authenticated.
    """
    
    def __init__(self):
        """Initialize Snyk adapter."""
        self._available = None  # Cache availability check
    
    def is_available(self) -> bool:
        """
        Check if snyk CLI is available and authenticated.
        
        Returns:
            True if snyk is installed and authenticated
        """
        if self._available is not None:
            return self._available
        
        try:
            # Check if snyk is installed
            version_result = subprocess.run(
                ["snyk", "--version"],
                capture_output=True,
                timeout=5
            )
            
            if version_result.returncode != 0:
                self._available = False
                return False
            
            # Check if authenticated (snyk auth status)
            auth_result = subprocess.run(
                ["snyk", "auth", "status"],
                capture_output=True,
                timeout=5
            )
            
            # Snyk auth status returns 0 if authenticated
            self._available = auth_result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            self._available = False
        
        return self._available
    
    def scan(self, worktree_path: Path) -> Dict[str, Any]:
        """
        Scan worktree using Snyk.
        
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
                "error": "Snyk not available or not authenticated",
                "adapter": "snyk"
            }
        
        try:
            # Run snyk test
            # Using --json for structured output
            result = subprocess.run(
                ["snyk", "test", "--json"],
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
                cwd=str(worktree_path)
            )
            
            # Snyk returns non-zero when vulnerabilities found
            # Parse output regardless of exit code
            try:
                snyk_output = json.loads(result.stdout)
                
                # Extract vulnerabilities
                vulnerabilities = snyk_output.get("vulnerabilities", [])
                
                return {
                    "vulnerability_count": len(vulnerabilities),
                    "vulnerabilities": vulnerabilities,
                    "scan_successful": True,
                    "error": None,
                    "adapter": "snyk"
                }
            except json.JSONDecodeError:
                # If JSON parsing fails, check stderr for errors
                error_msg = result.stderr or "Failed to parse Snyk JSON output"
                return {
                    "vulnerability_count": 0,
                    "vulnerabilities": [],
                    "scan_successful": False,
                    "error": error_msg,
                    "adapter": "snyk"
                }
        
        except subprocess.TimeoutExpired:
            return {
                "vulnerability_count": 0,
                "vulnerabilities": [],
                "scan_successful": False,
                "error": "Snyk scan timed out",
                "adapter": "snyk"
            }
        except Exception as e:
            return {
                "vulnerability_count": 0,
                "vulnerabilities": [],
                "scan_successful": False,
                "error": f"Snyk scan failed: {str(e)}",
                "adapter": "snyk"
            }
    
    def name(self) -> str:
        """Return name of this adapter."""
        return "Snyk"
