# Quick Start: Claude Code + Cursor Cloud Agents

This guide will get you up and running with Claude Code integration to Cursor Cloud Agents in under 5 minutes.

## Prerequisites

- Cursor account with Cloud Agents access
- Cursor API key (get from [Dashboard → Integrations](https://cursor.com/dashboard))
- Python 3.8+ (for custom MCP server) OR Node.js (for npm package)

---

## Option 1: Using Pre-built MCP Server (Fastest)

### Step 1: Get API Key

1. Go to [Cursor Dashboard](https://cursor.com/dashboard)
2. Navigate to **Integrations**
3. Create a new API key for Cloud Agents
4. Copy the key (format: `key_...`)

### Step 2: Set Environment Variable

```bash
export CURSOR_API_KEY=key_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 3: Install MCP Server

```bash
# Option A: Use npx (no installation)
npx @willpowell8/cursor-cloud-agent-mcp

# Option B: Install globally
npm install -g @willpowell8/cursor-cloud-agent-mcp
```

### Step 4: Configure MCP Client

If using Claude Desktop, add to `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac) or similar:

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

### Step 5: Test It

In Claude Desktop or your MCP client, try:

```
List my Cursor Cloud Agents using the list_agents tool
```

---

## Option 2: Using Your Custom MCP Framework

### Step 1: Set API Key

```bash
export CURSOR_API_KEY=key_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 2: Use the Integration Module

```python
from blackwall.mcp.cloud_agents_integration import (
    setup_cloud_agents_integration,
    create_cloud_agent_via_mcp,
    EnhancedMCPAgent
)

# Setup
bridge = await setup_cloud_agents_integration()

# Create agent
agent = EnhancedMCPAgent("my-agent", bridge)
await agent.initialize()

# Launch Cloud Agent
result = await create_cloud_agent_via_mcp(
    bridge=bridge,
    prompt_text="Fix all linting errors in the codebase",
    repository="https://github.com/your-org/your-repo",
    auto_create_pr=True
)

print(f"Agent ID: {result['id']}")
```

### Step 3: Monitor Agent

```python
# Check status
status = await agent.use_tool("get_agent", id=result['id'])
print(f"Status: {status['status']}")

# Get conversation
conversation = await agent.use_tool(
    "get_agent_conversation",
    id=result['id']
)
```

---

## Option 3: Using Hooks (Enterprise/Team Only)

### Step 1: Create Hook Script

Create `hooks/claude-cloud-bridge.js`:

```javascript
// hooks/claude-cloud-bridge.js
export async function beforeSubmitPrompt(context) {
  // Check if prompt contains cloud agent trigger
  if (context.prompt.includes('[CLOUD]')) {
    const mcpClient = await getMCPClient();
    
    // Extract repository from context
    const repo = extractRepository(context);
    
    // Launch Cloud Agent
    const result = await mcpClient.callTool('launch_agent', {
      prompt: {
        text: context.prompt.replace('[CLOUD]', '').trim()
      },
      source: {
        repository: repo
      },
      target: {
        autoCreatePr: true
      }
    });
    
    // Return Cloud Agent response
    return {
      ...context,
      response: `Cloud Agent launched: ${result.id}. Check status at cursor.com/agents`,
      executeLocally: false
    };
  }
  
  return context;
}

async function getMCPClient() {
  // Initialize MCP client connection
  // Implementation depends on your MCP client setup
}

function extractRepository(context) {
  // Extract repository from context or use default
  return context.repository || 'https://github.com/your-org/your-repo';
}
```

### Step 2: Configure Hook in Cursor

In Cursor settings (Enterprise/Team):

```json
{
  "hooks": {
    "beforeSubmitPrompt": {
      "script": "/path/to/hooks/claude-cloud-bridge.js",
      "enabled": true
    }
  }
}
```

### Step 3: Use It

In Cursor chat, prefix prompts with `[CLOUD]`:

```
[CLOUD] Implement user authentication system
```

This will automatically launch a Cloud Agent instead of executing locally.

---

## Common Use Cases

### 1. Launch Agent from Claude Code

```
Use the launch_agent tool to:
- Repository: https://github.com/myorg/myrepo
- Task: Refactor the authentication module to use JWT
- Auto-create PR when done
```

### 2. Monitor Multiple Agents

```python
# List all agents
agents = await agent.use_tool("list_agents", limit=50)

# Check each agent's status
for agent_data in agents.get('agents', []):
    status = await agent.use_tool("get_agent", id=agent_data['id'])
    print(f"{agent_data['id']}: {status['status']}")
```

### 3. Add Follow-up Instructions

```python
# Agent is working, add clarification
await agent.use_tool(
    "add_followup",
    id="bc_abc123",
    prompt={
        "text": "Also add integration tests for the new endpoints"
    }
)
```

### 4. Coordinate with Your Agent System

```python
from agent_system.coordinator import AgentCoordinator
from blackwall.mcp.cloud_agents_integration import setup_cloud_agents_integration

coordinator = AgentCoordinator()
bridge = await setup_cloud_agents_integration()

# Launch Cloud Agent for a task
result = await create_cloud_agent_via_mcp(
    bridge,
    "Fix critical security vulnerability",
    "https://github.com/org/repo"
)

# Register with coordinator
coordinator.register_cloud_agent(result['id'], "security-fix")
```

---

## Troubleshooting

### "CURSOR_API_KEY not found"

Make sure you've exported the environment variable:
```bash
export CURSOR_API_KEY=your_key_here
```

### "401 Unauthorized"

- Verify your API key is correct
- Check that the key has Cloud Agents API access
- Regenerate key if needed

### "Rate limit exceeded"

- The `list_repositories` endpoint has strict limits (1/min, 30/hour)
- Implement caching for repository lists
- Use exponential backoff for retries

### MCP Server Not Found

- Ensure Node.js is installed: `node --version`
- Try using npx: `npx @willpowell8/cursor-cloud-agent-mcp`
- Check MCP client configuration

---

## Next Steps

1. **Explore Tools**: Try all available MCP tools (`list_agents`, `get_agent`, etc.)
2. **Build Workflows**: Create automation scripts using the integration
3. **Set Up Hooks**: Configure hooks for automatic Cloud Agent routing
4. **Monitor Agents**: Build dashboards to track agent status

---

## Resources

- [Full Integration Guide](./CLAUDE_CLOUD_AGENTS_INTEGRATION.md)
- [MCP Framework Docs](./blackwall/mcp/)
- [Cursor API Docs](https://cursor.com/docs)
- [Cloud Agents Dashboard](https://cursor.com/agents)
