# Claude Code + Cloud Agents Integration

## Overview

This setup allows Claude Code (running in Cursor) to interface with Cursor Cloud Agents via MCP (Model Context Protocol). Since you're logged into Cursor with SSO, Claude Code can now access Cloud Agents tools directly.

## Configuration

I've created a `.mcp.json` file in your project root that configures Claude Code to connect to the Cloud Agents MCP server.

### File Location

The MCP configuration is at:
```
/Users/abhinav/Desktop/Cequence BlackWall/.mcp.json
```

### Configuration Details

The configuration uses:
- **MCP Server**: `@willpowell8/cursor-cloud-agent-mcp` (same as Cursor)
- **Transport**: stdio (local command execution)
- **Authentication**: Uses your Cursor API key

## How It Works

```
┌─────────────────┐
│   Claude Code   │
│   (in Cursor)   │
└────────┬────────┘
         │ MCP Protocol
         │
    ┌────▼──────────────────────┐
    │   .mcp.json              │
    │   (Project Config)       │
    └────┬──────────────────────┘
         │
    ┌────▼──────────────────────┐
    │   MCP Server              │
    │   (cursor-cloud-agent)   │
    └────┬──────────────────────┘
         │ HTTP API
         │
    ┌────▼──────────────────────┐
    │   Cursor Cloud Agents     │
    │   (api.cursor.com)        │
    └────────────────────────────┘
```

## Using Cloud Agents in Claude Code

Once Claude Code loads the MCP server, you can use Cloud Agents tools directly in Claude Code chat:

### Available Tools

1. **launch_agent** - Launch a new Cloud Agent
   ```
   Launch a Cloud Agent to refactor my authentication code
   ```

2. **list_agents** - List all your Cloud Agents
   ```
   List my Cloud Agents
   ```

3. **get_agent** - Get agent status
   ```
   What's the status of agent bc_abc123?
   ```

4. **add_followup** - Send follow-up instructions
   ```
   Add a follow-up to agent bc_abc123: Also add unit tests
   ```

5. **list_repositories** - List accessible repositories
   ```
   What GitHub repositories can Cloud Agents access?
   ```

6. **list_models** - List available models
   ```
   What LLM models are available for Cloud Agents?
   ```

## Testing the Integration

1. **Restart Claude Code** (or reload the window in Cursor)
   - Cmd+Shift+P → "Reload Window"

2. **Check if MCP server is loaded**
   - In Claude Code chat, ask: "What MCP tools are available?"
   - Should show Cloud Agents tools

3. **Test a simple command**
   ```
   List my Cloud Agents
   ```

## SSO Authentication

Since you're logged into Cursor with SSO:
- Your Cursor session is authenticated
- The API key in `.mcp.json` uses your Cursor account credentials
- Cloud Agents will have access to repositories your Cursor account can access

## Project-Level vs User-Level Configuration

- **Project-level** (`.mcp.json` in project root): Only available in this project
- **User-level** (`~/.claude/.mcp.json`): Available in all Claude Code sessions

To make it available everywhere, you can also add it to:
```
~/.claude/.mcp.json
```

## Troubleshooting

### MCP Server Not Loading

1. **Check Claude Code logs**
   - Open Developer Tools (Help → Toggle Developer Tools)
   - Check Console for MCP errors

2. **Verify API key**
   - Run: `python3 test_mcp_connection.py`
   - Should show successful API connection

3. **Check Node.js/npm**
   - Run: `node --version` and `npm --version`
   - Should be installed

### Tools Not Appearing

1. **Reload Claude Code window**
   - Cmd+Shift+P → "Reload Window"

2. **Check MCP server status**
   - Ask Claude Code: "What MCP servers are configured?"
   - Should list `cursor-cloud-agents`

3. **Verify `.mcp.json` syntax**
   - JSON should be valid
   - Check for typos in server name or configuration

## Benefits

1. **Unified Interface**: Use Cloud Agents from Claude Code chat
2. **SSO Integration**: Leverages your Cursor SSO session
3. **Project-Specific**: Configuration stays with your project
4. **Same Tools**: Access to all Cloud Agents capabilities

## Next Steps

1. Reload Claude Code window
2. Test with: "List my Cloud Agents"
3. Try launching an agent: "Launch a Cloud Agent to analyze my codebase"
4. Monitor agents: "What Cloud Agents are currently running?"
