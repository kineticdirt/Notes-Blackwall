# Quick Start - Node-Based Workflow Canvas

## 🚀 Access the Canvas

### Option 1: Direct File Access
```bash
cd "/Users/abhinav/Desktop/Cequence BlackWall/workflow-canvas"
open frontend/index.html
```

### Option 2: Browser URL
```
file:///Users/abhinav/Desktop/Cequence%20BlackWall/workflow-canvas/frontend/index.html
```

## ✅ Prerequisites

Make sure the API server is running:
```bash
cd backend
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

Server should be accessible at: `http://localhost:8000`

## 🎨 Using the Canvas

### 1. **Drag Blocks**
- Blocks are organized by category in the left palette:
  - 🔧 **Tools** - MCP tools, HTTP requests
  - 💬 **Prompts** - LLM prompts and templates
  - 📦 **Resources** - Data sources, RAG operations
  - 🔄 **Transform** - Data transformations
  - 🔀 **Control** - Flow control (if/else, loops)
  - 🚫 **Restrictions** - Access control, rate limiting
  - 📤 **Output** - Output destinations

### 2. **Connect Nodes**
- **Click** on an output port (green circle on right)
- **Drag** to an input port (blue circle on left)
- **Release** to create connection

### 3. **Edit Nodes**
- **Click** a node to select it
- Edit properties in the right panel
- **Delete** key to remove selected node

### 4. **Navigate Canvas**
- **Drag** nodes to move them
- **Scroll** to zoom in/out
- **Click** empty space to deselect

### 5. **Save & Execute**
- Click **Save** to save workflow
- Click **Execute** to run workflow
- View execution log in bottom panel

## 🎯 Example Workflow

1. Drag **HTTP Request** (Tools) → fetches data
2. Drag **RAG Ingest** (Resources) → stores in graph
3. Drag **RAG Search** (Resources) → searches graph
4. Drag **LLM Prompt** (Prompts) → generates response
5. Connect them: HTTP → RAG Ingest → RAG Search → LLM Prompt
6. Click **Execute** to run!

## 🔧 Features

- ✅ **24 blocks** across 7 categories
- ✅ **Visual node editor** with ports
- ✅ **Drag & drop** interface
- ✅ **Connection system** with bezier curves
- ✅ **Properties panel** for configuration
- ✅ **Grid background** for alignment
- ✅ **Zoom & pan** support
- ✅ **Real-time execution** with streaming

## 📝 Tips

- **Port Colors**: Blue = Input, Green = Output
- **Selected Node**: Blue border indicates selection
- **Connections**: Curved lines show data flow
- **Grid**: Helps align nodes
- **Keyboard**: Delete/Backspace removes selected node

Enjoy building workflows! 🚀
