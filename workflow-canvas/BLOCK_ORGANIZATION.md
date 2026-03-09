# Block Organization - Tools, Prompts, Resources

## Overview

Blocks are now organized into three main categories plus supporting categories:

1. **Tools** 🔧 - MCP tools and utilities
2. **Prompts** 💬 - LLM prompts and templates  
3. **Resources** 📦 - Data sources and RAG

Plus:
4. **Transform** 🔄 - Data transformation
5. **Control** 🔀 - Flow control
6. **Output** 📤 - Output destinations

## Category Breakdown

### 🔧 Tools
MCP tools and utility blocks for executing operations:

- **MCP Tool** - Execute an MCP tool
- **MCP Chain** - Chain multiple MCP tools
- **HTTP Request** - Make HTTP requests
- **HTTP Response** - Send HTTP responses

### 💬 Prompts
LLM and prompt-related blocks:

- **LLM Prompt** - Send prompt to LLM
- **Prompt Template** - Template prompt with variables
- **Prompt Chain** - Chain multiple prompts

### 📦 Resources
Data sources, RAG, and resource blocks:

- **Data Resource** - Input data value
- **RAG Ingest** - Ingest document into RAG graph
- **RAG Search** - Search RAG graph
- **RAG Subgraph** - Get subgraph from node
- **File Resource** - Read/write file resource
- **Database Resource** - Query database resource

### 🔄 Transform
Data transformation blocks:

- **JSON Transform** - Transform JSON data
- **Text Transform** - Transform text data

### 🔀 Control
Flow control blocks:

- **If/Else** - Conditional logic
- **Loop** - Loop through items

### 📤 Output
Output destination blocks:

- **Console Output** - Output to console

## Usage Patterns

### Tool → Resource → Prompt Workflow

1. **Tool**: HTTP Request fetches data
2. **Resource**: RAG Ingest stores data
3. **Resource**: RAG Search finds context
4. **Prompt**: LLM Prompt generates response
5. **Tool**: HTTP Response returns result

### Resource → Prompt Chain

1. **Resource**: File Resource reads template
2. **Prompt**: Prompt Template fills variables
3. **Prompt**: LLM Prompt generates content
4. **Prompt**: Prompt Chain processes multiple prompts

### MCP Tool Orchestration

1. **Tool**: MCP Tool executes file read
2. **Tool**: MCP Chain processes multiple tools
3. **Resource**: RAG Ingest stores results
4. **Tool**: HTTP Response returns data

## Frontend Display

The frontend now displays blocks organized by category with:
- Category icons and names
- Category descriptions
- Grouped block lists
- Empty category messages

## API Response

The `/api/blocks` endpoint returns blocks organized by category:

```json
{
  "blocks": [...],
  "categories": ["tools", "prompts", "resources", "transform", "control", "output"]
}
```

Blocks are automatically grouped and displayed in the correct category in the UI.
