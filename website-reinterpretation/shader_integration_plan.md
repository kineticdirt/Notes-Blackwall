# Shader/Postprocessing Integration Plan

## Overview

Integrate shader effects and postprocessing capabilities into the website proxy system, inspired by:
- **postprocessing** library (pmndrs/postprocessing) - three.js post-processing effects
- **The Book of Shaders** - Fragment shader techniques
- Original grainrad vision - Dithering + ASCII + Shader effects

## Architecture

### Current Flow
```
Request → Cache → Fetch → Cache → Return
```

### Enhanced Flow (with Shaders)
```
Request → Cache (original) → Fetch → Shader Pipeline → Cache (processed) → Return
                              ↓
                    Shader Effects:
                    - Dithering (Floyd-Steinberg)
                    - ASCII conversion
                    - Grain/noise
                    - Scanlines
                    - Color grading
                    - Post-processing
```

## Implementation Strategy

### Phase 1: Research & Design

#### 1.1 Study postprocessing Library
- Review API: EffectComposer, EffectPass, RenderPass
- Understand effect system: BloomEffect, BlurEffect, etc.
- Note performance optimizations (single triangle, effect merging)

#### 1.2 Study Book of Shaders
- Fragment shader basics
- Algorithmic drawing techniques
- Image processing methods
- Noise and patterns

#### 1.3 Design Integration Points
- Where to inject shader processing
- How to cache shader-processed content
- API design for shader parameters

### Phase 2: Core Shader System

#### 2.1 Create Shader Engine
```python
class ShaderEngine:
    """Processes HTML/CSS/images through shader effects."""
    
    def __init__(self):
        self.effects = {}
        self.composer = None
    
    def apply_effect(self, content, effect_type, params):
        """Apply shader effect to content."""
        pass
    
    def apply_pipeline(self, content, effects):
        """Apply multiple effects in sequence."""
        pass
```

#### 2.2 Implement Core Effects
- **Dithering**: Floyd-Steinberg dithering
- **ASCII**: Convert images/text to ASCII art
- **Grain**: Add film grain effect
- **Scanlines**: CRT-style scanlines
- **Color Grading**: Adjust colors, contrast, saturation

#### 2.3 Integration with Proxy
- Add shader processing step after fetch
- Cache both original and processed versions
- Add effect parameters to API

### Phase 3: WebGL Client-Side

#### 3.1 Client Shader System
- Use WebGL for real-time effects
- Load shader code from server
- Apply effects in browser

#### 3.2 UI Controls
- Add shader effect controls to browser UI
- Real-time preview
- Preset effects (grainrad-style)

### Phase 4: Advanced Features

#### 4.1 Custom Shaders
- Allow users to upload custom shader code
- Validate and compile shaders
- Cache compiled shaders

#### 4.2 Effect Presets
- Grainrad preset (dithering + ASCII + grain)
- Retro preset (scanlines + color grading)
- Modern preset (bloom + blur)

## Technical Details

### Shader Processing Options

#### Option A: Server-Side (Python)
- Use PIL/Pillow for image processing
- Use numpy for dithering algorithms
- Pros: Works for all clients
- Cons: CPU-intensive, slower

#### Option B: Client-Side (WebGL)
- Use WebGL shaders in browser
- Load shader code via API
- Pros: Real-time, GPU-accelerated
- Cons: Requires JavaScript, browser support

#### Option C: Hybrid
- Server: Pre-process common effects, cache
- Client: Real-time effects when available
- Fallback: Serve pre-processed versions
- **Recommended approach**

### Effect Pipeline

```python
class EffectPipeline:
    """Manages shader effect pipeline."""
    
    def __init__(self):
        self.effects = []
    
    def add_effect(self, effect_type, params):
        """Add effect to pipeline."""
        self.effects.append({
            'type': effect_type,
            'params': params
        })
    
    def process(self, content):
        """Process content through pipeline."""
        result = content
        for effect in self.effects:
            result = self.apply_effect(result, effect)
        return result
```

### Cache Strategy

- **Original Content**: Cache fetched HTML/CSS/images
- **Processed Content**: Cache shader-processed versions
- **Cache Keys**: Include effect parameters in key
- **TTL**: Shorter TTL for processed content (1 day vs 7 days)

### API Design

```python
# Request with shader effects
GET /proxy/{url}?effects=dither,ascii,grain&intensity=0.5

# Shader effect API
GET /api/shader/effects  # List available effects
POST /api/shader/process  # Process content with effects
GET /api/shader/presets   # List effect presets
```

## Resources

### Libraries
- **postprocessing**: https://github.com/pmndrs/postprocessing
  - three.js post-processing library
  - EffectComposer, EffectPass system
  - Performance optimized
  
- **The Book of Shaders**: https://thebookofshaders.com/
  - Fragment shader guide
  - Examples and techniques
  - GLSL code samples

### Existing Code
- `grainrad-poc/`: Original grainrad demo
- `website-reinterpretation/`: Component transformation system
- `blackwall/worktrees/mcp_integration/`: MCP UI integration

## Next Steps

1. **Research** (This Week)
   - Study postprocessing library
   - Review Book of Shaders examples
   - Design shader pipeline architecture

2. **Prototype** (Next Week)
   - Create basic shader engine
   - Implement dithering effect
   - Test with sample websites

3. **Integration** (Following Week)
   - Integrate with proxy
   - Add UI controls
   - Performance optimization

## Success Criteria

- [ ] Shader effects work on cached content
- [ ] Real-time preview in browser UI
- [ ] Effect presets (grainrad-style)
- [ ] Performance: < 100ms processing time
- [ ] Cache hit rate maintained > 80%
