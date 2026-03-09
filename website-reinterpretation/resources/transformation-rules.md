---
type: resource
name: transformation-rules
description: Rules for transforming different component types
---

# Transformation Rules

Rules for converting HTML/CSS/React components to ASCII/dithered/shaded panes.

## Component Type Rules

### Header
- **Pane Type**: Panel
- **Effects**: ASCII border, dithering background, shader overlay
- **Preserve**: Navigation links, logo (as ASCII)
- **Transform**: Background images → ASCII art

### Navigation
- **Pane Type**: Panel
- **Effects**: ASCII menu bar, dithering
- **Preserve**: All links and functionality
- **Transform**: Icons → ASCII characters

### Card/Article
- **Pane Type**: Card
- **Effects**: Dithering background, ASCII content, shader overlay
- **Preserve**: Text content, links
- **Transform**: Images → ASCII art, backgrounds → dithered

### Button
- **Pane Type**: Button
- **Effects**: ASCII border, dithering, hover effects
- **Preserve**: Click functionality, text
- **Transform**: Background → dithered pattern

### Image
- **Pane Type**: Image
- **Effects**: ASCII art conversion
- **Preserve**: Alt text, aspect ratio
- **Transform**: Full image → ASCII representation

### Text Block
- **Pane Type**: Text Block
- **Effects**: Dithering on text, ASCII conversion
- **Preserve**: Content, structure
- **Transform**: Font rendering → ASCII characters

### Form/Input
- **Pane Type**: Panel
- **Effects**: ASCII borders, dithering background
- **Preserve**: Input functionality, labels
- **Transform**: Styling → ASCII/dithered

### Modal/Dialog
- **Pane Type**: Modal
- **Effects**: ASCII border, shader overlay
- **Preserve**: Content, buttons, functionality
- **Transform**: Background → dithered, images → ASCII

## Effect Application Rules

### ASCII Conversion
- Apply to: Text, images, icons
- Width: 80 characters default
- Character set: Extended ASCII
- Preserve: Structure, hierarchy

### Dithering
- Apply to: Backgrounds, images, graphics
- Method: Floyd-Steinberg default
- Intensity: 0.7 default
- Preserve: Content readability

### Shader Effects
- Apply to: Entire page overlay
- Effects: Noise (0.15), grain (0.08), scanlines (true)
- Preserve: Content visibility
- Transform: Visual aesthetic only

## Layout Rules

### Pane Arrangement
- Maintain original layout structure
- Use ASCII borders to separate panes
- Preserve spacing relationships
- Stack vertically by default

### Content Hierarchy
- Preserve heading hierarchy (h1 > h2 > h3)
- Use ASCII borders to show hierarchy
- Maintain visual weight relationships

### Interactive Elements
- Preserve all links and buttons
- Maintain click targets
- Show hover states with ASCII effects
- Keep form functionality

## Content Preservation

### Must Preserve
- All text content
- Link URLs and functionality
- Form inputs and submissions
- Navigation structure
- Accessibility attributes

### Can Transform
- Visual styling
- Images and graphics
- Backgrounds
- Fonts and typography
- Colors and effects

### Can Remove
- Advertisements
- Tracking scripts
- Unnecessary animations
- Heavy media files
