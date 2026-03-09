#!/usr/bin/env bash
# Paste your GitHub PAT below between the quotes, save, then run: ./scripts/setup-github-pat.sh
# Remove the token from this file before committing (or leave it empty and use the prompt).

# ↓↓↓ PASTE YOUR TOKEN BETWEEN THE QUOTES ↓↓↓
GITHUB_PAT=""
# ↑↑↑ PASTE YOUR TOKEN BETWEEN THE QUOTES ↑↑↑

set -e

GITHUB_USER="${GITHUB_USER:-kineticdirt}"
GITHUB_HOST="github.com"

echo "GitHub PAT setup (HTTPS) — account: ${GITHUB_USER}"
echo "---------------------------------------------------"

# Ensure credential helper is set
if ! git config --global credential.helper >/dev/null 2>&1; then
  if [[ "$OSTYPE" == darwin* ]]; then
    git config --global credential.helper osxkeychain
    echo "Set credential.helper to osxkeychain (macOS Keychain)."
  else
    git config --global credential.helper store
    echo "Set credential.helper to store (~/.git-credentials)."
  fi
  echo ""
fi

TOKEN="$GITHUB_PAT"
if [[ -z "$TOKEN" ]]; then
  echo "No token in script. Paste your GitHub PAT below (input hidden), then Enter."
  printf "Token: "
  read -rs TOKEN
  echo ""
fi

if [[ -z "$TOKEN" ]]; then
  echo "No token entered. Exiting."
  exit 1
fi

# Feed token to git credential helper
printf "protocol=https\nhost=%s\nusername=%s\npassword=%s\n" "$GITHUB_HOST" "$GITHUB_USER" "$TOKEN" \
  | git credential approve

# Use plain HTTPS URL (no user@ in URL — that can cause "Bad hostname")
# Default: Cequence-BlackWall (monorepo). For a standalone repo set REPO_NAME e.g. REPO_NAME=DaDumpMan
REPO_NAME="${REPO_NAME:-Cequence-BlackWall}"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git remote set-url origin "https://${GITHUB_HOST}/${GITHUB_USER}/${REPO_NAME}.git" 2>/dev/null || true
  git config credential.https://github.com.username "$GITHUB_USER"
  echo "Set origin to https://${GITHUB_HOST}/${GITHUB_USER}/${REPO_NAME}.git"
fi

echo "Done. Credential stored for https://${GITHUB_HOST} as ${GITHUB_USER}."
echo "Run: git push -u origin main"
unset TOKEN
unset GITHUB_PAT
