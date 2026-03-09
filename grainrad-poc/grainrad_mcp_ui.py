"""
Grainrad MCP UI Integration: Registers transformed content as MCP UI resources.
"""

import sys
from pathlib import Path
from typing import Dict, Optional
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from blackwall.worktrees.mcp_integration.mcp_ui_integration import MCPUIIntegration


class GrainradMCPUI:
    """MCP UI integration for grainrad theme system."""
    
    def __init__(self):
        """Initialize MCP UI integration."""
        self.ui_integration = MCPUIIntegration()
        self.registered_resources: Dict[str, str] = {}  # content_id -> resource_uri
    
    def register_transformed_content(self, content_id: str, transformed_data: Dict) -> str:
        """
        Register transformed content as MCP resource.
        
        Args:
            content_id: Content identifier
            transformed_data: Transformed content data
            
        Returns:
            Resource URI
        """
        # Determine resource type
        content_type = transformed_data.get("type", "unknown")
        
        # Create resource URI
        resource_uri = f"mcp-ui://grainrad/{content_type}/{content_id}"
        
        # Format content as markdown
        markdown_content = self._format_as_markdown(transformed_data)
        
        # Register resource
        self.ui_integration.resources[resource_uri] = {
            "uri": resource_uri,
            "name": f"Grainrad {content_type.title()} {content_id}",
            "description": f"Transformed content: {content_type}",
            "mimeType": "text/markdown",
            "content": markdown_content,
            "metadata": {
                "content_id": content_id,
                "content_type": content_type,
                "transformations": transformed_data.get("applied", {}),
                "ai_verification": transformed_data.get("ai_verification", {})
            }
        }
        
        self.registered_resources[content_id] = resource_uri
        
        return resource_uri
    
    def _format_as_markdown(self, data: Dict) -> str:
        """Format transformed data as markdown."""
        content_type = data.get("type", "unknown")
        
        if content_type == "dithered":
            return f"""# Dithered Image

**Method**: {data.get('method', 'unknown')}

![Dithered Image](data:image/png;base64,{data.get('image_data', '')})
"""
        
        elif content_type == "ascii":
            ascii_art = data.get("ascii_art", "")
            return f"""# ASCII Art

**Width**: {data.get('width', 80)} characters

```
{ascii_art}
```
"""
        
        elif content_type == "complete":
            results = data.get("results", {})
            markdown = "# Complete Transformation\n\n"
            
            if "dithered" in results:
                markdown += "## Dithered Image\n\n✓ Applied\n\n"
            
            if "ascii" in results:
                ascii_data = results["ascii"]
                markdown += f"## ASCII Art\n\n```\n{ascii_data.get('ascii_art', '')}\n```\n\n"
            
            if "shaders" in results:
                markdown += "## Shader Effects\n\n✓ Applied\n\n"
            
            return markdown
        
        else:
            return f"# Transformed Content\n\n```json\n{json.dumps(data, indent=2)}\n```"
    
    def get_resource(self, content_id: str) -> Optional[Dict]:
        """Get resource by content ID."""
        resource_uri = self.registered_resources.get(content_id)
        if resource_uri:
            return self.ui_integration.get_resource(resource_uri)
        return None
    
    def list_resources(self) -> list:
        """List all registered grainrad resources."""
        grainrad_resources = []
        for uri, resource in self.ui_integration.resources.items():
            if uri.startswith("mcp-ui://grainrad/"):
                grainrad_resources.append(resource)
        return grainrad_resources


def create_mcp_ui() -> GrainradMCPUI:
    """Create MCP UI integration instance."""
    return GrainradMCPUI()
