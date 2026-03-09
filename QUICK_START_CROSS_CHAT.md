# Quick Start: Cross-Chat Communication

## How It Works

The cross-chat system enables **multiple Cursor chat sessions** to share findings and verify each other are listening, **without formal registration**.

### Same Workspace (Automatic) ✅

If you open **another Cursor chat** in the same workspace, it automatically shares the database:

```python
# Chat Session 1
from blackwall.worktrees import CrossChatBridge
bridge1 = CrossChatBridge(session_name="Chat 1")
bridge1.publish(title="Found bug", content="Token issue", category="bug")

# Chat Session 2 (same workspace, different Cursor window)
bridge2 = CrossChatBridge(session_name="Chat 2")
findings = bridge2.discover()  # Automatically finds Chat 1's finding!
```

**No setup needed** - it just works!

### Different Workspace (Clone Repository)

1. **Push to remote:**
   ```bash
   git add .
   git commit -m "Add worktree and cross-chat system"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Other user clones:**
   ```bash
   git clone <your-repo-url>
   cd Notes-Blackwall
   pip install -r blackwall/requirements.txt
   ```

3. **Use cross-chat:**
   ```python
   from blackwall.worktrees import CrossChatBridge
   bridge = CrossChatBridge(session_name="Remote Session")
   bridge.publish(title="Hello", content="From remote")
   ```

**Note:** Each workspace has its own database by default. To share across workspaces, configure a shared database path (see `SHARING_GUIDE.md`).

## Quick Commands

### Publish a Finding
```bash
python -m blackwall.worktrees.cross_chat_cli publish \
  "Found bug" "Token validation issue" \
  --category bug --tags "authentication"
```

### Discover Findings
```bash
python -m blackwall.worktrees.cross_chat_cli discover --category bug
```

### Verify Listeners
```bash
python -m blackwall.worktrees.cross_chat_cli verify
```

### Python API
```python
from blackwall.worktrees import CrossChatBridge

bridge = CrossChatBridge(session_name="My Session")

# Publish
bridge.publish(
    title="Finding",
    content="Details",
    category="bug",
    tags=["tag1", "tag2"]
)

# Discover
findings = bridge.discover(category="bug")

# Verify
listeners = bridge.verify_listeners()
print(f"{listeners['listener_count']} active sessions")
```

## Pushing to Remote

```bash
# Initialize (if not done)
git init

# Add files
git add .

# Commit
git commit -m "Add worktree system with cross-chat"

# Add remote
git remote add origin https://github.com/yourusername/repo.git

# Push
git push -u origin main
```

See `PUSH_TO_REMOTE.md` for detailed instructions.

## Key Points

1. **Same workspace**: Works automatically - all Cursor sessions share database
2. **Different workspace**: Clone repo, each has own database (or configure shared)
3. **No registration**: Sessions discover each other automatically
4. **Broadcasting**: Publish findings without knowing recipients
5. **Verification**: Heartbeats show active sessions

The system is ready to use! 🚀
