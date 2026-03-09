# MCP Server Framework

A comprehensive framework for creating reusable MCP (Model Context Protocol) servers that connect to larger backend services. This framework makes it easy to create MCP servers with tools, prompts, and full resource access for AI agents.

## Features

- **Reusable MCP Servers**: Create MCP servers that connect to larger backend services
- **Tool Definitions**: Define tools with full resource access capabilities
- **Prompt Templates**: Create prompt templates with automatic resource context injection
- **Resource Management**: Manage resources with access control levels
- **Backend Connections**: Connect to HTTP APIs, databases, and other backend services
- **Agent Integration**: Easy-to-use bridge for AI agents to access MCP servers
- **Configuration-Based**: Save and load server configurations from JSON/YAML files

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Agent / Claude                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              MCP Agent Bridge                                │
│  - Tool Discovery                                            │
│  - Prompt Rendering                                          │
│  - Resource Access                                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              MCP Server Registry                             │
│  - Server Management                                         │
│  - Tool/Prompt/Resource Discovery                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ MCP Server  │ │ MCP Server  │ │ MCP Server  │
│  (File Ops) │ │  (Database) │ │   (AI/LLM)  │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘
       │               │               │
       ▼               ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  Backend    │ │  Backend    │ │  Backend    │
│  (Local FS) │ │  (HTTP API) │ │  (HTTP API) │
└─────────────┘ └─────────────┘ └─────────────┘
```

## Quick Start

### 1. Create a Simple MCP Server

```python
from blackwall.mcp import MCPServerBuilder, ResourceAccess

# Create server builder
builder = MCPServerBuilder(
    server_id="my-server",
    name="My MCP Server",
    description="Example MCP server"
)

# Add a tool
builder.add_tool(
    name="greet",
    description="Greet someone",
    parameters={
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Name to greet"}
        },
        "required": ["name"]
    },
    handler=lambda params, resources, backend: f"Hello, {params['name']}!"
)

# Build and initialize server
server = builder.build()
await server.initialize()
```

### 2. Connect to a Backend Service

```python
# Connect to HTTP backend
builder.with_http_backend(
    base_url="https://api.example.com",
    api_key="your-api-key"
)

# Add tool that uses backend
builder.add_tool(
    name="fetch_data",
    description="Fetch data from backend",
    parameters={
        "type": "object",
        "properties": {
            "endpoint": {"type": "string"}
        }
    }
)
```

### 3. Add Resources with Access Control

```python
# Add resource
builder.add_resource(
    uri="data://users",
    name="User Data",
    description="User information",
    access_level=ResourceAccess.READ_ONLY
)

# Add tool with resource access
builder.add_tool(
    name="get_user",
    description="Get user information",
    parameters={...},
    resource_access=["data://users"],
    access_level=ResourceAccess.READ_ONLY
)
```

### 4. Create Prompt Templates

```python
# Add prompt template
builder.add_prompt(
    name="analyze_data",
    description="Analyze data with context",
    template="""Analyze the following data:

{data}

Context from resources:
{_resources}

Provide insights and recommendations.""",
    variables=["data"],
    resource_access=["data://users"],
    access_level=ResourceAccess.READ_ONLY
)
```

### 5. Use with AI Agents

```python
from blackwall.mcp import MCPServerRegistry, MCPAgentBridge, EnhancedMCPAgent

# Create registry and register server
registry = MCPServerRegistry()
await registry.register_server(server)

# Create agent bridge
bridge = MCPAgentBridge(registry)
await bridge.initialize()

# Create enhanced agent
agent = EnhancedMCPAgent("my-agent", bridge)
await agent.initialize()

# Use tools
result = await agent.use_tool("greet", name="World")

# Use prompts
prompt = await agent.use_prompt("analyze_data", data="...")
```

## Resource Access Levels

- **NONE**: No resource access
- **READ_ONLY**: Can read resources
- **READ_WRITE**: Can read and write resources
- **FULL**: Full access to resources

## Configuration Files

Save server configurations to JSON or YAML:

```json
{
  "server_id": "my-server",
  "name": "My MCP Server",
  "description": "Example server",
  "backend": {
    "type": "http",
    "base_url": "https://api.example.com",
    "api_key": "your-key"
  },
  "tools": [
    {
      "name": "greet",
      "description": "Greet someone",
      "parameters": {...},
      "resource_access": [],
      "access_level": "none"
    }
  ],
  "prompts": [...],
  "resources": [...]
}
```

Load from configuration:

```python
from blackwall.mcp import create_server_from_config

server = create_server_from_config("server_config.json")
await server.initialize()
```

## CLI Tool

Manage MCP servers from the command line:

```bash
# List all servers
python -m blackwall.mcp.cli list-servers

# List tools
python -m blackwall.mcp.cli list-tools

# List prompts
python -m blackwall.mcp.cli list-prompts

# List resources
python -m blackwall.mcp.cli list-resources

# Create server from config
python -m blackwall.mcp.cli create server_config.json

# Test tool
python -m blackwall.mcp.cli test-tool my-server greet '{"name": "World"}'

# Test prompt
python -m blackwall.mcp.cli test-prompt my-server analyze_data '{"data": "..."}'
```

## Examples

See `examples.py` for complete examples:
- File operations server
- Database server with HTTP backend
- AI/LLM server with prompts
- Multi-server workflow
- Configuration save/load

## Integration with Existing Agents

The framework integrates seamlessly with existing Blackwall agents:

```python
from blackwall.agents.mcp_aware_agent import MCPAwareAgent
from blackwall.mcp import MCPServerRegistry, MCPAgentBridge

# Create registry and bridge
registry = MCPServerRegistry()
# ... register servers ...

bridge = MCPAgentBridge(registry)
await bridge.initialize()

# Enhanced agent has access to all MCP servers
agent = EnhancedMCPAgent("agent-1", bridge)
await agent.initialize()

# Agent can now use tools from all registered servers
result = await agent.use_tool("tool-name", param1="value1")
```

## Benefits

1. **Reusability**: Create MCP servers once, use everywhere
2. **Resource Access**: Tools and prompts have full access to resources
3. **Backend Integration**: Easy connection to larger backend services
4. **Agent-Friendly**: Simple API for AI agents to discover and use tools
5. **Configuration-Based**: Save and share server configurations
6. **Type Safety**: Full type hints and validation

## Best Practices

1. **Server Organization**: Group related tools, prompts, and resources in one server
2. **Resource Access**: Use appropriate access levels for security
3. **Error Handling**: Implement proper error handling in tool handlers
4. **Documentation**: Provide clear descriptions for tools and prompts
5. **Testing**: Use the CLI tool to test servers before deployment
6. **Configuration**: Save server configurations for version control

## Advanced Usage

### Custom Backend Connections

```python
from blackwall.mcp import BackendConnection

class CustomBackend(BackendConnection):
    async def connect(self) -> bool:
        # Custom connection logic
        return True
    
    async def disconnect(self):
        # Custom disconnection logic
        pass
    
    async def execute(self, method: str, params: Dict[str, Any]) -> Any:
        # Custom execution logic
        return result
    
    def is_connected(self) -> bool:
        return self._connected

# Use custom backend
builder.with_backend(CustomBackend())
```

### Async Tool Handlers

```python
async def async_tool_handler(params, resources, backend):
    # Async operations
    result = await some_async_operation(params)
    return result

builder.add_tool(
    name="async_tool",
    description="Async tool",
    parameters={...},
    handler=async_tool_handler
)
```

## See Also

- `server_framework.py`: Core framework classes
- `server_builder.py`: Builder pattern for creating servers
- `agent_integration.py`: Agent bridge and integration
- `examples.py`: Complete usage examples
- `cli.py`: Command-line interface
