# Cloud Notifications — Notification Service and Webhooks

**Cloud agents notifications** provide a notification service and webhook support for events (e.g. task completion, alerts). See [[Architecture-Overview]] for placement.

---

## Location

- **Path**: `cloud_agents_notifications/`
- **Key files**: `notification_service.py`, `example_launch_with_webhook.py`, `test_notifications.py`, `setup_notifications.sh`, `.env.example`

---

## Components

- **notification_service.py**: Core notification logic; sends to configured channels (e.g. webhook URLs).
- **example_launch_with_webhook.py**: Example of launching or triggering with webhook.
- **test_notifications.py**: Tests for notification delivery.
- **setup_notifications.sh**: Setup script for env and dependencies.
- **.env.example**: Template for API keys and webhook URLs.

---

## Docs in Repo

- **README.md**, **QUICKSTART.md**, **SETUP_GUIDE.md**, **ALL_NOTIFICATION_OPTIONS.md**: Setup, options, and usage.

---

## Related

- [[Agent-System]] — Can be extended to send notifications on task completion.
- [[index]] — Compendium index.
