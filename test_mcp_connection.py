#!/usr/bin/env python3
"""
Quick test of Cursor Cloud Agents API connection.
"""

import subprocess
import json

api_key = "key_c6941230ec4b54143ea2d6d379f04b01f8625d0626644c3da1d7d645a480411a"

print("Testing Cursor Cloud Agents API Connection")
print("=" * 50)

# Test 1: API Key Info
print("\n1. Testing API Key...")
result = subprocess.run(
    ["curl", "-s", "-u", f"{api_key}:", "https://api.cursor.com/v0/me"],
    capture_output=True,
    text=True
)
if result.returncode == 0:
    info = json.loads(result.stdout)
    print(f"   ✓ API Key: {info.get('apiKeyName')}")
    print(f"   ✓ User: {info.get('userEmail')}")
else:
    print(f"   ✗ Failed: {result.stderr}")

# Test 2: List Agents
print("\n2. Testing List Agents...")
result = subprocess.run(
    ["curl", "-s", "-u", f"{api_key}:", "https://api.cursor.com/v0/agents?limit=5"],
    capture_output=True,
    text=True
)
if result.returncode == 0:
    data = json.loads(result.stdout)
    count = len(data.get("agents", []))
    print(f"   ✓ Found {count} agent(s)")
else:
    print(f"   ✗ Failed: {result.stderr}")

# Test 3: List Repositories
print("\n3. Testing List Repositories...")
result = subprocess.run(
    ["curl", "-s", "-u", f"{api_key}:", "https://api.cursor.com/v0/repositories"],
    capture_output=True,
    text=True,
    timeout=30
)
if result.returncode == 0:
    repos = json.loads(result.stdout)
    count = len(repos.get("repositories", []))
    print(f"   ✓ Found {count} repository/repositories")
else:
    print(f"   ✗ Failed (may be rate limited): {result.stderr[:100]}")

# Test 4: List Models
print("\n4. Testing List Models...")
result = subprocess.run(
    ["curl", "-s", "-u", f"{api_key}:", "https://api.cursor.com/v0/models"],
    capture_output=True,
    text=True
)
if result.returncode == 0:
    models = json.loads(result.stdout)
    model_list = models.get("models", [])
    print(f"   ✓ Found {len(model_list)} model(s)")
    if model_list:
        example = model_list[0] if isinstance(model_list[0], str) else model_list[0].get('id', 'N/A')
        print(f"   - Example: {example}")
else:
    print(f"   ✗ Failed: {result.stderr}")

print("\n" + "=" * 50)
print("✓ API Connection Test Complete!")
print("\nNext Steps:")
print("1. Restart Cursor IDE to load MCP server configuration")
print("2. The MCP server should be available in Cursor Chat")
print("3. Try asking: 'List my Cloud Agents' or 'What Cloud Agents tools are available?'")
