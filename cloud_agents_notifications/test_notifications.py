#!/usr/bin/env python3
"""
Test notification service without launching actual Cloud Agents.
"""

import asyncio
import httpx
import json
import os
from datetime import datetime

async def test_notifications():
    """Test notification channels."""
    
    webhook_url = os.getenv("WEBHOOK_URL", "http://localhost:8001/webhook/cloud-agents")
    
    print("Testing Cloud Agents Notification Service")
    print("=" * 60)
    print(f"Webhook URL: {webhook_url}")
    print()
    
    # Test payloads
    test_cases = [
        {
            "name": "Agent Finished Successfully",
            "payload": {
                "event": "statusChange",
                "agent_id": "test_bc_123",
                "status": "FINISHED",
                "timestamp": datetime.now().isoformat(),
                "repository": "https://github.com/test/repo",
                "branch": "feature/test",
                "pull_request_url": "https://github.com/test/repo/pull/123"
            }
        },
        {
            "name": "Agent Failed",
            "payload": {
                "event": "statusChange",
                "agent_id": "test_bc_456",
                "status": "FAILED",
                "timestamp": datetime.now().isoformat(),
                "repository": "https://github.com/test/repo",
                "error": "Connection timeout after 30 seconds"
            }
        },
        {
            "name": "Agent Started Running",
            "payload": {
                "event": "statusChange",
                "agent_id": "test_bc_789",
                "status": "RUNNING",
                "timestamp": datetime.now().isoformat(),
                "repository": "https://github.com/test/repo"
            }
        }
    ]
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for test_case in test_cases:
            print(f"\n[Test] {test_case['name']}")
            print(f"  Status: {test_case['payload']['status']}")
            
            try:
                response = await client.post(
                    webhook_url,
                    json=test_case['payload'],
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"  ✓ Success!")
                    print(f"    Notifications sent: {result.get('notifications_sent', {})}")
                else:
                    print(f"  ✗ Failed: {response.status_code}")
                    print(f"    {response.text}")
            except Exception as e:
                print(f"  ✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Test complete! Check your notification channels:")
    print("  - Discord: Check your Discord channel")
    print("  - Slack: Check your Slack channel")
    print("  - SMS: Check your phone (if configured)")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_notifications())
