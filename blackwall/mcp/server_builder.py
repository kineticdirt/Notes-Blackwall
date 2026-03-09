"""
MCP Server Builder - Easy creation of reusable MCP servers with tools, prompts, and resources.
"""

from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
import json

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

from .server_framework import (
    MCPServer, MCPToolDefinition, MCPPromptTemplate, MCPResource,
    ResourceAccess, BackendConnection, HTTPBackendConnection
)


class MCPServerBuilder:
    """Builder for creating MCP servers easily."""
    
    def __init__(self, server_id: str, name: str, description: str):
        """
        Initialize server builder.
        
        Args:
            server_id: Unique server identifier
            name: Server name
            description: Server description
        """
        self.server_id = server_id
        self.name = name
        self.description = description
        self.backend: Optional[BackendConnection] = None
        self.tools: List[MCPToolDefinition] = []
        self.prompts: List[MCPPromptTemplate] = []
        self.resources: List[MCPResource] = []
    
    def with_backend(self, backend: BackendConnection) -> 'MCPServerBuilder':
        """Add backend connection."""
        self.backend = backend
        return self
    
    def with_http_backend(self, base_url: str, api_key: Optional[str] = None,
                          headers: Optional[Dict[str, str]] = None) -> 'MCPServerBuilder':
        """Add HTTP backend connection."""
        self.backend = HTTPBackendConnection(base_url, api_key, headers)
        return self
    
    def add_tool(self, name: str, description: str, parameters: Dict[str, Any],
                 handler: Optional[Callable] = None,
                 resource_access: Optional[List[str]] = None,
                 access_level: ResourceAccess = ResourceAccess.NONE,
                 metadata: Optional[Dict[str, Any]] = None) -> 'MCPServerBuilder':
        """
        Add a tool to the server.
        
        Args:
            name: Tool name
            description: Tool description
            parameters: Tool parameters schema
            handler: Tool handler function (optional)
            resource_access: List of resource URIs this tool can access
            access_level: Required access level for resources
            metadata: Additional metadata
        """
        tool = MCPToolDefinition(
            name=name,
            description=description,
            parameters=parameters,
            resource_access=resource_access or [],
            access_level=access_level,
            handler=handler,
            metadata=metadata or {}
        )
        self.tools.append(tool)
        return self
    
    def add_prompt(self, name: str, description: str, template: str,
                   variables: Optional[List[str]] = None,
                   resource_access: Optional[List[str]] = None,
                   access_level: ResourceAccess = ResourceAccess.READ_ONLY,
                   metadata: Optional[Dict[str, Any]] = None) -> 'MCPServerBuilder':
        """
        Add a prompt template to the server.
        
        Args:
            name: Prompt name
            description: Prompt description
            template: Prompt template string (use {variable} for variables)
            variables: List of variable names in template
            resource_access: List of resource URIs this prompt can access
            access_level: Required access level for resources
            metadata: Additional metadata
        """
        # Auto-detect variables from template
        if not variables:
            import re
            variables = re.findall(r'\{(\w+)\}', template)
        
        prompt = MCPPromptTemplate(
            name=name,
            description=description,
            template=template,
            variables=variables or [],
            resource_access=resource_access or [],
            access_level=access_level,
            metadata=metadata or {}
        )
        self.prompts.append(prompt)
        return self
    
    def add_resource(self, uri: str, name: str, description: str,
                     mime_type: str = "application/json",
                     access_level: ResourceAccess = ResourceAccess.READ_ONLY,
                     data: Optional[Any] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> 'MCPServerBuilder':
        """
        Add a resource to the server.
        
        Args:
            uri: Resource URI
            name: Resource name
            description: Resource description
            mime_type: MIME type
            access_level: Access level for this resource
            data: Resource data (optional)
            metadata: Additional metadata
        """
        resource_metadata = metadata or {}
        if data is not None:
            resource_metadata["data"] = data
        
        resource = MCPResource(
            uri=uri,
            name=name,
            description=description,
            mime_type=mime_type,
            access_level=access_level,
            metadata=resource_metadata
        )
        self.resources.append(resource)
        return self
    
    def build(self) -> MCPServer:
        """Build the MCP server."""
        server = MCPServer(
            server_id=self.server_id,
            name=self.name,
            description=self.description,
            backend=self.backend
        )
        
        # Register all components
        for tool in self.tools:
            server.register_tool(tool)
        
        for prompt in self.prompts:
            server.register_prompt(prompt)
        
        for resource in self.resources:
            server.register_resource(resource)
        
        return server
    
    def from_config(self, config_path: str) -> 'MCPServerBuilder':
        """
        Load server configuration from file.
        
        Args:
            config_path: Path to config file (JSON or YAML)
        """
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(path, 'r') as f:
            if path.suffix in ['.yaml', '.yml']:
                if not YAML_AVAILABLE:
                    raise ImportError("PyYAML is required for YAML config files. Install with: pip install pyyaml")
                config = yaml.safe_load(f)
            else:
                config = json.load(f)
        
        # Load backend config
        if "backend" in config:
            backend_config = config["backend"]
            if backend_config.get("type") == "http":
                self.with_http_backend(
                    backend_config["base_url"],
                    backend_config.get("api_key"),
                    backend_config.get("headers")
                )
        
        # Load tools
        for tool_config in config.get("tools", []):
            self.add_tool(
                name=tool_config["name"],
                description=tool_config["description"],
                parameters=tool_config.get("parameters", {}),
                resource_access=tool_config.get("resource_access", []),
                access_level=ResourceAccess(tool_config.get("access_level", "none")),
                metadata=tool_config.get("metadata", {})
            )
        
        # Load prompts
        for prompt_config in config.get("prompts", []):
            self.add_prompt(
                name=prompt_config["name"],
                description=prompt_config["description"],
                template=prompt_config["template"],
                variables=prompt_config.get("variables", []),
                resource_access=prompt_config.get("resource_access", []),
                access_level=ResourceAccess(prompt_config.get("access_level", "read_only")),
                metadata=prompt_config.get("metadata", {})
            )
        
        # Load resources
        for resource_config in config.get("resources", []):
            self.add_resource(
                uri=resource_config["uri"],
                name=resource_config["name"],
                description=resource_config["description"],
                mime_type=resource_config.get("mime_type", "application/json"),
                access_level=ResourceAccess(resource_config.get("access_level", "read_only")),
                data=resource_config.get("data"),
                metadata=resource_config.get("metadata", {})
            )
        
        return self
    
    def save_config(self, output_path: str):
        """Save server configuration to file."""
        config = {
            "server_id": self.server_id,
            "name": self.name,
            "description": self.description,
            "backend": {
                "type": type(self.backend).__name__.lower().replace("backendconnection", "") if self.backend else None,
                "base_url": self.backend.base_url if isinstance(self.backend, HTTPBackendConnection) else None,
                "api_key": self.backend.api_key if isinstance(self.backend, HTTPBackendConnection) else None
            } if self.backend else None,
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                    "resource_access": tool.resource_access,
                    "access_level": tool.access_level.value,
                    "metadata": tool.metadata
                }
                for tool in self.tools
            ],
            "prompts": [
                {
                    "name": prompt.name,
                    "description": prompt.description,
                    "template": prompt.template,
                    "variables": prompt.variables,
                    "resource_access": prompt.resource_access,
                    "access_level": prompt.access_level.value,
                    "metadata": prompt.metadata
                }
                for prompt in self.prompts
            ],
            "resources": [
                {
                    "uri": resource.uri,
                    "name": resource.name,
                    "description": resource.description,
                    "mime_type": resource.mime_type,
                    "access_level": resource.access_level.value,
                    "data": resource.metadata.get("data"),
                    "metadata": {k: v for k, v in resource.metadata.items() if k != "data"}
                }
                for resource in self.resources
            ]
        }
        
        path = Path(output_path)
        with open(path, 'w') as f:
            if path.suffix in ['.yaml', '.yml']:
                if not YAML_AVAILABLE:
                    raise ImportError("PyYAML is required for YAML config files. Install with: pip install pyyaml")
                yaml.dump(config, f, default_flow_style=False)
            else:
                json.dump(config, f, indent=2)


def create_server_from_config(config_path: str) -> MCPServer:
    """Convenience function to create server from config file."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(path, 'r') as f:
        if path.suffix in ['.yaml', '.yml']:
            if not YAML_AVAILABLE:
                raise ImportError("PyYAML is required for YAML config files. Install with: pip install pyyaml")
            config = yaml.safe_load(f)
        else:
            config = json.load(f)
    
    builder = MCPServerBuilder(
        server_id=config["server_id"],
        name=config["name"],
        description=config["description"]
    )
    
    builder.from_config(config_path)
    return builder.build()
