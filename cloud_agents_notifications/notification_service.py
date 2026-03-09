"""
Cloud Agents Notification Service
Receives webhooks from Cursor Cloud Agents and sends notifications via multiple channels.
"""

from fastapi import FastAPI, Request, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import httpx
import os
import json
from datetime import datetime
import hmac
import hashlib
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = FastAPI(title="Cloud Agents Notification Service")

# Notification types
class NotificationType(str, Enum):
    EMAIL = "email"
    TELEGRAM = "telegram"
    MICROSOFT_TEAMS = "microsoft_teams"
    PUSHOVER = "pushover"
    GOTIFY = "gotify"
    MATRIX = "matrix"
    APPLE_PUSH = "apple_push"
    DESKTOP_NOTIFICATION = "desktop_notification"
    CUSTOM_WEBHOOK = "custom_webhook"
    FILE_LOG = "file_log"


# Configuration
class NotificationConfig(BaseModel):
    """Notification channel configuration."""
    type: NotificationType
    enabled: bool = True
    
    # Email
    email_smtp_server: Optional[str] = None
    email_smtp_port: Optional[int] = 587
    email_username: Optional[str] = None
    email_password: Optional[str] = None
    email_to: Optional[str] = None
    email_from: Optional[str] = None
    email_use_tls: bool = True
    
    # Telegram
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    
    # Microsoft Teams
    teams_webhook_url: Optional[str] = None
    
    # Pushover
    pushover_api_token: Optional[str] = None
    pushover_user_key: Optional[str] = None
    
    # Gotify
    gotify_url: Optional[str] = None
    gotify_token: Optional[str] = None
    
    # Matrix
    matrix_homeserver: Optional[str] = None
    matrix_user_id: Optional[str] = None
    matrix_access_token: Optional[str] = None
    matrix_room_id: Optional[str] = None
    
    # Apple Push (via APNs)
    apple_push_key_id: Optional[str] = None
    apple_push_team_id: Optional[str] = None
    apple_push_bundle_id: Optional[str] = None
    apple_push_key_file: Optional[str] = None
    apple_push_device_token: Optional[str] = None
    
    # Desktop Notifications (macOS/Linux/Windows)
    desktop_enabled: bool = False
    
    # Custom Webhook
    custom_webhook_url: Optional[str] = None
    custom_webhook_headers: Optional[Dict[str, str]] = None
    
    # File Logging
    file_log_path: Optional[str] = None


# Webhook payload models
class WebhookPayload(BaseModel):
    """Webhook payload from Cursor Cloud Agents."""
    event: str
    agent_id: str
    status: str
    timestamp: str
    repository: Optional[str] = None
    branch: Optional[str] = None
    pull_request_url: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# Notification service
class NotificationService:
    """Handles sending notifications via various channels."""
    
    def __init__(self):
        self.configs: Dict[str, NotificationConfig] = {}
        self.load_configs()
    
    def load_configs(self):
        """Load notification configurations from environment variables."""
        # Email
        if os.getenv("EMAIL_SMTP_SERVER"):
            self.configs["email"] = NotificationConfig(
                type=NotificationType.EMAIL,
                enabled=True,
                email_smtp_server=os.getenv("EMAIL_SMTP_SERVER"),
                email_smtp_port=int(os.getenv("EMAIL_SMTP_PORT", "587")),
                email_username=os.getenv("EMAIL_USERNAME"),
                email_password=os.getenv("EMAIL_PASSWORD"),
                email_to=os.getenv("EMAIL_TO"),
                email_from=os.getenv("EMAIL_FROM", os.getenv("EMAIL_USERNAME")),
                email_use_tls=os.getenv("EMAIL_USE_TLS", "true").lower() == "true"
            )
        
        # Telegram
        if os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID"):
            self.configs["telegram"] = NotificationConfig(
                type=NotificationType.TELEGRAM,
                enabled=True,
                telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
                telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID")
            )
        
        # Microsoft Teams
        if os.getenv("TEAMS_WEBHOOK_URL"):
            self.configs["teams"] = NotificationConfig(
                type=NotificationType.MICROSOFT_TEAMS,
                enabled=True,
                teams_webhook_url=os.getenv("TEAMS_WEBHOOK_URL")
            )
        
        # Pushover
        if os.getenv("PUSHOVER_API_TOKEN") and os.getenv("PUSHOVER_USER_KEY"):
            self.configs["pushover"] = NotificationConfig(
                type=NotificationType.PUSHOVER,
                enabled=True,
                pushover_api_token=os.getenv("PUSHOVER_API_TOKEN"),
                pushover_user_key=os.getenv("PUSHOVER_USER_KEY")
            )
        
        # Gotify
        if os.getenv("GOTIFY_URL") and os.getenv("GOTIFY_TOKEN"):
            self.configs["gotify"] = NotificationConfig(
                type=NotificationType.GOTIFY,
                enabled=True,
                gotify_url=os.getenv("GOTIFY_URL"),
                gotify_token=os.getenv("GOTIFY_TOKEN")
            )
        
        # Matrix
        if os.getenv("MATRIX_HOMESERVER") and os.getenv("MATRIX_ACCESS_TOKEN"):
            self.configs["matrix"] = NotificationConfig(
                type=NotificationType.MATRIX,
                enabled=True,
                matrix_homeserver=os.getenv("MATRIX_HOMESERVER"),
                matrix_user_id=os.getenv("MATRIX_USER_ID"),
                matrix_access_token=os.getenv("MATRIX_ACCESS_TOKEN"),
                matrix_room_id=os.getenv("MATRIX_ROOM_ID")
            )
        
        # Desktop Notifications
        if os.getenv("DESKTOP_NOTIFICATIONS", "false").lower() == "true":
            self.configs["desktop"] = NotificationConfig(
                type=NotificationType.DESKTOP_NOTIFICATION,
                enabled=True,
                desktop_enabled=True
            )
        
        # Custom Webhook
        if os.getenv("CUSTOM_WEBHOOK_URL"):
            headers = {}
            if os.getenv("CUSTOM_WEBHOOK_HEADERS"):
                headers = json.loads(os.getenv("CUSTOM_WEBHOOK_HEADERS"))
            
            self.configs["custom"] = NotificationConfig(
                type=NotificationType.CUSTOM_WEBHOOK,
                enabled=True,
                custom_webhook_url=os.getenv("CUSTOM_WEBHOOK_URL"),
                custom_webhook_headers=headers
            )
        
        # File Logging
        if os.getenv("FILE_LOG_PATH"):
            self.configs["file"] = NotificationConfig(
                type=NotificationType.FILE_LOG,
                enabled=True,
                file_log_path=os.getenv("FILE_LOG_PATH")
            )
    
    async def send_email_notification(self, config: NotificationConfig, subject: str, message: str):
        """Send email notification."""
        if not all([config.email_smtp_server, config.email_to, config.email_from]):
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = config.email_from
            msg['To'] = config.email_to
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(config.email_smtp_server, config.email_smtp_port)
            if config.email_use_tls:
                server.starttls()
            
            if config.email_username and config.email_password:
                server.login(config.email_username, config.email_password)
            
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"Email notification error: {e}")
            return False
    
    async def send_telegram_notification(self, config: NotificationConfig, message: str):
        """Send Telegram notification via bot."""
        if not config.telegram_bot_token or not config.telegram_chat_id:
            return False
        
        url = f"https://api.telegram.org/bot{config.telegram_bot_token}/sendMessage"
        payload = {
            "chat_id": config.telegram_chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload)
                return response.status_code == 200
            except Exception as e:
                print(f"Telegram notification error: {e}")
                return False
    
    async def send_teams_notification(self, config: NotificationConfig, title: str, message: str, status: str):
        """Send Microsoft Teams notification."""
        if not config.teams_webhook_url:
            return False
        
        # Teams uses Office 365 Connector Card format
        payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": title,
            "themeColor": "0078D4" if status == "FINISHED" else "FF0000" if status == "FAILED" else "FFAA00",
            "title": title,
            "text": message
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(config.teams_webhook_url, json=payload)
                return response.status_code == 200
            except Exception as e:
                print(f"Teams notification error: {e}")
                return False
    
    async def send_pushover_notification(self, config: NotificationConfig, title: str, message: str, priority: int = 0):
        """Send Pushover notification."""
        if not config.pushover_api_token or not config.pushover_user_key:
            return False
        
        url = "https://api.pushover.net/1/messages.json"
        payload = {
            "token": config.pushover_api_token,
            "user": config.pushover_user_key,
            "title": title,
            "message": message,
            "priority": priority  # 0=normal, 1=high, 2=emergency
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, data=payload)
                return response.status_code == 200
            except Exception as e:
                print(f"Pushover notification error: {e}")
                return False
    
    async def send_gotify_notification(self, config: NotificationConfig, title: str, message: str, priority: int = 5):
        """Send Gotify notification."""
        if not config.gotify_url or not config.gotify_token:
            return False
        
        url = f"{config.gotify_url.rstrip('/')}/message"
        headers = {"X-Gotify-Key": config.gotify_token}
        payload = {
            "title": title,
            "message": message,
            "priority": priority
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                return response.status_code == 200
            except Exception as e:
                print(f"Gotify notification error: {e}")
                return False
    
    async def send_matrix_notification(self, config: NotificationConfig, message: str):
        """Send Matrix notification."""
        if not all([config.matrix_homeserver, config.matrix_access_token, config.matrix_room_id]):
            return False
        
        url = f"{config.matrix_homeserver.rstrip('/')}/_matrix/client/r0/rooms/{config.matrix_room_id}/send/m.room.message"
        headers = {
            "Authorization": f"Bearer {config.matrix_access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "msgtype": "m.text",
            "body": message
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.put(url, headers=headers, json=payload)
                return response.status_code == 200
            except Exception as e:
                print(f"Matrix notification error: {e}")
                return False
    
    async def send_desktop_notification(self, config: NotificationConfig, title: str, message: str):
        """Send desktop/system notification."""
        if not config.desktop_enabled:
            return False
        
        try:
            import platform
            system = platform.system()
            
            if system == "Darwin":  # macOS
                import subprocess
                subprocess.run([
                    "osascript", "-e",
                    f'display notification "{message}" with title "{title}"'
                ])
                return True
            elif system == "Linux":
                import subprocess
                subprocess.run([
                    "notify-send", title, message
                ])
                return True
            elif system == "Windows":
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast(title, message, duration=10)
                return True
        except Exception as e:
            print(f"Desktop notification error: {e}")
            return False
    
    async def send_custom_webhook(self, config: NotificationConfig, payload: Dict[str, Any]):
        """Send to custom webhook endpoint."""
        if not config.custom_webhook_url:
            return False
        
        headers = config.custom_webhook_headers or {}
        headers.setdefault("Content-Type", "application/json")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    config.custom_webhook_url,
                    json=payload,
                    headers=headers
                )
                return response.status_code < 400
            except Exception as e:
                print(f"Custom webhook error: {e}")
                return False
    
    def log_to_file(self, config: NotificationConfig, message: str):
        """Log notification to file."""
        if not config.file_log_path:
            return False
        
        try:
            log_entry = f"[{datetime.now().isoformat()}] {message}\n"
            with open(config.file_log_path, "a") as f:
                f.write(log_entry)
            return True
        except Exception as e:
            print(f"File logging error: {e}")
            return False
    
    async def notify_agent_status_change(self, payload: WebhookPayload):
        """Send notifications for agent status changes."""
        status = payload.status
        agent_id = payload.agent_id
        
        # Build message
        emoji_map = {
            "CREATING": "🔄",
            "RUNNING": "⚙️",
            "FINISHED": "✅",
            "FAILED": "❌",
            "CANCELLED": "⏹️"
        }
        
        emoji = emoji_map.get(status, "ℹ️")
        title = f"{emoji} Cloud Agent {status}"
        
        message_lines = [
            f"Agent ID: `{agent_id}`",
            f"Status: **{status}**"
        ]
        
        if payload.repository:
            message_lines.append(f"Repository: {payload.repository}")
        if payload.branch:
            message_lines.append(f"Branch: {payload.branch}")
        if payload.pull_request_url:
            message_lines.append(f"PR: {payload.pull_request_url}")
        if payload.error:
            message_lines.append(f"Error: {payload.error}")
        
        message_lines.append(f"\nView: https://cursor.com/agents/{agent_id}")
        
        message = "\n".join(message_lines)
        message_plain = message.replace("**", "").replace("`", "")
        
        # Determine priority
        important_statuses = ["FINISHED", "FAILED", "CANCELLED"]
        needs_attention = status in important_statuses
        
        # Send to all enabled channels
        results = {}
        for name, config in self.configs.items():
            if not config.enabled:
                continue
            
            try:
                if config.type == NotificationType.EMAIL:
                    results[name] = await self.send_email_notification(
                        config, title, message_plain
                    )
                elif config.type == NotificationType.TELEGRAM:
                    results[name] = await self.send_telegram_notification(
                        config, message
                    )
                elif config.type == NotificationType.MICROSOFT_TEAMS:
                    results[name] = await self.send_teams_notification(
                        config, title, message_plain, status
                    )
                elif config.type == NotificationType.PUSHOVER:
                    priority = 1 if needs_attention else 0
                    results[name] = await self.send_pushover_notification(
                        config, title, message_plain, priority
                    )
                elif config.type == NotificationType.GOTIFY:
                    priority = 8 if needs_attention else 5
                    results[name] = await self.send_gotify_notification(
                        config, title, message_plain, priority
                    )
                elif config.type == NotificationType.MATRIX:
                    results[name] = await self.send_matrix_notification(
                        config, message
                    )
                elif config.type == NotificationType.DESKTOP_NOTIFICATION:
                    results[name] = await self.send_desktop_notification(
                        config, title, message_plain
                    )
                elif config.type == NotificationType.CUSTOM_WEBHOOK:
                    results[name] = await self.send_custom_webhook(
                        config, payload.dict()
                    )
                elif config.type == NotificationType.FILE_LOG:
                    results[name] = self.log_to_file(
                        config, f"{title}: {message_plain}"
                    )
            except Exception as e:
                print(f"Error sending {name} notification: {e}")
                results[name] = False
        
        return results


# Initialize service
notification_service = NotificationService()


@app.post("/webhook/cloud-agents")
async def receive_webhook(
    request: Request,
    x_cursor_signature: Optional[str] = Header(None, alias="X-Cursor-Signature")
):
    """Receive webhook from Cursor Cloud Agents."""
    try:
        body = await request.body()
        payload_data = json.loads(body)
        
        # Verify webhook signature if secret is configured
        webhook_secret = os.getenv("WEBHOOK_SECRET")
        if webhook_secret and x_cursor_signature:
            expected_signature = hmac.new(
                webhook_secret.encode(),
                body,
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(x_cursor_signature, expected_signature):
                raise HTTPException(status_code=401, detail="Invalid signature")
        
        payload = WebhookPayload(**payload_data)
        
        if payload.event == "statusChange":
            results = await notification_service.notify_agent_status_change(payload)
            return {
                "status": "success",
                "notifications_sent": results,
                "event": payload.event,
                "agent_id": payload.agent_id
            }
        else:
            return {
                "status": "success",
                "event": payload.event,
                "message": "Event received but not handled"
            }
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        print(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "notification_channels": list(notification_service.configs.keys()),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/config")
async def get_config():
    """Get current notification configuration (without secrets)."""
    config_summary = {}
    for name, config in notification_service.configs.items():
        config_summary[name] = {
            "type": config.type.value,
            "enabled": config.enabled,
            "configured": True
        }
    return config_summary


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)
