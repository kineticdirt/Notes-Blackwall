# Workflow Canvas - MCP & RAG Integration Guide

## Overview

The Workflow Canvas now integrates:
- **MCP Tools**: Connect and orchestrate Model Context Protocol tools
- **RAG Graph**: Graph-based storage for Retrieval Augmented Generation
- **BDH (Batch Dynamic Ingestion)**: Dynamic document ingestion into RAG graph
- **Enhanced Node Editor**: Visual block-based workflow editor with connection ports

## MCP Integration

### Available MCP Tools

1. **File Operations**
   - `mcp_file_read`: Read file content
   - `mcp_file_write`: Write file content

2. **Database Operations**
   - `mcp_db_query`: Execute database queries

3. **HTTP Operations**
   - `mcp_http_request`: Make HTTP requests

4. **AI/LLM Operations**
   - `mcp_llm_complete`: Complete text using LLM

### Using MCP Tools in Workflows

1. **Drag MCP Tool block** onto canvas
2. **Configure tool**:
   - Select tool ID from dropdown
   - Set parameters
3. **Connect to other blocks** via ports
4. **Execute workflow** with streaming output

### MCP Tool Chain

Use **MCP Chain** block to execute multiple MCP tools:
- Configure list of tools
- Tools execute sequentially
- Results aggregated in array

## RAG Graph System

### Graph Structure

- **Nodes**: Documents, chunks, entities, relations
- **Edges**: Relationships between nodes
- **Metadata**: Additional information per node

### RAG Blocks

1. **RAG Ingest**
   - Ingests documents into graph
   - Automatically chunks content
   - Creates node relationships
   - Returns node ID

2. **RAG Search**
   - Searches graph by query
   - Returns matching nodes
   - Supports filtering by node type

3. **RAG Subgraph**
   - Gets subgraph from node
   - Configurable depth
   - Returns nodes and edges

### BDH (Batch Dynamic Ingestion)

Documents are automatically:
- **Chunked** into smaller pieces
- **Linked** to parent document
- **Connected** to adjacent chunks
- **Stored** in graph structure

## Enhanced Node Editor

### Features

- **Connection Ports**: Input/output ports on nodes
- **Visual Connections**: Bezier curves between nodes
- **Drag & Drop**: Move nodes around canvas
- **Port Connections**: Click ports to connect nodes
- **Properties Panel**: Edit node properties
- **Keyboard Shortcuts**: Delete key to remove nodes

### Creating Connections

1. **Click output port** (green circle on right)
2. **Drag to input port** (blue circle on left)
3. **Release** to create connection

### Node Types

- **Input Nodes**: Data sources (HTTP, Data Input)
- **Transform Nodes**: Data processing (JSON, Text)
- **Control Nodes**: Flow control (If/Else, Loop)
- **MCP Nodes**: MCP tool execution
- **RAG Nodes**: RAG operations
- **Output Nodes**: Data sinks (HTTP, Console)

## Execution Scheduling

### Execution Modes

1. **Sequential**: Execute blocks one after another
2. **Parallel**: Execute all blocks simultaneously
3. **Staggered**: Execute with delays between blocks
4. **Conditional**: Execute based on conditions

### Staggering Execution

Configure execution mode in workflow:
- Set `execution_mode` in workflow metadata
- Set `stagger_delay` for staggered mode
- Blocks execute with specified timing

## API Endpoints

### MCP Endpoints

- `GET /api/mcp/tools` - List all MCP tools
- `GET /api/mcp/tools/{tool_id}` - Get tool info
- `POST /api/mcp/tools/{tool_id}/execute` - Execute tool

### RAG Endpoints

- `POST /api/rag/ingest` - Ingest document
- `GET /api/rag/search` - Search graph
- `GET /api/rag/graph/{node_id}` - Get subgraph
- `GET /api/rag/graph` - Get full graph

## Example Workflow

### MCP + RAG Workflow

1. **HTTP Request** → Fetch document
2. **RAG Ingest** → Ingest into graph
3. **RAG Search** → Search for related content
4. **MCP LLM** → Generate response using RAG results
5. **HTTP Response** → Return result

### Creating the Workflow

1. Drag blocks onto canvas
2. Connect ports:
   - HTTP Request output → RAG Ingest document input
   - RAG Ingest node_id → RAG Search query
   - RAG Search results → MCP LLM prompt
   - MCP LLM result → HTTP Response data
3. Save workflow
4. Execute with streaming

## Visual Style

The editor matches the image style:
- **Dark theme** with grid background
- **Node-based** visual programming
- **Connection ports** on left/right
- **Color-coded** blocks by category
- **Smooth connections** with bezier curves

## Next Steps

1. **Add more MCP tools** from your MCP servers
2. **Configure RAG graph** for your use case
3. **Create workflows** connecting MCP tools
4. **Use RAG** for context-aware workflows
5. **Schedule execution** with staggering

The system is ready for MCP orchestration and RAG-powered workflows! 🚀
