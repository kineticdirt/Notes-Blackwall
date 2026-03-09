# Complete Blackwall Agent System Redesign

## Understanding the System

### Current State
- **blackwall/**: Text + image protection
- **agent-system/**: Agent coordination (separate)
- **nightshade-tracker/**: Image protection (separate)

### Problem
Everything is fragmented. Blackwall should be **the unified system**.

## Redesigned Architecture

### Unified Blackwall System

```
blackwall/
├── agents/                    # Agent coordination (from agent-system)
│   ├── base/
│   │   ├── agent.py          # Base agent
│   │   ├── mcp_aware_agent.py # MCP-aware base
│   │   ├── coordinator.py   # Agent coordinator
│   │   ├── ledger.py         # Communication ledger
│   │   └── scratchpad.py      # Shared scratchpad
│   ├── specialized/
│   │   ├── protection_agent.py  # Protects content
│   │   ├── detection_agent.py  # Detects watermarks
│   │   ├── cleanup_agent.py    # Code cleanup
│   │   ├── test_agent.py       # Test writing
│   │   └── doc_agent.py        # Documentation
│   └── workflow/
│       └── workflow_coordinator.py
├── protection/                # Protection modules
│   ├── text/
│   │   ├── poisoning.py
│   │   └── watermarking.py
│   ├── image/                 # From nightshade-tracker
│   │   ├── poisoning.py
│   │   ├── watermarking.py
│   │   └── processor.py
│   └── unified/
│       └── processor.py
├── mcp/                       # MCP integration
│   ├── integration.py         # MCP tool/resource discovery
│   ├── server.py             # MCP server implementation
│   └── tools/                # Tool implementations
├── lsp/                       # LSP integration
│   └── manager.py
├── database/
│   └── registry.py           # Unified registry
└── cli.py                     # Unified CLI
```

## Key Design Principles

### 1. MCP as Foundation
- **All tools are MCP tools**: read_file, write_file, etc. are MCP tools
- **Agents use MCP tools**: Agents call tools via MCP protocol
- **Resources are MCP resources**: Ledger, scratchpad exposed as MCP resources

### 2. Unified System
- **One system**: Blackwall is everything
- **Integrated components**: Agents, protection, MCP, LSP all together
- **Shared infrastructure**: Ledger, scratchpad, registry shared

### 3. Agent Awareness
- **Tool awareness**: Agents know what MCP tools are available
- **Resource access**: Agents access MCP resources
- **Coordination**: Agents coordinate via ledger and scratchpad

## MCP Integration Details

### Available MCP Tools (Part of Blackwall)

These tools ARE Blackwall:
- `read_file` - Read files
- `write_file` - Write files  
- `search_replace` - Edit files
- `codebase_search` - Semantic search
- `grep` - Pattern search
- `run_terminal_cmd` - Execute commands
- `read_lints` - Linter errors
- `list_dir` - List directories
- `glob_file_search` - Find files
- `delete_file` - Delete files

### MCP Resources

- `ledger://ai_groupchat` - Communication ledger
- `scratchpad://shared` - Shared scratchpad
- `registry://blackwall` - Content registry

### MCP-Aware Agents

```python
class MCPAwareAgent:
    def __init__(self):
        self.mcp = MCPIntegration()
        self.available_tools = self.mcp.list_tools()
    
    def use_tool(self, tool_name, **kwargs):
        # Call MCP tool
        return self._call_mcp_tool(tool_name, **kwargs)
```

## Migration Plan

### Phase 1: Consolidate Structure
1. Move `agent-system/` → `blackwall/agents/`
2. Move `nightshade-tracker/core/` → `blackwall/protection/image/`
3. Keep `blackwall/core/text/` for text protection
4. Create `blackwall/mcp/` for MCP integration

### Phase 2: MCP Integration
1. Create MCP integration layer
2. Make agents MCP-aware
3. Expose ledger/scratchpad as MCP resources
4. Document tool usage

### Phase 3: Unified Coordinator
1. Create `BlackwallCoordinator` that integrates everything
2. Unified CLI
3. Unified registry
4. Complete documentation

## Benefits

1. **Unified System**: Everything in one place
2. **MCP Native**: Proper use of Claude's tool system
3. **Tool Awareness**: Agents know what they can do
4. **Better Coordination**: Shared ledger and scratchpad
5. **Complete Solution**: Protection + tracking + workflow

## Why This Design?

- **MCP Tools ARE Blackwall**: The tools available are part of Blackwall
- **Unified Architecture**: One system, not three separate ones
- **Proper Integration**: Uses Claude's systems (MCP, subagents, LSP) correctly
- **Scalable**: Easy to add new agents, tools, resources
