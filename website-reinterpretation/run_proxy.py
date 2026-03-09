#!/usr/bin/env python3
"""
Run Website Reinterpretation Proxy Server
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from website_proxy import create_proxy_app
from fastapi.responses import HTMLResponse

# Create app with browser support and aggressive caching
use_browser = os.getenv("USE_BROWSER", "true").lower() == "true"
cache_ttl = int(os.getenv("CACHE_TTL", str(86400 * 7)))  # 7 days default
cache_dir = os.getenv("CACHE_DIR", None)
enable_effects = os.getenv("ENABLE_EFFECTS", "false").lower() == "true"
effect_preset = os.getenv("EFFECT_PRESET", "grainrad")

if cache_dir:
    from pathlib import Path
    cache_dir = Path(cache_dir)

app = create_proxy_app(use_browser=use_browser, cache_ttl=cache_ttl, cache_dir=cache_dir,
                      enable_effects=enable_effects, effect_preset=effect_preset)

# Serve HTML POC at root
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve HTML POC."""
    # Try visual test first if effects enabled
    if enable_effects:
        visual_test = Path(__file__).parent / "visual_test.html"
        if visual_test.exists():
            return visual_test.read_text()
    
    html_path = Path(__file__).parent / "website-poc.html"
    if html_path.exists():
        return html_path.read_text()
    return "<h1>Website Reinterpretation Proxy</h1><p>HTML file not found</p>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
