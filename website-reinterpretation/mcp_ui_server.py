"""
MCP UI Server: Serves transformation prompts and resources to AI agent.
Provides prompts and templates for website transformation guidance.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from blackwall.worktrees.mcp_integration.mcp_ui_integration import MCPUIIntegration


class MCPUIServer:
    """MCP UI Server for transformation prompts and resources."""
    
    def __init__(self, prompts_dir: Optional[Path] = None, resources_dir: Optional[Path] = None):
        """
        Initialize MCP UI server.
        
        Args:
            prompts_dir: Directory containing prompt templates
            resources_dir: Directory containing resource templates
        """
        if prompts_dir is None:
            prompts_dir = Path(__file__).parent / "prompts"
        if resources_dir is None:
            resources_dir = Path(__file__).parent / "resources"
        
        self.prompts_dir = Path(prompts_dir)
        self.resources_dir = Path(resources_dir)
        
        # Initialize MCP UI integration
        self.ui_integration = MCPUIIntegration()
        
        # Load prompts and resources
        self.prompts: Dict[str, str] = {}
        self.resources: Dict[str, Dict] = {}
        
        self._load_prompts()
        self._load_resources()
        self._register_as_resources()
    
    def _load_prompts(self):
        """Load prompt templates from markdown files."""
        if not self.prompts_dir.exists():
            return
        
        for prompt_file in self.prompts_dir.glob("*.md"):
            prompt_name = prompt_file.stem
            content = prompt_file.read_text()
            
            # Extract frontmatter if present
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    # Extract template content (after frontmatter)
                    template_content = parts[2].strip()
                    self.prompts[prompt_name] = template_content
            else:
                self.prompts[prompt_name] = content
    
    def _load_resources(self):
        """Load resource templates."""
        if not self.resources_dir.exists():
            return
        
        for resource_file in self.resources_dir.glob("*.md"):
            resource_name = resource_file.stem
            content = resource_file.read_text()
            
            # Extract frontmatter
            metadata = {}
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    # Parse frontmatter (simple YAML-like)
                    frontmatter = parts[1]
                    for line in frontmatter.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            metadata[key.strip()] = value.strip().strip('"\'')
                    content = parts[2].strip()
            
            self.resources[resource_name] = {
                "name": resource_name,
                "content": content,
                "metadata": metadata
            }
    
    def _register_as_resources(self):
        """Register prompts and resources as MCP UI resources."""
        # Register prompts
        for prompt_name, prompt_content in self.prompts.items():
            resource_uri = f"mcp-ui://prompts/{prompt_name}"
            self.ui_integration.resources[resource_uri] = {
                "uri": resource_uri,
                "name": f"Prompt: {prompt_name}",
                "description": f"Transformation prompt template: {prompt_name}",
                "mimeType": "text/markdown",
                "content": prompt_content,
                "metadata": {
                    "type": "prompt",
                    "prompt_name": prompt_name
                }
            }
        
        # Register resources
        for resource_name, resource_data in self.resources.items():
            resource_uri = f"mcp-ui://resources/{resource_name}"
            self.ui_integration.resources[resource_uri] = {
                "uri": resource_uri,
                "name": f"Resource: {resource_name}",
                "description": resource_data.get("metadata", {}).get("description", f"Resource: {resource_name}"),
                "mimeType": "text/markdown",
                "content": resource_data["content"],
                "metadata": {
                    "type": "resource",
                    "resource_name": resource_name,
                    **resource_data.get("metadata", {})
                }
            }
    
    def get_prompt(self, prompt_id: str, context: Optional[Dict] = None) -> str:
        """
        Get rendered prompt template.
        
        Args:
            prompt_id: Prompt identifier (e.g., "website-analysis")
            context: Context variables to render into prompt
            
        Returns:
            Rendered prompt string
        """
        prompt_template = self.prompts.get(prompt_id)
        if not prompt_template:
            raise ValueError(f"Prompt '{prompt_id}' not found")
        
        # Simple template rendering
        rendered = prompt_template
        if context:
            for key, value in context.items():
                # Handle different value types
                if isinstance(value, (dict, list)):
                    value_str = json.dumps(value, indent=2)
                else:
                    value_str = str(value)
                
                # Replace placeholders
                rendered = rendered.replace(f"{{{key}}}", value_str)
        
        return rendered
    
    def get_resource(self, resource_id: str) -> Optional[Dict]:
        """
        Get resource data.
        
        Args:
            resource_id: Resource identifier (e.g., "component-templates")
            
        Returns:
            Resource data dict or None
        """
        return self.resources.get(resource_id)
    
    def list_prompts(self) -> List[str]:
        """List available prompt IDs."""
        return list(self.prompts.keys())
    
    def list_resources(self) -> List[str]:
        """List available resource IDs."""
        return list(self.resources.keys())
    
    def get_mcp_resource(self, uri: str) -> Optional[Dict]:
        """
        Get MCP UI resource by URI.
        
        Args:
            uri: Resource URI (e.g., "mcp-ui://prompts/website-analysis")
            
        Returns:
            Resource dict or None
        """
        return self.ui_integration.get_resource(uri)
    
    def list_mcp_resources(self) -> List[Dict]:
        """List all MCP UI resources."""
        return self.ui_integration.list_resources()


def create_mcp_ui_server(prompts_dir: Optional[Path] = None,
                         resources_dir: Optional[Path] = None) -> MCPUIServer:
    """Create MCP UI server instance."""
    return MCPUIServer(prompts_dir=prompts_dir, resources_dir=resources_dir)
