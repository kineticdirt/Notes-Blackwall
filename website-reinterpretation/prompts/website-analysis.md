---
type: prompt
name: website-analysis
description: Prompt for analyzing website structure and components
---

# Website Analysis Prompt

You are analyzing a website to transform it into ASCII/dithered/shaded visual panes.

## Website Data

**URL**: {url}

**HTML Structure**:
```html
{html_preview}
```

**CSS Files**: {css_count} stylesheets found

**JavaScript Files**: {js_count} scripts found

**Components Detected**: {component_count}
- {component_list}

## Analysis Task

Analyze this website and provide:

1. **Visual Hierarchy**
   - Identify main sections (header, nav, content, footer, sidebar)
   - Determine component relationships (parent-child)
   - Note layout patterns (grid, flex, stacked)

2. **Component Types**
   - Classify each component (panel, card, button, nav, modal, etc.)
   - Identify interactive elements
   - Note content-heavy vs. structural components

3. **Styling Patterns**
   - Color schemes
   - Typography patterns
   - Spacing and layout
   - Visual effects (shadows, gradients, etc.)

4. **Transformation Recommendations**
   - Which components should become visual panes?
   - What ASCII/dithering/shader effects should be applied?
   - How should panes be arranged?
   - What content should be preserved vs. transformed?

## Output Format

Return JSON with:
```json
{
  "hierarchy": {
    "main_sections": [...],
    "component_tree": {...}
  },
  "component_analysis": [
    {
      "component_id": "...",
      "type": "panel|card|button|...",
      "recommended_pane_type": "...",
      "transformation_strategy": {
        "apply_ascii": true|false,
        "apply_dithering": true|false,
        "apply_shaders": true|false,
        "preserve_content": true|false
      }
    }
  ],
  "overall_strategy": {
    "layout": "vertical|horizontal|grid",
    "theme": "dark|light",
    "effects": ["dithering", "ascii", "shaders"]
  }
}
```

Analyze the website and provide structured recommendations for transformation.
