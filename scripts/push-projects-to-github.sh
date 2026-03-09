#!/usr/bin/env bash
# Push each project folder to its own GitHub repo.
# Prereqs: Git installed. For auto-create: install gh and run: gh auth login
# Usage: GITHUB_USER=yourusername [USE_GH=1] ./scripts/push-projects-to-github.sh

set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Project folders to push as separate repos (all local content, task-based)
PROJECTS=(
  agent-system
  assistant
  blackwall
  cloud_agents_notifications
  compendium
  docs
  grainrad-poc
  hooks
  library
  nightshade-tracker
  orchestrator-node
  overseer
  scripts
  toolbox_test
  website-reinterpretation
  workflow-canvas
  worktree-orchestration
  worktree-orchestration-v2
  worktrees
  ledger
)

if [ -z "$GITHUB_USER" ]; then
  echo "Set GITHUB_USER (e.g. export GITHUB_USER=yourusername)"
  exit 1
fi

USE_GH="${USE_GH:-}"
if [ -n "$USE_GH" ]; then
  if ! command -v gh &>/dev/null; then
    echo "USE_GH=1 but gh not found. Install: brew install gh && gh auth login"
    exit 1
  fi
  if ! gh auth status &>/dev/null; then
    echo "Run: gh auth login"
    exit 1
  fi
fi

# Ensure root .gitignore is used so we never push .env / secrets
ROOT_GITIGNORE="$ROOT/.gitignore"
TMP_BASE="${TMPDIR:-/tmp}/cequence-push-$$"
mkdir -p "$TMP_BASE"
# Only auto-clean when using gh (pushed in same run). Otherwise leave for manual push.
[ -n "$USE_GH" ] && trap 'rm -rf "$TMP_BASE"' EXIT

# Root-level content repo (docs, scripts, test files at workspace root)
ROOT_REPO_NAME="cequence-blackwall-root"
echo "--- $ROOT_REPO_NAME ---"
tmp_root="$TMP_BASE/$ROOT_REPO_NAME"
rm -rf "$tmp_root"
mkdir -p "$tmp_root"
cp "$ROOT/.gitignore" "$tmp_root/.gitignore" 2>/dev/null || true
for f in "$ROOT"/*.md "$ROOT"/*.yaml "$ROOT"/*.json "$ROOT"/run_*.py "$ROOT"/worktree_manager.py "$ROOT"/test_*.py "$ROOT"/test_*.md "$ROOT"/verify_*.py; do
  [ -f "$f" ] && cp "$f" "$tmp_root/"
done
(cd "$tmp_root" && git init -b main && git add -A && git status -s)
if ! (cd "$tmp_root" && git diff --cached --quiet 2>/dev/null); then
  (cd "$tmp_root" && git commit -m "Initial commit: $ROOT_REPO_NAME")
  if [ -n "$USE_GH" ]; then
    (cd "$tmp_root" && gh repo create "$ROOT_REPO_NAME" --private --source=. --remote=origin --push)
  else
    echo "1) Create repo: https://github.com/new?name=$ROOT_REPO_NAME"
    echo "2) Push: (cd $tmp_root && git remote add origin git@github.com:$GITHUB_USER/$ROOT_REPO_NAME.git && git push -u origin main)"
  fi
else
  echo "[skip] $ROOT_REPO_NAME (nothing to commit)"
fi

for name in "${PROJECTS[@]}"; do
  src="$ROOT/$name"
  if [ ! -d "$src" ]; then
    echo "[skip] $name (no such folder)"
    continue
  fi
  repo_name="$name"
  echo "--- $repo_name ---"
  tmp="$TMP_BASE/$repo_name"
  rm -rf "$tmp"
  mkdir -p "$tmp"
  cp -R "$src"/. "$tmp"
  if [ -f "$ROOT_GITIGNORE" ] && [ ! -f "$tmp/.gitignore" ]; then
    cp "$ROOT_GITIGNORE" "$tmp/.gitignore"
  fi
  (cd "$tmp" && git init -b main && git add -A && git status -s)
  if ! (cd "$tmp" && git diff --cached --quiet); then
    (cd "$tmp" && git commit -m "Initial commit: $repo_name")
  else
    echo "[skip] $repo_name (nothing to commit)"
    continue
  fi
  if [ -n "$USE_GH" ]; then
    (cd "$tmp" && gh repo create "$repo_name" --private --source=. --remote=origin --push)
  else
    echo "1) Create repo: https://github.com/new?name=$repo_name"
    echo "2) Push: (cd $tmp && git remote add origin git@github.com:$GITHUB_USER/$repo_name.git && git push -u origin main)"
  fi
done

if [ -z "$USE_GH" ]; then
  echo "---"
  echo "Repos are in: $TMP_BASE"
  echo "After pushing each, remove with: rm -rf $TMP_BASE"
fi
echo "Done."
