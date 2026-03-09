"""
CLI tool for managing MCP servers.
"""

import argparse
import asyncio
import json
from pathlib import Path
from typing import Optional

from .server_builder import MCPServerBuilder, create_server_from_config
from .server_framework import MCPServerRegistry
from .agent_integration import MCPAgentBridge, EnhancedMCPAgent


async def cmd_list_servers(registry_path: Optional[str] = None):
    """List all registered MCP servers."""
    registry = MCPServerRegistry()
    
    # Load servers from registry path if provided
    if registry_path and Path(registry_path).exists():
        with open(registry_path, 'r') as f:
            configs = json.load(f)
            for server_id, config in configs.items():
                builder = MCPServerBuilder(
                    server_id=config["server_id"],
                    name=config["name"],
                    description=config["description"]
                )
                builder.from_config(config)
                server = builder.build()
                await registry.register_server(server)
    
    bridge = MCPAgentBridge(registry)
    await bridge.initialize()
    
    servers = bridge.list_servers()
    
    if not servers:
        print("No servers registered.")
        return
    
    print("\nRegistered MCP Servers:")
    print("=" * 80)
    for server in servers:
        print(f"\nServer ID: {server['server_id']}")
        print(f"  Name: {server['name']}")
        print(f"  Description: {server['description']}")
        print(f"  Tools: {server['tool_count']}")
        print(f"  Prompts: {server['prompt_count']}")
        print(f"  Resources: {server['resource_count']}")
        if server['backend_connected'] is not None:
            print(f"  Backend: {'Connected' if server['backend_connected'] else 'Disconnected'}")


async def cmd_list_tools(server_id: Optional[str] = None):
    """List available tools."""
    registry = MCPServerRegistry()
    bridge = MCPAgentBridge(registry)
    await bridge.initialize()
    
    tools = bridge.get_available_tools(server_id)
    
    if not tools:
        print("No tools available.")
        return
    
    print(f"\nAvailable Tools{' (Server: ' + server_id + ')' if server_id else ''}:")
    print("=" * 80)
    for tool in tools:
        print(f"\nTool: {tool['name']}")
        print(f"  Description: {tool['description']}")
        if 'metadata' in tool and 'resource_access' in tool['metadata']:
            if tool['metadata']['resource_access']:
                print(f"  Resource Access: {', '.join(tool['metadata']['resource_access'])}")
        print(f"  Parameters: {json.dumps(tool.get('inputSchema', {}).get('properties', {}), indent=4)}")


async def cmd_list_prompts(server_id: Optional[str] = None):
    """List available prompts."""
    registry = MCPServerRegistry()
    bridge = MCPAgentBridge(registry)
    await bridge.initialize()
    
    prompts = bridge.get_available_prompts(server_id)
    
    if not prompts:
        print("No prompts available.")
        return
    
    print(f"\nAvailable Prompts{' (Server: ' + server_id + ')' if server_id else ''}:")
    print("=" * 80)
    for prompt in prompts:
        print(f"\nPrompt: {prompt['name']}")
        print(f"  Description: {prompt['description']}")
        if 'arguments' in prompt:
            print(f"  Variables: {[arg['name'] for arg in prompt['arguments']]}")
        if 'metadata' in prompt and 'resource_access' in prompt['metadata']:
            if prompt['metadata']['resource_access']:
                print(f"  Resource Access: {', '.join(prompt['metadata']['resource_access'])}")


async def cmd_list_resources(server_id: Optional[str] = None):
    """List available resources."""
    registry = MCPServerRegistry()
    bridge = MCPAgentBridge(registry)
    await bridge.initialize()
    
    resources = bridge.get_available_resources(server_id)
    
    if not resources:
        print("No resources available.")
        return
    
    print(f"\nAvailable Resources{' (Server: ' + server_id + ')' if server_id else ''}:")
    print("=" * 80)
    for resource in resources:
        print(f"\nResource: {resource['uri']}")
        print(f"  Name: {resource['name']}")
        print(f"  Description: {resource['description']}")
        print(f"  MIME Type: {resource.get('mimeType', 'N/A')}")
        if 'metadata' in resource and 'access_level' in resource['metadata']:
            print(f"  Access Level: {resource['metadata']['access_level']}")


async def cmd_create_server(config_path: str, output_path: Optional[str] = None):
    """Create a server from configuration file."""
    server = create_server_from_config(config_path)
    await server.initialize()
    
    print(f"Server '{server.server_id}' created successfully!")
    print(f"  Name: {server.name}")
    print(f"  Tools: {len(server.tools)}")
    print(f"  Prompts: {len(server.prompts)}")
    print(f"  Resources: {len(server.resources)}")
    
    if output_path:
        config = server.export_config()
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"\nConfiguration exported to: {output_path}")


async def cmd_test_tool(server_id: str, tool_name: str, params_json: str):
    """Test a tool execution."""
    registry = MCPServerRegistry()
    bridge = MCPAgentBridge(registry)
    await bridge.initialize()
    
    try:
        params = json.loads(params_json)
        result = await bridge.execute_tool(tool_name, params, server_id)
        print(f"\nTool '{tool_name}' executed successfully:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error executing tool: {e}")


async def cmd_test_prompt(server_id: str, prompt_name: str, context_json: str):
    """Test a prompt rendering."""
    registry = MCPServerRegistry()
    bridge = MCPAgentBridge(registry)
    await bridge.initialize()
    
    try:
        context = json.loads(context_json)
        result = await bridge.render_prompt(prompt_name, context, server_id)
        print(f"\nPrompt '{prompt_name}' rendered:")
        print("=" * 80)
        print(result)
    except Exception as e:
        print(f"Error rendering prompt: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="MCP Server Management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List servers
    list_servers_parser = subparsers.add_parser("list-servers", help="List all registered servers")
    list_servers_parser.add_argument("--registry", help="Path to registry file")
    
    # List tools
    list_tools_parser = subparsers.add_parser("list-tools", help="List available tools")
    list_tools_parser.add_argument("--server", help="Filter by server ID")
    
    # List prompts
    list_prompts_parser = subparsers.add_parser("list-prompts", help="List available prompts")
    list_prompts_parser.add_argument("--server", help="Filter by server ID")
    
    # List resources
    list_resources_parser = subparsers.add_parser("list-resources", help="List available resources")
    list_resources_parser.add_argument("--server", help="Filter by server ID")
    
    # Create server
    create_parser = subparsers.add_parser("create", help="Create server from config")
    create_parser.add_argument("config", help="Path to config file")
    create_parser.add_argument("--output", help="Output path for exported config")
    
    # Test tool
    test_tool_parser = subparsers.add_parser("test-tool", help="Test tool execution")
    test_tool_parser.add_argument("server", help="Server ID")
    test_tool_parser.add_argument("tool", help="Tool name")
    test_tool_parser.add_argument("params", help="Parameters as JSON string")
    
    # Test prompt
    test_prompt_parser = subparsers.add_parser("test-prompt", help="Test prompt rendering")
    test_prompt_parser.add_argument("server", help="Server ID")
    test_prompt_parser.add_argument("prompt", help="Prompt name")
    test_prompt_parser.add_argument("context", help="Context as JSON string")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    if args.command == "list-servers":
        asyncio.run(cmd_list_servers(args.registry))
    elif args.command == "list-tools":
        asyncio.run(cmd_list_tools(args.server))
    elif args.command == "list-prompts":
        asyncio.run(cmd_list_prompts(args.server))
    elif args.command == "list-resources":
        asyncio.run(cmd_list_resources(args.server))
    elif args.command == "create":
        asyncio.run(cmd_create_server(args.config, args.output))
    elif args.command == "test-tool":
        asyncio.run(cmd_test_tool(args.server, args.tool, args.params))
    elif args.command == "test-prompt":
        asyncio.run(cmd_test_prompt(args.server, args.prompt, args.context))


if __name__ == "__main__":
    main()
