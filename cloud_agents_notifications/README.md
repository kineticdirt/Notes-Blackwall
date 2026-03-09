# Cloud Agents Notification Service

Receive real-time notifications when Cloud Agents need attention via Discord, Slack, or SMS.

## Features

- **Discord Webhooks** - Get notifications in Discord channels
- **Slack Integration** - Send messages to Slack channels
- **SMS Notifications** - Receive text messages for important events (via Twilio)
- **Webhook Receiver** - Secure webhook endpoint for Cursor Cloud Agents
- **Multi-Channel** - Send to multiple channels simultaneously

## Quick Setup

### 1. Install Dependencies

```bash
cd cloud_agents_notifications
pip install fastapi uvicorn httpx python-dotenv
```

### 2. Configure Notification Channels

#### Option A: Discord Webhook

1. Go to your Discord server → Server Settings → Integrations → Webhooks
2. Create a new webhook
3. Copy the webhook URL
4. Set environment variable:
   ```bash
   export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR_WEBHOOK_URL"
   ```

#### Option B: Slack Webhook

1. Go to https://api.slack.com/apps → Create New App
2. Enable "Incoming Webhooks"
3. Create webhook for your channel
4. Copy the webhook URL
5. Set environment variable:
   ```bash
   export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
   ```

#### Option C: SMS via Twilio

1. Sign up for Twilio: https://www.twilio.com/
2. Get Account SID and Auth Token
3. Get a Twilio phone number
4. Set environment variables:
   ```bash
   export TWILIO_ACCOUNT_SID="your_account_sid"
   export TWILIO_AUTH_TOKEN="your_auth_token"
   export TWILIO_PHONE_NUMBER="+1234567890"  # Your Twilio number
   export SMS_PHONE_NUMBER="+1987654321"     # Your phone number
   ```

### 3. Start the Notification Service

```bash
# Set webhook secret (optional but recommended)
export WEBHOOK_SECRET="your-secret-key-min-32-chars"

# Start the service
python notification_service.py
```

The service will run on `http://localhost:8001`

### 4. Configure Cloud Agents to Use Webhook

When launching a Cloud Agent, include the webhook configuration:

```python
from blackwall.mcp.cloud_agents_integration import create_cloud_agent_via_mcp

result = await create_cloud_agent_via_mcp(
    bridge=bridge,
    prompt_text="Fix bugs in authentication",
    repository="https://github.com/org/repo",
    webhook_url="http://your-server.com:8001/webhook/cloud-agents",
    webhook_secret="your-secret-key-min-32-chars"
)
```

Or via MCP tool:

```json
{
  "prompt": {"text": "Fix bugs"},
  "source": {"repository": "https://github.com/org/repo"},
  "webhook": {
    "url": "http://your-server.com:8001/webhook/cloud-agents",
    "secret": "your-secret-key-min-32-chars"
  }
}
```

## Using with ngrok (Local Development)

For local testing, use ngrok to expose your webhook endpoint:

```bash
# Install ngrok
brew install ngrok  # or download from ngrok.com

# Start notification service
python notification_service.py

# In another terminal, expose it
ngrok http 8001

# Use the ngrok URL in webhook config
# Example: https://abc123.ngrok.io/webhook/cloud-agents
```

## Notification Events

The service handles these Cloud Agent events:

- **CREATING** - Agent is being created
- **RUNNING** - Agent is actively working
- **FINISHED** - Agent completed successfully ✅
- **FAILED** - Agent encountered an error ❌
- **CANCELLED** - Agent was cancelled ⏹️

**SMS notifications** are only sent for important events (FINISHED, FAILED, CANCELLED) to avoid spam.

## API Endpoints

- `POST /webhook/cloud-agents` - Receive webhooks from Cursor
- `GET /health` - Health check
- `GET /config` - View notification configuration

## Environment Variables

```bash
# Discord
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
# OR
SLACK_TOKEN=xoxb-...
SLACK_CHANNEL=#cloud-agents

# SMS (Twilio)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1234567890
SMS_PHONE_NUMBER=+1987654321

# Webhook Security
WEBHOOK_SECRET=your-secret-key-min-32-chars

# Server
PORT=8001
```

## Example Notifications

### Discord
```
✅ Cloud Agent Status: FINISHED
Agent ID: `bc_abc123`
Repository: https://github.com/org/repo
Branch: feature/auth-fix
PR: https://github.com/org/repo/pull/123

View at: https://cursor.com/agents/bc_abc123
```

### Slack
Same format, sent to your configured Slack channel.

### SMS
```
Cloud Agent FINISHED
Agent: bc_abc123
Repo: org/repo
PR: #123
View: cursor.com/agents/bc_abc123
```

## Deployment

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY notification_service.py .

EXPOSE 8001
CMD ["uvicorn", "notification_service:app", "--host", "0.0.0.0", "--port", "8001"]
```

### Using Railway/Render/Fly.io

1. Deploy the service
2. Set environment variables
3. Use the public URL in webhook configuration

## Security

- Webhook signature verification (if `WEBHOOK_SECRET` is set)
- HTTPS recommended for production
- Environment variables for sensitive credentials

## Troubleshooting

### Notifications not sending

1. Check service logs: `python notification_service.py`
2. Verify environment variables are set
3. Test webhook endpoint: `curl http://localhost:8001/health`
4. Check Discord/Slack webhook URLs are valid

### Webhook not receiving events

1. Verify webhook URL is accessible (use ngrok for local)
2. Check Cloud Agent was launched with webhook config
3. Verify webhook secret matches (if using)

## Next Steps

1. Set up your preferred notification channel(s)
2. Start the notification service
3. Configure Cloud Agents to use webhooks
4. Launch an agent and test!
