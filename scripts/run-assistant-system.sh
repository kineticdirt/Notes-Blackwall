#!/usr/bin/env bash
# Run the assistant as part of the system: key-holder (optional) + assistant.
# From repo root: ./scripts/run-assistant-system.sh
# Requires: CEQUENCE_SECRETS_FILE or ANTHROPIC_API_KEY for key-holder (if using Claude).

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

KEYHOLDER_PID=""
cleanup() {
  if [ -n "$KEYHOLDER_PID" ]; then
    kill "$KEYHOLDER_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

# Use key-holder if we have a secrets source: env vars or air-gapped config (assistant/config/user_config.yaml)
USE_KEYHOLDER=
if [ -n "$CEQUENCE_SECRETS_FILE" ] || [ -n "$ANTHROPIC_API_KEY" ]; then
  USE_KEYHOLDER=1
fi
if [ -f "$ROOT/assistant/config/user_config.yaml" ]; then
  USE_KEYHOLDER=1
fi
if [ -n "$USE_KEYHOLDER" ]; then
  echo "Starting key-holder on 127.0.0.1:8766..."
  python3 -m assistant.key_holder.server &
  KEYHOLDER_PID=$!
  sleep 1
  export PI_LLM_API_BASE="http://127.0.0.1:8766/v1"
  export PI_LLM_PROVIDER="openai"
  export PI_LLM_MODEL="${PI_LLM_MODEL:-claude-sonnet-4-5}"
  unset PI_LLM_API_KEY
  unset PI_LLM_API_KEY_FILE
else
  echo "No key source. Add key to assistant/config/user_config.yaml or set CEQUENCE_SECRETS_FILE / ANTHROPIC_API_KEY."
fi

echo "Starting assistant on port 8765 (POST /message)..."
echo "Config file (keys + MCP): $ROOT/assistant/config/user_config.yaml"
exec python3 -m assistant.pi_runner --daemon
