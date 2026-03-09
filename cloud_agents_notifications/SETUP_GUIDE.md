# Notification Channel Setup Guide

## What You Need for Each Channel

### Discord (Easiest - No Bot Needed!)

**What you need:** Just a **Webhook URL** (no bot, no API key)

**Steps:**
1. Open Discord → Your Server
2. Server Settings → Integrations → Webhooks
3. Click "New Webhook"
4. Name it (e.g., "Cloud Agents")
5. Choose a channel
6. Click "Copy Webhook URL"
7. Done! That's all you need.

**Example URL format:**
```
https://discord.com/api/webhooks/1234567890123456789/abcdefghijklmnopqrstuvwxyz1234567890
```

**No bot required!** Webhooks are simpler - they're just URLs that Discord gives you.

---

### Slack (Two Options)

#### Option A: Webhook (Easiest - No Bot)

**What you need:** Just a **Webhook URL**

**Steps:**
1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name it (e.g., "Cloud Agents") → Choose workspace
4. Go to "Incoming Webhooks" → Turn it ON
5. Click "Add New Webhook to Workspace"
6. Choose a channel → Allow
7. Copy the webhook URL
8. Done!

**Example URL format:**
```
https://hooks.slack.com/services/TXXXXXXXXX/BXXXXXXXXX/your-webhook-secret-here
```

#### Option B: Bot Token (More Features)

**What you need:** Bot Token + Channel Name

**Steps:**
1. Create app at https://api.slack.com/apps
2. Go to "OAuth & Permissions"
3. Add scopes: `chat:write`, `channels:read`
4. Install to workspace → Copy "Bot User OAuth Token"
5. Use token + channel name

**More setup, but gives you more control.**

---

### SMS via Twilio

**What you need:** Twilio Account + API Credentials

**Steps:**
1. Sign up at https://www.twilio.com/try-twilio (free trial)
2. Get your Account SID (starts with "AC...")
3. Get your Auth Token
4. Get a Twilio phone number (free trial includes one)
5. Use your personal phone number for receiving SMS

**Cost:** Free trial, then ~$0.0075 per SMS

**Environment variables:**
```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890  # Twilio's number
SMS_PHONE_NUMBER=+1987654321     # Your phone
```

---

## Comparison

| Channel | What You Need | Difficulty | Cost |
|---------|---------------|------------|------|
| **Discord Webhook** | Webhook URL only | ⭐ Easiest | Free |
| **Slack Webhook** | Webhook URL only | ⭐⭐ Easy | Free |
| **Slack Bot** | Bot token + channel | ⭐⭐⭐ Medium | Free |
| **SMS (Twilio)** | API credentials | ⭐⭐⭐⭐ Harder | Free trial, then paid |

## Recommendation

**Start with Discord Webhook** - it's the easiest:
- No API keys needed
- No bot setup
- Just copy a URL
- Works immediately
- Free forever

## Quick Setup Commands

### Discord (Recommended)
```bash
# 1. Get webhook URL from Discord (see steps above)
# 2. Set it:
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR_URL"

# 3. Start service:
cd cloud_agents_notifications
./setup_notifications.sh
source venv/bin/activate
python notification_service.py
```

### Slack Webhook
```bash
# Same as Discord, but:
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/URL"
```

### SMS (If you want text messages)
```bash
# Requires Twilio account:
export TWILIO_ACCOUNT_SID="AC..."
export TWILIO_AUTH_TOKEN="..."
export TWILIO_PHONE_NUMBER="+1234567890"
export SMS_PHONE_NUMBER="+1987654321"
```

## Testing Your Setup

After setting up, test it:

```bash
# Start service
python notification_service.py

# In another terminal, test:
python test_notifications.py
```

You should receive a test notification in your chosen channel!

## FAQ

**Q: Do I need to create a Discord bot?**  
A: No! Webhooks don't require bots. Just use the webhook URL.

**Q: Do I need Slack API credentials?**  
A: Not if you use webhooks. Webhooks are simpler.

**Q: Can I use multiple channels?**  
A: Yes! Set multiple environment variables and all will receive notifications.

**Q: Is SMS free?**  
A: Twilio has a free trial, then it's ~$0.0075 per message (very cheap).

**Q: Which is easiest?**  
A: Discord webhook - just copy a URL, no setup needed.
