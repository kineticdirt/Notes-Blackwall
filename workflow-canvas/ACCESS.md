# How to Access Workflow Canvas

## 🚀 Quick Access

### Frontend (Visual Editor)
**Open in your browser:**
```
file:///Users/abhinav/Desktop/Notes-Blackwall/workflow-canvas/frontend/index.html
```

Or simply navigate to:
```
/Users/abhinav/Desktop/Notes - Blackwall/workflow-canvas/frontend/index.html
```
and open it in your browser.

### API Server (Already Running!)
**API Base URL:**
```
http://localhost:8000
```

**API Documentation (Swagger UI):**
```
http://localhost:8000/docs
```

**Alternative API Docs (ReDoc):**
```
http://localhost:8000/redoc
```

## 📋 Available Endpoints

### Blocks
- `GET http://localhost:8000/api/blocks` - List all blocks
- `GET http://localhost:8000/api/blocks/{block_type}` - Get block info

### Workflows
- `GET http://localhost:8000/api/workflows` - List workflows
- `POST http://localhost:8000/api/workflows` - Create workflow
- `GET http://localhost:8000/api/workflows/{id}` - Get workflow
- `PUT http://localhost:8000/api/workflows/{id}` - Update workflow
- `DELETE http://localhost:8000/api/workflows/{id}` - Delete workflow
- `POST http://localhost:8000/api/workflows/{id}/execute` - Execute workflow
- `GET http://localhost:8000/api/workflows/{id}/stream` - Stream execution

### MCP Tools
- `GET http://localhost:8000/api/mcp/tools` - List MCP tools
- `GET http://localhost:8000/api/mcp/tools/{tool_id}` - Get tool info
- `POST http://localhost:8000/api/mcp/tools/{tool_id}/execute` - Execute tool

### RAG Graph
- `POST http://localhost:8000/api/rag/ingest` - Ingest document
- `GET http://localhost:8000/api/rag/search?query=...` - Search graph
- `GET http://localhost:8000/api/rag/graph/{node_id}` - Get subgraph
- `GET http://localhost:8000/api/rag/graph` - Get full graph

## 🔧 Server Commands

### Start Server (if not running)
```bash
cd "/Users/abhinav/Desktop/Notes - Blackwall/workflow-canvas/backend"
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### Stop Server
```bash
pkill -f "uvicorn api:app"
```

### Check Server Status
```bash
curl http://localhost:8000/
```

## 📱 Quick Test

### Test API
```bash
curl http://localhost:8000/api/blocks
```

### Test MCP Tools
```bash
curl http://localhost:8000/api/mcp/tools
```

### Open Frontend
Just open the `frontend/index.html` file in your browser, or use:
```bash
open "/Users/abhinav/Desktop/Notes - Blackwall/workflow-canvas/frontend/index.html"
```

## 🎯 Recommended Workflow

1. **Open Frontend:**
   - Navigate to `frontend/index.html` in your browser
   - Or use: `open frontend/index.html` in terminal

2. **View API Docs:**
   - Go to `http://localhost:8000/docs` for interactive API documentation

3. **Start Building:**
   - Drag blocks from the palette (Tools, Prompts, Resources, Restrictions)
   - Connect them via ports
   - Save and execute workflows

## ✅ Current Status

- ✅ Server is **RUNNING** on port 8000
- ✅ API is accessible at `http://localhost:8000`
- ✅ Frontend is ready at `frontend/index.html`
- ✅ 24 blocks available across 7 categories

Enjoy building workflows! 🚀
