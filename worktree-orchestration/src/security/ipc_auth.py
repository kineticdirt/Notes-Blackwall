"""
IPC authentication and authorization for Unix socket server.
"""
import os
import socket
import struct
from typing import Optional, Set, Dict, List
from pathlib import Path
import json
import base64
import hmac
import hashlib
from datetime import datetime, timedelta


class IPCAuthenticator:
    """Unix socket peer credential authentication."""
    
    def __init__(self, allowed_uids: Optional[Set[int]] = None,
                 allowed_gids: Optional[Set[int]] = None,
                 token_secret: Optional[str] = None):
        """
        Args:
            allowed_uids: Set of allowed UIDs (None = current user only)
            allowed_gids: Set of allowed GIDs (None = current user's groups)
            token_secret: Secret for token-based auth (optional)
        """
        self.allowed_uids = allowed_uids or {os.getuid()}
        self.allowed_gids = allowed_gids or set(os.getgroups())
        self.token_secret = token_secret or os.environ.get('IPC_TOKEN_SECRET')
    
    def authenticate_peer(self, sock: socket.socket) -> Optional[Dict]:
        """
        Authenticate client via Unix socket peer credentials.
        
        Returns:
            Dict with 'uid', 'gid', 'pid' if authenticated, None otherwise
        """
        try:
            # Try SO_PEERCRED (Linux)
            try:
                creds = sock.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED,
                                        struct.calcsize('3i'))
                pid, uid, gid = struct.unpack('3i', creds)
            except (OSError, AttributeError):
                # Fallback: Check socket file ownership (macOS/BSD)
                try:
                    sock_path = sock.getsockname()
                    if isinstance(sock_path, str) and os.path.exists(sock_path):
                        stat_info = os.stat(sock_path)
                        uid = stat_info.st_uid
                        gid = stat_info.st_gid
                        pid = None
                    else:
                        # Last resort: trust current user
                        uid = os.getuid()
                        gid = os.getgid()
                        pid = None
                except:
                    return None
            
            # Validate UID
            if uid not in self.allowed_uids:
                return None
            
            # Optional: Validate GID
            if self.allowed_gids and gid not in self.allowed_gids:
                return None
            
            return {'uid': uid, 'gid': gid, 'pid': pid}
        except Exception:
            return None
    
    def authenticate_token(self, token: str) -> Optional[Dict]:
        """
        Authenticate via bearer token (optional).
        
        Token format: base64(hmac_sha256(payload, secret))
        Payload: {"uid": int, "exp": timestamp, "roles": ["admin"]}
        """
        if not self.token_secret:
            return None
        
        try:
            # Decode token
            payload_bytes = base64.urlsafe_b64decode(token.encode('utf-8'))
            payload_str = payload_bytes.decode('utf-8')
            payload = json.loads(payload_str)
            
            # Verify HMAC
            expected_token = self._generate_token(payload)
            if not hmac.compare_digest(token, expected_token):
                return None
            
            # Check expiration
            exp = payload.get('exp')
            if exp and datetime.fromtimestamp(exp) < datetime.now():
                return None
            
            return payload
        except Exception:
            return None
    
    def _generate_token(self, payload: Dict) -> str:
        """Generate HMAC token from payload."""
        payload_str = json.dumps(payload, sort_keys=True)
        hmac_digest = hmac.new(
            self.token_secret.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).digest()
        return base64.urlsafe_b64encode(hmac_digest).decode('utf-8')


class IPCAuthorizer:
    """Authorization for IPC operations."""
    
    ROLES = {
        'admin': ['*'],  # All operations
        'competitor': [
            'submit_solution',
            'submit_critique',
            'get_own_artifacts',
            'list_own_rounds',
        ],
        'viewer': [
            'list_rounds',
            'get_artifacts',
            'get_results',
        ],
    }
    
    def __init__(self, user_roles: Optional[Dict[int, List[str]]] = None):
        """
        Args:
            user_roles: Mapping of UID -> list of role names
                       (None = use default: current user = admin)
        """
        if user_roles is None:
            self.user_roles = {os.getuid(): ['admin']}
        else:
            self.user_roles = user_roles
    
    def authorize(self, uid: int, operation: str) -> bool:
        """Check if user has permission for operation."""
        roles = self.user_roles.get(uid, ['viewer'])  # Default: viewer
        
        for role in roles:
            permissions = self.ROLES.get(role, [])
            if '*' in permissions or operation in permissions:
                return True
        
        return False
    
    def add_user_role(self, uid: int, role: str) -> None:
        """Add role to user."""
        if uid not in self.user_roles:
            self.user_roles[uid] = []
        if role not in self.user_roles[uid]:
            self.user_roles[uid].append(role)
    
    def remove_user_role(self, uid: int, role: str) -> None:
        """Remove role from user."""
        if uid in self.user_roles:
            self.user_roles[uid] = [r for r in self.user_roles[uid] if r != role]
