#!/usr/bin/env python3
"""
Example: Launch Cloud Agent with Webhook Notifications
"""

import asyncio
import os
from blackwall.mcp.cloud_agents_integration import (
    setup_cloud_agents_integration,
    create_cloud_agent_via_mcp
)


async def launch_agent_with_notifications():
    """Launch a Cloud Agent with webhook notifications configured."""
    
    # Setup MCP bridge
    bridge = await setup_cloud_agents_integration()
    
    # Your webhook URL (use ngrok URL for local testing)
    # Example: https://abc123.ngrok.io/webhook/cloud-agents
    webhook_url = os.getenv(
        "WEBHOOK_URL",
        "http://localhost:8001/webhook/cloud-agents"
    )
    
    webhook_secret = os.getenv("WEBHOOK_SECRET", "your-secret-key-min-32-chars")
    
    print(f"Launching Cloud Agent with webhook: {webhook_url}")
    
    # Launch agent with webhook
    result = await bridge.execute_tool(
        "launch_agent",
        {
            "prompt": {
                "text": "Analyze the codebase and suggest improvements"
            },
            "source": {
                "repository": "https://github.com/your-org/your-repo"
            },
            "target": {
                "autoCreatePr": True
            },
            "webhook": {
                "url": webhook_url,
                "secret": webhook_secret
            }
        }
    )
    
    agent_id = result.get("id")
    print(f"\n✓ Agent launched: {agent_id}")
    print(f"  Status: {result.get('status', 'CREATING')}")
    print(f"  View at: https://cursor.com/agents/{agent_id}")
    print(f"\nYou will receive notifications when the agent status changes!")
    
    return agent_id


if __name__ == "__main__":
    asyncio.run(launch_agent_with_notifications())
