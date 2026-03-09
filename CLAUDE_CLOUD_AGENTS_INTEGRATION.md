# Claude Code Integration with Cursor Cloud Agents

This guide explains how to integrate Claude Code (or similar tools) with Cursor Cloud Agents using MCP (Model Context Protocol) and Hooks.

## Overview

There are **three main integration methods**:

1. **MCP Server Integration** - Connect Claude Code to Cloud Agents via Model Context Protocol
2. **Hooks System** - Extend and control Cloud Agents behavior with custom scripts
3. **Custom MCP Server** - Build your own MCP server using your existing framework

---

## Method 1: Using Existing MCP Servers for Cloud Agents

### Option A: cursor-cloud-agent-mcp (Recommended)

This is a ready-to-use MCP server that wraps the Cursor Cloud Agents API.

#### Installation

```bash
# Using npx (no installation needed)
npx @willpowell8/cursor-cloud-agent-mcp

# Or install globally
npm install -g @willpowell8/cursor-cloud-agent-mcp
```

#### Configuration

Set your Cursor API key:
```bash
export CURSOR_API_KEY=key_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Get your API key from: [Cursor Dashboard → Integrations](https://cursor.com/dashboard)

#### MCP Client Configuration

Add to your MCP client config (e.g., Claude Desktop `mcp.json`):

```json
{
  "mcpServers": {
    "cursor-cloud-agents": {
      "command": "npx",
      "args": ["-y", "@willpowell8/cursor-cloud-agent-mcp"],
      "env": {
        "CURSOR_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

#### Available Tools

The MCP server exposes these tools:

- `launch_agent` - Create and start a new cloud agent
- `list_agents` - List all cloud agents
- `get_agent` - Get agent status and details
- `get_agent_conversation` - Retrieve conversation history
- `add_followup` - Send follow-up instructions to an agent
- `stop_agent` - Pause agent execution
- `delete_agent` - Delete an agent
- `list_repositories` - List accessible GitHub repositories
- `list_models` - Get available LLM models
- `get_api_key_info` - Get API key metadata

#### Example: Launching an Agent via Claude Code

Once configured, you can use these tools in Claude Code:

```
Use the launch_agent tool to create a cloud agent that:
- Works on repository: https://github.com/your-org/your-repo
- Implements feature: Add user authentication
- Creates a PR automatically when done
```

---

## Method 2: Using Cursor Hooks

Hooks allow you to observe, control, and extend the agent loop with custom scripts.

### Hook Capabilities

1. **Observability** - Log agent actions, tool calls, prompts, and completions
2. **Control** - Enforce policies, block commands, scrub secrets
3. **Extension** - Connect external systems, inject context, trigger automations

### Hook Lifecycle Stages

Hooks can be configured at different stages:

- `beforeSubmitPrompt` - Run before agent submits a prompt
- `beforeShellCommand` - Run before shell commands execute
- `afterToolCall` - Run after tool execution
- `beforeAgentResponse` - Run before agent responds

### Hook Configuration

Hooks are configured in Cursor settings (Enterprise/Team plans):

```json
{
  "hooks": {
    "beforeSubmitPrompt": {
      "script": "/path/to/your/script.js",
      "enabled": true
    },
    "beforeShellCommand": {
      "script": "/path/to/security-check.js",
      "enabled": true
    }
  }
}
```

### Example Hook Script

Create a hook that integrates with Claude Code:

```javascript
// hooks/claude-integration.js
export async function beforeSubmitPrompt(context) {
  // Inject Claude Code context
  const claudeContext = await fetchClaudeCodeContext();
  
  // Add to prompt
  context.prompt = `${context.prompt}\n\n## Claude Code Context:\n${claudeContext}`;
  
  // Log for observability
  console.log('Prompt enhanced with Claude Code context');
  
  return context;
}

async function fetchClaudeCodeContext() {
  // Connect to Claude Code API or MCP server
  // Return relevant context
}
```

### Distribution

- **Enterprise**: Distributed via MDM or Cursor's cloud distribution
- **Team**: Configured per workspace/user

---

## Method 3: Custom MCP Server Using Your Framework

You already have a robust MCP framework in `blackwall/mcp/`. Here's how to create a Cloud Agents MCP server:

### Step 1: Create Cloud Agents MCP Server

```python
# blackwall/mcp/cloud_agents_server.py
from .server_framework import MCPServer, HTTPBackendConnection, MCPToolDefinition
from typing import Dict, Any
import os

class CursorCloudAgentsBackend(HTTPBackendConnection):
    """Backend connection to Cursor Cloud Agents API."""
    
    def __init__(self, api_key: str):
        super().__init__(
            base_url="https://api.cursor.com/v0",
            api_key=api_key,
            headers={"Content-Type": "application/json"}
        )

def create_cloud_agents_server(api_key: str) -> MCPServer:
    """Create MCP server for Cursor Cloud Agents."""
    
    backend = CursorCloudAgentsBackend(api_key)
    server = MCPServer(
        server_id="cursor-cloud-agents",
        name="Cursor Cloud Agents",
        description="MCP server for Cursor Cloud Agents API",
        backend=backend
    )
    
    # Register launch_agent tool
    server.register_tool(MCPToolDefinition(
        name="launch_agent",
        description="Launch a new Cursor Cloud Agent on a GitHub repository",
        parameters={
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "images": {"type": "array"}
                    },
                    "required": ["text"]
                },
                "source": {
                    "type": "object",
                    "properties": {
                        "repository": {"type": "string"},
                        "ref": {"type": "string"}
                    },
                    "required": ["repository"]
                },
                "model": {"type": "string"},
                "target": {
                    "type": "object",
                    "properties": {
                        "branchName": {"type": "string"},
                        "autoCreatePr": {"type": "boolean"}
                    }
                }
            },
            "required": ["prompt", "source"]
        },
        handler=launch_agent_handler
    ))
    
    # Add more tools...
    
    return server

async def launch_agent_handler(params: Dict[str, Any], resources: Any, backend: Any) -> Dict[str, Any]:
    """Handle launch_agent tool execution."""
    result = await backend.execute("agents", params)
    return result
```

### Step 2: Register with Your MCP Framework

```python
# blackwall/mcp/register_cloud_agents.py
from .cloud_agents_server import create_cloud_agents_server
from .agent_integration import MCPAgentBridge
import os

async def setup_cloud_agents_integration():
    """Setup Cloud Agents MCP server integration."""
    
    api_key = os.getenv("CURSOR_API_KEY")
    if not api_key:
        raise ValueError("CURSOR_API_KEY environment variable required")
    
    # Create server
    server = create_cloud_agents_server(api_key)
    
    # Register with bridge
    bridge = MCPAgentBridge()
    await bridge.registry.register_server(server)
    
    return bridge
```

### Step 3: Use with Enhanced Agent

```python
# Example usage
from blackwall.mcp.agent_integration import EnhancedMCPAgent
from blackwall.mcp.register_cloud_agents import setup_cloud_agents_integration

async def main():
    # Setup integration
    bridge = await setup_cloud_agents_integration()
    
    # Create enhanced agent
    agent = EnhancedMCPAgent("claude-agent-001", bridge)
    await agent.initialize()
    
    # Launch cloud agent via MCP
    result = await agent.use_tool(
        "launch_agent",
        prompt={
            "text": "Implement user authentication system"
        },
        source={
            "repository": "https://github.com/your-org/your-repo"
        },
        target={
            "autoCreatePr": True
        }
    )
    
    print(f"Cloud agent launched: {result['id']}")
```

---

## Integration Architecture

```
┌─────────────────┐
│   Claude Code   │
│   (or similar)  │
└────────┬────────┘
         │ MCP Protocol
         │
    ┌────▼──────────────────────┐
    │   MCP Client              │
    │   (Claude Desktop, etc.)  │
    └────┬──────────────────────┘
         │
    ┌────▼──────────────────────┐
    │   MCP Server              │
    │   (Cloud Agents API)      │
    └────┬──────────────────────┘
         │ HTTP API
         │
    ┌────▼──────────────────────┐
    │   Cursor Cloud Agents      │
    │   (cursor.com/agents)      │
    └────────────────────────────┘
```

---

## Practical Use Cases

### 1. Automated Code Generation Pipeline

```python
# Use Cloud Agents to generate code based on Claude Code analysis
async def generate_code_with_cloud_agent(analysis_result):
    agent = EnhancedMCPAgent("code-gen", bridge)
    
    # Launch cloud agent with Claude Code analysis
    result = await agent.use_tool(
        "launch_agent",
        prompt={
            "text": f"Based on this analysis: {analysis_result}, implement the recommended changes"
        },
        source={"repository": "https://github.com/org/repo"},
        target={"autoCreatePr": True}
    )
    
    return result
```

### 2. Multi-Agent Coordination

```python
# Coordinate multiple Cloud Agents using your existing agent system
from agent_system.coordinator import AgentCoordinator

coordinator = AgentCoordinator()

# Launch multiple Cloud Agents for parallel work
async def parallel_cloud_agents():
    tasks = [
        "Fix bug in authentication",
        "Add unit tests",
        "Update documentation"
    ]
    
    for task in tasks:
        agent_id = await launch_cloud_agent(task)
        coordinator.register_cloud_agent(agent_id, task)
```

### 3. Hook-Based Integration

```javascript
// hooks/claude-cloud-bridge.js
export async function beforeSubmitPrompt(context) {
  // Check if this should be sent to Cloud Agent
  if (context.shouldUseCloudAgent) {
    // Launch Cloud Agent via MCP
    const result = await mcpClient.callTool('launch_agent', {
      prompt: { text: context.prompt },
      source: { repository: context.repository }
    });
    
    // Return Cloud Agent ID instead of local execution
    return {
      ...context,
      cloudAgentId: result.id,
      executeLocally: false
    };
  }
  
  return context;
}
```

---

## Configuration Checklist

- [ ] Get Cursor API key from Dashboard
- [ ] Set `CURSOR_API_KEY` environment variable
- [ ] Install MCP server (or use npx)
- [ ] Configure MCP client (Claude Desktop, etc.)
- [ ] Test connection with `list_agents` tool
- [ ] Set up hooks (if using Enterprise/Team plan)
- [ ] Configure custom MCP server (if building your own)

---

## Resources

- [Cursor Cloud Agents API Docs](https://cursor.com/docs)
- [MCP Specification](https://modelcontextprotocol.io)
- [cursor-cloud-agent-mcp GitHub](https://github.com/willpowell8/cursor-cloud-agent-mcp)
- [Cursor Dashboard](https://cursor.com/dashboard)
- [Your MCP Framework](./blackwall/mcp/)

---

## Next Steps

1. **Try Method 1** - Quickest way to get started with existing MCP server
2. **Explore Method 2** - If you have Enterprise/Team plan, set up hooks
3. **Build Method 3** - Use your existing MCP framework to create custom integration

Would you like me to help implement any of these methods in your codebase?
