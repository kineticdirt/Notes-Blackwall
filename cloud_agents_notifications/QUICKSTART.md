# Quick Start: Cloud Agents Notifications

Get notified via Discord, Slack, or SMS when your Cloud Agents need attention!

## 5-Minute Setup

### Step 1: Choose Your Notification Channel

#### Discord (Easiest)
1. Open Discord → Your Server → Settings → Integrations → Webhooks
2. Click "New Webhook"
3. Copy the webhook URL
4. Run:
   ```bash
   export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR_URL"
   ```

#### Slack (Easy)
1. Go to https://api.slack.com/apps → Create App
2. Enable "Incoming Webhooks"
3. Add to workspace → Copy webhook URL
4. Run:
   ```bash
   export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/URL"
   ```

#### SMS via Twilio (More Setup)
1. Sign up at https://www.twilio.com/try-twilio
2. Get Account SID, Auth Token, and phone number
3. Run:
   ```bash
   export TWILIO_ACCOUNT_SID="AC..."
   export TWILIO_AUTH_TOKEN="..."
   export TWILIO_PHONE_NUMBER="+1234567890"
   export SMS_PHONE_NUMBER="+1987654321"  # Your phone
   ```

### Step 2: Setup Notification Service

```bash
cd cloud_agents_notifications
./setup_notifications.sh
source venv/bin/activate
```

### Step 3: Start Service (Local Testing)

```bash
# Terminal 1: Start notification service
python notification_service.py

# Terminal 2: Expose with ngrok (for local testing)
ngrok http 8001
# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

### Step 4: Launch Agent with Webhook

```python
from blackwall.mcp.cloud_agents_integration import setup_cloud_agents_integration

bridge = await setup_cloud_agents_integration()

# Use your ngrok URL
result = await bridge.execute_tool("launch_agent", {
    "prompt": {"text": "Fix bugs"},
    "source": {"repository": "https://github.com/org/repo"},
    "webhook": {
        "url": "https://abc123.ngrok.io/webhook/cloud-agents",
        "secret": "your-secret-min-32-chars"
    }
})
```

Or use the example script:
```bash
export WEBHOOK_URL="https://abc123.ngrok.io/webhook/cloud-agents"
python example_launch_with_webhook.py
```

## What You'll Receive

### When Agent Finishes ✅
```
✅ Cloud Agent Status: FINISHED
Agent ID: bc_abc123
Repository: https://github.com/org/repo
PR: https://github.com/org/repo/pull/123
View at: cursor.com/agents/bc_abc123
```

### When Agent Fails ❌
```
❌ Cloud Agent Status: FAILED
Agent ID: bc_abc123
Error: Connection timeout
View at: cursor.com/agents/bc_abc123
```

## Production Deployment

For production, deploy the service to:
- **Railway**: `railway up`
- **Render**: Connect GitHub repo
- **Fly.io**: `fly deploy`
- **Heroku**: `git push heroku main`

Then use your production URL in webhook config.

## Multiple Channels

You can enable multiple channels at once:
```bash
export DISCORD_WEBHOOK_URL="..."
export SLACK_WEBHOOK_URL="..."
export TWILIO_ACCOUNT_SID="..."
```

All will receive notifications!

## Testing

1. Start service: `python notification_service.py`
2. Test health: `curl http://localhost:8001/health`
3. Test webhook (simulate):
   ```bash
   curl -X POST http://localhost:8001/webhook/cloud-agents \
     -H "Content-Type: application/json" \
     -d '{
       "event": "statusChange",
       "agent_id": "test_123",
       "status": "FINISHED",
       "timestamp": "2026-01-23T12:00:00Z",
       "repository": "https://github.com/test/repo"
     }'
   ```

## Troubleshooting

- **No notifications?** Check service logs and verify webhook URLs
- **Webhook not receiving?** Ensure ngrok/production URL is accessible
- **SMS not working?** Verify Twilio credentials and phone numbers

## Next Steps

- Set up multiple notification channels
- Deploy to production
- Configure webhooks for all your Cloud Agents
- Enjoy real-time notifications! 🎉
