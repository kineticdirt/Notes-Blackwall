#!/usr/bin/env python3
"""
Verify Cursor MCP Configuration
Checks all components needed for Cloud Agents MCP integration.
"""

import json
import subprocess
import os
import sys
from pathlib import Path

def check_cursor_settings():
    """Check if Cursor settings.json has correct MCP configuration."""
    print("\n[1/5] Checking Cursor Settings Configuration...")
    
    settings_path = Path.home() / "Library/Application Support/Cursor/User/settings.json"
    
    if not settings_path.exists():
        print(f"   ✗ Settings file not found at: {settings_path}")
        return False
    
    try:
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        
        mcp_servers = settings.get("mcpServers", {})
        
        if "cursor-cloud-agents" not in mcp_servers:
            print("   ✗ cursor-cloud-agents not found in mcpServers")
            return False
        
        config = mcp_servers["cursor-cloud-agents"]
        
        # Check required fields
        checks = [
            ("command", config.get("command") == "npx", "command should be 'npx'"),
            ("args", "@willpowell8/cursor-cloud-agent-mcp" in str(config.get("args", [])), "args should include package name"),
            ("env", "CURSOR_API_KEY" in config.get("env", {}), "CURSOR_API_KEY should be in env"),
        ]
        
        all_good = True
        for name, check, msg in checks:
            if check:
                print(f"   ✓ {name}: OK")
            else:
                print(f"   ✗ {name}: {msg}")
                all_good = False
        
        api_key = config.get("env", {}).get("CURSOR_API_KEY", "")
        if api_key and api_key.startswith("key_"):
            print(f"   ✓ API Key: Present (starts with 'key_')")
        else:
            print(f"   ⚠ API Key: May be missing or invalid format")
            all_good = False
        
        return all_good
        
    except json.JSONDecodeError as e:
        print(f"   ✗ Invalid JSON in settings file: {e}")
        return False
    except Exception as e:
        print(f"   ✗ Error reading settings: {e}")
        return False

def check_node_npm():
    """Check if Node.js and npm are available."""
    print("\n[2/5] Checking Node.js and npm...")
    
    try:
        node_version = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True
        )
        if node_version.returncode == 0:
            print(f"   ✓ Node.js: {node_version.stdout.strip()}")
        else:
            print("   ✗ Node.js not found")
            return False
    except FileNotFoundError:
        print("   ✗ Node.js not found")
        return False
    
    try:
        npm_version = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            text=True
        )
        if npm_version.returncode == 0:
            print(f"   ✓ npm: {npm_version.stdout.strip()}")
        else:
            print("   ✗ npm not found")
            return False
    except FileNotFoundError:
        print("   ✗ npm not found")
        return False
    
    try:
        npx_version = subprocess.run(
            ["npx", "--version"],
            capture_output=True,
            text=True
        )
        if npx_version.returncode == 0:
            print(f"   ✓ npx: {npx_version.stdout.strip()}")
        else:
            print("   ✗ npx not found")
            return False
    except FileNotFoundError:
        print("   ✗ npx not found")
        return False
    
    return True

def check_npm_package():
    """Check if the MCP package is accessible."""
    print("\n[3/5] Checking npm package availability...")
    
    try:
        result = subprocess.run(
            ["npm", "view", "@willpowell8/cursor-cloud-agent-mcp", "version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"   ✓ Package available: version {version}")
            return True
        else:
            print(f"   ✗ Package not found: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ✗ Error checking package: {e}")
        return False

def check_api_connection():
    """Check if API key works."""
    print("\n[4/5] Checking API Connection...")
    
    # Read API key from settings
    settings_path = Path.home() / "Library/Application Support/Cursor/User/settings.json"
    try:
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        api_key = settings.get("mcpServers", {}).get("cursor-cloud-agents", {}).get("env", {}).get("CURSOR_API_KEY", "")
    except:
        api_key = ""
    
    if not api_key or not api_key.startswith("key_"):
        print("   ⚠ API key not found in settings, skipping API test")
        return True
    
    try:
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
            return True
        else:
            print(f"   ✗ API Connection: Failed")
            return False
    except Exception as e:
        print(f"   ✗ API Connection: Error - {e}")
        return False

def check_mcp_server_startup():
    """Test if MCP server can start."""
    print("\n[5/5] Testing MCP Server Startup...")
    
    settings_path = Path.home() / "Library/Application Support/Cursor/User/settings.json"
    try:
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        api_key = settings.get("mcpServers", {}).get("cursor-cloud-agents", {}).get("env", {}).get("CURSOR_API_KEY", "")
    except:
        api_key = ""
    
    if not api_key:
        print("   ⚠ Skipping - API key not found")
        return True
    
    env = os.environ.copy()
    env["CURSOR_API_KEY"] = api_key
    
    try:
        # Try to start the server (will timeout, which is expected)
        process = subprocess.Popen(
            ["npx", "-y", "@willpowell8/cursor-cloud-agent-mcp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )
        
        # Give it a moment to start
        import time
        time.sleep(1)
        
        if process.poll() is None:
            print("   ✓ MCP Server: Can start (process running)")
            process.terminate()
            try:
                process.wait(timeout=2)
            except:
                process.kill()
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"   ✗ MCP Server: Exited immediately")
            if stderr:
                print(f"     Error: {stderr.decode()[:200]}")
            return False
            
    except Exception as e:
        print(f"   ✗ MCP Server: Error - {e}")
        return False

def main():
    print("=" * 60)
    print("Cursor Cloud Agents MCP Integration Verification")
    print("=" * 60)
    
    checks = [
        check_cursor_settings(),
        check_node_npm(),
        check_npm_package(),
        check_api_connection(),
        check_mcp_server_startup(),
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("✓ All checks passed! MCP integration should work.")
        print("\nNext steps:")
        print("1. Open Cursor Chat")
        print("2. Try: 'List my Cloud Agents'")
        print("3. Try: 'What Cloud Agents tools are available?'")
    else:
        print("⚠ Some checks failed. Please review the output above.")
        print("\nCommon fixes:")
        print("- Ensure Cursor is restarted after configuration changes")
        print("- Verify API key is correct in settings.json")
        print("- Check that Node.js and npm are installed")
    print("=" * 60)

if __name__ == "__main__":
    main()
