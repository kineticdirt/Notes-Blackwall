# Blackwall Agent System Redesign

## Current Issues

1. **Separation**: Blackwall, agent-system, and nightshade-tracker are separate
2. **No MCP Integration**: Not using Model Context Protocol properly
3. **Tool Awareness**: Agents don't know about available MCP tools
4. **Resource Access**: Not leveraging MCP resources

## Redesigned Architecture

### Unified Blackwall System

```
blackwall/
├── core/                    # Core protection modules
│   ├── image/              # Image protection (from nightshade-tracker)
│   │   ├── poisoning.py
│   │   ├── watermarking.py
│   │   └── processor.py
│   ├── text/               # Text protection
│   │   ├── poisoning.py
│   │   ├── watermarking.py
│   │   └── processor.py
│   └── unified/            # Unified processor
│       └── processor.py
├── agents/                 # Agent coordination system
│   ├── base/
│   │   ├── agent.py        # Base agent with MCP awareness
│   │   ├── coordinator.py  # Agent coordinator
│   │   ├── ledger.py       # Communication ledger
│   │   └── scratchpad.py   # Shared scratchpad
│   ├── specialized/        # Specialized agents
│   │   ├── cleanup_agent.py
│   │   ├── test_agent.py
│   │   ├── doc_agent.py
│   │   ├── protection_agent.py  # NEW: Handles protection tasks
│   │   └── detection_agent.py  # NEW: Handles detection
│   └── mcp/               # MCP integration
│       ├── mcp_integration.py
│       └── tool_bridge.py
├── database/
│   └── registry.py         # Unified registry
├── mcp/                    # MCP server implementation
│   ├── server.py
│   ├── tools/
│   └── resources/
└── cli.py                  # Unified CLI
```

## Key Changes

### 1. MCP-Aware Agents

Agents now understand and use MCP tools:

```python
class MCPAwareAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.mcp = MCPIntegration()
        self.available_tools = self.mcp.list_tools()
    
    def use_tool(self, tool_name: str, **kwargs):
        """Use an MCP tool."""
        if tool_name in self.available_tools:
            # Tool is available via MCP
            return self._call_mcp_tool(tool_name, **kwargs)
```

### 2. Unified Protection Agents

New agents that handle protection tasks:
- **protection_agent**: Processes content (text/image) with poison + watermark
- **detection_agent**: Detects watermarks in content

### 3. MCP Resource Access

Agents can access MCP resources:
- Ledger as MCP resource
- Scratchpad as MCP resource
- Registry as MCP resource

### 4. Tool Bridge

Bridge between agent system and MCP tools:

```python
class MCPToolBridge:
    """Bridges agent system with MCP tools."""
    
    def execute_tool(self, agent_id: str, tool_name: str, params: Dict):
        """Execute tool on behalf of agent."""
        # Log to ledger
        # Check permissions
        # Execute tool
        # Return result
```

## Integration Benefits

1. **Unified System**: Everything in one place
2. **MCP Native**: Uses Claude's MCP system properly
3. **Tool Awareness**: Agents know what tools are available
4. **Resource Sharing**: MCP resources accessible to all agents
5. **Better Coordination**: MCP enables better agent communication

## Migration Plan

1. Move agent-system into blackwall/agents/
2. Move nightshade-tracker into blackwall/core/image/
3. Add MCP integration layer
4. Update all imports and references
5. Create unified CLI
