#!/usr/bin/env python3
"""
Test MCP Toolbox Server
Comprehensive testing of Toolbox server functionality.
"""

import requests
import time
import subprocess
import sys
from pathlib import Path


def check_server_running(url: str = "http://127.0.0.1:5000", timeout: int = 2) -> bool:
    """Check if Toolbox server is running."""
    try:
        response = requests.get(f"{url}/health", timeout=timeout)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def test_toolbox_endpoints(url: str = "http://127.0.0.1:5000"):
    """Test Toolbox server endpoints."""
    print("=" * 60)
    print("TESTING TOOLBOX SERVER ENDPOINTS")
    print("=" * 60)
    
    tests = []
    
    # Test 1: Health check
    print("\n1. Health Check...")
    try:
        response = requests.get(f"{url}/health", timeout=2)
        passed = response.status_code == 200
        tests.append(("Health Check", passed, f"Status: {response.status_code}"))
        print(f"   {'✓' if passed else '✗'} Status: {response.status_code}")
    except Exception as e:
        tests.append(("Health Check", False, str(e)))
        print(f"   ✗ Error: {e}")
    
    # Test 2: Tools endpoint
    print("\n2. Tools Endpoint...")
    try:
        response = requests.get(f"{url}/tools", timeout=2)
        if response.status_code == 200:
            tools = response.json()
            tests.append(("Tools Endpoint", True, f"Found {len(tools)} tools"))
            print(f"   ✓ Found {len(tools)} tools")
            for tool in tools[:5]:
                print(f"     - {tool.get('name', 'unknown')}")
        else:
            tests.append(("Tools Endpoint", False, f"Status: {response.status_code}"))
            print(f"   ✗ Status: {response.status_code}")
    except Exception as e:
        tests.append(("Tools Endpoint", False, str(e)))
        print(f"   ✗ Error: {e}")
    
    # Test 3: Toolsets endpoint
    print("\n3. Toolsets Endpoint...")
    try:
        response = requests.get(f"{url}/toolsets", timeout=2)
        if response.status_code == 200:
            toolsets = response.json()
            tests.append(("Toolsets Endpoint", True, f"Found {len(toolsets)} toolsets"))
            print(f"   ✓ Found {len(toolsets)} toolsets")
            for toolset in toolsets[:5]:
                print(f"     - {toolset.get('name', 'unknown')}")
        else:
            tests.append(("Toolsets Endpoint", False, f"Status: {response.status_code}"))
            print(f"   ✗ Status: {response.status_code}")
    except Exception as e:
        tests.append(("Toolsets Endpoint", False, str(e)))
        print(f"   ✗ Error: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, p, _ in tests if p)
    total = len(tests)
    
    for test_name, passed, message in tests:
        status = "✓" if passed else "✗"
        print(f"  {status} {test_name}: {message}")
    
    print(f"\nSuccess Rate: {passed}/{total} ({passed/total*100:.1f}%)")
    
    return passed == total


def main():
    """Main test function."""
    print("\n" + "=" * 60)
    print("MCP TOOLBOX SERVER TEST")
    print("=" * 60)
    
    url = "http://127.0.0.1:5000"
    
    # Check if server is running
    print(f"\nChecking if server is running at {url}...")
    if not check_server_running(url):
        print("✗ Server is not running")
        print("\nTo start the server:")
        print("  bash toolbox_test/start_toolbox.sh")
        print("  or")
        print("  npx @toolbox-sdk/server --tools-file toolbox_test/tools_fixed.yaml")
        return False
    
    print("✓ Server is running")
    
    # Run tests
    success = test_toolbox_endpoints(url)
    
    if success:
        print("\n✓ All tests passed!")
    else:
        print("\n⚠ Some tests failed")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
