# AI Gateway & N8N Integration Setup

## ✅ What's Been Added

1. **N8N Format Support** - Import/export workflows in N8N format
2. **AI Gateway** - AI-powered chat using Claude API
3. **Enhanced Chat Interface** - Now uses AI for natural language commands

## 🚀 Quick Setup

### Step 1: Install Dependencies

```bash
cd "/Users/abhinav/Desktop/Cequence BlackWall/workflow-canvas/backend"
pip install httpx anthropic
```

Or update all:
```bash
pip install -r ../requirements.txt
```

### Step 2: Set Up AI Gateway

#### Option A: Claude API (Recommended)

Get your API key from: https://console.anthropic.com/

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Or create `.env` file:
```bash
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
```

#### Option B: Use Without API (Fallback)

The system will use rule-based processing if no API key is set. Still works, just less intelligent.

### Step 3: Restart Server

```bash
cd backend
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

## 📋 New API Endpoints

### N8N Format

**Export to N8N:**
```bash
POST /api/workflows/{workflow_id}/export/n8n
```

**Import from N8N:**
```bash
POST /api/workflows/import/n8n
Body: { N8N workflow JSON }
```

### AI Gateway

**Chat Command:**
```bash
POST /api/ai/chat
Body: {
  "command": "Add HTTP request node",
  "context": { "nodes": [...], "connections": [...] }
}
```

**Get History:**
```bash
GET /api/ai/history
```

**Clear History:**
```bash
POST /api/ai/clear
```

## 💬 Using the Chat Interface

### Natural Language Commands

The chat now uses AI to understand commands:

- **"Add HTTP request node"** → Adds node to canvas
- **"Add MCP tool node"** → Adds MCP tool block
- **"Clear the canvas"** → Removes all nodes
- **"Show me all blocks"** → Lists current blocks
- **"Export to N8N"** → Exports workflow in N8N format
- **"Save workflow"** → Saves current workflow
- **"Execute workflow"** → Runs the workflow

### How It Works

1. **Type command** in chat (bottom right)
2. **AI processes** command through gateway
3. **Action executed** automatically
4. **Response shown** in chat

## 🔄 N8N Integration

### Export Workflow

**Via Chat:**
```
"Export to N8N"
```

**Via API:**
```bash
curl -X POST http://localhost:8000/api/workflows/{id}/export/n8n
```

**Result:** Downloads N8N-compatible JSON file

### Import Workflow

**Via API:**
```bash
curl -X POST http://localhost:8000/api/workflows/import/n8n \
  -H "Content-Type: application/json" \
  -d @n8n_workflow.json
```

**Result:** Creates new workflow from N8N format

## 🎯 Workflow

### Best Approach

1. **Set API Key** (for full AI functionality)
   ```bash
   export ANTHROPIC_API_KEY="your-key"
   ```

2. **Start Server**
   ```bash
   cd backend
   uvicorn api:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Open Frontend**
   ```bash
   open frontend/index.html
   ```

4. **Use Chat** (bottom right)
   - Type natural language commands
   - AI processes and executes
   - See results in chat

5. **Export/Import N8N**
   - Build workflow in canvas
   - Export to N8N format
   - Import N8N workflows

## 🔧 Configuration

### AI Gateway Settings

Edit `backend/ai_gateway.py`:

```python
ai_gateway = AIGateway(
    provider="anthropic",  # or "openai", "local"
    api_key=os.getenv("ANTHROPIC_API_KEY")
)
```

### N8N Node Mappings

Edit `backend/n8n_converter.py` to customize block type mappings.

## 📊 Testing

### Test AI Gateway

```bash
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"command": "Add HTTP request node", "context": {}}'
```

### Test N8N Export

1. Create a workflow in the canvas
2. Save it
3. Use chat: "Export to N8N"
4. Check downloaded JSON file

### Test N8N Import

```bash
curl -X POST http://localhost:8000/api/workflows/import/n8n \
  -H "Content-Type: application/json" \
  -d @test_n8n_workflow.json
```

## 🎨 Features

### AI-Powered Chat
- ✅ Natural language understanding
- ✅ Context-aware responses
- ✅ Automatic action execution
- ✅ Conversation history

### N8N Compatibility
- ✅ Export workflows to N8N format
- ✅ Import N8N workflows
- ✅ Node type mapping
- ✅ Connection preservation

## 🚨 Troubleshooting

### AI Gateway Not Working

1. **Check API key:**
   ```bash
   echo $ANTHROPIC_API_KEY
   ```

2. **Check server logs** for errors

3. **Falls back** to rule-based if API unavailable

### N8N Import/Export Issues

1. **Check workflow format** matches N8N structure
2. **Verify node mappings** in converter
3. **Check server logs** for conversion errors

## ✨ Next Steps

1. **Set your API key** for full AI functionality
2. **Test chat interface** with natural language
3. **Export workflows** to N8N format
4. **Import existing** N8N workflows
5. **Build complex workflows** using AI assistance

Everything is ready! The AI gateway and N8N support are integrated! 🚀
