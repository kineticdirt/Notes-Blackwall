# MCP Toolbox Integration Guide

## Overview

[MCP Toolbox for Databases](https://github.com/googleapis/genai-toolbox) is an open-source MCP server that enables AI agents to interact with databases through natural language. This document explores how it integrates with our worktree system.

## What is MCP Toolbox?

MCP Toolbox provides:
- **Database connectivity**: Connect to various databases (PostgreSQL, MySQL, SQLite, etc.)
- **Tool definitions**: Define SQL queries as tools that AI can use
- **MCP protocol**: Standard protocol for AI-database interaction
- **Framework integration**: Works with LangChain, LlamaIndex, Genkit, etc.

## Integration with Our System

Our system uses SQLite databases for:
- `.worktrees/worktree.db` - Worktree and task tracking
- `.kanban/kanban.db` - Kanban board state
- `.crosschat/registry.db` - Cross-chat findings
- `.workflows/workflows.db` - Workflow executions

**MCP Toolbox can make all these databases queryable by AI agents!**

## Use Cases

### 1. AI-Powered Kanban Board Queries

**Problem**: AI agents need to query Kanban boards programmatically

**Solution**: Define SQL tools for Kanban operations

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

**AI can now ask**: "Show me all high-priority cards in progress"

### 2. Cross-Chat Discovery

**Problem**: AI needs to discover findings from other sessions

**Solution**: Query cross-chat findings database

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

**AI can now ask**: "What bugs have other sessions found?"

### 3. Workflow Status Monitoring

**Problem**: AI needs to check workflow execution status

**Solution**: Query workflow database

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

**AI can now ask**: "What workflows are currently running?"

### 4. Task Analysis

**Problem**: AI needs to analyze task patterns

**Solution**: Complex SQL queries for analytics

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

**AI can now ask**: "Which agents complete tasks fastest?"

### 5. Resource Discovery

**Problem**: AI needs to find related markdown files

**Solution**: Query resources table

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

**AI can now ask**: "What markdown files are linked to this card?"

## Configuration Example

See `toolbox_test/tools.yaml` for a complete configuration that:
- Connects to our SQLite databases
- Defines tools for Kanban, worktrees, cross-chat, and workflows
- Groups tools into toolsets for easy loading

## Installation

### 1. Install Toolbox Server

```bash
# Using npx (quick test)
npx @toolbox-sdk/server --tools-file toolbox_test/tools.yaml

# Or install binary
export VERSION=0.26.0
curl -L -o toolbox https://storage.googleapis.com/genai-toolbox/v$VERSION/darwin/arm64/toolbox
chmod +x toolbox
./toolbox --tools-file toolbox_test/tools.yaml
```

### 2. Install Python SDK

```bash
pip install toolbox-core
```

### 3. Use in Python

```python
from toolbox_core import ToolboxClient

async with ToolboxClient("http://127.0.0.1:5000") as client:
    # Load worktree tools
    tools = await client.load_toolset("worktree_toolset")
    
    # Use tools with your AI framework
    for tool in tools:
        print(f"{tool.name()}: {tool.description()}")
```

## Integration with Our Components

### Kanban Board

```python
# AI can query Kanban cards
tool = await client.load_tool("get_kanban_cards")
result = await tool.execute({"status": "in_progress"})
```

### Cross-Chat

```python
# AI can discover findings
tool = await client.load_tool("get_cross_chat_findings")
result = await tool.execute({"category": "bug"})
```

### Worktrees

```python
# AI can get worktree tasks
tool = await client.load_tool("get_worktree_tasks")
result = await tool.execute({"worktree_id": "wt-123"})
```

## Benefits

1. **Natural Language**: AI can query databases using natural language
2. **Unified Access**: All our databases accessible through one interface
3. **Framework Agnostic**: Works with LangChain, LlamaIndex, Genkit, etc.
4. **Type Safety**: SQL tools have defined schemas
5. **Security**: Centralized database access control

## Example: AI Agent Workflow

1. **AI receives task**: "Find all high-priority bugs"
2. **AI uses Toolbox**: Queries cross-chat findings database
3. **AI gets results**: List of bug findings
4. **AI creates Kanban card**: Uses Kanban tool to create card
5. **AI assigns to worktree**: Uses worktree tool to assign task

All through natural language!

## Next Steps

1. **Test Integration**: Run `python toolbox_test/test_toolbox.py`
2. **Start Server**: `npx @toolbox-sdk/server --tools-file toolbox_test/tools.yaml`
3. **Use in Agents**: Integrate tools into your AI agents
4. **Expand Tools**: Add more SQL tools as needed

## Resources

- [MCP Toolbox GitHub](https://github.com/googleapis/genai-toolbox)
- [Documentation](https://googleapis.github.io/genai-toolbox/getting-started/introduction/)
- [Python SDK](https://github.com/googleapis/mcp-toolbox-sdk-python)
