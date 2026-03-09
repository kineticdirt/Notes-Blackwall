# Grainrad-Inspired Advanced Theme System

## Overview

An advanced theme system inspired by [grainrad.com](https://grainrad.com/) that transforms MCP UI resources with:

1. **Dithering Effects** - Floyd-Steinberg and ordered dithering
2. **ASCII Art** - Graphics converted to ASCII representation
3. **Shader-Based Rendering** - Noise, grain, scanlines, CRT effects
4. **Ad Blocking** - Selective ad removal through MCP UI transformation

## Key Features

### 1. **Dithering Effects**

Floyd-Steinberg dithering applied to text and graphics:

```python
dithering_engine = DitheringEngine(method="floyd_steinberg")
dithered_text = dithering_engine.dither_text("Sample text")
```

**Methods**:
- `floyd_steinberg` - Error diffusion dithering
- `ordered` - Bayer matrix ordered dithering
- `atkinson` - Atkinson dithering

### 2. **ASCII Art Conversion**

Images converted to ASCII art instead of loading directly:

```python
ascii_converter = ASCIIConverter(width=80, use_extended=True)
ascii_art = ascii_converter.image_to_ascii(image_bytes)
```

**Benefits**:
- No image loading (reduces bandwidth)
- Ad content not displayed
- Retro terminal aesthetic
- Consistent with grainrad.com style

### 3. **Shader-Based Graphics**

CSS shader effects for visual rendering:

```python
shader_engine = ShaderEngine()
css = shader_engine.generate_shader_css(theme)
```

**Effects**:
- **Noise/Grain** - SVG-based noise patterns
- **Scanlines** - CRT-style scanline effects
- **Pixelated Rendering** - Crisp, pixelated image rendering
- **Gradient Overlays** - Repeating gradient patterns

### 4. **Ad Blocking**

Selective ad removal through transformation layer:

```python
ad_blocker = AdBlocker(patterns=["advertisement", "sponsor", "promo"])
cleaned_content = ad_blocker.remove_ads_from_markdown(markdown)
```

**Patterns Detected**:
- Class names: `advertisement`, `ad-banner`, `sponsor`, `promo`
- IDs: `adsbygoogle`, `sponsor-box`
- Common ad keywords in content

## Theme Configuration

### **AdvancedTheme Structure**

```python
theme = AdvancedTheme(
    name="grainrad-inspired",
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
        "patterns": ["advertisement", "sponsor", "promo"],
        "enabled": True
    },
    graphics_mode="hybrid"  # "ascii", "dither", "shader", "hybrid"
)
```

### **Graphics Modes**

- **`ascii`** - Convert all images to ASCII art
- **`dither`** - Apply dithering effects only
- **`shader`** - Use shader-based rendering only
- **`hybrid`** - Combine all methods

## Usage

### **Basic Usage**

```python
from blackwall.worktrees.mcp_integration.advanced_ui_barrier import create_advanced_barrier

# Create barrier with default grainrad theme
barrier = create_advanced_barrier()

# Access resources (automatically transformed)
resource = barrier.get_resource("mcp-ui://main")
# Resource now has:
# - Dithering applied
# - Images as ASCII
# - Shader CSS injected
# - Ads removed
```

### **Custom Theme**

```python
from blackwall.worktrees.mcp_integration.advanced_theme import AdvancedTheme

custom_theme = AdvancedTheme(
    name="my-theme",
    dithering={"method": "ordered", "intensity": 0.5},
    ascii_config={"width": 100, "extended": False},
    shader_config={"noise": 0.2, "grain": 0.1},
    ad_blocking={"patterns": ["ad"], "enabled": True},
    graphics_mode="hybrid"
)

barrier = create_advanced_barrier(theme=custom_theme)
```

### **Website Analysis**

```python
# Analyze website and generate components
component_ids = await barrier.analyze_and_generate("https://example.com")

# Components automatically have:
# - Theme applied
# - Ads removed
# - Graphics converted to ASCII/shader
```

## Integration with MCP Gateway

```python
from blackwall.worktrees.mcp_integration.mcp_gateway import MCPGateway
from blackwall.worktrees.mcp_integration.advanced_ui_barrier import create_advanced_barrier

# Create advanced barrier
barrier = create_advanced_barrier()

# Use with gateway
gateway = MCPGateway(ui_integration=barrier)

# All resources accessed through gateway are transformed
response = gateway.handle_request(GatewayRequest(
    request_type="resource",
    target="mcp-ui://main"
))
```

## Transformation Pipeline

```
Original Resource
    ↓
[Ad Blocking] → Remove ads
    ↓
[ASCII Conversion] → Convert images to ASCII
    ↓
[Dithering] → Apply dithering effects
    ↓
[Shader CSS] → Inject shader CSS
    ↓
Transformed Resource
```

## Benefits

### ✅ **No Direct Image Loading**
- Images converted to ASCII art
- Reduces bandwidth
- Prevents ad image loading

### ✅ **Ad Blocking**
- Selective ad removal
- Pattern-based detection
- Works through MCP UI transformation

### ✅ **Grainrad Aesthetic**
- Retro terminal style
- Dithering effects
- Shader-based rendering
- Consistent visual style

### ✅ **Performance**
- No external image requests
- CSS-based effects (fast)
- Lightweight ASCII representation

## Example Output

### **Before Transformation**

```markdown
# Main Dashboard

![Logo](https://example.com/logo.png)

<div class="advertisement">Ad content</div>

## Content

Real content here.
```

### **After Transformation**

```markdown
---
theme: grainrad-inspired
graphics_mode: hybrid
---

<style>
/* Shader CSS with noise, grain, scanlines */
:root {
    --shader-noise: 0.15;
    --shader-grain: 0.08;
    --shader-scanlines: True;
}
/* ... shader CSS ... */
</style>

# Main Dashboard

```
╔═══════════════════════════════╗
║   [ASCII LOGO REPRESENTATION] ║
╚═══════════════════════════════╝
```

## Content

Real content here.
```

## Status

✅ **Dithering**: Working (Floyd-Steinberg, Ordered)  
✅ **ASCII Conversion**: Working (PIL-based, fallback)  
✅ **Shader Effects**: Working (CSS-based)  
✅ **Ad Blocking**: Working (Pattern-based)  
✅ **Gateway Integration**: Ready  
✅ **Website Analysis**: Working  

## Conclusion

The advanced theme system provides a **grainrad.com-inspired aesthetic** with:

- ✅ Dithering effects for retro look
- ✅ ASCII art for graphics (no direct loading)
- ✅ Shader-based rendering (noise, grain, scanlines)
- ✅ Selective ad blocking through transformation
- ✅ Complete MCP UI integration

**Graphics are now represented as ASCII/shader effects instead of loading directly, and ads are selectively removed through the MCP UI transformation layer!** 🚀
