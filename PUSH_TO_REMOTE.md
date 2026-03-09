# How to Push Worktree System to Remote Repository

## Quick Start: Push to GitHub/GitLab/etc.

### Step 1: Initialize Git Repository

```bash
cd "/Users/abhinav/Desktop/Notes - Blackwall"

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Worktree system with cross-chat communication"
```

### Step 2: Create Remote Repository

**Option A: GitHub**
1. Go to https://github.com/new
2. Create a new repository (e.g., `Notes-Blackwall`)
3. **Don't** initialize with README (we already have files)

**Option B: GitLab**
1. Go to https://gitlab.com/projects/new
2. Create a new project

**Option C: Other Git Host**
- Follow your provider's instructions

### Step 3: Connect and Push

```bash
# Add remote (replace with your repo URL)
git remote add origin https://github.com/yourusername/Notes-Blackwall.git
# or
git remote add origin git@github.com:yourusername/Notes-Blackwall.git

# Rename branch to main (if needed)
git branch -M main

# Push to remote
git push -u origin main
```

### Step 4: Verify

```bash
# Check remote
git remote -v

# View commits
git log --oneline
```

## What Gets Pushed

✅ **Code Files:**
- `blackwall/worktrees/` - All Python modules
- `.skills/` - Skill definitions (markdown files)
- Documentation files

❌ **Runtime Data (in .gitignore):**
- `.crosschat/` - Cross-chat database (workspace-specific)
- `.worktrees/` - Worktree data (workspace-specific)
- `ledger/` - Agent ledger (workspace-specific)

## How Other Cursor Sessions Use It

### Same Workspace (Automatic)

If another Cursor chat opens in the **same workspace directory**, it automatically shares the database:

```
/Users/abhinav/Desktop/Notes - Blackwall/
├── .crosschat/
│   └── registry.db          ← Automatically shared!
└── ...
```

**No setup needed!** Just use:

```python
from blackwall.worktrees import CrossChatBridge

bridge = CrossChatBridge(session_name="Chat 2")
findings = bridge.discover()  # Finds findings from Chat 1
```

### Different Workspace (Clone Repository)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Notes-Blackwall.git
   cd Notes-Blackwall
   ```

2. **Install dependencies:**
   ```bash
   pip install -r blackwall/requirements.txt
   ```

3. **Use cross-chat:**
   ```python
   from blackwall.worktrees import CrossChatBridge
   
   bridge = CrossChatBridge(session_name="Remote Session")
   bridge.publish(title="Hello", content="From remote session")
   ```

**Note:** Each workspace has its own database by default. To share across workspaces, see `SHARING_GUIDE.md`.

### Shared Database Across Workspaces

If you want multiple workspaces to share findings:

#### Option 1: Symlink to Shared Location

```bash
# Create shared directory
mkdir -p ~/shared-crosschat

# In each workspace, symlink
ln -s ~/shared-crosschat/registry.db .crosschat/registry.db
```

#### Option 2: Use Environment Variable

```python
import os
from pathlib import Path
from blackwall.worktrees.cross_chat import CrossChatRegistry, CrossChatBridge

# Use shared database path
shared_path = os.getenv('CROSSCHAT_SHARED_PATH', '~/.shared-crosschat')
registry = CrossChatRegistry(
    registry_path=Path(shared_path).expanduser() / "registry.db"
)

bridge = CrossChatBridge(session_name="Shared Session")
bridge.registry = registry  # Use shared registry
```

## Example Workflow

### Developer A (Original Workspace)

```bash
cd "/Users/abhinav/Desktop/Notes - Blackwall"

# Publish finding
python -m blackwall.worktrees.cross_chat_cli publish \
  "Found bug" "Token validation issue" \
  --category bug
```

### Developer B (Cloned Repository)

```bash
cd ~/cloned/Notes-Blackwall

# Discover findings
python -m blackwall.worktrees.cross_chat_cli discover --category bug
# Finds Developer A's finding!

# Publish own finding
python -m blackwall.worktrees.cross_chat_cli publish \
  "Solution" "Use JWT validation" \
  --category solution
```

### Developer C (Same Workspace as A)

```bash
cd "/Users/abhinav/Desktop/Notes - Blackwall"

# Automatically sees findings from both A and B
python -m blackwall.worktrees.cross_chat_cli discover
```

## Repository Structure

After pushing, your repo will have:

```
Notes-Blackwall/
├── blackwall/
│   └── worktrees/
│       ├── cross_chat.py          # Cross-chat system
│       ├── cross_chat_cli.py       # CLI
│       ├── worktree.py             # Worktree system
│       ├── worktree_db.py          # Database layer
│       ├── worktree_manager.py    # Unified manager
│       ├── cli.py                  # Worktree CLI
│       ├── README.md               # Documentation
│       ├── CROSS_CHAT_GUIDE.md     # Cross-chat guide
│       └── SHARING_GUIDE.md        # Sharing guide
├── .skills/                        # Skills (nested markdown)
│   ├── code-analysis.md
│   ├── protection.md
│   └── documentation.md
├── CROSS_CHAT_SOLUTION.md          # Solution overview
├── WORKTREE_SYSTEM_COMPLETE.md     # System overview
├── .gitignore                      # Ignores runtime data
└── README.md                       # Main README
```

## Summary

1. **Initialize git**: `git init`
2. **Add files**: `git add .`
3. **Commit**: `git commit -m "Add worktree system"`
4. **Add remote**: `git remote add origin <your-repo-url>`
5. **Push**: `git push -u origin main`

**For other Cursor sessions:**
- **Same workspace**: Works automatically (shared database)
- **Different workspace**: Clone repo, use own database or configure shared path
- **Multiple users**: Configure shared database location

The cross-chat system is designed to work seamlessly across Cursor sessions!
