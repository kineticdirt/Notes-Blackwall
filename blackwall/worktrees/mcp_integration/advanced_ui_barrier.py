"""
Advanced UI Barrier: Integrates advanced theme system with UI proxy barrier.
Combines dithering, ASCII, shaders, and ad blocking.
"""

from typing import Optional, List, Callable
from .ui_transformer import UIProxyBarrier
from .mcp_ui_integration import MCPUIIntegration
from .advanced_theme import (
    AdvancedTheme,
    AdvancedThemeTransformer,
    DitheringEngine,
    ASCIIConverter,
    ShaderEngine,
    AdBlocker
)


class AdvancedUIBarrier(UIProxyBarrier):
    """
    Advanced UI Barrier with grainrad-inspired theme system.
    Extends UIProxyBarrier with advanced theming capabilities.
    """
    
    def __init__(self,
                 base_integration: MCPUIIntegration,
                 advanced_theme: Optional[AdvancedTheme] = None,
                 transformations: Optional[List[Callable]] = None):
        """
        Initialize advanced UI barrier.
        
        Args:
            base_integration: Base MCP UI integration
            advanced_theme: Advanced theme configuration
            transformations: Optional additional transformations
        """
        # Initialize base barrier (without theme, we'll handle it ourselves)
        super().__init__(base_integration, theme=None, transformations=transformations)
        
        # Set up advanced theme
        if advanced_theme is None:
            advanced_theme = self._create_default_theme()
        
        self.advanced_theme = advanced_theme
        self.advanced_transformer = AdvancedThemeTransformer(advanced_theme)
    
    def _create_default_theme(self) -> AdvancedTheme:
        """Create default grainrad-inspired theme."""
        return AdvancedTheme(
            name="grainrad-default",
            dithering={
                "method": "floyd_steinberg",
                "intensity": 0.7
            },
            ascii_config={
                "width": 80,
                "extended": True,
                "contrast": 1.2
            },
            shader_config={
                "noise": 0.15,
                "grain": 0.08,
                "scanlines": True,
                "crt_effect": True
            },
            ad_blocking={
                "patterns": [
                    "advertisement",
                    "ad-banner",
                    "sponsor",
                    "promo",
                    "adsbygoogle"
                ],
                "enabled": True
            },
            graphics_mode="hybrid"
        )
    
    def get_resource(self, uri: str) -> Optional[dict]:
        """
        Get resource with advanced theme transformations.
        
        Args:
            uri: Resource URI
            
        Returns:
            Transformed resource
        """
        # Get base resource
        resource = self.base_integration.get_resource(uri)
        if not resource:
            return None
        
        # Apply advanced theme transformation
        transformed = self.advanced_transformer.transform_resource(resource)
        
        # Apply any additional transformations
        for transform_func in self.transformations:
            transformed = transform_func(transformed)
        
        return transformed
    
    async def analyze_and_generate(self, url: str, component_prefix: str = "web") -> List[str]:
        """
        Analyze website and generate components with advanced theme.
        
        Args:
            url: Website URL
            component_prefix: Component ID prefix
            
        Returns:
            List of generated component IDs
        """
        # Use base analyzer
        components = await self.analyzer.analyze_url(url)
        
        generated_ids = []
        for component in components:
            component_id = f"{component_prefix}/{component.component_id}"
            resource_uri = f"mcp-ui://{component_id}"
            
            # Create resource with ad blocking applied
            content = component.markdown_content
            
            # Remove ads from content
            if self.advanced_theme.ad_blocking.get('enabled', True):
                content = self.advanced_transformer.ad_blocker.remove_ads_from_markdown(content)
            
            # Apply advanced theme transformations
            resource = {
                "uri": resource_uri,
                "name": component.component_id.replace('_', ' ').title(),
                "description": f"Generated from {component.metadata.get('source_url', url)}",
                "mimeType": "text/markdown",
                "content": content,
                "metadata": {
                    "component_id": component_id,
                    "component_type": component.component_type,
                    "generated": True,
                    "source_url": component.metadata.get('source_url', url),
                    "original_html": component.html_content,
                    "css_styles": component.css_styles
                }
            }
            
            # Transform with advanced theme
            transformed_resource = self.advanced_transformer.transform_resource(resource)
            
            self.base_integration.resources[resource_uri] = transformed_resource
            self.generated_components[component_id] = component
            generated_ids.append(component_id)
        
        return generated_ids
    
    def update_theme(self, theme: AdvancedTheme):
        """
        Update advanced theme.
        
        Args:
            theme: New theme configuration
        """
        self.advanced_theme = theme
        self.advanced_transformer = AdvancedThemeTransformer(theme)
    
    def get_theme_stats(self) -> dict:
        """Get theme statistics."""
        total_ads_blocked = sum(
            r.get('metadata', {}).get('ads_blocked', 0)
            for r in self.base_integration.resources.values()
        )
        
        return {
            "theme_name": self.advanced_theme.name,
            "graphics_mode": self.advanced_theme.graphics_mode,
            "dithering_method": self.advanced_theme.dithering.get('method'),
            "ascii_width": self.advanced_theme.ascii_config.get('width'),
            "ad_patterns": len(self.advanced_theme.ad_blocking.get('patterns', [])),
            "total_ads_blocked": total_ads_blocked,
            "resources": len(self.base_integration.resources)
        }


def create_advanced_barrier(theme: Optional[AdvancedTheme] = None) -> AdvancedUIBarrier:
    """
    Create advanced UI barrier with grainrad-inspired theme.
    
    Args:
        theme: Optional custom theme
        
    Returns:
        AdvancedUIBarrier instance
    """
    base_integration = MCPUIIntegration()
    return AdvancedUIBarrier(base_integration, advanced_theme=theme)
