# Secure secrets (keys outside the repo)

Keep API keys and other secrets in a file **outside** the workspace so they are never in the repo and not in agent context.

## Pattern

1. **Project `.env`** (optional) — In the project root, for non-secret config only. Gitignored.
2. **Secrets file** — A single file elsewhere (e.g. `~/.cequence-rnd/.env`) that holds real keys. Set `CEQUENCE_SECRETS_FILE` to point at it. That file is loaded at startup and **overrides** env; the app never needs to read it again and the path is not in the repo.

`~` in the path is expanded (e.g. `~/.cequence-rnd/.env`).

---

## Assistant (Pi-style runner)

The assistant loads env in two steps before any key access:

1. **Project `.env`** (cwd) if present — applied first (no override of existing env).
2. **`CEQUENCE_SECRETS_FILE`** — if set, that file is loaded and **overrides** existing env.

So you can keep non-secret config in project `.env` and put all API keys in a file outside the workspace.

- **Files:** `assistant/load_secrets.py` runs at import of `assistant.pi_runner`; keys are then available via `os.environ` (e.g. `PI_LLM_API_KEY`, `ANTHROPIC_API_KEY`).
- If the secrets file sets `ANTHROPIC_API_KEY`, the loader also sets `PI_LLM_API_KEY` from it so the assistant can use Claude without naming the key twice.

### How to use (assistant)

1. Create a secrets file outside the repo:
   ```bash
   mkdir -p ~/.cequence-rnd
   # Edit ~/.cequence-rnd/.env and add:
   # ANTHROPIC_API_KEY=sk-ant-api03-...
   ```

2. Point the assistant at it (one of these):
   - In your shell profile: `export CEQUENCE_SECRETS_FILE=~/.cequence-rnd/.env`
   - Or in project `.env` (gitignored): `CEQUENCE_SECRETS_FILE=/Users/you/.cequence-rnd/.env`

3. Run the assistant as usual; it loads the external file at startup and uses keys from env only.

---

## Cursor rule: no secrets access

**`.cursor/rules/no-secrets-access.mdc`** (always applied) instructs the agent to:

- Not read or include `.env`, `.env.*`, or the path in `CEQUENCE_SECRETS_FILE`.
- Not run or suggest commands that print secrets (e.g. `echo $ANTHROPIC_API_KEY`, `cat .env`).
- Not include keys in chat or snippets; use placeholders like `<API_KEY>` or `process.env.ANTHROPIC_API_KEY` / `os.environ.get("PI_LLM_API_KEY")` instead.

So even if a secrets file were in scope, the rule says not to read it or echo it, reducing the chance keys are sent to the model.

---

## Key-holder service (key never to AI or internet)

To **serve the key from a separate process** so the AI and the internet never get access to it: run the **key-holder** service (it holds the key and proxies LLM requests). The assistant then talks only to the key-holder and never receives the key. See **[KEY_HOLDER_SERVICE.md](KEY_HOLDER_SERVICE.md)**.

---

## Summary

| Goal                         | Action |
|-----------------------------|--------|
| Non-secret config in repo   | Optional project `.env` (gitignored). |
| Real keys only outside repo | Create e.g. `~/.cequence-rnd/.env`, set `CEQUENCE_SECRETS_FILE` to that path. |
| Assistant uses Claude       | Put `ANTHROPIC_API_KEY=...` in the secrets file; loader maps it to `PI_LLM_API_KEY`. |
| Agent must not see keys     | Rule: don’t read secrets files or echo env vars that contain keys. |
| Key never to AI or internet | Run key-holder service; assistant points at it and sends no key. See [KEY_HOLDER_SERVICE.md](KEY_HOLDER_SERVICE.md). |
