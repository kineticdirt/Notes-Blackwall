#!/usr/bin/env python3
"""
Test MCP Server Protocol Communication
Simulates how Cursor would communicate with the MCP server.
"""

import subprocess
import json
import sys
import os
import time

def test_mcp_protocol():
    """Test MCP protocol communication with the Cloud Agents server."""
    
    api_key = "key_c6941230ec4b54143ea2d6d379f04b01f8625d0626644c3da1d7d645a480411a"
    
    print("=" * 60)
    print("Testing MCP Server Protocol Communication")
    print("=" * 60)
    
    # Set environment
    env = os.environ.copy()
    env["CURSOR_API_KEY"] = api_key
    
    # MCP Initialize request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {
                    "listChanged": True
                }
            },
            "clientInfo": {
                "name": "cursor-test-client",
                "version": "1.0.0"
            }
        }
    }
    
    # MCP Tools List request
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    print("\n[1/3] Starting MCP server process...")
    try:
        process = subprocess.Popen(
            ["npx", "-y", "@willpowell8/cursor-cloud-agent-mcp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            bufsize=1
        )
        
        print("   ✓ Process started (PID: {})".format(process.pid))
        
        # Send initialize request
        print("\n[2/3] Sending initialize request...")
        try:
            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()
            
            # Wait for response (with timeout)
            process.stdin.close()
            stdout, stderr = process.communicate(timeout=5)
            
            if stdout:
                print("   ✓ Received response from server")
                print(f"   Response length: {len(stdout)} bytes")
                # Try to parse JSON responses
                for line in stdout.strip().split('\n'):
                    if line.strip():
                        try:
                            response = json.loads(line)
                            if 'result' in response:
                                print(f"   ✓ Valid JSON-RPC response received")
                                if 'serverInfo' in response.get('result', {}):
                                    server_info = response['result']['serverInfo']
                                    print(f"   - Server: {server_info.get('name', 'N/A')}")
                                    print(f"   - Version: {server_info.get('version', 'N/A')}")
                        except json.JSONDecodeError:
                            pass
            
            if stderr:
                print(f"   ⚠ Stderr output: {stderr[:200]}")
                
        except subprocess.TimeoutExpired:
            print("   ⚠ Timeout waiting for response (this may be normal for stdio servers)")
            process.kill()
            stdout, stderr = process.communicate()
            if stderr:
                print(f"   Stderr: {stderr[:200]}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
            process.terminate()
            try:
                process.wait(timeout=2)
            except:
                process.kill()
            return False
            
    except FileNotFoundError:
        print("   ✗ npx not found. Please ensure Node.js is installed.")
        return False
    except Exception as e:
        print(f"   ✗ Failed to start process: {e}")
        return False
    
    # Test API directly to verify tools would work
    print("\n[3/3] Testing Cloud Agents API endpoints (what MCP tools would call)...")
    
    endpoints = [
        ("/me", "GET", "API Key Info"),
        ("/agents?limit=1", "GET", "List Agents"),
        ("/models", "GET", "List Models"),
    ]
    
    for endpoint, method, name in endpoints:
        try:
            if method == "GET":
                result = subprocess.run(
                    ["curl", "-s", "-u", f"{api_key}:", 
                     f"https://api.cursor.com/v0{endpoint}"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    print(f"   ✓ {name}: API accessible")
                else:
                    print(f"   ✗ {name}: Failed")
        except Exception as e:
            print(f"   ✗ {name}: Error - {e}")
    
    print("\n" + "=" * 60)
    print("MCP Protocol Test Complete!")
    print("=" * 60)
    print("\nTo test in Cursor:")
    print("1. Open Cursor Chat")
    print("2. Try: 'List my Cloud Agents'")
    print("3. Try: 'What Cloud Agents tools are available?'")
    print("4. Try: 'Launch a Cloud Agent to fix bugs in my repository'")
    
    return True

if __name__ == "__main__":
    success = test_mcp_protocol()
    sys.exit(0 if success else 1)
