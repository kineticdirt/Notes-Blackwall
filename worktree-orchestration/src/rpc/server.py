"""
Unix socket JSON-RPC server for critique arena.

Provides JSON-RPC interface over Unix domain socket for critique operations.
"""
import asyncio
import logging
import os
from pathlib import Path
from typing import Optional

from .protocol import JSONRPCHandler

logger = logging.getLogger(__name__)


class UnixSocketRPCServer:
    """
    Unix socket JSON-RPC server.
    
    Listens on Unix domain socket and handles JSON-RPC requests.
    """
    
    def __init__(self, socket_path: Path, handler: JSONRPCHandler):
        """
        Initialize server.
        
        Args:
            socket_path: Path to Unix socket file
            handler: JSON-RPC request handler
        """
        self.socket_path = Path(socket_path)
        self.handler = handler
        self.server: Optional[asyncio.Server] = None
        self._running = False
    
    async def start(self):
        """Start server."""
        if self._running:
            return
        
        # Remove existing socket file if it exists
        if self.socket_path.exists():
            self.socket_path.unlink()
        
        # Create parent directory if needed
        self.socket_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create Unix socket server
        self.server = await asyncio.start_unix_server(
            self._handle_client,
            str(self.socket_path)
        )
        
        # Set socket permissions (read/write for owner and group)
        os.chmod(self.socket_path, 0o660)
        
        self._running = True
        logger.info(f"Unix socket RPC server started at {self.socket_path}")
    
    async def stop(self):
        """Stop server."""
        if not self._running:
            return
        
        self._running = False
        
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        # Remove socket file
        if self.socket_path.exists():
            self.socket_path.unlink()
        
        logger.info("Unix socket RPC server stopped")
    
    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle client connection."""
        client_addr = writer.get_extra_info('peername')
        logger.debug(f"Client connected: {client_addr}")
        
        try:
            while True:
                # Read request (line-delimited JSON)
                line = await reader.readline()
                if not line:
                    break
                
                request_str = line.decode('utf-8').strip()
                if not request_str:
                    continue
                
                # Handle request
                response_str = await self.handler.handle_request(request_str)
                
                # Send response (if not a notification)
                if response_str:
                    writer.write(response_str.encode('utf-8'))
                    writer.write(b'\n')
                    await writer.drain()
        
        except Exception as e:
            logger.error(f"Error handling client: {e}", exc_info=True)
        finally:
            writer.close()
            await writer.wait_closed()
            logger.debug(f"Client disconnected: {client_addr}")
