# All Notification Options for Cloud Agents

Here are all the ways you can be notified when Cloud Agents need attention:

## 📧 Email

**Best for:** Traditional notifications, email-based workflows

**Setup:**
```bash
export EMAIL_SMTP_SERVER="smtp.gmail.com"
export EMAIL_SMTP_PORT="587"
export EMAIL_USERNAME="your-email@gmail.com"
export EMAIL_PASSWORD="your-app-password"
export EMAIL_TO="notifications@example.com"
export EMAIL_FROM="your-email@gmail.com"
```

**Pros:**
- Works everywhere
- Can be forwarded/routed
- Searchable history
- No app installation needed

**Cons:**
- May go to spam
- Less immediate than push notifications

---

## 📱 Telegram

**Best for:** Quick mobile notifications, team chats

**Setup:**
1. Message @BotFather on Telegram
2. Create bot: `/newbot`
3. Get bot token
4. Get your chat ID: Message your bot, then visit `https://api.telegram.org/bot<TOKEN>/getUpdates`
5. Set environment variables:
```bash
export TELEGRAM_BOT_TOKEN="123456:ABC-DEF..."
export TELEGRAM_CHAT_ID="123456789"
```

**Pros:**
- Free
- Fast delivery
- Works on all devices
- Can send to groups/channels
- Rich formatting support

**Cons:**
- Requires Telegram account
- Need to create a bot

---

## 💼 Microsoft Teams

**Best for:** Enterprise teams, Office 365 users

**Setup:**
1. Teams → Your Team → Connectors
2. Add "Incoming Webhook"
3. Configure → Copy webhook URL
4. Set environment variable:
```bash
export TEAMS_WEBHOOK_URL="https://outlook.office.com/webhook/..."
```

**Pros:**
- Native Teams integration
- Rich cards/formatting
- Enterprise-friendly
- No bot needed (webhook)

**Cons:**
- Requires Teams account
- Microsoft ecosystem

---

## 🔔 Pushover

**Best for:** Reliable push notifications, priority levels

**Setup:**
1. Sign up at https://pushover.net
2. Create application → Get API token
3. Get your user key
4. Set environment variables:
```bash
export PUSHOVER_API_TOKEN="your-app-token"
export PUSHOVER_USER_KEY="your-user-key"
```

**Pros:**
- Reliable delivery
- Priority levels (normal/high/emergency)
- Works on iOS/Android/Desktop
- $5 one-time purchase per platform

**Cons:**
- Paid service ($5 per platform)
- Requires app installation

---

## 🚀 Gotify

**Best for:** Self-hosted push notifications

**Setup:**
1. Self-host Gotify server (Docker: `docker run -p 80:80 gotify/server`)
2. Create app → Get token
3. Set environment variables:
```bash
export GOTIFY_URL="https://gotify.yourdomain.com"
export GOTIFY_TOKEN="your-app-token"
```

**Pros:**
- Self-hosted (privacy)
- Free and open source
- No external dependencies
- Full control

**Cons:**
- Requires server setup
- More technical

---

## 🔐 Matrix

**Best for:** Decentralized, privacy-focused teams

**Setup:**
1. Join Matrix server (or self-host)
2. Get access token from Element client
3. Get room ID
4. Set environment variables:
```bash
export MATRIX_HOMESERVER="https://matrix.org"
export MATRIX_USER_ID="@user:matrix.org"
export MATRIX_ACCESS_TOKEN="syt_..."
export MATRIX_ROOM_ID="!roomid:matrix.org"
```

**Pros:**
- Decentralized
- End-to-end encrypted
- Open source
- Self-hostable

**Cons:**
- More complex setup
- Less common

---

## 💻 Desktop Notifications

**Best for:** Local development, immediate alerts

**Setup:**
```bash
export DESKTOP_NOTIFICATIONS="true"
```

**Works on:**
- macOS: Uses `osascript` (built-in)
- Linux: Uses `notify-send` (install `libnotify-bin`)
- Windows: Uses `win10toast` (install `pip install win10toast`)

**Pros:**
- No external services
- Instant notifications
- Works offline
- Free

**Cons:**
- Only works on local machine
- No mobile support
- Requires app to be running

---

## 🔗 Custom Webhook

**Best for:** Integrating with your own systems

**Setup:**
```bash
export CUSTOM_WEBHOOK_URL="https://your-api.com/webhook"
export CUSTOM_WEBHOOK_HEADERS='{"Authorization": "Bearer token"}'
```

**Use cases:**
- Your own API
- Zapier/Make.com
- IFTTT
- Custom dashboards
- Database logging

**Pros:**
- Complete flexibility
- Integrate with anything
- Custom payload format

**Cons:**
- Need to build receiver
- More setup

---

## 📝 File Logging

**Best for:** Logging, auditing, debugging

**Setup:**
```bash
export FILE_LOG_PATH="/path/to/notifications.log"
```

**Pros:**
- Simple
- Persistent history
- Easy to parse/search
- No external dependencies

**Cons:**
- Not "real-time" notification
- Need to monitor file
- Local only

---

## Comparison Table

| Method | Setup Difficulty | Cost | Mobile | Real-time | Best For |
|--------|-----------------|------|--------|-----------|----------|
| **Email** | ⭐ Easy | Free | ✅ | ⚠️ | Traditional workflows |
| **Telegram** | ⭐⭐ Medium | Free | ✅ | ✅ | Quick mobile alerts |
| **Teams** | ⭐ Easy | Free* | ✅ | ✅ | Enterprise teams |
| **Pushover** | ⭐⭐ Medium | $5 | ✅ | ✅ | Reliable push |
| **Gotify** | ⭐⭐⭐ Hard | Free | ✅ | ✅ | Self-hosted |
| **Matrix** | ⭐⭐⭐ Hard | Free | ✅ | ✅ | Privacy-focused |
| **Desktop** | ⭐ Easy | Free | ❌ | ✅ | Local dev |
| **Custom** | ⭐⭐⭐⭐ Varies | Free | ⚠️ | ✅ | Custom systems |
| **File Log** | ⭐ Easy | Free | ❌ | ❌ | Logging/audit |

*Teams requires Office 365 subscription

## Recommendations

**For most users:**
- **Telegram** - Best balance of ease and features
- **Email** - Universal, always works
- **Desktop** - Great for local development

**For teams:**
- **Microsoft Teams** - If you use Office 365
- **Telegram Group** - For small teams
- **Custom Webhook** - For custom dashboards

**For privacy:**
- **Gotify** - Self-hosted
- **Matrix** - Decentralized
- **File Log** - Local only

## Multiple Channels

You can enable multiple channels at once! Just set all the environment variables you want:

```bash
export EMAIL_SMTP_SERVER="..."
export TELEGRAM_BOT_TOKEN="..."
export DESKTOP_NOTIFICATIONS="true"
export FILE_LOG_PATH="/var/log/agents.log"
```

All will receive notifications simultaneously!
