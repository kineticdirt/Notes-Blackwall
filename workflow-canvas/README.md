# Workflow Canvas: Visual Block-Based Workflow System

A visual, block-based workflow editor with HTTP streaming capabilities - similar to Node-RED or Scratch, but for general workflows.

## Features

- **Visual Block Editor**: Drag-and-drop blocks on canvas
- **Workflow Execution**: Execute workflows with streaming output
- **HTTP Streaming**: Real-time streaming of workflow execution
- **Block Library**: Pre-built blocks for common operations
- **HTTP Streaming**: Server-Sent Events (SSE) for real-time updates
- **RESTful API**: Backend API for workflow management

## Architecture

```
workflow-canvas/
├── backend/
│   ├── api.py              # FastAPI backend
│   ├── workflow_engine.py # Workflow execution engine
│   ├── blocks.py           # Block definitions
│   └── streaming.py        # HTTP streaming (SSE)
├── frontend/
│   ├── index.html          # Main canvas interface
│   ├── canvas.js           # Canvas rendering and interaction
│   ├── blocks.js           # Block definitions and rendering
│   ├── workflow.js          # Workflow execution
│   └── streaming.js        # HTTP streaming client
└── requirements.txt
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start backend
python backend/api.py

# Open frontend
open frontend/index.html
```

## Block Types

- **Input Blocks**: HTTP Request, File Input, User Input
- **Processing Blocks**: Transform, Filter, Map, Reduce
- **Output Blocks**: HTTP Response, File Output, Console
- **Control Blocks**: If/Else, Loop, Delay, Parallel
- **Data Blocks**: JSON, XML, CSV, Text

## HTTP Streaming

Workflows can stream execution progress via Server-Sent Events (SSE):

```javascript
const eventSource = new EventSource('/api/workflow/123/stream');
eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Block executed:', data.blockId, data.output);
};
```
