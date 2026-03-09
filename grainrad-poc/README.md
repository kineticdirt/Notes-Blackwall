# Grainrad Theme System - Proof of Concept

Complete proof of concept demonstrating grainrad-inspired theme system with AI agent, MCP server, and MCP UI integration.

## Components

### 1. MCP Server (`grainrad_mcp_server.py`)
- Exposes 5 tools: `apply_dithering`, `convert_to_ascii`, `apply_shader_effects`, `remove_ads`, `transform_content`
- Exposes 2 resources: `grainrad://theme/config`, `grainrad://stats`
- Processes images directly (no AI needed)
- Maintains state and statistics

### 2. AI Agent (`grainrad_ai_agent.py`)
- Uses Claude Vision API (primary) or Gemini (fallback)
- **Only used for final quality check** (not for processing)
- Verifies transformed content before serving
- Fails open (doesn't block if unavailable)

### 3. MCP UI Integration (`grainrad_mcp_ui.py`)
- Registers transformed content as MCP UI resources
- Formats content as markdown
- Resource URIs: `mcp-ui://grainrad/{type}/{id}`

### 4. HTML POC (`grainrad-poc.html`)
- Visual demonstration page
- Image upload and transformation
- Real-time display of results
- AI verification status

## Quick Start

### 1. Install Dependencies

```bash
cd grainrad-poc
pip install -r requirements.txt
```

### 2. Set API Key (Optional)

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### 3. Start Server

```bash
python3 grainrad-poc-server.py
```

Server runs on `http://localhost:8000`

### 4. Open in Browser

Open `http://localhost:8000` in your browser.

### 5. Test Components

```bash
python3 test_poc.py
```

## Usage

1. **Upload Image**: Click "Choose File" and select an image
2. **Select Effects**: Toggle dithering, ASCII, shaders
3. **Transform**: Click "Transform" button
4. **View Results**: See transformed content in right panel
5. **AI Verification**: Check verification status (if API key set)

## API Endpoints

- `GET /` - HTML POC page
- `POST /api/transform` - Transform uploaded image
- `GET /api/resource/{content_id}` - Get transformed resource
- `GET /api/resources` - List all resources
- `GET /api/stats` - Get processing statistics

## Architecture

- **Multi-path processing**: Components can interact independently
- **Component independence**: Each component operates standalone
- **Optional AI**: AI agent only for final verification
- **MCP Protocol**: Tools and resources exposed via MCP
- **MCP UI**: Transformed content accessible as resources

## Status

✅ MCP Server: Working (5 tools, 2 resources)
✅ AI Agent: Working (Claude Vision ready)
✅ MCP UI: Working (resource registration)
✅ HTML POC: Working (visual demonstration)
✅ Server: Running on port 8000

## Files

- `grainrad_mcp_server.py` - MCP server
- `grainrad_ai_agent.py` - AI agent
- `grainrad_mcp_ui.py` - MCP UI integration
- `grainrad-poc.html` - HTML proof of concept
- `grainrad-poc-server.py` - HTTP server
- `test_poc.py` - Component tests

## Next Steps

1. Test with real images
2. Verify AI quality checks work
3. Test MCP UI resource access
4. Enhance HTML POC with more features
