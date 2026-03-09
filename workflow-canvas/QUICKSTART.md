# Workflow Canvas - Quick Start

## Installation

```bash
cd workflow-canvas
pip install -r requirements.txt
```

## Running

### 1. Start Backend Server

```bash
cd backend
python api.py
```

The API will be available at `http://localhost:8000`

### 2. Open Frontend

Open `frontend/index.html` in a web browser, or serve it:

```bash
cd frontend
python -m http.server 8080
```

Then open `http://localhost:8080`

## Creating a Workflow

1. **Drag blocks** from the palette onto the canvas
2. **Click blocks** to select and edit properties
3. **Connect blocks** by dragging from output to input (coming soon)
4. **Save** your workflow
5. **Execute** to run with streaming output

## Example Workflow

1. Add "HTTP Request" block
2. Add "JSON Transform" block
3. Add "Console Output" block
4. Connect them
5. Execute to see streaming results

## API Endpoints

- `GET /api/blocks` - Get all block types
- `POST /api/workflows` - Create workflow
- `GET /api/workflows/{id}/stream` - Stream workflow execution (SSE)

## Features

- ✅ Visual block editor
- ✅ Drag-and-drop interface
- ✅ HTTP streaming (Server-Sent Events)
- ✅ Real-time execution logs
- ✅ Block properties editor
