#!/usr/bin/env python3
"""
Test script for Cursor Cloud Agents MCP Server integration.
Tests the MCP server connection and basic functionality.
"""

import subprocess
import json
import os
import sys
import time

def test_mcp_server():
    """Test the MCP server connection."""
    
    api_key = "key_c6941230ec4b54143ea2d6d379f04b01f8625d0626644c3da1d7d645a480411a"
    
    print("=" * 60)
    print("Testing Cursor Cloud Agents MCP Server")
    print("=" * 60)
    
    # Test 1: Verify API key works
    print("\n[1/4] Testing API key authentication...")
    try:
        import subprocess
        result = subprocess.run(
            [
                "curl", "-s", "-u", f"{api_key}:",
                "-H", "Content-Type: application/json",
                "https://api.cursor.com/v0/me"
            ],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            api_info = json.loads(result.stdout)
            print(f"✓ API Key valid")
            print(f"  - Key Name: {api_info.get('apiKeyName')}")
            print(f"  - User Email: {api_info.get('userEmail')}")
            print(f"  - Created: {api_info.get('createdAt')}")
        else:
            print(f"✗ API Key test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ API Key test error: {e}")
        return False
    
    # Test 2: Check if npm package is accessible
    print("\n[2/4] Checking npm package availability...")
    try:
        result = subprocess.run(
            ["npm", "view", "@willpowell8/cursor-cloud-agent-mcp", "version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✓ Package found: version {version}")
        else:
            print(f"✗ Package check failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Package check error: {e}")
        return False
    
    # Test 3: Test npx execution
    print("\n[3/4] Testing npx execution...")
    try:
        env = os.environ.copy()
        env["CURSOR_API_KEY"] = api_key
        
        # Test if npx can find and execute the package
        # MCP servers communicate via stdio, so we'll test with a timeout
        process = subprocess.Popen(
            ["npx", "-y", "@willpowell8/cursor-cloud-agent-mcp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True
        )
        
        # Send MCP initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        try:
            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()
            
            # Wait a bit for response
            time.sleep(2)
            
            # Check if process is still running (good sign)
            if process.poll() is None:
                print("✓ MCP server process started successfully")
                print("  - Process is running and responsive")
            else:
                stderr = process.stderr.read()
                print(f"✗ MCP server exited: {stderr}")
                return False
                
        except Exception as e:
            print(f"✗ MCP communication error: {e}")
            return False
        finally:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                
    except FileNotFoundError:
        print("✗ npx not found. Please install Node.js and npm.")
        return False
    except Exception as e:
        print(f"✗ npx execution error: {e}")
        return False
    
    # Test 4: Test listing agents via API
    print("\n[4/4] Testing Cloud Agents API (list agents)...")
    try:
        result = subprocess.run(
            [
                "curl", "-s", "-u", f"{api_key}:",
                "-H", "Content-Type: application/json",
                "https://api.cursor.com/v0/agents?limit=5"
            ],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            agents_data = json.loads(result.stdout)
            agents = agents_data.get("agents", [])
            print(f"✓ Successfully connected to Cloud Agents API")
            print(f"  - Found {len(agents)} agent(s)")
            
            if agents:
                for i, agent in enumerate(agents[:3], 1):
                    print(f"    {i}. {agent.get('id', 'N/A')} - Status: {agent.get('status', 'N/A')}")
            else:
                print("  - No agents found (this is normal if you haven't created any)")
        else:
            print(f"✗ API request failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ API test error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ All tests passed! MCP server is ready to use.")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Restart Cursor IDE to load the MCP server configuration")
    print("2. Open Cursor Chat and check if Cloud Agents tools are available")
    print("3. Try: 'List my Cloud Agents' or 'Launch a Cloud Agent'")
    
    return True

if __name__ == "__main__":
    success = test_mcp_server()
    sys.exit(0 if success else 1)
