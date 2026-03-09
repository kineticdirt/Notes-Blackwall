"""
Grainrad MCP Server: Exposes grainrad theme capabilities as MCP tools/resources.
"""

import base64
import io
import uuid
from typing import Dict, List, Optional, Any
from pathlib import Path

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from blackwall.mcp.server_framework import MCPServer, MCPToolDefinition, MCPResource, ResourceAccess
from blackwall.worktrees.mcp_integration.advanced_theme import (
    DitheringEngine,
    ASCIIConverter,
    ShaderEngine,
    AdBlocker,
    AdvancedTheme
)


class GrainradMCPServer(MCPServer):
    """MCP Server exposing grainrad theme transformations."""
    
    def __init__(self):
        """Initialize grainrad MCP server."""
        super().__init__(
            server_id="grainrad-theme",
            name="Grainrad Theme Server",
            description="MCP server for grainrad theme transformations (dithering, ASCII, shaders, ad blocking)"
        )
        
        # Processing engines
        self.dithering_engine = DitheringEngine(method="floyd_steinberg")
        self.ascii_converter = ASCIIConverter(width=80, use_extended=True)
        self.shader_engine = ShaderEngine()
        self.ad_blocker = AdBlocker(["advertisement", "ad-banner", "sponsor", "promo", "adsbygoogle"])
        
        # State management
        self.processed_content: Dict[str, Dict] = {}
        self.stats = {
            "images_processed": 0,
            "ads_blocked": 0,
            "transformations_applied": 0
        }
        
        # Register tools and resources
        self._register_tools()
        self._register_resources()
    
    def _register_tools(self):
        """Register MCP tools."""
        # Tool 1: Apply dithering
        self.register_tool(MCPToolDefinition(
            name="apply_dithering",
            description="Apply Floyd-Steinberg dithering to image",
            parameters={
                "type": "object",
                "properties": {
                    "image_data": {
                        "type": "string",
                        "description": "Base64 encoded image data"
                    },
                    "method": {
                        "type": "string",
                        "enum": ["floyd_steinberg", "ordered"],
                        "default": "floyd_steinberg",
                        "description": "Dithering method"
                    }
                },
                "required": ["image_data"]
            },
            handler=self._apply_dithering_handler
        ))
        
        # Tool 2: Convert to ASCII
        self.register_tool(MCPToolDefinition(
            name="convert_to_ascii",
            description="Convert image to ASCII art",
            parameters={
                "type": "object",
                "properties": {
                    "image_data": {
                        "type": "string",
                        "description": "Base64 encoded image data"
                    },
                    "width": {
                        "type": "integer",
                        "default": 80,
                        "description": "ASCII art width in characters"
                    }
                },
                "required": ["image_data"]
            },
            handler=self._convert_to_ascii_handler
        ))
        
        # Tool 3: Apply shader effects
        self.register_tool(MCPToolDefinition(
            name="apply_shader_effects",
            description="Generate shader CSS effects (noise, grain, scanlines)",
            parameters={
                "type": "object",
                "properties": {
                    "noise": {
                        "type": "number",
                        "default": 0.15,
                        "description": "Noise intensity (0-1)"
                    },
                    "grain": {
                        "type": "number",
                        "default": 0.08,
                        "description": "Grain intensity (0-1)"
                    },
                    "scanlines": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable scanline effects"
                    }
                }
            },
            handler=self._apply_shader_effects_handler
        ))
        
        # Tool 4: Remove ads
        self.register_tool(MCPToolDefinition(
            name="remove_ads",
            description="Remove ads from HTML content",
            parameters={
                "type": "object",
                "properties": {
                    "html_content": {
                        "type": "string",
                        "description": "HTML content to clean"
                    },
                    "patterns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["advertisement", "sponsor", "promo"],
                        "description": "Ad patterns to block"
                    }
                },
                "required": ["html_content"]
            },
            handler=self._remove_ads_handler
        ))
        
        # Tool 5: Transform content (complete pipeline)
        self.register_tool(MCPToolDefinition(
            name="transform_content",
            description="Complete transformation pipeline: dithering + ASCII + shaders",
            parameters={
                "type": "object",
                "properties": {
                    "image_data": {
                        "type": "string",
                        "description": "Base64 encoded image data"
                    },
                    "apply_dithering": {
                        "type": "boolean",
                        "default": True
                    },
                    "apply_ascii": {
                        "type": "boolean",
                        "default": True
                    },
                    "apply_shaders": {
                        "type": "boolean",
                        "default": True
                    }
                },
                "required": ["image_data"]
            },
            handler=self._transform_content_handler
        ))
    
    def _register_resources(self):
        """Register MCP resources."""
        # Resource: Theme config
        self.register_resource(MCPResource(
            uri="grainrad://theme/config",
            name="Grainrad Theme Config",
            description="Current theme configuration",
            mime_type="application/json",
            access_level=ResourceAccess.READ_ONLY,
            metadata={"type": "config"}
        ))
        
        # Resource: Stats
        self.register_resource(MCPResource(
            uri="grainrad://stats",
            name="Processing Statistics",
            description="Transformation statistics",
            mime_type="application/json",
            access_level=ResourceAccess.READ_ONLY,
            metadata={"type": "stats"}
        ))
    
    async def _apply_dithering_handler(self, image_data: str, method: str = "floyd_steinberg") -> Dict:
        """Handle dithering tool call."""
        try:
            from PIL import Image
            
            # Decode base64
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to grayscale if needed
            if image.mode != 'L':
                image = image.convert('L')
            
            # Apply dithering (simplified - using PIL's built-in)
            dithered = image.convert('1')  # 1-bit (dithered)
            
            # Convert back to grayscale for display
            dithered = dithered.convert('L')
            
            # Save to bytes
            output = io.BytesIO()
            dithered.save(output, format='PNG')
            output_bytes = output.getvalue()
            
            # Store result
            content_id = str(uuid.uuid4())[:8]
            self.processed_content[content_id] = {
                "type": "dithered",
                "image_data": base64.b64encode(output_bytes).decode(),
                "method": method
            }
            
            self.stats["images_processed"] += 1
            self.stats["transformations_applied"] += 1
            
            return {
                "success": True,
                "content_id": content_id,
                "dithered_image": base64.b64encode(output_bytes).decode(),
                "method": method
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _convert_to_ascii_handler(self, image_data: str, width: int = 80) -> Dict:
        """Handle ASCII conversion tool call."""
        try:
            from PIL import Image
            
            # Decode base64
            image_bytes = base64.b64decode(image_data)
            
            # Convert to ASCII
            ascii_art = self.ascii_converter.image_to_ascii(image_bytes)
            
            # Store result
            content_id = str(uuid.uuid4())[:8]
            self.processed_content[content_id] = {
                "type": "ascii",
                "ascii_art": ascii_art,
                "width": width
            }
            
            self.stats["images_processed"] += 1
            self.stats["transformations_applied"] += 1
            
            return {
                "success": True,
                "content_id": content_id,
                "ascii_art": ascii_art,
                "width": width
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _apply_shader_effects_handler(self, noise: float = 0.15, grain: float = 0.08, scanlines: bool = True) -> Dict:
        """Handle shader effects tool call."""
        try:
            # Create theme config
            theme = AdvancedTheme(
                name="grainrad-default",
                dithering={"method": "floyd_steinberg"},
                ascii_config={"width": 80},
                shader_config={
                    "noise": noise,
                    "grain": grain,
                    "scanlines": scanlines
                },
                ad_blocking={"patterns": []},
                graphics_mode="hybrid"
            )
            
            # Generate CSS
            css = self.shader_engine.generate_shader_css(theme)
            
            return {
                "success": True,
                "shader_css": css,
                "config": {
                    "noise": noise,
                    "grain": grain,
                    "scanlines": scanlines
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _remove_ads_handler(self, html_content: str, patterns: List[str] = None) -> Dict:
        """Handle ad removal tool call."""
        try:
            if patterns:
                blocker = AdBlocker(patterns)
            else:
                blocker = self.ad_blocker
            
            cleaned = blocker.remove_ads_from_html(html_content)
            
            self.stats["ads_blocked"] += blocker.blocked_count
            
            return {
                "success": True,
                "cleaned_html": cleaned,
                "ads_blocked": blocker.blocked_count
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _transform_content_handler(self, image_data: str, 
                                        apply_dithering: bool = True,
                                        apply_ascii: bool = True,
                                        apply_shaders: bool = True) -> Dict:
        """Handle complete transformation pipeline."""
        try:
            results = {}
            content_id = str(uuid.uuid4())[:8]
            
            # Apply dithering
            if apply_dithering:
                dither_result = await self._apply_dithering_handler(image_data)
                if dither_result.get("success"):
                    results["dithered"] = dither_result
            
            # Apply ASCII
            if apply_ascii:
                ascii_result = await self._convert_to_ascii_handler(image_data)
                if ascii_result.get("success"):
                    results["ascii"] = ascii_result
            
            # Apply shaders
            if apply_shaders:
                shader_result = await self._apply_shader_effects_handler()
                if shader_result.get("success"):
                    results["shaders"] = shader_result
            
            # Store complete transformation
            self.processed_content[content_id] = {
                "type": "complete",
                "results": results,
                "applied": {
                    "dithering": apply_dithering,
                    "ascii": apply_ascii,
                    "shaders": apply_shaders
                }
            }
            
            return {
                "success": True,
                "content_id": content_id,
                "results": results
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_resource(self, uri: str) -> Optional[Dict]:
        """Get resource by URI."""
        if uri == "grainrad://theme/config":
            return {
                "uri": uri,
                "name": "Grainrad Theme Config",
                "mimeType": "application/json",
                "content": {
                    "dithering_method": "floyd_steinberg",
                    "ascii_width": 80,
                    "shader_noise": 0.15,
                    "shader_grain": 0.08
                }
            }
        
        elif uri == "grainrad://stats":
            return {
                "uri": uri,
                "name": "Processing Statistics",
                "mimeType": "application/json",
                "content": self.stats
            }
        
        elif uri.startswith("grainrad://transformed/"):
            content_id = uri.replace("grainrad://transformed/", "")
            if content_id in self.processed_content:
                return {
                    "uri": uri,
                    "name": f"Transformed Content {content_id}",
                    "mimeType": "application/json",
                    "content": self.processed_content[content_id]
                }
        
        return None


def create_grainrad_server() -> GrainradMCPServer:
    """Create grainrad MCP server instance."""
    return GrainradMCPServer()
