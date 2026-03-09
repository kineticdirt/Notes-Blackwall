---
type: prompt
name: transformation-strategy
description: Prompt for planning website transformation strategy
---

# Transformation Strategy Prompt

Plan the transformation of website components into ASCII/dithered/shaded visual panes.

## Components to Transform

{components_json}

## Transformation Goals

Convert this website into a grainrad-inspired aesthetic:
- ASCII art for text and images
- Dithering effects for backgrounds and graphics
- Shader effects (noise, grain, scanlines) for overall feel
- Visual panes with ASCII borders
- Maintain website functionality (links, navigation)

## Strategy Planning

For each component, determine:

1. **Pane Type**
   - Panel (bordered ASCII section)
   - Card (dithered card with content)
   - Button (ASCII button)
   - Image (ASCII art)
   - Text Block (dithered text)

2. **Effects to Apply**
   - ASCII conversion (for text/images)
   - Dithering (for backgrounds/graphics)
   - Shader effects (noise/grain/scanlines)

3. **Layout Considerations**
   - How panes should be arranged
   - Spacing between panes
   - Hierarchy preservation

4. **Content Preservation**
   - What content must be preserved (links, text)
   - What can be transformed (images, backgrounds)
   - What can be removed (ads, trackers)

## Output Format

```json
{
  "strategy": {
    "overall_approach": "description",
    "layout": {
      "type": "vertical|horizontal|grid",
      "pane_spacing": "number"
    }
  },
  "component_strategies": [
    {
      "component_id": "...",
      "pane_type": "panel|card|button|image|text",
      "effects": {
        "ascii": true|false,
        "dithering": true|false,
        "shaders": true|false
      },
      "parameters": {
        "ascii_width": 80,
        "dithering_method": "floyd_steinberg",
        "shader_intensity": 0.15
      },
      "preserve": ["links", "text", "structure"]
    }
  ]
}
```

Provide a complete transformation strategy.
