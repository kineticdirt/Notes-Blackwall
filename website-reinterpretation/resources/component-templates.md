---
type: resource
name: component-templates
description: Templates for transforming different component types
---

# Component Transformation Templates

Templates for converting HTML components to ASCII/dithered/shaded visual panes.

## Panel Template

**Input**: HTML section/div
**Output**: ASCII-bordered panel

```
╔═══════════════════════════════════╗
║  {title}                          ║
╠═══════════════════════════════════╣
║                                   ║
║  {content}                         ║
║                                   ║
╚═══════════════════════════════════╝
```

**Transformation**:
- Extract title from h1-h6 or first text
- Convert content to ASCII
- Apply dithering to background
- Add shader overlay

## Card Template

**Input**: HTML card/article
**Output**: Dithered card with ASCII content

```
┌─────────────────────────────┐
│ {card_title}                │
├─────────────────────────────┤
│                             │
│ {card_content}              │
│                             │
│ [Button] [Link]             │
└─────────────────────────────┘
```

**Transformation**:
- Extract card title and content
- Apply dithering to card background
- Convert images to ASCII art
- Preserve links and buttons as ASCII

## Button Template

**Input**: HTML button/link-button
**Output**: ASCII button

```
┌──────────────┐
│  {text}      │
└──────────────┘
```

**Transformation**:
- Extract button text
- Create ASCII border
- Apply dithering effect
- Maintain click functionality

## Image Template

**Input**: HTML img element
**Output**: ASCII art representation

```
{ascii_art}
*{alt_text}*
```

**Transformation**:
- Convert image to ASCII art
- Use extended character set
- Preserve aspect ratio
- Show alt text below

## Text Block Template

**Input**: HTML text content
**Output**: Dithered ASCII text

```
{dithered_text}
```

**Transformation**:
- Convert text to ASCII
- Apply dithering pattern
- Preserve line breaks
- Maintain readability

## Navigation Template

**Input**: HTML nav/menu
**Output**: ASCII navigation menu

```
╔═══════════════════════════════╗
║ [Home] [About] [Contact]     ║
╚═══════════════════════════════╝
```

**Transformation**:
- Extract navigation links
- Create ASCII menu bar
- Preserve link functionality
- Apply dithering to background

## Modal/Dialog Template

**Input**: HTML modal/dialog
**Output**: ASCII modal pane

```
╔═══════════════════════════════╗
║  {modal_title}            [X] ║
╠═══════════════════════════════╣
║                               ║
║  {modal_content}              ║
║                               ║
║  [OK] [Cancel]                ║
╚═══════════════════════════════╝
```

**Transformation**:
- Extract modal content
- Create ASCII border
- Preserve buttons
- Apply shader overlay
