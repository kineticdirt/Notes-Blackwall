#!/usr/bin/env bash
# Copy any related secrets/config from ~/.cequence-rnd into assistant/config/ (air-gap: only here).
# Run from repo root: ./scripts/move-cequence-rnd-here.sh

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG_DIR="$ROOT/assistant/config"
CEQUENCE_RND="${CEQUENCE_RND:-$HOME/.cequence-rnd}"

mkdir -p "$CONFIG_DIR"

# Copy .env or anthropic key from cequence-rnd into assistant/config/secrets.env
if [ -f "$CEQUENCE_RND/.env" ]; then
  cp "$CEQUENCE_RND/.env" "$CONFIG_DIR/secrets.env"
  echo "Copied $CEQUENCE_RND/.env -> assistant/config/secrets.env"
fi
if [ -d "$CEQUENCE_RND" ] && [ ! -f "$CONFIG_DIR/secrets.env" ]; then
  for f in "$CEQUENCE_RND"/anthropic_key "$CEQUENCE_RND"/ANTHROPIC_API_KEY "$CEQUENCE_RND"/.env; do
    if [ -f "$f" ]; then
      cp "$f" "$CONFIG_DIR/secrets.env"
      echo "Copied $f -> assistant/config/secrets.env"
      break
    fi
  done
fi

# Ensure user_config.yaml exists
USER_CONFIG="$CONFIG_DIR/user_config.yaml"
if [ ! -f "$USER_CONFIG" ]; then
  cp "$CONFIG_DIR/user_config.example.yaml" "$USER_CONFIG"
  echo "Created assistant/config/user_config.yaml from example"
fi
if [ -f "$CONFIG_DIR/secrets.env" ] && ! grep -q "assistant/config/secrets.env" "$USER_CONFIG" 2>/dev/null; then
  echo "" >> "$USER_CONFIG"
  echo "# Air-gap: secrets only in this repo" >> "$USER_CONFIG"
  echo "anthropic_api_key_path: \"assistant/config/secrets.env\"" >> "$USER_CONFIG"
  echo "Pointed user_config.yaml at assistant/config/secrets.env (local only)"
fi

echo "Config and secrets are now only under: $CONFIG_DIR"
echo "Edit keys and MCP here: $USER_CONFIG"
