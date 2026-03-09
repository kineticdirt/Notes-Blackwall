# MCP Gateway Architecture: UI Integration

## Overview

The MCP Gateway provides a unified entry point for accessing MCP UI components, Toolbox queries, and Worktree capabilities through the MCP protocol.

## Architecture Diagram

```
                    ┌─────────────────────┐
                    │   MCP Client        │
                    │  (Claude, etc.)     │
                    └──────────┬──────────┘
                                │
                                │ MCP Protocol
                                │ (JSON-RPC)
                                ▼
                    ┌─────────────────────┐
                    │   MCP GATEWAY        │
                    │  (Unified Entry)     │
                    │                      │
                    │  - Request Routing   │
                    │  - Resource Access   │
                    │  - Status Monitor    │
                    └──────────┬──────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
        ┌───────────┐   ┌───────────┐   ┌───────────┐
        │  MCP UI   │   │ Toolbox   │   │ Worktrees │
        │           │   │           │   │           │
        │ Resources │   │ Queries   │   │ Agents    │
        └───────────┘   └───────────┘   └───────────┘
                │               │               │
                ▼               ▼               ▼
        mcp-ui://main    get_kanban_cards  create_worktree
        mcp-ui://kanban  discover_findings assign_task
```

## Request Flow

### 1. Client Request

```
Client → Gateway: {
    "request_type": "ui",
    "target": "main",
    "parameters": {}
}
```

### 2. Gateway Routing

```
Gateway analyzes request:
- Type: "ui" → Route to MCP UI Integration
- Target: "main" → Get component "main"
```

### 3. Component Retrieval

```
MCP UI Integration:
- Loads component from .mcp-ui/main.md
- Converts to MCP resource format
- Returns resource data
```

### 4. Response

```
Gateway → Client: {
    "success": true,
    "data": {
        "uri": "mcp-ui://main",
        "name": "Main Dashboard",
        "content": "# Main Dashboard\n\n..."
    }
}
```

## Resource URIs

### UI Resources

- `mcp-ui://main` - Main dashboard
- `mcp-ui://kanban/board` - Kanban board panel
- `mcp-ui://tree` - Complete UI tree

### Toolbox Resources

- `toolbox://toolset/kanban_toolset` - Kanban toolset
- `toolbox://toolset/worktree_toolset` - Worktree toolset

### Worktree Resources

- `worktree://{worktree_id}` - Worktree state
- `worktree://{worktree_id}/tasks` - Worktree tasks

## Request Types

### 1. UI Resource Request

```python
GatewayRequest(
    request_type="ui",
    target="main",  # Component ID
    parameters={}
)
```

**Handler**: MCP UI Integration
**Returns**: UI component as MCP resource

### 2. MCP URI Request

```python
GatewayRequest(
    request_type="resource",
    target="mcp-ui://kanban/board",  # Full MCP URI
    parameters={}
)
```

**Handler**: MCP UI Integration (parses URI)
**Returns**: Resource data

### 3. Tool Execution

```python
GatewayRequest(
    request_type="tool",
    target="get_kanban_cards",
    parameters={"status": "in_progress"}
)
```

**Handler**: Toolbox Integration
**Returns**: Tool execution results

### 4. Natural Language Query

```python
GatewayRequest(
    request_type="query",
    target="Show me Kanban cards in progress",
    parameters={}
)
```

**Handler**: Intelligent routing based on query
**Returns**: Processed results

## Gateway Capabilities

### ✅ Request Routing
- Routes requests to appropriate component
- Handles different request types
- Error handling and reporting

### ✅ Resource Discovery
- Lists all available resources
- UI components discoverable
- Toolbox toolsets discoverable
- Worktree resources discoverable

### ✅ Status Monitoring
- Tracks request/response history
- Component health monitoring
- Resource availability tracking

### ✅ Unified Interface
- Single entry point for all capabilities
- Consistent request/response format
- Easy to extend with new components

## Integration Points

### MCP UI Integration

```python
# UI components as MCP resources
ui_resource = gateway.integrated_system.get_ui_resource("main")
# Returns: MCP resource with markdown content
```

### Toolbox Integration

```python
# Database queries via Toolbox
result = gateway.integrated_system.query_database(
    "get_kanban_cards",
    status="in_progress"
)
```

### Worktree Integration

```python
# Worktree operations
worktree = gateway.integrated_system.worktree_system.worktree_manager.create_worktree(
    name="Team"
)
```

## Example: Complete Workflow

```python
from blackwall.worktrees.mcp_integration.mcp_gateway import create_mcp_gateway, GatewayRequest

# 1. Create gateway
gateway = create_mcp_gateway()

# 2. Discover resources
resources = gateway.list_available_resources()
# Returns: UI components, Toolbox toolsets, etc.

# 3. Get UI component
ui_request = GatewayRequest(
    request_type="ui",
    target="main"
)
ui_response = gateway.handle_request(ui_request)
# Returns: UI component as MCP resource

# 4. Query database
query_request = GatewayRequest(
    request_type="tool",
    target="get_kanban_cards",
    parameters={"status": "in_progress"}
)
query_response = gateway.handle_request(query_request)
# Returns: Query results

# 5. Get status
status = gateway.get_gateway_status()
# Returns: Complete system status
```

## Benefits

### ✅ Standard Protocol
- Uses MCP protocol standards
- Compatible with MCP clients
- Resource URIs follow MCP conventions

### ✅ Unified Access
- Single gateway for all capabilities
- Consistent interface
- Easy to extend

### ✅ Resource Discovery
- Automatic resource listing
- UI components discoverable
- All resources accessible via MCP

### ✅ Request Tracking
- Request/response history
- Success/failure tracking
- Performance monitoring

## Status

✅ **Gateway**: Working
✅ **UI Integration**: 2 components, 2 resources
✅ **Request Routing**: Working
✅ **Resource Discovery**: Working
✅ **Status Monitoring**: Working

## Conclusion

The MCP Gateway successfully integrates MCP UI components into a unified gateway system, making all capabilities accessible via the MCP protocol. UI components are now discoverable and accessible as standard MCP resources! 🚀
