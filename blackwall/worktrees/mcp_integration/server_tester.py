"""
MCP Server Tester: Comprehensive testing for MCP servers.
Tests connectivity, tools, resources, and functionality.
"""

import json
import subprocess
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class TestResult:
    """Result of a test."""
    test_name: str
    passed: bool
    message: str
    details: Optional[Dict] = None


class MCPServerTester:
    """
    Comprehensive tester for MCP servers.
    Tests connectivity, tools, resources, and functionality.
    """
    
    def __init__(self, server_config: Dict):
        """
        Initialize MCP server tester.
        
        Args:
            server_config: Server configuration (command, args, env)
        """
        self.server_config = server_config
        self.server_process: Optional[subprocess.Popen] = None
        self.test_results: List[TestResult] = []
    
    def start_server(self, timeout: int = 5) -> bool:
        """
        Start the MCP server process.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            True if server started successfully
        """
        try:
            command = self.server_config.get("command", "")
            args = self.server_config.get("args", [])
            env = self.server_config.get("env", {})
            
            full_command = [command] + args
            
            self.server_process = subprocess.Popen(
                full_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True
            )
            
            # Wait a bit for server to start
            time.sleep(1)
            
            # Check if process is still running
            if self.server_process.poll() is None:
                return True
            else:
                stderr = self.server_process.stderr.read() if self.server_process.stderr else ""
                return False
                
        except Exception as e:
            return False
    
    def stop_server(self):
        """Stop the MCP server process."""
        if self.server_process:
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
    
    def test_connection(self) -> TestResult:
        """Test server connection."""
        try:
            started = self.start_server()
            if started:
                return TestResult(
                    test_name="Connection",
                    passed=True,
                    message="Server started successfully"
                )
            else:
                return TestResult(
                    test_name="Connection",
                    passed=False,
                    message="Server failed to start"
                )
        except Exception as e:
            return TestResult(
                test_name="Connection",
                passed=False,
                message=f"Connection error: {e}"
            )
    
    def test_toolbox_server(self, toolbox_url: str = "http://127.0.0.1:5000") -> List[TestResult]:
        """
        Test MCP Toolbox server.
        
        Args:
            toolbox_url: Toolbox server URL
            
        Returns:
            List of test results
        """
        results = []
        
        # Test 1: Server is running
        try:
            response = requests.get(f"{toolbox_url}/health", timeout=2)
            results.append(TestResult(
                test_name="Toolbox Health",
                passed=response.status_code == 200,
                message=f"Health check: {response.status_code}"
            ))
        except requests.exceptions.RequestException:
            results.append(TestResult(
                test_name="Toolbox Health",
                passed=False,
                message="Toolbox server not responding"
            ))
        
        # Test 2: Tools endpoint
        try:
            response = requests.get(f"{toolbox_url}/tools", timeout=2)
            if response.status_code == 200:
                tools = response.json()
                results.append(TestResult(
                    test_name="Toolbox Tools",
                    passed=True,
                    message=f"Found {len(tools)} tools",
                    details={"tools": tools}
                ))
            else:
                results.append(TestResult(
                    test_name="Toolbox Tools",
                    passed=False,
                    message=f"Tools endpoint returned {response.status_code}"
                ))
        except requests.exceptions.RequestException as e:
            results.append(TestResult(
                test_name="Toolbox Tools",
                passed=False,
                message=f"Tools endpoint error: {e}"
            ))
        
        return results
    
    def test_mcp_ui(self, ui_path: Path) -> List[TestResult]:
        """
        Test MCP UI integration.
        
        Args:
            ui_path: Path to UI markdown files
            
        Returns:
            List of test results
        """
        results = []
        
        # Test 1: UI path exists
        if ui_path.exists():
            results.append(TestResult(
                test_name="UI Path Exists",
                passed=True,
                message=f"UI path exists: {ui_path}"
            ))
        else:
            results.append(TestResult(
                test_name="UI Path Exists",
                passed=False,
                message=f"UI path not found: {ui_path}"
            ))
        
        # Test 2: Load UI components
        try:
            from ..mcp_ui import MCPUILoader
            loader = MCPUILoader(ui_path=ui_path)
            component_count = len(loader.components)
            
            results.append(TestResult(
                test_name="UI Components Load",
                passed=component_count > 0,
                message=f"Loaded {component_count} components",
                details={"components": list(loader.components.keys())}
            ))
        except Exception as e:
            results.append(TestResult(
                test_name="UI Components Load",
                passed=False,
                message=f"Failed to load components: {e}"
            ))
        
        return results
    
    def run_all_tests(self, toolbox_url: Optional[str] = None,
                     ui_path: Optional[Path] = None) -> List[TestResult]:
        """
        Run all tests.
        
        Args:
            toolbox_url: Toolbox server URL
            ui_path: Path to UI files
            
        Returns:
            List of all test results
        """
        self.test_results = []
        
        # Test connection
        conn_result = self.test_connection()
        self.test_results.append(conn_result)
        
        # Test Toolbox if URL provided
        if toolbox_url:
            toolbox_results = self.test_toolbox_server(toolbox_url)
            self.test_results.extend(toolbox_results)
        
        # Test MCP UI if path provided
        if ui_path:
            ui_results = self.test_mcp_ui(ui_path)
            self.test_results.extend(ui_results)
        
        # Stop server
        self.stop_server()
        
        return self.test_results
    
    def get_summary(self) -> Dict:
        """Get test summary."""
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.passed)
        failed = total - passed
        
        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "success_rate": passed / total if total > 0 else 0,
            "results": [
                {
                    "test": r.test_name,
                    "passed": r.passed,
                    "message": r.message
                }
                for r in self.test_results
            ]
        }
