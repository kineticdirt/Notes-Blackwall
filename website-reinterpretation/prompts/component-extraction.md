---
type: prompt
name: component-extraction
description: Prompt for extracting and identifying website components
---

# Component Extraction Prompt

Extract and identify components from website HTML/CSS.

## HTML Content

```html
{html}
```

## CSS Styles

```css
{css}
```

## Task

Identify all visual components in this website:

1. **Structural Components**
   - Headers, footers, navigation
   - Main content areas
   - Sidebars, panels

2. **Content Components**
   - Cards, articles, posts
   - Lists, tables
   - Forms, inputs

3. **Interactive Components**
   - Buttons, links
   - Modals, dialogs
   - Dropdowns, menus

4. **Media Components**
   - Images, videos
   - Icons, logos
   - Backgrounds

For each component, provide:
- Component ID or selector
- Component type
- HTML structure
- CSS styles
- Visual characteristics (colors, size, position)

## Output Format

```json
{
  "components": [
    {
      "id": "header",
      "type": "header",
      "selector": "header#main-header",
      "html": "<header id='main-header'>...</header>",
      "styles": {
        "background": "#fff",
        "height": "60px"
      },
      "visual": {
        "colors": ["#fff", "#000"],
        "size": {"width": "100%", "height": "60px"},
        "position": "top"
      }
    }
  ]
}
```

Extract all components with their visual characteristics.
