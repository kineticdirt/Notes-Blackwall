# Pre and Post Processing Implementation Plan

Based on [Efecto (Codrops)](https://tympanus.net/codrops/2026/01/04/efecto-building-real-time-ascii-and-dithering-effects-with-webgl-shaders/) and [grainrad.com](https://grainrad.com/)

## Overview

Implement comprehensive pre and post-processing system for website proxy with:
- **Pre-processing**: Image preparation, pixelation, luminance calculation
- **Dithering**: Multiple algorithms (Floyd-Steinberg, Atkinson, Jarvis-Judice-Ninke, etc.)
- **ASCII Art**: Procedural character rendering
- **Post-processing**: Bloom, CRT effects (scanlines, curvature, chromatic aberration, vignette)

## Architecture

### Processing Pipeline

```
Original Image
    ↓
[Pre-Processing]
    ↓ Pixelation, Luminance
    ↓
[Dithering] (CPU)
    ↓ Error Diffusion
    ↓
[ASCII Conversion] (Optional, GPU)
    ↓ Procedural Characters
    ↓
[Post-Processing] (GPU)
    ↓ Bloom, CRT Effects
    ↓
Final Output
```

## Implementation Status

### ✅ Pre-Processing (`pre_post_processing.py`)

**PreProcessor Class**:
- `prepare_image()` - Image resizing and normalization
- `calculate_luminance()` - Perceptually accurate brightness (0.299*R + 0.587*G + 0.114*B)
- `pixelate()` - Block-based pixelation (1-10 block size)

### ✅ Dithering (`pre_post_processing.py`)

**DitheringProcessor Class**:
- **Floyd-Steinberg** (1976) - Classic error diffusion
- **Atkinson** (1984) - Macintosh style (75% error distribution)
- **Jarvis-Judice-Ninke** - 12-neighbor smooth gradients
- **Stucki, Burkes, Sierra** - Variations
- **Ordered** - Bayer matrix dithering

**Features**:
- Multi-color palette support
- Pixelation integration
- Error diffusion algorithms

### ✅ Color Palettes (`pre_post_processing.py`)

**Preset Palettes**:
- Game Boy (4-color green)
- Synthwave (pink, purple, cyan)
- Noir (monochrome)
- Amber (warm tones)
- Cyberpunk (neon)
- Campfire (warm)

**Custom Palette Support**:
- 2-6 colors
- Hex color input
- Category organization

### ✅ ASCII Conversion (`pre_post_processing.py`)

**ASCIIConverter Class**:
- 8 character set styles:
  - Standard, Dense, Minimal
  - Blocks, Braille, Technical
  - Matrix, Hatching
- Procedural character drawing
- Brightness-based character selection

### ✅ Post-Processing (`pre_post_processing.py`)

**PostProcessor Class**:
- **Bloom** - Bright pixel glow effect
- **Scanlines** - CRT horizontal bands
- **Curvature** - Screen curvature simulation
- **Chromatic Aberration** - RGB channel separation
- **Vignette** - Edge darkening

### ✅ WebGL Shaders (`webgl_shader_effects.py`)

**Shader Code**:
- ASCII fragment shader (procedural characters)
- CRT effects shader (scanlines, curvature, chromatic aberration, vignette)
- Bloom shader (glow effect)
- Post-processing pipeline (combined effects)

## Integration with Proxy

### Current Flow
```
Request → Cache → Fetch → Return
```

### Enhanced Flow (with Pre/Post Processing)
```
Request → Cache Check
    ↓
Fetch Website
    ↓
Extract Images
    ↓
[Pre-Processing]
    ↓
[Dithering] (CPU)
    ↓
[ASCII] (Optional, GPU)
    ↓
[Post-Processing] (GPU)
    ↓
Cache Processed
    ↓
Return
```

## Technical Details

### Dithering (CPU-Based)

**Why CPU?**
- Error diffusion is inherently sequential
- Each pixel depends on previously processed pixels
- Cannot be easily parallelized

**Implementation**:
- NumPy arrays for pixel data
- Sequential error diffusion
- Palette color matching

### ASCII & Post-Processing (GPU-Based)

**Why GPU?**
- Each cell/pixel is independent
- Can be parallelized
- Real-time performance

**Implementation**:
- WebGL shaders (GLSL)
- Three.js + postprocessing library
- Procedural character drawing

## API Design

### Processing Endpoint

```python
POST /api/process
{
    "url": "https://example.com",
    "effects": {
        "dithering": {
            "algorithm": "floyd_steinberg",
            "palette": "gameboy",
            "pixelation": 2
        },
        "ascii": {
            "enabled": false,
            "style": "standard",
            "cell_size": 8
        },
        "postprocessing": {
            "bloom": 0.5,
            "scanlines": 0.1,
            "curvature": 0.1,
            "vignette": 0.5
        }
    }
}
```

### Effect Presets

```python
GET /api/effects/presets
# Returns: grainrad, retro, modern, etc.

POST /api/effects/apply?preset=grainrad
```

## Resources

### Articles & Tutorials
- [Efecto: Building Real-Time ASCII and Dithering Effects](https://tympanus.net/codrops/2026/01/04/efecto-building-real-time-ascii-and-dithering-effects-with-webgl-shaders/)
- [The Book of Shaders](https://thebookofshaders.com/)
- [grainrad.com](https://grainrad.com/)

### Papers
- Floyd & Steinberg (1976): "An adaptive algorithm for spatial grey scale"
- Jarvis, Judice & Ninke (1976): "A survey of techniques for the display of continuous tone pictures"
- Donald Knuth (1987): "Digital Halftones by Dot Diffusion"

### Libraries
- [postprocessing](https://github.com/pmndrs/postprocessing) - Three.js post-processing
- React Three Fiber - React + Three.js integration

## Next Steps

1. **Integrate with Proxy** (`website_proxy.py`)
   - Add processing pipeline after fetch
   - Cache processed versions
   - Add effect parameters to API

2. **WebGL Integration**
   - Set up Three.js scene
   - Load shaders
   - Real-time preview

3. **UI Controls**
   - Add effect controls to browser UI
   - Real-time parameter adjustment
   - Preset selection

4. **Performance Optimization**
   - GPU acceleration where possible
   - Efficient caching strategy
   - Lazy loading of effects

## Success Criteria

- [ ] Pre-processing works on images
- [ ] All dithering algorithms implemented
- [ ] ASCII conversion functional
- [ ] Post-processing effects working
- [ ] WebGL shaders rendering correctly
- [ ] Integrated with proxy system
- [ ] Real-time preview available
- [ ] Performance: < 100ms processing time
