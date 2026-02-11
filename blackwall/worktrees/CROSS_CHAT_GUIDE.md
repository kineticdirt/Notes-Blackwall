# Cross-Chat Communication Guide

## Problem Statement

**How do you get disparate AIs to work together with a single chat, and know that the other person is listening?**

When working with multiple Cursor chat sessions, you need:
1. **Discovery**: Find findings from other chat sessions
2. **Broadcasting**: Share findings without knowing recipients
3. **Verification**: Verify other sessions are active and "listening"
4. **Persistence**: Findings persist across sessions

## Solution: Cross-Chat Registry

The `CrossChatRegistry` provides a shared database where any Cursor chat session can:
- Publish findings
- Discover findings from other sessions
- Send heartbeats to indicate activity
- Verify other sessions are listening

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Cross-Chat Registry (SQLite)               │
│  .crosschat/registry.db                                 │
│                                                         │
│  - chat_sessions: Active chat sessions                  │
│  - findings: Published findings                         │
│  - heartbeats: Activity indicators                      │
│  - subscriptions: Topic subscriptions (optional)        │
└─────────────────────────────────────────────────────────┘
         ▲                    ▲                    ▲
         │                    │                    │
    ┌────┴────┐         ┌────┴────┐         ┌────┴────┐
    │ Chat 1  │         │ Chat 2  │         │ Chat 3  │
    │         │         │         │         │         │
    │ Publishes│         │ Discovers│        │ Verifies │
    │ Findings │         │ Findings │        │ Listeners│
    └──────────┘         └──────────┘         └──────────┘
```

## Usage

### Python API

```python
from blackwall.worktrees.cross_chat import CrossChatBridge

# Initialize bridge (auto-registers session)
bridge = CrossChatBridge(session_name="My Chat Session")

# Publish a finding
finding_id = bridge.publish(
    title="Found bug in authentication",
    content="The login function doesn't validate tokens correctly",
    category="bug",
    tags=["authentication", "security"],
    related_files=["auth.py"],
    confidence=0.9
)

# Discover findings from other chats
findings = bridge.discover(
    category="bug",
    tags=["authentication"],
    limit=10
)

for finding in findings:
    print(f"[{finding.chat_session_id}] {finding.title}")
    print(f"  {finding.content}")

# Verify other sessions are listening
listeners = bridge.verify_listeners()
print(f"Active listeners: {listeners['listener_count']}")

# Send heartbeat (indicates this session is active)
bridge.heartbeat()
```

### CLI

```bash
# Publish a finding
python -m blackwall.worktrees.cross_chat_cli publish \
  "Found bug in auth" \
  "The login function doesn't validate tokens" \
  --category bug \
  --tags "authentication,security" \
  --files "auth.py"

# Discover findings
python -m blackwall.worktrees.cross_chat_cli discover \
  --category bug \
  --tags "authentication"

# Search findings
python -m blackwall.worktrees.cross_chat_cli search "authentication"

# Verify other sessions are listening
python -m blackwall.worktrees.cross_chat_cli verify

# Show stats
python -m blackwall.worktrees.cross_chat_cli stats
```

## How It Works

### 1. Session Registration

When a chat session initializes `CrossChatBridge`, it:
- Generates a unique session ID (or uses provided one)
- Registers itself in the `chat_sessions` table
- Becomes discoverable by other sessions

### 2. Publishing Findings

When you publish a finding:
- Finding is stored in the `findings` table
- Session's `findings_count` is incremented
- Finding becomes immediately discoverable by other sessions
- No need to know who will read it (broadcasting)

### 3. Discovering Findings

When you discover findings:
- Query the `findings` table
- Filter by category, tags, or session
- Results sorted by creation time (newest first)
- No need to know who published them (discovery)

### 4. Verifying Listeners

To verify others are "listening":
- Send a heartbeat (updates `last_seen` timestamp)
- Query for sessions with recent heartbeats
- Exclude your own session
- Result shows active listener count

### 5. Heartbeats

Heartbeats indicate a session is active:
- Stored in `heartbeats` table
- Used to determine "active" sessions
- Old heartbeats are cleaned up automatically
- Other sessions can check heartbeats to verify activity

## Example Workflow

### Scenario: Multiple developers working on the same codebase

**Chat Session 1** (Developer A):
```python
bridge = CrossChatBridge(session_name="Dev A - Auth Work")

# Discover what others have found
findings = bridge.discover(category="bug")
for finding in findings:
    print(f"Known issue: {finding.title}")

# Publish own finding
bridge.publish(
    title="Auth token validation bug",
    content="Found in auth.py line 42",
    category="bug",
    tags=["authentication"]
)

# Verify others are listening
listeners = bridge.verify_listeners()
print(f"{listeners['listener_count']} other developers active")
```

**Chat Session 2** (Developer B):
```python
bridge = CrossChatBridge(session_name="Dev B - Frontend")

# Discover findings from others
findings = bridge.discover(category="bug", tags=["authentication"])
# Finds Dev A's finding about auth token validation

# Publish related finding
bridge.publish(
    title="Frontend auth flow issue",
    content="Related to backend token validation",
    category="bug",
    tags=["authentication", "frontend"]
)

# Both sessions can now see each other's findings
```

## Integration with Worktrees

The cross-chat system can be integrated with worktrees:

```python
from blackwall.worktrees import UnifiedWorktreeManager
from blackwall.worktrees.cross_chat import CrossChatBridge

# Worktree for agent coordination
manager = UnifiedWorktreeManager()
worktree = manager.create_worktree(name="Dev Team")

# Cross-chat for sharing findings
bridge = CrossChatBridge(session_name="Dev Team Chat")

# Agents can publish findings
finding_id = bridge.publish(
    title="Code analysis complete",
    content="Found 5 potential issues",
    category="code",
    related_files=["src/main.py"]
)

# Other chats can discover these findings
findings = bridge.discover(category="code")
```

## Database Schema

### chat_sessions
- `session_id` (PRIMARY KEY): Unique session identifier
- `session_name`: Human-readable name
- `last_seen`: Last heartbeat timestamp
- `status`: active/idle/inactive
- `findings_count`: Number of findings published
- `metadata_json`: Additional metadata

### findings
- `finding_id` (PRIMARY KEY): Unique finding identifier
- `chat_session_id`: Session that published it
- `title`: Finding title
- `content`: Finding content
- `category`: Category (general, code, bug, solution, etc.)
- `tags_json`: Tags for discovery
- `related_files_json`: Related file paths
- `related_code`: Code snippet
- `confidence`: Confidence level (0.0 to 1.0)
- `created_at`: Creation timestamp
- `updated_at`: Update timestamp
- `metadata_json`: Additional metadata

### heartbeats
- `heartbeat_id` (PRIMARY KEY AUTOINCREMENT)
- `session_id`: Session sending heartbeat
- `timestamp`: Heartbeat timestamp
- `metadata_json`: Optional metadata

## Best Practices

1. **Send Heartbeats Regularly**: Send heartbeats every few minutes to indicate activity
2. **Use Descriptive Categories**: Use consistent categories (bug, feature, research, etc.)
3. **Tag Appropriately**: Use tags for better discoverability
4. **Include Context**: Provide file paths and code snippets when relevant
5. **Check Listeners**: Periodically verify others are active before publishing

## Limitations

- **File-based**: Uses SQLite, so all sessions must have access to the same filesystem
- **No Real-time**: Not real-time; relies on polling/discovery
- **No Direct Messaging**: Findings are broadcast, not direct messages
- **No Authentication**: Any session can read/write (relies on filesystem permissions)

## Future Enhancements

- [ ] Real-time notifications via file watching
- [ ] Topic-based subscriptions
- [ ] Finding reactions/comments
- [ ] Finding relationships/dependencies
- [ ] MCP resource integration
- [ ] Webhook support for external integrations
