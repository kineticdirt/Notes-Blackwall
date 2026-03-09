"""
Secure IPC server over Unix socket.
"""
import socket
import json
import os
from pathlib import Path
from typing import Optional, Callable, Dict, Any
from ..security.ipc_auth import IPCAuthenticator, IPCAuthorizer
from ..security.schemas import IPCRequest


class IPCServer:
    """Secure IPC server over Unix socket."""
    
    def __init__(self, socket_path: Path,
                 authenticator: IPCAuthenticator,
                 authorizer: IPCAuthorizer,
                 handlers: Dict[str, Callable]):
        """
        Args:
            socket_path: Path to Unix socket
            authenticator: Authentication handler
            authorizer: Authorization handler
            handlers: Mapping of method name -> handler function
        """
        self.socket_path = socket_path
        self.authenticator = authenticator
        self.authorizer = authorizer
        self.handlers = handlers
        self.sock = None
        self.running = False
    
    def start(self):
        """Start IPC server with secure socket."""
        # Remove existing socket
        if self.socket_path.exists():
            self.socket_path.unlink()
        
        # Create Unix socket
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.bind(str(self.socket_path))
        
        # Set restrictive permissions (owner read/write only)
        os.chmod(self.socket_path, 0o600)
        
        # Listen for connections
        self.sock.listen(5)
        self.running = True
        
        while self.running:
            try:
                conn, addr = self.sock.accept()
                self._handle_connection(conn)
            except Exception as e:
                if self.running:
                    print(f"Error accepting connection: {e}")
    
    def stop(self):
        """Stop IPC server."""
        self.running = False
        if self.sock:
            self.sock.close()
        if self.socket_path.exists():
            self.socket_path.unlink()
    
    def _handle_connection(self, conn: socket.socket):
        """Handle client connection with authentication."""
        # Authenticate peer
        peer_info = self.authenticator.authenticate_peer(conn)
        if not peer_info:
            self._send_error(conn, -32000, 'Authentication failed')
            conn.close()
            return
        
        uid = peer_info['uid']
        
        try:
            # Receive request
            data = conn.recv(4096).decode('utf-8')
            if not data:
                return
            
            # Parse and validate request
            try:
                request_data = json.loads(data)
                request = IPCRequest(**request_data)
            except Exception as e:
                self._send_error(conn, -32700, f'Parse error: {e}')
                return
            
            # Authorize operation
            if not self.authorizer.authorize(uid, request.method):
                self._send_error(conn, -32001, 'Unauthorized')
                return
            
            # Execute handler
            handler = self.handlers.get(request.method)
            if not handler:
                self._send_error(conn, -32601, 'Method not found')
                return
            
            # Call handler with params and user context
            result = handler(request.params, uid=uid)
            
            # Send response
            response = {
                'jsonrpc': '2.0',
                'result': result,
                'id': request.id,
            }
            conn.sendall(json.dumps(response).encode('utf-8'))
        except Exception as e:
            self._send_error(conn, -32603, f'Internal error: {e}')
        finally:
            conn.close()
    
    def _send_error(self, conn: socket.socket, code: int, message: str):
        """Send JSON-RPC error response."""
        response = {
            'jsonrpc': '2.0',
            'error': {
                'code': code,
                'message': message,
            },
            'id': None,
        }
        conn.sendall(json.dumps(response).encode('utf-8'))
