# Blackwall: Final Unified Architecture

## Why Blackwall is Separate (And Should Be Unified)

**Current State**: Blackwall is separate because it was created as an extension of Nightshade for text protection.

**Should Be**: Blackwall should be **the unified system** that includes:
- Agent coordination system
- Protection system (text + images)
- MCP integration (tools and resources)
- LSP integration (code intelligence)
- Unified registry

## Complete System Architecture

```
blackwall/                          # THE UNIFIED SYSTEM
│
├── agents/                         # Agent coordination
│   ├── base/
│   │   ├── agent.py               # Base agent class
│   │   ├── mcp_aware_agent.py    # MCP-aware base (NEW)
│   │   ├── coordinator.py         # Agent coordinator
│   │   ├── ledger.py              # AI_GROUPCHAT ledger
│   │   └── scratchpad.py           # Shared scratchpad
│   │
│   ├── specialized/
│   │   ├── protection_agent.py    # Protects content (text + images)
│   │   ├── detection_agent.py    # Detects watermarks
│   │   ├── cleanup_agent.py      # Code cleanup
│   │   ├── test_agent.py          # Test writing
│   │   └── doc_agent.py           # Documentation
│   │
│   └── workflow/
│       └── workflow_coordinator.py # Workflow orchestration
│
├── protection/                     # Protection modules
│   ├── text/
│   │   ├── poisoning.py          # Text adversarial poisoning
│   │   └── watermarking.py       # Text steganography
│   │
│   ├── image/                     # From nightshade-tracker
│   │   ├── poisoning.py          # Image adversarial poisoning
│   │   ├── watermarking.py       # Image steganography
│   │   └── processor.py           # Image processing
│   │
│   └── unified/
│       └── processor.py           # Unified text + image processor
│
├── mcp/                            # MCP integration
│   ├── mcp_integration.py         # MCP tool/resource discovery
│   └── server.py                  # MCP server (future)
│
├── lsp/                            # LSP integration
│   └── manager.py                  # LSP detection and setup
│
├── database/
│   └── registry.py                # Unified registry (text + images)
│
├── utils/                          # Shared utilities
│   ├── ecc.py                     # Error correction codes
│   └── perceptual_hash.py          # Perceptual hashing
│
├── .claude/                        # Claude integration
│   └── agents/                     # Subagent definitions
│       ├── cleanup-agent.md
│       ├── test-agent.md
│       └── doc-agent.md
│
└── cli.py                          # Unified CLI
```

## MCP Tools (Part of Blackwall)

**Important**: The tools available in this Claude environment ARE part of Blackwall:
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

These are exposed via **MCP (Model Context Protocol)** and used by Blackwall agents.

## How It All Works Together

### 1. MCP Foundation
- Tools are MCP tools
- Resources (ledger, scratchpad) are MCP resources
- Agents use MCP to access tools and resources

### 2. Agent Coordination
- Agents declare intents (prevent race conditions)
- Agents communicate via ledger (AI_GROUPCHAT)
- Agents share context via scratchpad

### 3. Protection System
- Text protection: poisoning + watermarking
- Image protection: poisoning + watermarking (Nightshade)
- Unified processor handles both

### 4. Workflow System
- Cleanup → Test → Documentation pipeline
- Agents coordinate through scratchpad
- LSP provides code intelligence

### 5. Unified Registry
- Tracks all protected content (text + images)
- Stores UUIDs and metadata
- Enables detection and tracking

## Usage Example

```python
from unified_coordinator import BlackwallCoordinator

# Initialize unified system
coordinator = BlackwallCoordinator(project_path=".")

# System automatically:
# - Detects languages and sets up LSP
# - Discovers MCP tools
# - Initializes agents
# - Sets up registry

# Protect content
result = coordinator.protect_content("document.txt")
print(f"UUID: {result['uuid']}")

# Detect watermarks
detection = coordinator.detect_content("suspicious.txt")
if detection['detected']:
    print(f"Found: {detection['uuid']}")

# Run workflow
coordinator.run_workflow(".", ["file1.py"])

# Get status
status = coordinator.get_system_status()
```

## Migration Strategy

### Step 1: Understand Current State
- `blackwall/`: Text + image protection
- `agent-system/`: Agent coordination
- `nightshade-tracker/`: Image protection

### Step 2: Consolidate
- Move `agent-system/` → `blackwall/agents/`
- Move `nightshade-tracker/core/` → `blackwall/protection/image/`
- Keep text protection in `blackwall/protection/text/`

### Step 3: Integrate
- Add MCP integration layer
- Make agents MCP-aware
- Create unified coordinator
- Update all imports

### Step 4: Test
- Test protection workflows
- Test agent coordination
- Test MCP tool usage
- Test LSP integration

## Key Insights

1. **MCP Tools ARE Blackwall**: The tools (read_file, write_file, etc.) are part of Blackwall
2. **Unified System**: Everything should be in Blackwall, not separate folders
3. **Agent Awareness**: Agents must know about MCP tools and resources
4. **Proper Integration**: Use Claude's systems (MCP, subagents, LSP) correctly

## Next Steps

1. Complete migration (move files, update imports)
2. Test unified system
3. Document MCP integration
4. Create unified CLI
5. Update all documentation
