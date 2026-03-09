"""
FastAPI backend for Workflow Canvas.
Provides REST API and HTTP streaming for workflow execution.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import json
import asyncio
from datetime import datetime
import uuid

from workflow_engine import WorkflowEngine
from blocks import BlockRegistry
from streaming import StreamManager
from mcp_integration import MCPToolRegistry, MCPExecutor
from rag_graph import RAGGraph
from n8n_converter import N8NConverter
from ai_gateway import AIGateway

app = FastAPI(title="Workflow Canvas API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
workflow_engine = WorkflowEngine()
block_registry = BlockRegistry()
stream_manager = StreamManager()
mcp_registry = MCPToolRegistry()
mcp_executor = MCPExecutor()
rag_graph = RAGGraph()
n8n_converter = N8NConverter()
ai_gateway = AIGateway(provider="anthropic")


# Pydantic models
class Block(BaseModel):
    id: str
    type: str
    position: Dict[str, float]  # x, y
    data: Dict[str, Any]
    connections: List[Dict[str, str]]  # [{from: "block1", to: "block2"}]


class Workflow(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    blocks: List[Block]
    created_at: Optional[str] = None


class WorkflowExecution(BaseModel):
    workflow_id: str
    input_data: Optional[Dict[str, Any]] = None


# In-memory storage (replace with database in production)
workflows_db: Dict[str, Workflow] = {}


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": "Workflow Canvas API",
        "version": "1.0.0",
        "endpoints": {
            "workflows": "/api/workflows",
            "blocks": "/api/blocks",
            "streaming": "/api/workflows/{id}/stream"
        }
    }


@app.get("/api/blocks")
async def get_blocks():
    """Get all available block types."""
    return {
        "blocks": block_registry.get_all_blocks(),
        "categories": block_registry.get_categories()
    }


@app.get("/api/blocks/{block_type}")
async def get_block_info(block_type: str):
    """Get information about a specific block type."""
    block_info = block_registry.get_block_info(block_type)
    if not block_info:
        raise HTTPException(status_code=404, detail="Block type not found")
    return block_info


@app.post("/api/workflows")
async def create_workflow(workflow: Workflow):
    """Create a new workflow."""
    if not workflow.id:
        workflow.id = str(uuid.uuid4())
    
    workflow.created_at = datetime.now().isoformat()
    workflows_db[workflow.id] = workflow
    
    return {
        "id": workflow.id,
        "message": "Workflow created",
        "workflow": workflow.dict()
    }


@app.get("/api/workflows")
async def list_workflows():
    """List all workflows."""
    return {
        "workflows": [
            {
                "id": wf.id,
                "name": wf.name,
                "description": wf.description,
                "created_at": wf.created_at,
                "block_count": len(wf.blocks)
            }
            for wf in workflows_db.values()
        ]
    }


@app.get("/api/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get a specific workflow."""
    if workflow_id not in workflows_db:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return workflows_db[workflow_id].dict()


@app.put("/api/workflows/{workflow_id}")
async def update_workflow(workflow_id: str, workflow: Workflow):
    """Update a workflow."""
    if workflow_id not in workflows_db:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow.id = workflow_id
    workflows_db[workflow_id] = workflow
    
    return {
        "id": workflow_id,
        "message": "Workflow updated",
        "workflow": workflow.dict()
    }


@app.delete("/api/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """Delete a workflow."""
    if workflow_id not in workflows_db:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    del workflows_db[workflow_id]
    return {"message": "Workflow deleted", "id": workflow_id}


@app.post("/api/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, execution: WorkflowExecution):
    """Execute a workflow synchronously."""
    if workflow_id not in workflows_db:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow = workflows_db[workflow_id]
    
    try:
        result = await workflow_engine.execute_workflow(
            workflow,
            input_data=execution.input_data
        )
        return {
            "success": True,
            "result": result,
            "workflow_id": workflow_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workflows/{workflow_id}/stream")
async def stream_workflow(workflow_id: str, input_data: Optional[str] = None):
    """Execute a workflow with HTTP streaming (Server-Sent Events)."""
    if workflow_id not in workflows_db:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow = workflows_db[workflow_id]
    
    # Parse input data if provided
    parsed_input = None
    if input_data:
        try:
            parsed_input = json.loads(input_data)
        except:
            parsed_input = {"raw": input_data}
    
    # Create stream
    stream_id = stream_manager.create_stream(workflow_id)
    
    async def generate_stream():
        """Generate Server-Sent Events stream."""
        try:
            # Send initial event
            yield f"data: {json.dumps({'type': 'start', 'workflow_id': workflow_id, 'stream_id': stream_id})}\n\n"
            
            # Execute workflow with streaming
            async for event in workflow_engine.execute_workflow_stream(
                workflow,
                input_data=parsed_input,
                stream_id=stream_id
            ):
                yield f"data: {json.dumps(event)}\n\n"
            
            # Send completion event
            yield f"data: {json.dumps({'type': 'complete', 'workflow_id': workflow_id})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        finally:
            stream_manager.close_stream(stream_id)
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/api/streams/{stream_id}")
async def get_stream_status(stream_id: str):
    """Get status of a stream."""
    status = stream_manager.get_stream_status(stream_id)
    if not status:
        raise HTTPException(status_code=404, detail="Stream not found")
    return status


# MCP endpoints
@app.get("/api/mcp/tools")
async def list_mcp_tools():
    """List all available MCP tools."""
    return {
        "tools": mcp_registry.list_tools(),
        "servers": list(set(tool.server for tool in mcp_registry.tools.values() if tool.server))
    }


@app.get("/api/mcp/tools/{tool_id}")
async def get_mcp_tool(tool_id: str):
    """Get information about a specific MCP tool."""
    tool = mcp_registry.get_tool(tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool.to_dict()


@app.post("/api/mcp/tools/{tool_id}/execute")
async def execute_mcp_tool(tool_id: str, parameters: Dict[str, Any]):
    """Execute an MCP tool."""
    try:
        result = await mcp_executor.execute_tool(tool_id, parameters)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# RAG Graph endpoints
@app.post("/api/rag/ingest")
async def ingest_document(document: Dict[str, Any]):
    """Ingest a document into the RAG graph."""
    document_id = document.get("id") or str(uuid.uuid4())
    content = document.get("content", "")
    metadata = document.get("metadata", {})
    
    node_id = rag_graph.ingest_document(document_id, content, metadata)
    
    return {
        "success": True,
        "node_id": node_id,
        "document_id": document_id
    }


@app.get("/api/rag/search")
async def search_rag(query: str, node_type: Optional[str] = None, limit: int = 10):
    """Search the RAG graph."""
    results = rag_graph.search_nodes(query, node_type, limit)
    
    return {
        "query": query,
        "results": [node.to_dict() for node in results],
        "count": len(results)
    }


@app.get("/api/rag/graph/{node_id}")
async def get_subgraph(node_id: str, depth: int = 2):
    """Get subgraph from a node."""
    subgraph = rag_graph.get_subgraph(node_id, depth)
    return subgraph


@app.get("/api/rag/graph")
async def get_full_graph():
    """Get the entire RAG graph."""
    return rag_graph.to_dict()


# N8N Format Endpoints
@app.post("/api/workflows/{workflow_id}/export/n8n")
async def export_to_n8n(workflow_id: str):
    """Export workflow to N8N format."""
    if workflow_id not in workflows_db:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow = workflows_db[workflow_id]
    workflow_dict = workflow.dict()
    
    # Convert connections format
    connections = []
    for block in workflow.blocks:
        for conn in block.connections:
            connections.append({
                "from": conn.get("from", block.id),
                "to": conn.get("to"),
                "fromPort": conn.get("fromPort", "output_0"),
                "toPort": conn.get("toPort", "input_0")
            })
    
    workflow_dict["connections"] = connections
    n8n_workflow = n8n_converter.to_n8n(workflow_dict)
    return n8n_workflow


@app.post("/api/workflows/import/n8n")
async def import_from_n8n(n8n_workflow: Dict[str, Any]):
    """Import workflow from N8N format."""
    workflow_data = n8n_converter.from_n8n(n8n_workflow)
    
    # Convert to Workflow model
    workflow = Workflow(
        id=str(uuid.uuid4()),
        name=workflow_data.get("name", "Imported Workflow"),
        description=workflow_data.get("description", "Imported from N8N"),
        blocks=workflow_data.get("blocks", []),
        created_at=datetime.now().isoformat()
    )
    
    # Store workflow
    workflows_db[workflow.id] = workflow
    
    return {
        "id": workflow.id,
        "name": workflow.name,
        "status": "imported",
        "block_count": len(workflow.blocks)
    }


# AI Gateway Endpoints
@app.post("/api/ai/chat")
async def ai_chat(request: Dict[str, Any]):
    """Process chat command through AI gateway."""
    command = request.get("command", "")
    context = request.get("context", {})
    
    response = await ai_gateway.process_command(command, context)
    return response


@app.get("/api/ai/history")
async def get_ai_history():
    """Get AI conversation history."""
    return {
        "history": ai_gateway.conversation_history,
        "count": len(ai_gateway.conversation_history)
    }


@app.post("/api/ai/clear")
async def clear_ai_history():
    """Clear AI conversation history."""
    ai_gateway.conversation_history = []
    return {"status": "cleared"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
