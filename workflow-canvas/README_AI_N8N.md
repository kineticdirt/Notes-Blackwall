# Workflow Canvas - AI Gateway & N8N Integration

## 🎯 Overview

Your workflow canvas now supports:
- **N8N Format** - Import/export workflows compatible with N8N
- **AI Gateway** - Claude API integration for intelligent chat
- **Natural Language** - Chat interface understands commands

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install httpx anthropic
```

### 2. Set API Key (Optional but Recommended)
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### 3. Access the Canvas
```bash
open frontend/index.html
```

### 4. Use Chat Interface
- Bottom right corner
- Type commands like "Add HTTP request node"
- AI processes and executes automatically

## 📋 Commands

### Chat Commands
- "Add [block type] node"
- "Clear canvas"
- "Show blocks"
- "Save workflow"
- "Execute workflow"
- "Export to N8N"
- "Help"

### N8N Operations
- Export: Chat command or API endpoint
- Import: API endpoint with N8N JSON

## 🔗 API Endpoints

- `POST /api/ai/chat` - AI chat command
- `POST /api/workflows/{id}/export/n8n` - Export to N8N
- `POST /api/workflows/import/n8n` - Import from N8N

## ✨ Features

✅ AI-powered natural language processing
✅ N8N format compatibility
✅ Automatic workflow actions
✅ Chat interface with history
✅ Export/import workflows

Ready to use! 🚀
