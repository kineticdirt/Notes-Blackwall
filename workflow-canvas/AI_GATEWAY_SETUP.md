# AI Gateway Setup Guide

## Overview

The workflow canvas now includes:
1. **N8N Format Support** - Import/export workflows in N8N format
2. **AI Gateway** - AI-powered chat interface using Claude API

## Setup Steps

### 1. Install Dependencies

```bash
cd "/Users/abhinav/Desktop/Notes - Blackwall/workflow-canvas/backend"
pip install httpx anthropic
```

Or update requirements:
```bash
pip install -r ../requirements.txt
```

### 2. Configure AI Gateway

#### Option A: Claude API (Recommended)

Set your Anthropic API key:
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Or create a `.env` file:
```bash
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
```

#### Option B: OpenAI API

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Then update `ai_gateway.py` to use `provider="openai"`

#### Option C: Local/No API (Fallback)

The system will use rule-based processing if no API key is set.

### 3. Restart Server

```bash
cd backend
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

## Features

### N8N Format Support

**Export to N8N:**
```bash
POST /api/workflows/{id}/export/n8n
```

**Import from N8N:**
```bash
POST /api/workflows/import/n8n
Body: { N8N workflow JSON }
```

### AI Gateway

**Chat Endpoint:**
```bash
POST /api/ai/chat
Body: {
  "command": "Add HTTP request node",
  "context": { workflow context }
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

## Usage

### In Chat Interface

1. **Open chat** (bottom right corner)
2. **Type commands** like:
   - "Add HTTP request node"
   - "Clear canvas"
   - "Show all blocks"
   - "Export to N8N"
   - "Import N8N workflow"

### N8N Integration

1. **Export workflow:**
   - Use chat: "Export to N8N"
   - Or API: `POST /api/workflows/{id}/export/n8n`

2. **Import workflow:**
   - Use chat: "Import N8N workflow [paste JSON]"
   - Or API: `POST /api/workflows/import/n8n`

## Testing

### Test AI Gateway

```bash
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"command": "Add HTTP request node", "context": {}}'
```

### Test N8N Export

```bash
# First create a workflow, then:
curl http://localhost:8000/api/workflows/{id}/export/n8n
```

## Troubleshooting

### AI Gateway Not Working

1. Check API key is set: `echo $ANTHROPIC_API_KEY`
2. Check server logs for errors
3. Falls back to rule-based if API unavailable

### N8N Import/Export Issues

1. Check workflow format matches N8N structure
2. Verify node type mappings
3. Check server logs for conversion errors

## Next Steps

1. **Set API key** for full AI functionality
2. **Test chat interface** with natural language
3. **Export workflows** to N8N format
4. **Import existing** N8N workflows

The system is ready! 🚀
