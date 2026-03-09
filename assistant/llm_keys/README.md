# LLM API keys (file-based)

Put your API key in a **file** so the assistant can read it without using environment variables (e.g. in Kubernetes you mount a Secret as a file).

## Claude (Anthropic)

1. Create a file named `ANTHROPIC_API_KEY` in this directory (or anywhere you prefer).
2. Put your Anthropic API key in it: one line, no quotes, no extra spaces.
3. Point the runner at it:
   - **Env:** `export PI_LLM_API_KEY_FILE=assistant/llm_keys/ANTHROPIC_API_KEY`
   - **Or absolute path:** `export PI_LLM_API_KEY_FILE=/run/secrets/anthropic_api_key` (e.g. in K8s)
4. Use Claude: `export PI_LLM_PROVIDER=anthropic` and `export PI_LLM_MODEL=claude-sonnet-4-5` (or another Claude model).

**Example (local):**
```bash
# Create key file (do not commit this file)
echo "sk-ant-api03-..." > assistant/llm_keys/ANTHROPIC_API_KEY
export PI_LLM_API_KEY_FILE=assistant/llm_keys/ANTHROPIC_API_KEY
export PI_LLM_PROVIDER=anthropic
export PI_LLM_MODEL=claude-sonnet-4-5
python3 -m assistant.pi_runner
```

## OpenAI-compatible (Ollama, OpenAI, LiteLLM)

Use `PI_LLM_API_KEY` env var, or `PI_LLM_API_KEY_FILE` with a path to a file containing the key.  
Use `PI_LLM_PROVIDER=openai` (default) and set `PI_LLM_API_BASE` and `PI_LLM_MODEL`.

## Alternative: secrets file outside the repo

To keep keys completely outside the workspace, use **`CEQUENCE_SECRETS_FILE`**: point it at a file (e.g. `~/.cequence-rnd/.env`) that contains `ANTHROPIC_API_KEY=...`. The assistant loads it at startup and uses env only. See **`docs/runbooks/SECURE_SECRETS.md`**.

## Security

- **Do not commit** the file that contains your real API key.
- This directory is set up so `ANTHROPIC_API_KEY` (and similar key files) are ignored by git; only README and example files are tracked.
