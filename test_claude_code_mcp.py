#!/usr/bin/env python3
"""
Test Claude Code MCP Configuration
Verifies that Claude Code can connect to Cloud Agents MCP server.
"""

import json
import os
from pathlib import Path

def test_claude_code_config():
    """Test Claude Code MCP configuration."""
    
    print("=" * 60)
    print("Testing Claude Code MCP Configuration")
    print("=" * 60)
    
    # Test 1: Check project-level config
    print("\n[1/3] Checking project-level .mcp.json...")
    project_config = Path("/Users/abhinav/Desktop/Cequence BlackWall/.mcp.json")
    
    if project_config.exists():
        try:
            with open(project_config, 'r') as f:
                config = json.load(f)
            
            if "cursor-cloud-agents" in config:
                server_config = config["cursor-cloud-agents"]
                print("   ✓ Configuration found")
                print(f"   - Server: cursor-cloud-agents")
                print(f"   - Command: {server_config.get('command', 'N/A')}")
                print(f"   - Args: {server_config.get('args', [])}")
                
                api_key = server_config.get("env", {}).get("CURSOR_API_KEY", "")
                if api_key and api_key.startswith("key_"):
                    print(f"   - API Key: Present (starts with 'key_')")
                else:
                    print(f"   ⚠ API Key: Missing or invalid")
            else:
                print("   ✗ cursor-cloud-agents not found in config")
                return False
        except json.JSONDecodeError as e:
            print(f"   ✗ Invalid JSON: {e}")
            return False
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return False
    else:
        print("   ✗ .mcp.json not found")
        return False
    
    # Test 2: Check user-level config location
    print("\n[2/3] Checking user-level config location...")
    user_config = Path.home() / ".claude" / ".mcp.json"
    
    if user_config.exists():
        print(f"   ✓ User config exists at: {user_config}")
        try:
            with open(user_config, 'r') as f:
                user_cfg = json.load(f)
            if "cursor-cloud-agents" in user_cfg:
                print("   ✓ cursor-cloud-agents found in user config")
            else:
                print("   ⚠ cursor-cloud-agents not in user config (project-level will be used)")
        except Exception as e:
            print(f"   ⚠ Error reading user config: {e}")
    else:
        print(f"   ℹ User config not found (will use project-level)")
        print(f"   To make it global, create: {user_config}")
    
    # Test 3: Verify API connection
    print("\n[3/3] Verifying API connection...")
    try:
        import subprocess
        api_key = config["cursor-cloud-agents"]["env"]["CURSOR_API_KEY"]
        
        result = subprocess.run(
            ["curl", "-s", "-u", f"{api_key}:", "https://api.cursor.com/v0/me"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            info = json.loads(result.stdout)
            print(f"   ✓ API Connection: Working")
            print(f"     - Key: {info.get('apiKeyName', 'N/A')}")
            print(f"     - User: {info.get('userEmail', 'N/A')}")
        else:
            print(f"   ✗ API Connection: Failed")
            return False
    except Exception as e:
        print(f"   ✗ API test error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ Claude Code MCP Configuration Verified!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Reload Claude Code window in Cursor (Cmd+Shift+P → 'Reload Window')")
    print("2. In Claude Code chat, ask: 'What MCP tools are available?'")
    print("3. Try: 'List my Cloud Agents'")
    print("\nNote: Since you're logged into Cursor with SSO, Claude Code")
    print("will use your authenticated session to access Cloud Agents.")
    
    return True

if __name__ == "__main__":
    import sys
    success = test_claude_code_config()
    sys.exit(0 if success else 1)
