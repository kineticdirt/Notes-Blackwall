#!/usr/bin/env python3
"""
Grainrad POC Server: HTTP server for HTML proof of concept.
"""

import os
import json
import base64
from pathlib import Path
from typing import Dict, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from grainrad_mcp_server import create_grainrad_server
from grainrad_ai_agent import create_ai_agent
from grainrad_mcp_ui import create_mcp_ui

# Initialize components
mcp_server = create_grainrad_server()
ai_agent = create_ai_agent(
    anthropic_key=os.getenv("ANTHROPIC_API_KEY")
)
mcp_ui = create_mcp_ui()

app = FastAPI(title="Grainrad Theme POC")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve HTML POC."""
    html_path = Path(__file__).parent / "grainrad-poc.html"
    if html_path.exists():
        return html_path.read_text()
    return "<h1>Grainrad POC Server</h1><p>HTML file not found</p>"


@app.post("/api/transform")
async def transform_image(
    file: UploadFile = File(...),
    apply_dithering: bool = True,
    apply_ascii: bool = True,
    apply_shaders: bool = True
):
    """Transform uploaded image."""
    try:
        # Read image
        image_bytes = await file.read()
        image_b64 = base64.b64encode(image_bytes).decode()
        
        # Transform via MCP server
        result = await mcp_server._transform_content_handler(
            image_data=image_b64,
            apply_dithering=apply_dithering,
            apply_ascii=apply_ascii,
            apply_shaders=apply_shaders
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        content_id = result["content_id"]
        transformed_data = mcp_server.processed_content[content_id]
        
        # AI verification (optional, at the end)
        verification = await ai_agent.verify_quality(image_bytes, transformed_data)
        transformed_data["ai_verification"] = verification
        
        # Register as MCP UI resource
        resource_uri = mcp_ui.register_transformed_content(content_id, transformed_data)
        
        return {
            "success": True,
            "content_id": content_id,
            "resource_uri": resource_uri,
            "results": result["results"],
            "verification": verification
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/resource/{content_id}")
async def get_resource(content_id: str):
    """Get transformed content resource."""
    resource = mcp_ui.get_resource(content_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


@app.get("/api/resources")
async def list_resources():
    """List all resources."""
    return {"resources": mcp_ui.list_resources()}


@app.get("/api/stats")
async def get_stats():
    """Get processing statistics."""
    return mcp_server.stats


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
