"""
JSON-RPC 2.0 protocol implementation.

Lightweight, async JSON-RPC server over Unix domain sockets.
"""
import json
import logging
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class JSONRPCError(Exception):
    """JSON-RPC error."""
    def __init__(self, code: int, message: str, data: Any = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)


# Standard JSON-RPC error codes
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603


class JSONRPCHandler:
    """
    JSON-RPC 2.0 request handler.
    
    Handles JSON-RPC requests and routes them to registered methods.
    """
    
    def __init__(self):
        self._methods: Dict[str, Callable] = {}
    
    def register_method(self, name: str, handler: Callable):
        """Register a JSON-RPC method."""
        self._methods[name] = handler
        logger.debug(f"Registered JSON-RPC method: {name}")
    
    async def handle_request(self, request_str: str) -> str:
        """
        Handle a JSON-RPC request.
        
        Args:
            request_str: JSON-RPC request as string
        
        Returns:
            JSON-RPC response as string
        """
        try:
            request = json.loads(request_str)
        except json.JSONDecodeError as e:
            return self._error_response(None, PARSE_ERROR, f"Parse error: {e}")
        
        # Validate request structure
        if not isinstance(request, dict):
            return self._error_response(None, INVALID_REQUEST, "Invalid request")
        
        # Extract request ID (may be None for notifications)
        request_id = request.get("id")
        
        # Check for notification (no ID)
        is_notification = request_id is None
        
        # Validate required fields
        if "jsonrpc" not in request or request["jsonrpc"] != "2.0":
            return self._error_response(request_id, INVALID_REQUEST, "Invalid JSON-RPC version")
        
        if "method" not in request:
            return self._error_response(request_id, INVALID_REQUEST, "Missing method")
        
        method_name = request["method"]
        params = request.get("params", {})
        
        # Find method handler
        if method_name not in self._methods:
            return self._error_response(
                request_id,
                METHOD_NOT_FOUND,
                f"Method not found: {method_name}"
            )
        
        handler = self._methods[method_name]
        
        # Call handler
        try:
            if isinstance(params, dict):
                # Named parameters
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(**params)
                else:
                    result = handler(**params)
            elif isinstance(params, list):
                # Positional parameters
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(*params)
                else:
                    result = handler(*params)
            else:
                # No parameters
                if asyncio.iscoroutinefunction(handler):
                    result = await handler()
                else:
                    result = handler()
            
            # Return result (skip for notifications)
            if is_notification:
                return ""
            
            return json.dumps({
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id
            })
            
        except TypeError as e:
            return self._error_response(
                request_id,
                INVALID_PARAMS,
                f"Invalid parameters: {e}"
            )
        except Exception as e:
            logger.error(f"Error executing method {method_name}: {e}", exc_info=True)
            return self._error_response(
                request_id,
                INTERNAL_ERROR,
                f"Internal error: {str(e)}"
            )
    
    def _error_response(self, request_id: Optional[Any], code: int, message: str, data: Any = None) -> str:
        """Create error response."""
        error = {
            "code": code,
            "message": message
        }
        if data is not None:
            error["data"] = data
        
        response = {
            "jsonrpc": "2.0",
            "error": error,
            "id": request_id
        }
        
        return json.dumps(response)


# Import asyncio for coroutine check
import asyncio
