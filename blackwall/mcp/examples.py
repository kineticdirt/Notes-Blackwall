"""
Example MCP server configurations and usage patterns.
"""

import asyncio
from typing import Dict, Any

from .server_builder import MCPServerBuilder
from .server_framework import ResourceAccess
from .agent_integration import MCPAgentBridge, EnhancedMCPAgent
from .server_framework import MCPServerRegistry


# Example 1: Simple file operations server
async def create_file_server_example():
    """Create a simple file operations MCP server."""
    
    async def read_file_handler(params: Dict[str, Any], resources: Any, backend: Any) -> Dict[str, Any]:
        """Handler for reading files."""
        file_path = params.get("path")
        if not file_path:
            raise ValueError("path parameter required")
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            return {"content": content, "path": file_path}
        except Exception as e:
            return {"error": str(e), "path": file_path}
    
    builder = MCPServerBuilder(
        server_id="file-ops",
        name="File Operations Server",
        description="MCP server for file operations with resource access"
    )
    
    builder.add_tool(
        name="read_file",
        description="Read content from a file",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to read"}
            },
            "required": ["path"]
        },
        handler=read_file_handler,
        resource_access=["file://workspace"],
        access_level=ResourceAccess.READ_ONLY
    )
    
    builder.add_resource(
        uri="file://workspace",
        name="Workspace Files",
        description="Access to workspace file system",
        access_level=ResourceAccess.READ_ONLY
    )
    
    return builder.build()


# Example 2: Database server with HTTP backend
async def create_database_server_example():
    """Create a database MCP server connected to HTTP backend."""
    
    builder = MCPServerBuilder(
        server_id="database-api",
        name="Database API Server",
        description="MCP server for database operations via HTTP API"
    )
    
    builder.with_http_backend(
        base_url="https://api.example.com/db",
        api_key="your-api-key-here"
    )
    
    builder.add_tool(
        name="query_database",
        description="Execute a database query",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "SQL query"},
                "database": {"type": "string", "description": "Database name"}
            },
            "required": ["query"]
        },
        resource_access=["db://schema", "db://tables"],
        access_level=ResourceAccess.READ_ONLY
    )
    
    builder.add_resource(
        uri="db://schema",
        name="Database Schema",
        description="Database schema information",
        access_level=ResourceAccess.READ_ONLY
    )
    
    builder.add_resource(
        uri="db://tables",
        name="Database Tables",
        description="List of database tables",
        access_level=ResourceAccess.READ_ONLY
    )
    
    builder.add_prompt(
        name="generate_query",
        description="Generate SQL query from natural language",
        template="""Given the database schema:
{_resources}

Generate a SQL query for: {user_request}

Return only the SQL query, no explanation.""",
        variables=["user_request"],
        resource_access=["db://schema"],
        access_level=ResourceAccess.READ_ONLY
    )
    
    return builder.build()


# Example 3: AI/LLM server with prompts
async def create_ai_server_example():
    """Create an AI/LLM MCP server with prompt templates."""
    
    builder = MCPServerBuilder(
        server_id="ai-assistant",
        name="AI Assistant Server",
        description="MCP server for AI/LLM operations with prompt templates"
    )
    
    builder.with_http_backend(
        base_url="https://api.openai.com/v1",
        api_key="your-openai-key"
    )
    
    builder.add_tool(
        name="complete_text",
        description="Complete text using LLM",
        parameters={
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Prompt text"},
                "model": {"type": "string", "description": "Model name", "default": "gpt-4"},
                "temperature": {"type": "number", "description": "Temperature", "default": 0.7}
            },
            "required": ["prompt"]
        },
        resource_access=["ai://models", "ai://context"],
        access_level=ResourceAccess.READ_ONLY
    )
    
    builder.add_prompt(
        name="code_review",
        description="Code review prompt template",
        template="""Review the following code:

{code}

Context:
{_resources}

Provide a detailed code review focusing on:
1. Code quality and best practices
2. Potential bugs or issues
3. Performance optimizations
4. Security concerns""",
        variables=["code"],
        resource_access=["ai://context"],
        access_level=ResourceAccess.READ_ONLY
    )
    
    builder.add_resource(
        uri="ai://models",
        name="Available Models",
        description="List of available AI models",
        data={"models": ["gpt-4", "gpt-3.5-turbo", "claude-3"]},
        access_level=ResourceAccess.READ_ONLY
    )
    
    builder.add_resource(
        uri="ai://context",
        name="AI Context",
        description="Shared context for AI operations",
        access_level=ResourceAccess.READ_WRITE
    )
    
    return builder.build()


# Example 4: Complete workflow with multiple servers
async def example_multi_server_workflow():
    """Example of using multiple MCP servers together."""
    
    # Create registry
    registry = MCPServerRegistry()
    
    # Create and register servers
    file_server = await create_file_server_example()
    await registry.register_server(file_server)
    
    db_server = await create_database_server_example()
    await registry.register_server(db_server)
    
    ai_server = await create_ai_server_example()
    await registry.register_server(ai_server)
    
    # Create agent bridge
    bridge = MCPAgentBridge(registry)
    await bridge.initialize()
    
    # Create enhanced agent
    agent = EnhancedMCPAgent("example-agent", bridge)
    await agent.initialize()
    
    # Use tools from different servers
    print("Available tools:", len(agent.get_tools()))
    print("Available prompts:", len(agent.get_prompts()))
    print("Available resources:", len(agent.get_resources()))
    
    # Example: Use file tool
    # result = await agent.use_tool("read_file", path="example.txt")
    
    # Example: Use prompt
    # prompt = await agent.use_prompt("generate_query", user_request="Get all users")
    
    # Example: Use AI tool
    # completion = await agent.use_tool("complete_text", prompt="Hello, world!")
    
    return agent


# Example 5: Save and load server configuration
async def example_save_load_config():
    """Example of saving and loading server configurations."""
    
    builder = MCPServerBuilder(
        server_id="example-server",
        name="Example Server",
        description="Example server for configuration"
    )
    
    builder.add_tool(
        name="example_tool",
        description="Example tool",
        parameters={
            "type": "object",
            "properties": {
                "input": {"type": "string"}
            }
        }
    )
    
    # Save configuration
    builder.save_config("example_server_config.json")
    
    # Load configuration
    from .server_builder import create_server_from_config
    server = create_server_from_config("example_server_config.json")
    
    return server


if __name__ == "__main__":
    # Run examples
    asyncio.run(example_multi_server_workflow())
