"""
Cursor Cloud Agents MCP Integration

This module provides integration with Cursor Cloud Agents API using the MCP framework.
Enables launching, managing, and monitoring Cloud Agents via MCP tools.
"""

from typing import Dict, List, Any, Optional
import os
import json
from .server_framework import (
    MCPServer,
    HTTPBackendConnection,
    MCPToolDefinition,
    ResourceAccess,
    MCPServerRegistry
)
from .agent_integration import MCPAgentBridge, EnhancedMCPAgent


class CursorCloudAgentsBackend(HTTPBackendConnection):
    """Backend connection to Cursor Cloud Agents API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Cursor Cloud Agents API backend.
        
        Args:
            api_key: Cursor API key (defaults to CURSOR_API_KEY env var)
        """
        api_key = api_key or os.getenv("CURSOR_API_KEY")
        if not api_key:
            raise ValueError(
                "CURSOR_API_KEY environment variable required. "
                "Get your key from https://cursor.com/dashboard → Integrations"
            )
        
        # Cursor uses Basic Auth with API key as username
        super().__init__(
            base_url="https://api.cursor.com/v0",
            api_key=api_key,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Basic {api_key}"  # Cursor uses Basic Auth
            }
        )
    
    async def connect(self) -> bool:
        """Connect to Cursor API and verify authentication."""
        try:
            # Test connection with /me endpoint
            result = await self.execute("me", {})
            self._connected = True
            return True
        except Exception as e:
            print(f"Failed to connect to Cursor API: {e}")
            return False


def create_cloud_agents_server(api_key: Optional[str] = None) -> MCPServer:
    """
    Create MCP server for Cursor Cloud Agents API.
    
    Args:
        api_key: Optional API key (defaults to CURSOR_API_KEY env var)
        
    Returns:
        Configured MCPServer instance
    """
    backend = CursorCloudAgentsBackend(api_key)
    server = MCPServer(
        server_id="cursor-cloud-agents",
        name="Cursor Cloud Agents",
        description="MCP server for managing Cursor Cloud Agents via API",
        backend=backend
    )
    
    # Register launch_agent tool
    server.register_tool(MCPToolDefinition(
        name="launch_agent",
        description=(
            "Launch a new Cursor Cloud Agent to work on a GitHub repository. "
            "The agent will analyze the codebase and execute the provided instructions."
        ),
        parameters={
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "object",
                    "description": "Task instructions for the agent",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Instruction text describing the task"
                        },
                        "images": {
                            "type": "array",
                            "description": "Optional images (up to 5) with base64 data",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "data": {"type": "string"},
                                    "width": {"type": "integer"},
                                    "height": {"type": "integer"}
                                }
                            }
                        }
                    },
                    "required": ["text"]
                },
                "source": {
                    "type": "object",
                    "description": "Repository source configuration",
                    "properties": {
                        "repository": {
                            "type": "string",
                            "description": "GitHub repository URL (e.g., https://github.com/org/repo)"
                        },
                        "ref": {
                            "type": "string",
                            "description": "Git branch, tag, or commit hash (optional)"
                        }
                    },
                    "required": ["repository"]
                },
                "model": {
                    "type": "string",
                    "description": "LLM model to use (e.g., 'claude-4-sonnet'). Omit for auto-selection"
                },
                "target": {
                    "type": "object",
                    "description": "Target branch and PR configuration",
                    "properties": {
                        "branchName": {
                            "type": "string",
                            "description": "Custom branch name"
                        },
                        "autoCreatePr": {
                            "type": "boolean",
                            "description": "Automatically create PR on completion"
                        },
                        "openAsCursorGithubApp": {
                            "type": "boolean",
                            "description": "Open PR as Cursor GitHub App"
                        },
                        "skipReviewerRequest": {
                            "type": "boolean",
                            "description": "Skip adding user as reviewer"
                        }
                    }
                },
                "webhook": {
                    "type": "object",
                    "description": "Webhook configuration for status notifications",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "Webhook endpoint URL"
                        },
                        "secret": {
                            "type": "string",
                            "description": "Webhook secret for payload verification (min 32 chars)"
                        }
                    },
                    "required": ["url"]
                }
            },
            "required": ["prompt", "source"]
        },
        handler=launch_agent_handler,
        access_level=ResourceAccess.FULL
    ))
    
    # Register list_agents tool
    server.register_tool(MCPToolDefinition(
        name="list_agents",
        description="List all Cloud Agents with pagination support",
        parameters={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of agents to return (default: 20, max: 100)",
                    "minimum": 1,
                    "maximum": 100
                },
                "cursor": {
                    "type": "string",
                    "description": "Pagination cursor from previous response"
                }
            }
        },
        handler=list_agents_handler,
        access_level=ResourceAccess.READ_ONLY
    ))
    
    # Register get_agent tool
    server.register_tool(MCPToolDefinition(
        name="get_agent",
        description="Get detailed status information for a specific Cloud Agent",
        parameters={
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "description": "Unique agent identifier (e.g., bc_abc123)"
                }
            },
            "required": ["id"]
        },
        handler=get_agent_handler,
        access_level=ResourceAccess.READ_ONLY
    ))
    
    # Register get_agent_conversation tool
    server.register_tool(MCPToolDefinition(
        name="get_agent_conversation",
        description="Retrieve complete conversation history for an agent",
        parameters={
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "description": "Unique agent identifier"
                }
            },
            "required": ["id"]
        },
        handler=get_agent_conversation_handler,
        access_level=ResourceAccess.READ_ONLY
    ))
    
    # Register add_followup tool
    server.register_tool(MCPToolDefinition(
        name="add_followup",
        description="Send additional instructions to an existing Cloud Agent",
        parameters={
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "description": "Unique agent identifier"
                },
                "prompt": {
                    "type": "object",
                    "description": "Follow-up instructions",
                    "properties": {
                        "text": {"type": "string"},
                        "images": {
                            "type": "array",
                            "items": {"type": "object"}
                        }
                    },
                    "required": ["text"]
                }
            },
            "required": ["id", "prompt"]
        },
        handler=add_followup_handler,
        access_level=ResourceAccess.FULL
    ))
    
    # Register stop_agent tool
    server.register_tool(MCPToolDefinition(
        name="stop_agent",
        description="Pause execution of a running Cloud Agent",
        parameters={
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "description": "Unique agent identifier"
                }
            },
            "required": ["id"]
        },
        handler=stop_agent_handler,
        access_level=ResourceAccess.FULL
    ))
    
    # Register delete_agent tool
    server.register_tool(MCPToolDefinition(
        name="delete_agent",
        description="Permanently delete a Cloud Agent",
        parameters={
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "description": "Unique agent identifier"
                }
            },
            "required": ["id"]
        },
        handler=delete_agent_handler,
        access_level=ResourceAccess.FULL
    ))
    
    # Register list_repositories tool
    server.register_tool(MCPToolDefinition(
        name="list_repositories",
        description="List all GitHub repositories accessible to the authenticated user",
        parameters={
            "type": "object",
            "properties": {}
        },
        handler=list_repositories_handler,
        access_level=ResourceAccess.READ_ONLY
    ))
    
    # Register list_models tool
    server.register_tool(MCPToolDefinition(
        name="list_models",
        description="Get list of recommended LLM models available for Cloud Agents",
        parameters={
            "type": "object",
            "properties": {}
        },
        handler=list_models_handler,
        access_level=ResourceAccess.READ_ONLY
    ))
    
    return server


# Tool handlers

async def launch_agent_handler(params: Dict[str, Any], resources: Any, backend: Any) -> Dict[str, Any]:
    """Handle launch_agent tool execution."""
    return await backend.execute("agents", params)


async def list_agents_handler(params: Dict[str, Any], resources: Any, backend: Any) -> Dict[str, Any]:
    """Handle list_agents tool execution."""
    query_params = {}
    if "limit" in params:
        query_params["limit"] = params["limit"]
    if "cursor" in params:
        query_params["cursor"] = params["cursor"]
    
    # Note: This would need to be GET request, but our backend.execute uses POST
    # You may need to extend HTTPBackendConnection to support GET requests
    return await backend.execute("agents", query_params)


async def get_agent_handler(params: Dict[str, Any], resources: Any, backend: Any) -> Dict[str, Any]:
    """Handle get_agent tool execution."""
    agent_id = params["id"]
    return await backend.execute(f"agents/{agent_id}", {})


async def get_agent_conversation_handler(params: Dict[str, Any], resources: Any, backend: Any) -> Dict[str, Any]:
    """Handle get_agent_conversation tool execution."""
    agent_id = params["id"]
    return await backend.execute(f"agents/{agent_id}/conversation", {})


async def add_followup_handler(params: Dict[str, Any], resources: Any, backend: Any) -> Dict[str, Any]:
    """Handle add_followup tool execution."""
    agent_id = params["id"]
    followup_data = {"prompt": params["prompt"]}
    return await backend.execute(f"agents/{agent_id}/followup", followup_data)


async def stop_agent_handler(params: Dict[str, Any], resources: Any, backend: Any) -> Dict[str, Any]:
    """Handle stop_agent tool execution."""
    agent_id = params["id"]
    return await backend.execute(f"agents/{agent_id}/stop", {})


async def delete_agent_handler(params: Dict[str, Any], resources: Any, backend: Any) -> Dict[str, Any]:
    """Handle delete_agent tool execution."""
    agent_id = params["id"]
    return await backend.execute(f"agents/{agent_id}", {"method": "DELETE"})


async def list_repositories_handler(params: Dict[str, Any], resources: Any, backend: Any) -> Dict[str, Any]:
    """Handle list_repositories tool execution."""
    return await backend.execute("repositories", {})


async def list_models_handler(params: Dict[str, Any], resources: Any, backend: Any) -> Dict[str, Any]:
    """Handle list_models tool execution."""
    return await backend.execute("models", {})


# Convenience functions

async def setup_cloud_agents_integration(
    api_key: Optional[str] = None,
    registry: Optional[MCPServerRegistry] = None
) -> MCPAgentBridge:
    """
    Setup Cloud Agents MCP server integration.
    
    Args:
        api_key: Optional API key (defaults to CURSOR_API_KEY env var)
        registry: Optional existing registry (creates new if not provided)
        
    Returns:
        Configured MCPAgentBridge instance
    """
    server = create_cloud_agents_server(api_key)
    
    if registry:
        await registry.register_server(server)
        bridge = MCPAgentBridge(registry)
    else:
        bridge = MCPAgentBridge()
        await bridge.registry.register_server(server)
    
    await bridge.initialize()
    return bridge


async def create_cloud_agent_via_mcp(
    bridge: MCPAgentBridge,
    prompt_text: str,
    repository: str,
    branch: Optional[str] = None,
    auto_create_pr: bool = True,
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to launch a Cloud Agent via MCP.
    
    Args:
        bridge: MCPAgentBridge instance
        prompt_text: Task instructions
        repository: GitHub repository URL
        branch: Optional branch/ref
        auto_create_pr: Whether to auto-create PR
        model: Optional model name
        
    Returns:
        Agent creation result with agent ID
    """
    params = {
        "prompt": {"text": prompt_text},
        "source": {"repository": repository},
        "target": {"autoCreatePr": auto_create_pr}
    }
    
    if branch:
        params["source"]["ref"] = branch
    if model:
        params["model"] = model
    
    return await bridge.execute_tool("launch_agent", params)


# Example usage

async def example_usage():
    """Example of using Cloud Agents integration."""
    
    # Setup integration
    bridge = await setup_cloud_agents_integration()
    
    # Create enhanced agent
    agent = EnhancedMCPAgent("claude-cloud-bridge", bridge)
    await agent.initialize()
    
    # Launch a cloud agent
    result = await agent.use_tool(
        "launch_agent",
        prompt={
            "text": "Implement user authentication with JWT tokens"
        },
        source={
            "repository": "https://github.com/your-org/your-repo"
        },
        target={
            "autoCreatePr": True,
            "branchName": "feature/auth-implementation"
        }
    )
    
    agent_id = result.get("id")
    print(f"Cloud agent launched: {agent_id}")
    
    # Check status
    status = await agent.use_tool("get_agent", id=agent_id)
    print(f"Agent status: {status.get('status')}")
    
    # Add follow-up instruction
    await agent.use_tool(
        "add_followup",
        id=agent_id,
        prompt={
            "text": "Also add unit tests for the authentication flow"
        }
    )
    
    return agent_id


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
