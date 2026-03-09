# Running the assistant as part of the system

The assistant (Pi-style runner) is a first-class component of Cequence BlackWall. Run it together with the optional key-holder so the stack is up with one command.

---

## What runs

| Component    | Port | Role |
|-------------|------|------|
| **Key-holder** (optional) | 8766 | Holds API key; proxies LLM requests. Assistant sends no key. |
| **Assistant**             | 8765 | Gate → LLM + tools + preferences + MCP; POST `/message` for chat. |

Other parts of the system (workflow-canvas, agents, etc.) can call the assistant at `http://localhost:8765/message` when the assistant is running.

---

## Option 1: Run script (local)

From repo root:

```bash
./scripts/run-assistant-system.sh
```

This starts:

1. **Key-holder** (if `CEQUENCE_SECRETS_FILE` or `ANTHROPIC_API_KEY` is set) on 127.0.0.1:8766
2. **Assistant** in daemon mode on 8765, pointing at the key-holder so it never sees the key

Requires: `CEQUENCE_SECRETS_FILE` (or `ANTHROPIC_API_KEY`) for the key-holder. The assistant uses `PI_LLM_API_BASE=http://127.0.0.1:8766/v1`, `PI_LLM_PROVIDER=openai`, `PI_LLM_MODEL=claude-sonnet-4-5`.

To run **without** the key-holder (key in env or file on the assistant process):

```bash
export PI_LLM_PROVIDER=anthropic
export PI_LLM_MODEL=claude-sonnet-4-5
export CEQUENCE_SECRETS_FILE=~/.cequence-rnd/.env
python3 -m assistant.pi_runner --daemon
```

---

## Option 2: Docker Compose

From repo root:

```bash
docker compose -f docker-compose.assistant.yaml up --build
```

Runs key-holder + assistant as services. Secrets via env file or `CEQUENCE_SECRETS_FILE` mount. See `docker-compose.assistant.yaml` for ports and env.

---

## Option 3: Kubernetes

See `assistant/k8s/`: deploy key-holder (optional) and assistant; assistant can use key-holder URL or a mounted secret for the key.

---

## Using the assistant from the system

- **HTTP**: `POST http://localhost:8765/message` with `{"message": "Your text"}` → `{"reply": "..."}`.
- **REPL**: Run `python3 -m assistant.pi_runner` (no `--daemon`) for an interactive prompt; same process as above but stdin/stdout.

Workflow-canvas or any service can call the assistant by POSTing to the assistant URL when it is part of the running system.
