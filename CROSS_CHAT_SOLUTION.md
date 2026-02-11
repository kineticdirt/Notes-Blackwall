# Cross-Chat Communication Solution

## Problem

**How do you get disparate AIs to work together with a single chat, and know that the other person is listening?**

When working with multiple Cursor chat sessions:
- Sessions don't know about each other
- Findings from one chat aren't visible to others
- No way to verify other sessions are active
- No mechanism for discovery or broadcasting

## Solution: Cross-Chat Registry

A shared database system that enables:
1. **Discovery**: Find findings from other chat sessions
2. **Broadcasting**: Share findings without knowing recipients
3. **Verification**: Verify other sessions are "listening" via heartbeats
4. **Persistence**: Findings persist across sessions

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│         Cross-Chat Registry (SQLite Database)           │
│              .crosschat/registry.db                     │
│                                                         │
│  Tables:                                                │
│  - chat_sessions: Active chat sessions                  │
│  - findings: Published findings (discoverable)          │
│  - heartbeats: Activity indicators (for verification)    │
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

## Key Components

### 1. CrossChatBridge

Simple API for chat sessions to use:

```python
from blackwall.worktrees import CrossChatBridge

# Initialize (auto-registers session)
bridge = CrossChatBridge(session_name="My Chat")

# Publish a finding (broadcasting)
bridge.publish(
    title="Found bug in auth",
    content="Token validation issue",
    category="bug",
    tags=["authentication"]
)

# Discover findings from others
findings = bridge.discover(category="bug")

# Verify others are listening
listeners = bridge.verify_listeners()
print(f"{listeners['listener_count']} active sessions")

# Send heartbeat (indicates activity)
bridge.heartbeat()
```

### 2. CrossChatRegistry

Low-level registry for managing the database:

- `register_session()`: Register a chat session
- `publish_finding()`: Store a finding
- `discover_findings()`: Query findings
- `heartbeat()`: Record activity
- `verify_listeners()`: Check active sessions

### 3. Finding Data Structure

```python
@dataclass
class Finding:
    finding_id: str
    chat_session_id: str
    title: str
    content: str
    category: str  # general, code, bug, solution, etc.
    tags: List[str]
    related_files: List[str]
    related_code: Optional[str]
    confidence: float
    created_at: str
    updated_at: str
    metadata: Dict
```

## How It Works

### Discovery (Finding Other Sessions' Findings)

1. Any chat session can query the `findings` table
2. Filter by category, tags, or session ID
3. Results sorted by creation time (newest first)
4. **No need to know who published them**

### Broadcasting (Sharing Without Knowing Recipients)

1. Publish finding to database
2. Finding immediately available to all sessions
3. **No need to know who will read it**

### Verification (Knowing Others Are Listening)

1. Sessions send heartbeats periodically
2. Heartbeats stored with timestamps
3. Query for sessions with recent heartbeats
4. Exclude your own session
5. Result shows active listener count

### Heartbeats (Activity Indicators)

1. Each session sends heartbeat every few minutes
2. Updates `last_seen` timestamp
3. Other sessions can check heartbeats to verify activity
4. Old heartbeats cleaned up automatically

## Usage Examples

### Example 1: Multiple Developers

**Developer A's Chat:**
```python
bridge = CrossChatBridge(session_name="Dev A")

# Discover what others found
findings = bridge.discover(category="bug")
for finding in findings:
    print(f"Known issue: {finding.title}")

# Publish own finding
bridge.publish(
    title="Auth token bug",
    content="Found in auth.py line 42",
    category="bug",
    tags=["authentication"]
)

# Check if others are listening
listeners = bridge.verify_listeners()
print(f"{listeners['listener_count']} other developers active")
```

**Developer B's Chat:**
```python
bridge = CrossChatBridge(session_name="Dev B")

# Automatically discovers Dev A's finding
findings = bridge.discover(category="bug")
# Finds: "Auth token bug" from Dev A

# Can publish related finding
bridge.publish(
    title="Frontend auth flow issue",
    content="Related to backend token validation",
    category="bug",
    tags=["authentication", "frontend"]
)
```

### Example 2: CLI Usage

```bash
# Publish a finding
python -m blackwall.worktrees.cross_chat_cli publish \
  "Found bug" \
  "Token validation issue" \
  --category bug \
  --tags "authentication"

# Discover findings
python -m blackwall.worktrees.cross_chat_cli discover --category bug

# Verify listeners
python -m blackwall.worktrees.cross_chat_cli verify
```

## Integration with Worktrees

The cross-chat system integrates with worktrees:

```python
from blackwall.worktrees import UnifiedWorktreeManager, CrossChatBridge

# Worktree for agent coordination
manager = UnifiedWorktreeManager()
worktree = manager.create_worktree(name="Dev Team")

# Cross-chat for sharing findings
bridge = CrossChatBridge(session_name="Dev Team Chat")

# Agents can publish findings
finding_id = bridge.publish(
    title="Code analysis complete",
    content="Found 5 potential issues",
    category="code"
)

# Other chats can discover these findings
findings = bridge.discover(category="code")
```

## Database Schema

### chat_sessions
- `session_id` (PRIMARY KEY)
- `session_name`
- `last_seen`
- `status` (active/idle/inactive)
- `findings_count`
- `metadata_json`

### findings
- `finding_id` (PRIMARY KEY)
- `chat_session_id`
- `title`
- `content`
- `category`
- `tags_json`
- `related_files_json`
- `related_code`
- `confidence`
- `created_at`
- `updated_at`
- `metadata_json`

### heartbeats
- `heartbeat_id` (PRIMARY KEY AUTOINCREMENT)
- `session_id`
- `timestamp`
- `metadata_json`

## Benefits

1. **No Formal Registration**: Sessions discover each other automatically
2. **Broadcasting**: Share findings without knowing recipients
3. **Verification**: Know others are listening via heartbeats
4. **Persistence**: Findings persist across sessions
5. **Discovery**: Find relevant findings by category/tags
6. **Lightweight**: Simple SQLite database, no complex setup

## Limitations

- **File-based**: Requires shared filesystem access
- **Not Real-time**: Relies on polling/discovery
- **No Direct Messaging**: Findings are broadcast, not direct
- **No Authentication**: Relies on filesystem permissions

## Future Enhancements

- Real-time notifications via file watching
- Topic-based subscriptions
- Finding reactions/comments
- Finding relationships/dependencies
- MCP resource integration
- Webhook support

## Files

- `blackwall/worktrees/cross_chat.py`: Core implementation
- `blackwall/worktrees/cross_chat_cli.py`: CLI interface
- `blackwall/worktrees/cross_chat_example.py`: Example usage
- `blackwall/worktrees/CROSS_CHAT_GUIDE.md`: Full documentation

## Summary

The cross-chat communication system solves the problem of connecting disparate Cursor chat sessions by providing:

1. **Shared Database**: SQLite database accessible to all sessions
2. **Discovery Mechanism**: Query findings by category/tags
3. **Broadcasting**: Publish findings without knowing recipients
4. **Verification**: Heartbeat system to verify active sessions
5. **Simple API**: Easy-to-use `CrossChatBridge` class

This enables multiple AI chat sessions to work together, share findings, and verify each other's presence without formal registration or direct communication channels.
