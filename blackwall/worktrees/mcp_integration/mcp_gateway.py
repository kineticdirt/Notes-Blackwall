"""
MCP Gateway: Theoretical gateway system that integrates MCP UI + Toolbox + Servers
Acts as a unified entry point for all MCP capabilities.
"""

import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict

from .mcp_ui_integration import MCPUIIntegration
from .toolbox_integration import SyncToolboxIntegration
from .integrated_system import IntegratedMCPSystem


@dataclass
class GatewayRequest:
    """Request to the MCP Gateway."""
    request_id: str
    request_type: str  # tool, resource, ui, query
    target: str  # Tool name, resource URI, UI component, etc.
    parameters: Dict = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


@dataclass
class GatewayResponse:
    """Response from the MCP Gateway."""
    request_id: str
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MCPGateway:
    """
    MCP Gateway: Unified entry point for all MCP capabilities.
    
    Routes requests to:
    - MCP UI (resources)
    - MCP Toolbox (database queries)
    - MCP Servers (tools)
    - Worktree System (agents, kanban, workflows)
    """
    
    def __init__(self, 
                 ui_path: Optional[Path] = None,
                 toolbox_url: str = "http://127.0.0.1:5000"):
        """
        Initialize MCP Gateway.
        
        Args:
            ui_path: Path to UI markdown files
            toolbox_url: Toolbox server URL
        """
        self.integrated_system = IntegratedMCPSystem(ui_path=ui_path, toolbox_url=toolbox_url)
        self.request_history: List[GatewayRequest] = []
        self.response_history: List[GatewayResponse] = []
    
    def handle_request(self, request: GatewayRequest) -> GatewayResponse:
        """
        Handle a gateway request.
        
        Args:
            request: Gateway request
            
        Returns:
            Gateway response
        """
        self.request_history.append(request)
        
        try:
            if request.request_type == "ui":
                # UI resource request
                resource = self.integrated_system.get_ui_resource(request.target)
                if resource:
                    return GatewayResponse(
                        request_id=request.request_id,
                        success=True,
                        data=resource,
                        metadata={"type": "ui_resource"}
                    )
                else:
                    return GatewayResponse(
                        request_id=request.request_id,
                        success=False,
                        error=f"UI resource '{request.target}' not found"
                    )
            
            elif request.request_type == "tool":
                # Tool execution request
                if self.integrated_system.toolbox.async_integration.connected:
                    result = self.integrated_system.query_database(
                        request.target,
                        **request.parameters
                    )
                    return GatewayResponse(
                        request_id=request.request_id,
                        success=True,
                        data=result,
                        metadata={"type": "tool_execution"}
                    )
                else:
                    return GatewayResponse(
                        request_id=request.request_id,
                        success=False,
                        error="Toolbox not connected"
                    )
            
            elif request.request_type == "resource":
                # MCP resource request
                if request.target.startswith("mcp-ui://"):
                    resource = self.integrated_system.get_ui_resource(
                        request.target.replace("mcp-ui://", "")
                    )
                    if resource:
                        return GatewayResponse(
                            request_id=request.request_id,
                            success=True,
                            data=resource,
                            metadata={"type": "mcp_resource"}
                        )
                
                return GatewayResponse(
                    request_id=request.request_id,
                    success=False,
                    error=f"Resource '{request.target}' not found"
                )
            
            elif request.request_type == "query":
                # Natural language query
                # Route to appropriate handler
                query_lower = request.target.lower()
                
                if "kanban" in query_lower or "card" in query_lower:
                    # Route to Kanban query
                    status = request.parameters.get("status", "in_progress")
                    if self.integrated_system.toolbox.async_integration.connected:
                        result = self.integrated_system.query_database(
                            "get_kanban_cards",
                            status=status
                        )
                        return GatewayResponse(
                            request_id=request.request_id,
                            success=True,
                            data=result,
                            metadata={"type": "query", "handler": "kanban"}
                        )
                
                elif "finding" in query_lower or "bug" in query_lower:
                    # Route to cross-chat discovery
                    category = request.parameters.get("category", "bug")
                    findings = self.integrated_system.mcp_ui.ui_loader.nested_md.base_path.parent.parent.parent.parent
                    # Would query cross-chat here
                    return GatewayResponse(
                        request_id=request.request_id,
                        success=True,
                        data={"message": "Findings query routed"},
                        metadata={"type": "query", "handler": "cross_chat"}
                    )
                
                return GatewayResponse(
                    request_id=request.request_id,
                    success=False,
                    error=f"Query '{request.target}' could not be routed"
                )
            
            else:
                return GatewayResponse(
                    request_id=request.request_id,
                    success=False,
                    error=f"Unknown request type: {request.request_type}"
                )
        
        except Exception as e:
            return GatewayResponse(
                request_id=request.request_id,
                success=False,
                error=str(e)
            )
    
    def list_available_resources(self) -> List[Dict]:
        """List all available resources."""
        resources = []
        
        # UI resources
        ui_resources = self.integrated_system.list_ui_resources()
        resources.extend([
            {
                "uri": r["uri"],
                "name": r["name"],
                "type": "ui",
                "description": r.get("description", "")
            }
            for r in ui_resources
        ])
        
        # Toolbox tools (if connected)
        if self.integrated_system.toolbox.async_integration.connected:
            status = self.integrated_system.toolbox.get_status()
            for toolset in status.get("available_toolsets", []):
                resources.append({
                    "uri": f"toolbox://toolset/{toolset}",
                    "name": toolset,
                    "type": "toolset",
                    "description": f"Toolbox toolset: {toolset}"
                })
        
        return resources
    
    def get_gateway_status(self) -> Dict:
        """Get gateway status."""
        system_status = self.integrated_system.get_status()
        
        return {
            "gateway": {
                "requests_handled": len(self.request_history),
                "successful_requests": sum(1 for r in self.response_history if r.success),
                "available_resources": len(self.list_available_resources())
            },
            "components": {
                "mcp_ui": system_status["mcp_ui"],
                "toolbox": system_status["toolbox"],
                "ui_resources": system_status["ui_resources"]
            }
        }


def create_mcp_gateway(ui_path: Optional[Path] = None,
                      toolbox_url: str = "http://127.0.0.1:5000") -> MCPGateway:
    """
    Create MCP Gateway instance.
    
    Args:
        ui_path: Path to UI files
        toolbox_url: Toolbox server URL
        
    Returns:
        MCPGateway instance
    """
    return MCPGateway(ui_path=ui_path, toolbox_url=toolbox_url)
