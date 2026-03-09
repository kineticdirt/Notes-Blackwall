# Air-gap: keys and MCP only here

All config and secrets live **only** in this directory. Do not use paths outside the repo (e.g. `~/.cequence-rnd`). To bring over anything from `~/.cequence-rnd`, run from repo root:

```bash
./scripts/move-cequence-rnd-here.sh
```

1. **Config file:** `user_config.yaml` (copy from `user_config.example.yaml` if needed).

2. **Edit `user_config.yaml`:**
   - **anthropic_api_key:** Paste your Anthropic API key, or use **anthropic_api_key_path** pointing to a file in this dir, e.g. `assistant/config/secrets.env`.
   - **mcp_servers:** Add MCP servers (each needs `id` and `command`+`args` or `url`).

3. **Secrets file (optional):** Put a key in `assistant/config/secrets.env` (one line or `ANTHROPIC_API_KEY=...`). Then set `anthropic_api_key_path: "assistant/config/secrets.env"` in `user_config.yaml`. Both are gitignored.

The HTTP API never returns your key; see `assistant/API.md`.
