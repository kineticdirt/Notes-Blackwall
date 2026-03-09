# Blackwall: Unified System Architecture

## Why Blackwall is the Unified System

Blackwall is **the system** - it includes:
1. **Agent System**: Coordination, subagents, workflow
2. **Protection System**: Text + image poisoning and watermarking
3. **MCP Integration**: Tools and resources (read_file, write_file, etc.)
4. **LSP Integration**: Code intelligence
5. **Registry**: Unified tracking for all content

## Architecture

```
blackwall/
├── agents/                    # Agent coordination system
│   ├── mcp_aware_agent.py    # Base agent with MCP tool awareness
│   ├── protection_agent.py   # Protects content (text + images)
│   ├── detection_agent.py   # Detects watermarks
│   └── [workflow agents]      # Cleanup, test, doc agents
├── core/                      # Protection modules
│   ├── text/                 # Text protection
│   ├── image/                # Image protection (from nightshade-tracker)
│   └── unified/              # Unified processor
├── mcp/                       # MCP integration
│   └── mcp_integration.py   # MCP tools and resources
├── database/
│   └── registry.py          # Unified registry
└── unified_coordinator.py   # Main coordinator
```

## MCP Tools (Part of Blackwall)

The tools available in this Claude environment ARE part of Blackwall:
- `read_file` - Read files
- `write_file` - Write files
- `codebase_search` - Semantic search
- `grep` - Pattern search
- `run_terminal_cmd` - Execute commands
- `read_lints` - Linter errors
- And more...

These tools are exposed via MCP (Model Context Protocol) and are used by Blackwall agents.

## Usage

### Unified Coordinator

```python
from unified_coordinator import BlackwallCoordinator

# Initialize (automatically sets up LSP, MCP, agents)
coordinator = BlackwallCoordinator(project_path=".")

# Protect content
result = coordinator.protect_content("document.txt", content_type="text")
print(f"Protected: {result['output_path']}, UUID: {result['uuid']}")

# Detect watermarks
detection = coordinator.detect_content("suspicious_file.txt")
if detection['detected']:
    print(f"Found UUID: {detection['uuid']}")

# Run workflow
coordinator.run_workflow(".", ["file1.py", "file2.py"])

# Get system status
status = coordinator.get_system_status()
print(status)
```

### MCP-Aware Agents

```python
from agents.protection_agent import ProtectionAgent

agent = ProtectionAgent()

# Agent knows about available MCP tools
tools = agent.get_available_tools()
print(f"Available tools: {tools}")

# Agent can use tools
agent.use_tool("read_file", target_file="file.txt")
agent.use_tool("codebase_search", query="watermarking implementation")
```

## Integration Points

1. **Agent System** → Uses MCP tools for file operations
2. **Protection System** → Uses agents for coordination
3. **MCP Tools** → Available to all agents
4. **LSP** → Provides code intelligence to agents
5. **Registry** → Tracks all protected content

## Why Unified?

- **Single System**: Everything works together
- **MCP Native**: Uses Claude's tool system properly
- **Tool Awareness**: Agents know what tools are available
- **Better Coordination**: Unified ledger and scratchpad
- **Complete Solution**: Protection + tracking + workflow

## Next Steps

1. Migrate agent-system into blackwall/agents/
2. Migrate nightshade-tracker into blackwall/core/image/
3. Update all imports
4. Test unified system
5. Update documentation
