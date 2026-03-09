# MCP Server Framework - Quick Start Guide

Get started with creating reusable MCP servers in 5 minutes.

## Installation

The MCP framework is part of Blackwall. No additional installation needed.

## Step 1: Create Your First Server

Create a file `my_first_server.py`:

```python
import asyncio
from blackwall.mcp import MCPServerBuilder, MCPServerRegistry, MCPAgentBridge, EnhancedMCPAgent

async def main():
    # Create server builder
    builder = MCPServerBuilder(
        server_id="hello-world",
        name="Hello World Server",
        description="My first MCP server"
    )
    
    # Add a simple tool
    def greet_handler(params, resources, backend):
        name = params.get("name", "World")
        return {"message": f"Hello, {name}!"}
    
    builder.add_tool(
        name="greet",
        description="Say hello to someone",
        parameters={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name to greet"}
            }
        },
        handler=greet_handler
    )
    
    # Build server
    server = builder.build()
    await server.initialize()
    
    print(f"Server '{server.server_id}' initialized!")
    print(f"Tools: {list(server.tools.keys())}")
    
    # Test the tool
    result = await server.execute_tool("greet", {"name": "MCP Framework"})
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:
```bash
python my_first_server.py
```

## Step 2: Add a Backend Connection

Update your server to connect to an HTTP backend:

```python
# Add HTTP backend
builder.with_http_backend(
    base_url="https://api.example.com",
    api_key="your-api-key-here"
)

# Add tool that uses backend
builder.add_tool(
    name="fetch_data",
    description="Fetch data from backend API",
    parameters={
        "type": "object",
        "properties": {
            "endpoint": {"type": "string", "description": "API endpoint"}
        },
        "required": ["endpoint"]
    }
    # No handler - will use backend.execute()
)
```

## Step 3: Add Resources

Add resources that tools can access:

```python
from blackwall.mcp import ResourceAccess

# Add resource
builder.add_resource(
    uri="data://config",
    name="Configuration",
    description="Server configuration",
    data={"version": "1.0", "environment": "production"},
    access_level=ResourceAccess.READ_ONLY
)

# Add tool with resource access
builder.add_tool(
    name="get_config",
    description="Get server configuration",
    parameters={},
    resource_access=["data://config"],
    access_level=ResourceAccess.READ_ONLY,
    handler=lambda params, resources, backend: resources.get("data://config", {})
)
```

## Step 4: Add Prompt Templates

Create prompt templates with resource context:

```python
builder.add_prompt(
    name="analyze",
    description="Analyze data with context",
    template="""Analyze the following:

{input}

Available context:
{_resources}

Provide analysis.""",
    variables=["input"],
    resource_access=["data://config"],
    access_level=ResourceAccess.READ_ONLY
)
```

## Step 5: Use with an AI Agent

Create an agent that can use your server:

```python
# Create registry
registry = MCPServerRegistry()
await registry.register_server(server)

# Create agent bridge
bridge = MCPAgentBridge(registry)
await bridge.initialize()

# Create enhanced agent
agent = EnhancedMCPAgent("my-agent", bridge)
await agent.initialize()

# Use tools
result = await agent.use_tool("greet", name="Agent")

# Use prompts
prompt = await agent.use_prompt("analyze", input="Some data to analyze")
print(prompt)
```

## Step 6: Save Configuration

Save your server configuration for reuse:

```python
# Save configuration
builder.save_config("my_server_config.json")

# Later, load it
from blackwall.mcp import create_server_from_config

server = create_server_from_config("my_server_config.json")
await server.initialize()
```

## Complete Example

Here's a complete example combining everything:

```python
import asyncio
from blackwall.mcp import (
    MCPServerBuilder, MCPServerRegistry, MCPAgentBridge,
    EnhancedMCPAgent, ResourceAccess
)

async def main():
    # Build server
    builder = MCPServerBuilder(
        server_id="example-server",
        name="Example Server",
        description="Complete example server"
    )
    
    # Add HTTP backend
    builder.with_http_backend(
        base_url="https://api.example.com",
        api_key="api-key"
    )
    
    # Add resource
    builder.add_resource(
        uri="data://users",
        name="User Data",
        description="User information",
        data={"users": ["alice", "bob"]},
        access_level=ResourceAccess.READ_ONLY
    )
    
    # Add tool
    def get_user_handler(params, resources, backend):
        users = resources.get("data://users", {}).get("data", {}).get("users", [])
        user_id = params.get("user_id", 0)
        if user_id < len(users):
            return {"user": users[user_id]}
        return {"error": "User not found"}
    
    builder.add_tool(
        name="get_user",
        description="Get user by ID",
        parameters={
            "type": "object",
            "properties": {
                "user_id": {"type": "integer", "description": "User ID"}
            },
            "required": ["user_id"]
        },
        handler=get_user_handler,
        resource_access=["data://users"],
        access_level=ResourceAccess.READ_ONLY
    )
    
    # Add prompt
    builder.add_prompt(
        name="user_analysis",
        description="Analyze user data",
        template="""Analyze user: {user_id}

Available users:
{_resources}

Provide analysis.""",
        variables=["user_id"],
        resource_access=["data://users"],
        access_level=ResourceAccess.READ_ONLY
    )
    
    # Build and initialize
    server = builder.build()
    await server.initialize()
    
    # Register in registry
    registry = MCPServerRegistry()
    await registry.register_server(server)
    
    # Create agent
    bridge = MCPAgentBridge(registry)
    await bridge.initialize()
    
    agent = EnhancedMCPAgent("example-agent", bridge)
    await agent.initialize()
    
    # Use the server
    print("Available tools:", [t["name"] for t in agent.get_tools()])
    print("Available prompts:", [p["name"] for p in agent.get_prompts()])
    
    # Execute tool
    result = await agent.use_tool("get_user", user_id=0)
    print("Tool result:", result)
    
    # Render prompt
    prompt = await agent.use_prompt("user_analysis", user_id=0)
    print("Rendered prompt:", prompt)

if __name__ == "__main__":
    asyncio.run(main())
```

## Next Steps

1. Check out `examples.py` for more examples
2. Read `README.md` for detailed documentation
3. Use the CLI tool to manage servers: `python -m blackwall.mcp.cli`
4. Explore the framework code in `server_framework.py`

## Common Patterns

### Pattern 1: File Operations Server
```python
builder = MCPServerBuilder("file-ops", "File Operations", "...")
builder.add_resource(uri="file://workspace", ...)
builder.add_tool(name="read_file", handler=read_file_handler, ...)
```

### Pattern 2: Database Server
```python
builder = MCPServerBuilder("db", "Database", "...")
builder.with_http_backend("https://db-api.example.com", api_key="...")
builder.add_tool(name="query", ...)
```

### Pattern 3: AI/LLM Server
```python
builder = MCPServerBuilder("ai", "AI Server", "...")
builder.with_http_backend("https://api.openai.com/v1", api_key="...")
builder.add_prompt(name="code_review", template="...", ...)
```

## Troubleshooting

**Server won't connect to backend:**
- Check backend URL and API key
- Verify backend is accessible
- Check network connectivity

**Tool execution fails:**
- Verify tool parameters match schema
- Check handler function signature
- Ensure resources are accessible

**Prompt rendering fails:**
- Verify all template variables are provided
- Check resource access permissions
- Ensure prompt exists in server

## Need Help?

- See `examples.py` for working examples
- Check `README.md` for detailed docs
- Review `server_framework.py` for implementation details
