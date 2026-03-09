# Git Repository Setup Guide

## Do You Need a GitHub Repo?

**Short answer**: No, but it's highly recommended for:
- ✅ **Backup**: Protect your code from local machine failures
- ✅ **Sharing**: Share with other Cursor sessions/users
- ✅ **Version Control**: Track changes over time
- ✅ **Collaboration**: Multiple developers can work together
- ✅ **Cross-Chat**: Other Cursor sessions can clone and use the system

## Current Status

You have:
- ✅ Local git repository initialized
- ✅ Files staged (ready to commit)
- ❌ No commits yet
- ❌ No remote repository

## Options

### Option 1: Local Only (No Remote)

**Use case**: Personal use, single machine

```bash
# Just commit locally
git commit -m "Add worktree system with coordination"
```

**Pros**: Simple, no setup needed
**Cons**: No backup, can't share, single point of failure

### Option 2: GitHub (Recommended)

**Use case**: Backup, sharing, collaboration

**Steps:**

1. **Create initial commit:**
   ```bash
   git commit -m "Initial commit: Worktree system with cross-chat communication and agent coordination"
   ```

2. **Create GitHub repository:**
   - Go to https://github.com/new
   - Repository name: `Cequence-BlackWall` (or your choice)
   - Description: "Worktree system for organizing AI agents with cross-chat communication"
   - **Don't** initialize with README (you already have files)
   - Click "Create repository"

3. **Connect and push:**
   ```bash
   # Add remote (replace YOUR_USERNAME with your GitHub username)
   git remote add origin https://github.com/YOUR_USERNAME/Cequence-BlackWall.git
   
   # Or use SSH (if you have SSH keys set up)
   git remote add origin git@github.com:YOUR_USERNAME/Cequence-BlackWall.git
   
   # Push to GitHub
   git push -u origin main
   ```

**Pros**: 
- Free backup
- Easy sharing
- Version history
- Collaboration features
- Other Cursor sessions can clone it

**Cons**: 
- Requires GitHub account (free)
- Public repos are visible (use private if needed)

### Option 3: Private GitHub Repo

**Use case**: Want backup/sharing but keep code private

1. Create repo as above
2. Select **"Private"** when creating
3. Only you (and collaborators you add) can see it

### Option 4: GitLab / Bitbucket / Other

**Use case**: Prefer different platform

- **GitLab**: https://gitlab.com/projects/new (free private repos)
- **Bitbucket**: https://bitbucket.org/repo/create (free private repos)
- Same process: create repo, add remote, push

## Quick Setup Script

Create `setup_git.sh`:

```bash
#!/bin/bash

echo "Setting up Git repository..."

# Commit staged files
git commit -m "Initial commit: Worktree system with cross-chat communication and agent coordination

Features:
- Worktrees for organizing multiple agents
- Skills system with nested markdown files
- Cross-chat communication for disparate sessions
- Agent coordination with timeout and hanging detection
- Database layer for UI and task tracking"

echo "✓ Committed files"

# Check if remote exists
if git remote get-url origin 2>/dev/null; then
    echo "✓ Remote already configured"
    REMOTE_URL=$(git remote get-url origin)
    echo "  Remote: $REMOTE_URL"
else
    echo ""
    echo "To add remote repository:"
    echo "  git remote add origin https://github.com/YOUR_USERNAME/Cequence-BlackWall.git"
    echo "  git push -u origin main"
fi

echo ""
echo "Done!"
```

Run it:
```bash
chmod +x setup_git.sh
./setup_git.sh
```

## For Cross-Chat System

If you want **other Cursor sessions** to use the cross-chat system:

### Same Machine (Different Workspace)
- **No GitHub needed**: Just clone locally
  ```bash
  cd ~/other-workspace
  git clone /Users/abhinav/Desktop/Cequence\ BlackWall ./Cequence-BlackWall
  ```

### Different Machines
- **GitHub recommended**: Clone from remote
  ```bash
  git clone https://github.com/YOUR_USERNAME/Cequence-BlackWall.git
  cd Cequence-BlackWall
  pip install -r blackwall/requirements.txt
  ```

### Shared Database Across Machines
- Use shared database path (see `SHARING_GUIDE.md`)
- Or use network share/cloud sync for `.crosschat/registry.db`

## Recommended: GitHub Private Repo

**Best option for most users:**

1. **Create private GitHub repo** (free)
2. **Push your code** (backup + version control)
3. **Clone on other machines** (if needed)
4. **Share with team** (add collaborators if needed)

## What Gets Pushed

✅ **Code Files:**
- `blackwall/worktrees/` - All Python modules
- `.skills/` - Skill definitions
- Documentation files

❌ **Runtime Data** (in `.gitignore`):
- `.crosschat/` - Cross-chat database (workspace-specific)
- `.worktrees/` - Worktree data (workspace-specific)
- `ledger/` - Agent ledger (workspace-specific)
- `__pycache__/` - Python cache

## Next Steps

1. **Decide**: Local only or GitHub?
2. **If GitHub**: Create repo, add remote, push
3. **If local only**: Just commit locally

**Recommendation**: Use GitHub (private repo) for backup and future sharing.
