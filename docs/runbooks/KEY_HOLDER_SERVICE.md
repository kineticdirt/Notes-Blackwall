# Key-holder service: serve the key without exposing it

**Problem:** The assistant (or any app) needs an API key to call a service (e.g. Anthropic). If the key lives in the app process or in env the AI or logs might see it, or it could be exposed to the internet if the app is compromised.

**Solution:** A small **key-holder service** that:

1. Holds the key in one process only (loaded at startup from env or a secrets file).
2. Exposes a **proxy API** (e.g. OpenAI-compatible `/v1/chat/completions`). The assistant sends requests **without** the key; the key-holder adds the key and forwards to the real API, then returns **only** the model response (no key in response).
3. Binds to **localhost or cluster-internal** only, so it is **not** exposed to the internet. Only the assistant (or other trusted callers on the same host/network) can reach it.

The key never leaves the key-holder process. The AI and the client never receive the key.

---

## Architecture

```
[Assistant]  --(no key)-->  [Key-holder :8766]  --(key added)-->  [Anthropic / OpenAI]
     |                            |
     |   POST /v1/chat/...        |   POST with x-api-key / Authorization
     |   messages, tools          |   returns only: content, tool_calls
     |   <-- response only        |   key never in response
```

- **Key-holder:** Listens on `127.0.0.1:8766` (or `KEYHOLDER_HOST` / `KEYHOLDER_PORT`). Loads `ANTHROPIC_API_KEY` (and optionally `OPENAI_API_KEY`) from env or `CEQUENCE_SECRETS_FILE` at startup. Never logs or returns the key.
- **Assistant:** Set `PI_LLM_API_BASE=http://127.0.0.1:8766/v1`, leave `PI_LLM_API_KEY` empty (or unset). Assistant sends requests to the key-holder; key-holder forwards to the real API and returns the response.

---

## When to use

| Scenario | Use key-holder? |
|----------|------------------|
| Key in env or file, only your process uses it | No; env/file + no-secrets rule is enough. |
| You want the AI/assistant to **never** have the key in process | Yes; assistant talks to key-holder only. |
| Key must not be exposed to the internet | Key-holder binds to localhost; do not expose its port. |

---

## Running the key-holder

1. Put the key only in the key-holder’s env or secrets file (e.g. `CEQUENCE_SECRETS_FILE=~/.cequence-rnd/.env` with `ANTHROPIC_API_KEY=...`).
2. Start the key-holder (listens on localhost by default):
   ```bash
   python3 -m assistant.key_holder.server
   ```
3. Point the assistant at it (**no key** in the assistant env):
   ```bash
   export PI_LLM_API_BASE=http://127.0.0.1:8766/v1
   export PI_LLM_MODEL=claude-sonnet-4-5
   export PI_LLM_PROVIDER=openai   # key-holder exposes OpenAI-compatible /v1/chat/completions
   # Do not set PI_LLM_API_KEY or PI_LLM_API_KEY_FILE; the key-holder has the key
   python3 -m assistant.pi_runner
   ```

In Kubernetes, run the key-holder as a sidecar or a separate service in the same cluster; bind to a cluster-internal address and do not expose it via a public LoadBalancer or Ingress.

---

## Security summary

- Key lives only in the key-holder process.
- Key-holder is not exposed to the internet (localhost or in-cluster only).
- Assistant and AI never receive the key; they only get model output from the key-holder.
