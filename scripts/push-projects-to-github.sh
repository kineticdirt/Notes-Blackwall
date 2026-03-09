#!/usr/bin/env bash
# Create separate GitHub repos from each project folder so you can work on them independently.
# Prereqs: Git installed. For auto-create and push: install gh and run: gh auth login
# Usage: [GITHUB_USER=yourusername] [USE_GH=1] [PRIVATE=1] ./scripts/push-projects-to-github.sh
#
# USE_GH=1 (default when gh is available): create repo on GitHub and push. Repo name = folder name.
# USE_GH=0: only prepare temp dirs; you create repos manually and push.
# PRIVATE=0: create public repos. Default: private.

set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# All project folders to push as separate repos (order doesn't matter)
PROJECTS=(
  agent-system
  assistant
  blackwall
  cloud_agents_notifications
  compendium
  DaDumpMan
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
)

# Resolve GITHUB_USER: explicit > gh auth status > default
if [ -z "$GITHUB_USER" ]; then
  if command -v gh &>/dev/null && gh auth status &>/dev/null 2>&1; then
    GITHUB_USER="$(gh api user -q .login)"
  fi
  GITHUB_USER="${GITHUB_USER:-kineticdirt}"
fi

# Use gh when available and authenticated (default)
USE_GH="${USE_GH:-}"
if [ -z "$USE_GH" ] && command -v gh &>/dev/null && gh auth status &>/dev/null 2>&1; then
  USE_GH=1
fi
if [ -n "$USE_GH" ]; then
  if ! command -v gh &>/dev/null; then
    echo "USE_GH=1 but gh not found. Install: brew install gh && gh auth login"
    exit 1
  fi
  if ! gh auth status &>/dev/null 2>&1; then
    echo "Run: gh auth login"
    exit 1
  fi
fi

PRIVATE="${PRIVATE:-1}"
VISIBILITY="--private"
[ "$PRIVATE" = "0" ] && VISIBILITY="--public"

ROOT_GITIGNORE="$ROOT/.gitignore"
TMP_BASE="${TMPDIR:-/tmp}/notes-blackwall-push-$$"
mkdir -p "$TMP_BASE"
[ -n "$USE_GH" ] && trap 'rm -rf "$TMP_BASE"' EXIT

echo "GITHUB_USER=$GITHUB_USER  USE_GH=$USE_GH  $VISIBILITY"
echo ""

# Root-level content repo (optional: docs, scripts, test files at workspace root)
ROOT_REPO_NAME="notes-blackwall-root"
echo "--- $ROOT_REPO_NAME ---"
tmp_root="$TMP_BASE/$ROOT_REPO_NAME"
rm -rf "$tmp_root"
mkdir -p "$tmp_root"
cp "$ROOT/.gitignore" "$tmp_root/.gitignore" 2>/dev/null || true
for f in "$ROOT"/*.md "$ROOT"/*.yaml "$ROOT"/*.json "$ROOT"/run_*.py "$ROOT"/worktree_manager.py "$ROOT"/worktree-spec.json "$ROOT"/test_*.py "$ROOT"/test_*.md "$ROOT"/verify_*.py; do
  [ -f "$f" ] && cp "$f" "$tmp_root/"
done
# Don't copy .git from subdirs
if (cd "$tmp_root" && git init -b main && git add -A && ! git diff --cached --quiet 2>/dev/null); then
  (cd "$tmp_root" && git commit -m "Initial commit: $ROOT_REPO_NAME")
  if [ -n "$USE_GH" ]; then
    (cd "$tmp_root" && gh repo create "$ROOT_REPO_NAME" $VISIBILITY --source=. --remote=origin --push) || \
    (cd "$tmp_root" && git remote add origin "https://github.com/${GITHUB_USER}/${ROOT_REPO_NAME}.git" && git push -u origin main)
  else
    echo "1) Create repo: https://github.com/new?name=$ROOT_REPO_NAME"
    echo "2) Push: (cd $tmp_root && git remote add origin https://github.com/$GITHUB_USER/$ROOT_REPO_NAME.git && git push -u origin main)"
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
  # Copy contents but not .git (avoid nested repo)
  (cd "$src" && tar cf - --exclude='.git' .) | (cd "$tmp" && tar xf -)
  if [ -f "$ROOT_GITIGNORE" ] && [ ! -f "$tmp/.gitignore" ]; then
    cp "$ROOT_GITIGNORE" "$tmp/.gitignore"
  fi
  if ! (cd "$tmp" && git init -b main && git add -A && ! git diff --cached --quiet 2>/dev/null); then
    echo "[skip] $repo_name (nothing to commit)"
    continue
  fi
  (cd "$tmp" && git commit -m "Initial commit: $repo_name")
  if [ -n "$USE_GH" ]; then
    if (cd "$tmp" && gh repo create "$repo_name" $VISIBILITY --source=. --remote=origin --push) 2>/dev/null; then
      : # created and pushed
    else
      (cd "$tmp" && git remote add origin "https://github.com/${GITHUB_USER}/${repo_name}.git" 2>/dev/null || true && git push -u origin main)
    fi
  else
    echo "1) Create repo: https://github.com/new?name=$repo_name"
    echo "2) Push: (cd $tmp && git remote add origin https://github.com/$GITHUB_USER/$repo_name.git && git push -u origin main)"
  fi
done

if [ -z "$USE_GH" ]; then
  echo "---"
  echo "Repos prepared in: $TMP_BASE"
  echo "Create each repo on GitHub, then push from the dirs above."
  echo "Remove when done: rm -rf $TMP_BASE"
fi
echo "Done."
