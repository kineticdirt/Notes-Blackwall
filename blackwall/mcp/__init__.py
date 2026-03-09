"""
MCP (Model Context Protocol) integration for Blackwall.
Provides framework for creating reusable MCP servers with tools, prompts, and resources.
"""

from .server_framework import (
    MCPServer,
    MCPServerRegistry,
    MCPToolDefinition,
    MCPPromptTemplate,
    MCPResource,
    ResourceAccess,
    BackendConnection,
    HTTPBackendConnection
)

from .server_builder import (
    MCPServerBuilder,
    create_server_from_config
)

from .mcp_integration import MCPIntegration

__all__ = [
    # Server framework
    "MCPServer",
    "MCPServerRegistry",
    "MCPToolDefinition",
    "MCPPromptTemplate",
    "MCPResource",
    "ResourceAccess",
    "BackendConnection",
    "HTTPBackendConnection",
    # Server builder
    "MCPServerBuilder",
    "create_server_from_config",
    # Integration
    "MCPIntegration"
]
