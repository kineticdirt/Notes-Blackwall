# Runbooks

| Doc | Purpose |
|-----|---------|
| [SECURE_SECRETS.md](SECURE_SECRETS.md) | Keep API keys outside the repo; use `CEQUENCE_SECRETS_FILE` and the no-secrets Cursor rule. |
| [KEY_HOLDER_SERVICE.md](KEY_HOLDER_SERVICE.md) | Serve the key from a local proxy so the AI and the internet never get access to it. |
| [RUN_ASSISTANT_SYSTEM.md](RUN_ASSISTANT_SYSTEM.md) | Run the assistant as part of the system (key-holder + assistant, script or docker-compose). |
