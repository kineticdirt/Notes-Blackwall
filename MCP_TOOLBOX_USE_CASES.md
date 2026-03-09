# MCP Toolbox Use Cases for Our System

## Summary

[MCP Toolbox for Databases](https://github.com/googleapis/genai-toolbox) enables AI agents to query our SQLite databases using natural language. This transforms our worktree system into an AI-queryable knowledge base.

## Key Use Cases

### 1. **AI-Powered Kanban Board Queries**

**Problem**: AI agents need to interact with Kanban boards programmatically

**Solution**: Define SQL tools that expose Kanban card data

**Example Tool**:
```yaml
kind: tools
name: get_kanban_cards
type: postgres-sql
source: kanban-db
description: Get Kanban cards by status
parameters:
  - name: status
    type: string
statement: SELECT * FROM cards WHERE status = $1
```

**AI Can Ask**:
- "Show me all high-priority cards in progress"
- "What cards are assigned to agent-1?"
- "List all cards with tag 'bug'"

**Benefit**: Natural language interaction with Kanban boards

### 2. **Cross-Chat Discovery**

**Problem**: AI needs to discover findings from other sessions

**Solution**: Query cross-chat findings database

**Example Tool**:
```yaml
kind: tools
name: get_cross_chat_findings
type: postgres-sql
source: crosschat-db
description: Get findings by category
parameters:
  - name: category
    type: string
statement: SELECT * FROM findings WHERE category = $1
```

**AI Can Ask**:
- "What bugs have other sessions found?"
- "Show me all findings related to authentication"
- "What solutions have been discovered?"

**Benefit**: AI can leverage collective knowledge from all sessions

### 3. **Workflow Status Monitoring**

**Problem**: AI needs to check workflow execution status

**Solution**: Query workflow database

**Example Tool**:
```yaml
kind: tools
name: get_workflow_status
type: postgres-sql
source: workflows-db
description: Get workflow execution status
parameters:
  - name: dag_id
    type: string
statement: SELECT * FROM workflow_executions WHERE dag_id = $1
```

**AI Can Ask**:
- "What workflows are currently running?"
- "Show me failed workflow executions"
- "What's the status of the deployment workflow?"

**Benefit**: Real-time workflow monitoring and status checks

### 4. **Task Performance Analysis**

**Problem**: AI needs to analyze task patterns and optimize

**Solution**: Complex SQL queries for analytics

**Example Tool**:
```yaml
kind: tools
name: analyze_task_performance
type: postgres-sql
source: worktree-db
description: Analyze task completion times by agent
statement: |
  SELECT agent_id, 
         AVG(duration_seconds) as avg_duration,
         COUNT(*) as task_count
  FROM task_completions
  GROUP BY agent_id
  ORDER BY avg_duration
```

**AI Can Ask**:
- "Which agents complete tasks fastest?"
- "What's the average task completion time?"
- "Which agents handle high-priority tasks?"

**Benefit**: Data-driven agent optimization

### 5. **Resource Discovery**

**Problem**: AI needs to find related markdown files

**Solution**: Query resources table

**Example Tool**:
```yaml
kind: tools
name: get_card_resources
type: postgres-sql
source: kanban-db
description: Get resources linked to a card
parameters:
  - name: card_id
    type: string
statement: SELECT * FROM resources WHERE card_id = $1
```

**AI Can Ask**:
- "What markdown files are linked to this card?"
- "Show me all resources for the authentication card"
- "What documentation exists for this task?"

**Benefit**: Context-aware resource access

### 6. **Worktree Task Management**

**Problem**: AI needs to query and manage worktree tasks

**Solution**: Query worktree database

**Example Tool**:
```yaml
kind: tools
name: get_worktree_tasks
type: postgres-sql
source: worktree-db
description: Get tasks for a worktree
parameters:
  - name: worktree_id
    type: string
statement: SELECT * FROM tasks WHERE worktree_id = $1
```

**AI Can Ask**:
- "What tasks are pending in worktree wt-123?"
- "Show me all completed tasks"
- "What's the status of task task-456?"

**Benefit**: Unified task management across worktrees

## Integration Architecture

```
┌─────────────────────────────────────────────────────────┐
│              AI Agent (Claude, GPT, etc.)               │
│                                                         │
│  "Show me all high-priority bugs"                      │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│            MCP Toolbox Server                          │
│                                                         │
│  - Receives natural language query                     │
│  - Maps to SQL tool                                    │
│  - Executes query                                      │
│  - Returns results                                     │
└─────────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Kanban DB   │ │ Cross-Chat  │ │  Workflows   │
│  (SQLite)    │ │    DB       │ │     DB       │
└──────────────┘ └──────────────┘ └──────────────┘
```

## Example Workflow

1. **AI receives task**: "Find all high-priority bugs and create Kanban cards"

2. **AI uses Toolbox**:
   ```python
   # Query cross-chat findings
   findings_tool = await client.load_tool("get_cross_chat_findings")
   bugs = await findings_tool.execute({"category": "bug"})
   
   # Filter high-priority
   high_priority_bugs = [b for b in bugs if b.get('priority', 0) >= 8]
   
   # Create Kanban cards
   for bug in high_priority_bugs:
       create_card_tool.execute({
           "title": bug['title'],
           "status": "todo",
           "priority": bug['priority']
       })
   ```

3. **AI completes task**: All bugs are now in Kanban board

## Benefits Summary

✅ **Natural Language**: AI can query databases using plain English  
✅ **Unified Access**: All databases accessible through one interface  
✅ **Framework Agnostic**: Works with LangChain, LlamaIndex, Genkit, etc.  
✅ **Type Safety**: SQL tools have defined schemas  
✅ **Security**: Centralized database access control  
✅ **Real-time**: Direct database access for up-to-date information  
✅ **Extensible**: Easy to add new SQL tools  

## Quick Start

1. **Install Toolbox**:
   ```bash
   npx @toolbox-sdk/server --tools-file toolbox_test/tools.yaml
   ```

2. **Install Python SDK**:
   ```bash
   pip install toolbox-core
   ```

3. **Use in Code**:
   ```python
   from toolbox_core import ToolboxClient
   
   async with ToolboxClient("http://127.0.0.1:5000") as client:
       tools = await client.load_toolset("worktree_toolset")
       # Use tools with your AI framework
   ```

## Configuration

See `toolbox_test/tools.yaml` for complete configuration with:
- SQLite source connections
- Tools for Kanban, worktrees, cross-chat, workflows
- Toolsets for easy loading

## Conclusion

MCP Toolbox transforms our worktree system into an **AI-queryable knowledge base**. AI agents can:
- Query Kanban boards naturally
- Discover cross-chat findings
- Monitor workflows
- Analyze performance
- Find resources

All through natural language, making our system truly AI-native! 🚀
