#!/usr/bin/env python3
"""
Expanded UI Demo: Demonstrates website analysis, component generation, and theming.
Shows how MCP UI can act as a transformation/proxy barrier.
"""

import asyncio
from pathlib import Path
from .ui_transformer import (
    UIProxyBarrier, 
    Theme, 
    WebsiteAnalyzer,
    ThemeTransformer
)
from .mcp_ui_integration import MCPUIIntegration


async def demo_website_analysis():
    """Demonstrate website analysis and component generation."""
    print("=" * 60)
    print("WEBSITE ANALYSIS & COMPONENT GENERATION")
    print("=" * 60)
    
    base_integration = MCPUIIntegration()
    barrier = UIProxyBarrier(base_integration)
    
    # Example: Analyze a website (using example HTML)
    print("\n1. Analyzing website structure...")
    example_html = """
    <html>
        <head><style>
            .card { background: white; padding: 1rem; border-radius: 8px; }
            .button { background: blue; color: white; padding: 0.5rem 1rem; }
        </style></head>
        <body>
            <header id="main-header">
                <h1>Welcome</h1>
                <nav class="nav">
                    <a href="/home">Home</a>
                    <a href="/about">About</a>
                </nav>
            </header>
            <main>
                <article class="card">
                    <h2>Card Title</h2>
                    <p>Card content goes here.</p>
                    <button class="button">Click Me</button>
                </article>
            </main>
        </body>
    </html>
    """
    
    components = barrier.analyzer.analyze_html(example_html, base_url="https://example.com")
    print(f"   ✓ Extracted {len(components)} components")
    
    for comp in components:
        print(f"     - {comp.component_id} ({comp.component_type})")
    
    # Generate MCP resources
    print("\n2. Generating MCP UI components...")
    generated_ids = []
    for component in components:
        component_id = f"web/{component.component_id}"
        resource_uri = f"mcp-ui://{component_id}"
        
        base_integration.resources[resource_uri] = {
            "uri": resource_uri,
            "name": component.component_id.replace('_', ' ').title(),
            "description": f"Generated from website",
            "mimeType": "text/markdown",
            "content": component.markdown_content,
            "metadata": {
                "component_id": component_id,
                "component_type": component.component_type,
                "generated": True,
                "source_url": "https://example.com"
            }
        }
        generated_ids.append(component_id)
        print(f"   ✓ Created: {resource_uri}")
    
    print(f"\n   Generated {len(generated_ids)} components from website")


def demo_theme_transformation():
    """Demonstrate theme transformation."""
    print("\n" + "=" * 60)
    print("THEME TRANSFORMATION")
    print("=" * 60)
    
    # Create personal theme
    print("\n1. Creating personal theme...")
    personal_theme = Theme(
        name="dark-mode-personal",
        colors={
            "primary": "#00ff88",
            "secondary": "#444444",
            "background": "#1a1a1a",
            "text": "#ffffff"
        },
        fonts={
            "heading": "'Inter', sans-serif",
            "body": "'Inter', sans-serif",
            "monospace": "'Fira Code', monospace"
        },
        spacing={
            "small": "0.5rem",
            "medium": "1rem",
            "large": "2rem"
        },
        styles={
            "custom": """
            .card {
                background: var(--secondary-color);
                border-radius: 12px;
                padding: var(--spacing-medium);
            }
            """
        }
    )
    print(f"   ✓ Theme created: {personal_theme.name}")
    print(f"     Primary: {personal_theme.colors['primary']}")
    print(f"     Background: {personal_theme.colors['background']}")
    
    # Create transformer
    transformer = ThemeTransformer(personal_theme)
    
    # Transform a resource
    print("\n2. Transforming resource with theme...")
    original_resource = {
        "uri": "mcp-ui://main",
        "name": "Main Dashboard",
        "mimeType": "text/markdown",
        "content": "# Main Dashboard\n\nWelcome to the UI.",
        "metadata": {}
    }
    
    transformed = transformer.transform_resource(original_resource)
    print(f"   ✓ Resource transformed")
    print(f"     Theme applied: {transformed['metadata']['theme']}")
    print(f"     Content preview: {transformed['content'][:100]}...")


def demo_proxy_barrier():
    """Demonstrate proxy barrier functionality."""
    print("\n" + "=" * 60)
    print("PROXY BARRIER (Transformation Layer)")
    print("=" * 60)
    
    base_integration = MCPUIIntegration()
    
    # Create personal theme
    personal_theme = Theme(
        name="my-theme",
        colors={
            "primary": "#6366f1",
            "background": "#f8fafc",
            "text": "#1e293b"
        },
        fonts={
            "heading": "'Poppins', sans-serif",
            "body": "'Inter', sans-serif"
        },
        spacing={
            "small": "0.5rem",
            "medium": "1rem",
            "large": "2rem"
        },
        styles={}
    )
    
    # Create barrier with theme
    barrier = UIProxyBarrier(base_integration, theme=personal_theme)
    print("\n1. Proxy barrier created with personal theme")
    print(f"   Theme: {personal_theme.name}")
    
    # Get resource through barrier (with transformation)
    print("\n2. Accessing resource through barrier...")
    resource = barrier.get_resource("mcp-ui://main")
    
    if resource:
        print(f"   ✓ Resource retrieved")
        print(f"     URI: {resource['uri']}")
        print(f"     Theme applied: {resource['metadata'].get('theme', 'none')}")
        print(f"     Transformed: {resource['metadata'].get('transformed', False)}")
    
    # List all resources
    print("\n3. Available resources:")
    resources = barrier.list_resources()
    print(f"   Total resources: {len(resources)}")
    for r in resources[:3]:
        print(f"     - {r['uri']}: {r['name']}")


def demo_complete_workflow():
    """Demonstrate complete workflow: analyze → generate → theme."""
    print("\n" + "=" * 60)
    print("COMPLETE WORKFLOW")
    print("=" * 60)
    
    base_integration = MCPUIIntegration()
    
    # Step 1: Create personal theme
    print("\n1. Setting up personal theme...")
    theme = Theme(
        name="abhinav-theme",
        colors={
            "primary": "#8b5cf6",
            "secondary": "#a78bfa",
            "background": "#0f172a",
            "text": "#e2e8f0"
        },
        fonts={
            "heading": "'Space Grotesk', sans-serif",
            "body": "'Inter', sans-serif"
        },
        spacing={
            "small": "0.5rem",
            "medium": "1rem",
            "large": "2rem"
        },
        styles={}
    )
    
    barrier = UIProxyBarrier(base_integration, theme=theme)
    print(f"   ✓ Theme: {theme.name}")
    
    # Step 2: Analyze website (simulated)
    print("\n2. Analyzing website...")
    example_html = """
    <header id="site-header">
        <h1>My Website</h1>
        <nav><a href="/">Home</a></nav>
    </header>
    <main>
        <article class="card">
            <h2>Article Title</h2>
            <p>Content here.</p>
        </article>
    </main>
    """
    
    components = barrier.analyzer.analyze_html(example_html, base_url="https://example.com")
    print(f"   ✓ Extracted {len(components)} components")
    
    # Step 3: Generate MCP resources
    print("\n3. Generating MCP components...")
    for component in components:
        component_id = f"web/{component.component_id}"
        resource_uri = f"mcp-ui://{component_id}"
        
        base_integration.resources[resource_uri] = {
            "uri": resource_uri,
            "name": component.component_id.replace('_', ' ').title(),
            "mimeType": "text/markdown",
            "content": component.markdown_content,
            "metadata": {
                "component_id": component_id,
                "component_type": component.component_type,
                "generated": True
            }
        }
        print(f"   ✓ {resource_uri}")
    
    # Step 4: Access through barrier (with theme)
    print("\n4. Accessing through barrier (with theme transformation)...")
    for component in components[:2]:
        component_id = f"web/{component.component_id}"
        resource = barrier.get_resource(f"mcp-ui://{component_id}")
        if resource:
            print(f"   ✓ {resource['uri']} - Theme: {resource['metadata'].get('theme')}")
    
    print("\n" + "=" * 60)
    print("WORKFLOW COMPLETE")
    print("=" * 60)
    print("\nThe system can now:")
    print("  ✅ Analyze websites and extract components")
    print("  ✅ Generate MCP UI components from websites")
    print("  ✅ Apply personal themes to all resources")
    print("  ✅ Act as a transformation barrier/proxy")


async def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("EXPANDED MCP UI SYSTEM DEMONSTRATION")
    print("=" * 60)
    print("\nThis demonstrates how MCP UI can be expanded to:")
    print("  1. Analyze websites and extract UI components")
    print("  2. Generate similar MCP components")
    print("  3. Apply personal themes as a 'barrier' layer")
    print("  4. Transform resources before serving them\n")
    
    # Run demos
    await demo_website_analysis()
    demo_theme_transformation()
    demo_proxy_barrier()
    demo_complete_workflow()


if __name__ == "__main__":
    asyncio.run(main())
