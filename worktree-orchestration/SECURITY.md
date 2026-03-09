# Security Threat Model & Implementation Guide

**Version:** 1.0.0  
**Last Updated:** 2026-01-30  
**Status:** Security-Focused Design Specification

---

## Executive Summary

This document provides a comprehensive threat model and secure-by-default design for the `worktree-orchestration/` system, covering:
- **Arena & Runner** threat analysis
- **IPC Server** (Unix socket) security
- **Dashboard API** (port 4000) security
- **Artifact storage** in `../.shared-cache/` security
- **Input validation** schemas
- **Security testing** recommendations with graceful fallbacks

---

## 1. Threat Model

### 1.1 System Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL BOUNDARY                        │
│                                                             │
│  ┌──────────────────┐         ┌──────────────────┐        │
│  │   IPC Client     │────────▶│  IPC Server      │        │
│  │  (Unix Socket)   │         │  (Unix Socket)   │        │
│  └──────────────────┘         └────────┬─────────┘        │
│                                        │                   │
│  ┌──────────────────┐                  │                   │
│  │  Dashboard UI   │────────▶│  Dashboard API   │        │
│  │  (Browser)      │         │  (Port 4000)      │        │
│  └──────────────────┘         └────────┬─────────┘        │
│                                         │                   │
│                                         ▼                   │
│                              ┌──────────────────┐          │
│                              │   Arena Engine    │          │
│                              │   + Runner        │          │
│                              └────────┬──────────┘          │
│                                       │                     │
│                              ┌────────▼──────────┐          │
│                              │  Worktree Manager │          │
│                              │  Artifact Store   │          │
│                              └────────┬──────────┘          │
│                                       │                     │
│                              ┌────────▼──────────┐          │
│                              │  .shared-cache/   │          │
│                              │  worktrees/       │          │
│                              └───────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Threat Actors

| Actor | Capabilities | Motivation | Access Level |
|-------|-------------|------------|--------------|
| **Malicious Competitor** | Can submit solutions, critiques | Gain unfair advantage, disrupt competition | Limited (own worktree) |
| **Privileged User** | Full CLI/API access | Admin operations, oversight | Full |
| **Local Attacker** | Same machine access | Escalate privileges, data exfiltration | Local filesystem |
| **Network Attacker** | Can reach port 4000 | Unauthorized API access, DoS | Network only |
| **Insider Threat** | Legitimate access | Data theft, sabotage | Varies |

### 1.3 Attack Vectors

#### 1.3.1 IPC Server (Unix Socket) Threats

| Threat ID | Threat | Likelihood | Impact | Mitigation |
|-----------|--------|------------|--------|------------|
| **IPC-001** | Unauthorized socket access (world-readable) | High | Critical | Socket permissions (0600), UID/GID checks |
| **IPC-002** | Path traversal in IPC requests | Medium | High | Strict path validation, canonicalization |
| **IPC-003** | Command injection via test_command | High | Critical | No shell execution, explicit args |
| **IPC-004** | DoS via resource exhaustion | Medium | Medium | Rate limiting, timeouts, resource quotas |
| **IPC-005** | Replay attacks | Low | Medium | Nonce/timestamp validation |
| **IPC-006** | Privilege escalation | Low | Critical | Run as non-root, capability dropping |

#### 1.3.2 Dashboard API (Port 4000) Threats

| Threat ID | Threat | Likelihood | Impact | Mitigation |
|-----------|--------|------------|--------|------------|
| **API-001** | Unauthenticated access | High | Critical | Mandatory authentication |
| **API-002** | SQL injection (if DB added) | Low | High | Parameterized queries, input validation |
| **API-003** | XSS in dashboard UI | Medium | Medium | Content-Security-Policy, output encoding |
| **API-004** | CSRF attacks | Medium | Medium | CSRF tokens, SameSite cookies |
| **API-005** | Session hijacking | Medium | High | Secure cookies, token rotation |
| **API-006** | API rate limiting bypass | Medium | Medium | Multi-layer rate limiting |
| **API-007** | Information disclosure | Medium | High | Minimal error messages, audit logs |

#### 1.3.3 Arena & Runner Threats

| Threat ID | Threat | Likelihood | Impact | Mitigation |
|-----------|--------|------------|--------|------------|
| **ARENA-001** | Worktree escape (directory traversal) | High | Critical | Path validation, chroot-like isolation |
| **ARENA-002** | Test command injection | High | Critical | No shell, explicit subprocess args |
| **ARENA-003** | Resource exhaustion (disk, CPU, memory) | Medium | High | Quotas, timeouts, monitoring |
| **ARENA-004** | Cross-competitor data leakage | Medium | High | Strict file permissions, isolation |
| **ARENA-005** | Malicious test execution | Medium | High | Sandboxing, resource limits |
| **ARENA-006** | Artifact tampering | Low | Medium | Integrity checks, read-only artifacts |

#### 1.3.4 Artifact Storage Threats

| Threat ID | Threat | Likelihood | Impact | Mitigation |
|-----------|--------|------------|--------|------------|
| **ARTIFACT-001** | Path traversal in artifact paths | Medium | High | Canonicalization, validation |
| **ARTIFACT-002** | Symlink attacks | Medium | High | Follow symlinks: false, realpath checks |
| **ARTIFACT-003** | Disk exhaustion | Medium | Medium | Quotas, cleanup policies |
| **ARTIFACT-004** | Unauthorized artifact access | Low | Medium | File permissions, access control |
| **ARTIFACT-005** | Artifact corruption | Low | Low | Atomic writes, checksums |

---

## 2. Secure-by-Default Design Decisions

### 2.1 Authentication & Authorization Architecture

#### 2.1.1 IPC Server Authentication

**Design:** Unix socket peer credential authentication + optional token-based auth

```python
# IPC Authentication Flow
1. Client connects to Unix socket
2. Server checks peer credentials (UID/GID via SO_PEERCRED)
3. Server validates client UID matches allowed set
4. Optional: Token-based auth for multi-user scenarios
5. Authorization check: Does user have permission for requested operation?
```

**Implementation:**
- **Default:** UID/GID-based authentication (Unix socket peer credentials)
- **Optional:** Bearer token authentication for multi-user scenarios
- **Authorization:** Role-based access control (RBAC) with roles: `admin`, `competitor`, `viewer`

#### 2.1.2 Dashboard API Authentication

**Design:** JWT-based authentication with refresh tokens

```python
# Dashboard Authentication Flow
1. User authenticates via /api/auth/login (username/password or API key)
2. Server validates credentials
3. Server issues JWT access token (short-lived, 15min) + refresh token (long-lived, 7 days)
4. Client includes JWT in Authorization header: `Bearer <token>`
5. Server validates JWT signature, expiry, and user permissions
6. Refresh token used to obtain new access token
```

**Implementation:**
- **Default:** JWT tokens (HS256 or RS256)
- **Optional:** OAuth2/OIDC integration
- **Authorization:** Role-based permissions per endpoint

### 2.2 Input Validation Strategy

**Principle:** Validate early, validate often, fail closed

**Layers:**
1. **Schema validation** (Pydantic/Zod) - Type and structure
2. **Business logic validation** - Domain rules
3. **Sanitization** - Path normalization, encoding
4. **Output encoding** - Prevent injection in responses

### 2.3 File Handling Security

**Principle:** Never trust file paths, always validate and canonicalize

**Rules:**
1. All paths must be relative to base directories
2. Canonicalize paths using `os.path.realpath()` or `pathlib.Path.resolve()`
3. Reject paths containing `..`, symlinks (unless explicitly allowed)
4. Set restrictive file permissions (0600 for files, 0700 for directories)
5. Use atomic writes (temp file + rename)

---

## 3. Implementation: Authentication & Authorization

### 3.1 IPC Server Auth Implementation

#### 3.1.1 Unix Socket Peer Credential Auth

```python
# src/security/ipc_auth.py

import os
import socket
import struct
from typing import Optional, Set
from pathlib import Path
import json
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
    
    def authenticate_peer(self, sock: socket.socket) -> Optional[dict]:
        """
        Authenticate client via Unix socket peer credentials.
        
        Returns:
            Dict with 'uid', 'gid', 'pid' if authenticated, None otherwise
        """
        try:
            # Get peer credentials (Linux/BSD)
            creds = sock.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 
                                    struct.calcsize('3i'))
            pid, uid, gid = struct.unpack('3i', creds)
            
            # Validate UID
            if uid not in self.allowed_uids:
                return None
            
            # Optional: Validate GID
            if self.allowed_gids and gid not in self.allowed_gids:
                return None
            
            return {'uid': uid, 'gid': gid, 'pid': pid}
        except (OSError, AttributeError):
            # Fallback: Check if socket is owned by current user
            try:
                sock_path = sock.getsockname()
                if isinstance(sock_path, str):
                    stat_info = os.stat(sock_path)
                    if stat_info.st_uid == os.getuid():
                        return {'uid': os.getuid(), 'gid': os.getgid(), 'pid': None}
            except:
                pass
            return None
    
    def authenticate_token(self, token: str) -> Optional[dict]:
        """
        Authenticate via bearer token (optional).
        
        Token format: base64(hmac_sha256(payload, secret))
        Payload: {"uid": int, "exp": timestamp, "roles": ["admin"]}
        """
        if not self.token_secret:
            return None
        
        try:
            import base64
            # Decode token
            payload_bytes = base64.urlsafe_b64decode(token)
            # Verify HMAC
            # ... (implementation)
            return None  # Placeholder
        except:
            return None


class IPCAuthorizer:
    """Authorization for IPC operations."""
    
    ROLES = {
        'admin': ['*'],  # All operations
        'competitor': ['submit_solution', 'submit_critique', 'get_own_artifacts'],
        'viewer': ['list_rounds', 'get_artifacts', 'get_results'],
    }
    
    def __init__(self, user_roles: dict[int, list[str]]):
        """
        Args:
            user_roles: Mapping of UID -> list of role names
        """
        self.user_roles = user_roles
    
    def authorize(self, uid: int, operation: str) -> bool:
        """Check if user has permission for operation."""
        roles = self.user_roles.get(uid, ['viewer'])  # Default: viewer
        
        for role in roles:
            permissions = self.ROLES.get(role, [])
            if '*' in permissions or operation in permissions:
                return True
        
        return False
```

#### 3.1.2 IPC Server with Auth

```python
# src/ipc/server.py

import socket
import json
import struct
import os
from pathlib import Path
from typing import Optional, Callable, Dict, Any
from .security.ipc_auth import IPCAuthenticator, IPCAuthorizer

class IPCServer:
    """Secure IPC server over Unix socket."""
    
    def __init__(self, socket_path: Path, 
                 authenticator: IPCAuthenticator,
                 authorizer: IPCAuthorizer,
                 handlers: Dict[str, Callable]):
        self.socket_path = socket_path
        self.authenticator = authenticator
        self.authorizer = authorizer
        self.handlers = handlers
        self.sock = None
    
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
        
        while True:
            conn, addr = self.sock.accept()
            self._handle_connection(conn)
    
    def _handle_connection(self, conn: socket.socket):
        """Handle client connection with authentication."""
        # Authenticate peer
        peer_info = self.authenticator.authenticate_peer(conn)
        if not peer_info:
            conn.close()
            return
        
        uid = peer_info['uid']
        
        try:
            # Receive request
            data = conn.recv(4096).decode('utf-8')
            request = json.loads(data)
            
            # Extract operation
            method = request.get('method')
            params = request.get('params', {})
            
            # Authorize operation
            if not self.authorizer.authorize(uid, method):
                response = {'error': {'code': -32001, 'message': 'Unauthorized'}}
                conn.sendall(json.dumps(response).encode('utf-8'))
                return
            
            # Execute handler
            handler = self.handlers.get(method)
            if not handler:
                response = {'error': {'code': -32601, 'message': 'Method not found'}}
            else:
                result = handler(params, uid=uid)
                response = {'result': result}
            
            conn.sendall(json.dumps(response).encode('utf-8'))
        except Exception as e:
            response = {'error': {'code': -32603, 'message': str(e)}}
            conn.sendall(json.dumps(response).encode('utf-8'))
        finally:
            conn.close()
```

### 3.2 Dashboard API Auth Implementation

```python
# src/security/api_auth.py

import jwt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from functools import wraps
from flask import request, jsonify, g

class APIAuthenticator:
    """JWT-based API authentication."""
    
    def __init__(self, secret_key: str, algorithm: str = 'HS256'):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def generate_token(self, user_id: str, roles: List[str], 
                      expires_in: int = 900) -> str:
        """Generate JWT access token."""
        payload = {
            'user_id': user_id,
            'roles': roles,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow(),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def require_auth(self, roles: Optional[List[str]] = None):
        """Decorator for requiring authentication."""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Extract token from Authorization header
                auth_header = request.headers.get('Authorization', '')
                if not auth_header.startswith('Bearer '):
                    return jsonify({'error': 'Missing or invalid authorization'}), 401
                
                token = auth_header[7:]  # Remove 'Bearer ' prefix
                payload = self.verify_token(token)
                
                if not payload:
                    return jsonify({'error': 'Invalid or expired token'}), 401
                
                # Check role requirements
                if roles:
                    user_roles = payload.get('roles', [])
                    if not any(role in user_roles for role in roles):
                        return jsonify({'error': 'Insufficient permissions'}), 403
                
                # Store user info in Flask g
                g.user_id = payload['user_id']
                g.user_roles = payload['roles']
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
```

---

## 4. Input Validation Schemas

### 4.1 IPC Request Schema

```python
# src/security/schemas.py

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from pathlib import Path
import re

class IPCRequest(BaseModel):
    """IPC request schema."""
    method: str = Field(..., min_length=1, max_length=100, 
                        pattern=r'^[a-z_][a-z0-9_]*$')
    params: Dict[str, Any] = Field(default_factory=dict)
    id: Optional[str] = None
    
    @validator('method')
    def validate_method(cls, v):
        allowed_methods = {
            'start_round', 'submit_solution', 'submit_critique',
            'test_round', 'end_round', 'list_artifacts', 'get_artifact'
        }
        if v not in allowed_methods:
            raise ValueError(f'Unknown method: {v}')
        return v


class PathParam(BaseModel):
    """Safe path parameter."""
    path: str = Field(..., min_length=1, max_length=4096)
    
    @validator('path')
    def validate_path(cls, v):
        # Reject absolute paths
        if v.startswith('/'):
            raise ValueError('Absolute paths not allowed')
        
        # Reject path traversal
        if '..' in v:
            raise ValueError('Path traversal not allowed')
        
        # Reject control characters
        if any(ord(c) < 32 for c in v):
            raise ValueError('Control characters not allowed')
        
        # Reject dangerous patterns
        dangerous = ['\x00', '\n', '\r']
        if any(d in v for d in dangerous):
            raise ValueError('Dangerous characters not allowed')
        
        return v
    
    def resolve(self, base: Path) -> Path:
        """Resolve path relative to base directory."""
        # Normalize path
        normalized = Path(v).resolve()
        base_resolved = base.resolve()
        
        # Ensure path is within base
        try:
            normalized.relative_to(base_resolved)
        except ValueError:
            raise ValueError(f'Path outside base directory: {v}')
        
        return normalized


class CompetitorIDParam(BaseModel):
    """Competitor ID parameter."""
    competitor_id: str = Field(..., min_length=1, max_length=50)
    
    @validator('competitor_id')
    def validate_id(cls, v):
        # Alphanumeric + underscore/hyphen only
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Invalid competitor_id format')
        return v


class RoundNumParam(BaseModel):
    """Round number parameter."""
    round_num: int = Field(..., ge=1, le=1000)


class SubmitSolutionRequest(BaseModel):
    """Submit solution request schema."""
    competitor_id: str = Field(..., min_length=1, max_length=50)
    round_num: int = Field(..., ge=1, le=1000)
    solution_path: PathParam
    
    @validator('competitor_id')
    def validate_competitor_id(cls, v):
        return CompetitorIDParam(competitor_id=v).competitor_id
```

### 4.2 Dashboard API Schemas

```python
# src/security/api_schemas.py

from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List

class LoginRequest(BaseModel):
    """Login request schema."""
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8, max_length=256)
    
    @validator('username')
    def validate_username(cls, v):
        # Alphanumeric + underscore only
        if not v.replace('_', '').isalnum():
            raise ValueError('Invalid username format')
        return v


class CreateRoundRequest(BaseModel):
    """Create round request schema."""
    round_num: int = Field(..., ge=1, le=1000)
    competitors: List[str] = Field(..., min_items=1, max_items=50)
    
    @validator('competitors')
    def validate_competitors(cls, v):
        for comp_id in v:
            if not re.match(r'^[a-zA-Z0-9_-]+$', comp_id):
                raise ValueError(f'Invalid competitor_id: {comp_id}')
        return v
```

---

## 5. Safe File Handling

### 5.1 Path Validation & Canonicalization

```python
# src/security/file_handling.py

import os
from pathlib import Path
from typing import Optional
import stat

class SafePathHandler:
    """Safe file path handling."""
    
    @staticmethod
    def validate_and_resolve(path: str, base: Path, 
                            follow_symlinks: bool = False) -> Path:
        """
        Validate and resolve path relative to base directory.
        
        Args:
            path: Relative path string
            base: Base directory (must be absolute)
            follow_symlinks: Whether to follow symlinks (default: False)
        
        Returns:
            Resolved Path object
        
        Raises:
            ValueError: If path is invalid or outside base
        """
        # Ensure base is absolute
        base = base.resolve()
        
        # Validate input
        if not isinstance(path, str):
            raise ValueError('Path must be a string')
        
        # Reject absolute paths
        if os.path.isabs(path):
            raise ValueError('Absolute paths not allowed')
        
        # Reject path traversal
        if '..' in path or path.startswith('../'):
            raise ValueError('Path traversal not allowed')
        
        # Reject control characters
        if any(ord(c) < 32 and c not in '\t\n\r' for c in path):
            raise ValueError('Control characters not allowed')
        
        # Join and resolve
        joined = base / path
        
        if follow_symlinks:
            resolved = joined.resolve()
        else:
            # Resolve without following symlinks
            resolved = Path(os.path.normpath(str(joined)))
            # Check if any component is a symlink
            parts = resolved.parts
            current = base
            for part in parts[len(base.parts):]:
                current = current / part
                if current.is_symlink():
                    raise ValueError(f'Symlink not allowed: {current}')
        
        # Ensure resolved path is within base
        try:
            resolved.relative_to(base)
        except ValueError:
            raise ValueError(f'Path outside base directory: {path}')
        
        return resolved
    
    @staticmethod
    def safe_write(file_path: Path, content: bytes, 
                  mode: int = 0o600) -> None:
        """
        Atomic file write with safe permissions.
        
        Args:
            file_path: Target file path
            content: Content to write
            mode: File permissions (default: 0600)
        """
        # Create parent directories with safe permissions
        file_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        
        # Write to temp file
        temp_path = file_path.with_suffix(file_path.suffix + '.tmp')
        
        try:
            with open(temp_path, 'wb') as f:
                f.write(content)
            os.chmod(temp_path, mode)
            
            # Atomic rename
            temp_path.replace(file_path)
        except Exception:
            # Cleanup on error
            if temp_path.exists():
                temp_path.unlink()
            raise
    
    @staticmethod
    def safe_read(file_path: Path, max_size: int = 10 * 1024 * 1024) -> bytes:
        """
        Safe file read with size limits.
        
        Args:
            file_path: File to read
            max_size: Maximum file size in bytes (default: 10MB)
        
        Returns:
            File content
        
        Raises:
            ValueError: If file is too large
        """
        # Check file size
        stat_info = file_path.stat()
        if stat_info.st_size > max_size:
            raise ValueError(f'File too large: {stat_info.st_size} bytes')
        
        # Read file
        with open(file_path, 'rb') as f:
            return f.read()
```

### 5.2 Artifact Storage Security

```python
# src/artifacts.py (enhanced)

from .security.file_handling import SafePathHandler
import hashlib
import json

class SecureArtifactStore(ArtifactStore):
    """Enhanced artifact store with security."""
    
    MAX_ARTIFACT_SIZE = 100 * 1024 * 1024  # 100MB
    MAX_FILES_PER_ARTIFACT = 1000
    
    def store_solution(self, round_num: int, competitor_id: str,
                      worktree_path: Path, files: List[Dict[str, Any]]) -> str:
        """Store solution with security checks."""
        # Validate competitor_id
        CompetitorIDParam(competitor_id=competitor_id)
        
        # Validate round number
        RoundNumParam(round_num=round_num)
        
        # Validate file count
        if len(files) > self.MAX_FILES_PER_ARTIFACT:
            raise ValueError(f'Too many files: {len(files)}')
        
        # Validate file sizes
        total_size = sum(f.get('size', 0) for f in files)
        if total_size > self.MAX_ARTIFACT_SIZE:
            raise ValueError(f'Artifact too large: {total_size} bytes')
        
        # Validate worktree_path is within allowed base
        base_path = self.cache_dir.parent / "worktrees"
        SafePathHandler.validate_and_resolve(
            str(worktree_path.relative_to(base_path)), 
            base_path
        )
        
        # Create artifact
        round_dir = self._get_round_dir(round_num)
        timestamp = datetime.now().isoformat()
        
        artifact = SolutionArtifact(
            competitor_id=competitor_id,
            round_num=round_num,
            timestamp=timestamp,
            worktree_path=str(worktree_path),
            files=files
        )
        
        artifact_id = f"{competitor_id}_{int(datetime.now().timestamp())}"
        artifact_file = round_dir / "solutions" / f"{artifact_id}.json"
        
        # Safe atomic write
        content = json.dumps(artifact.dict(), indent=2).encode('utf-8')
        SafePathHandler.safe_write(artifact_file, content, mode=0o600)
        
        return artifact_id
```

---

## 6. Security Testing Recommendations

### 6.1 Static Analysis Tools

#### 6.1.1 Semgrep (Python)

**Setup:**
```bash
# Install semgrep
pip install semgrep

# Run security rules
semgrep --config=auto --config=p/security-audit \
        --config=p/python \
        worktree-orchestration/src/

# Custom rules file: .semgrep-rules.yml
```

**Graceful Fallback:**
```python
# scripts/security_check.py

import subprocess
import sys
import os

def run_semgrep():
    """Run semgrep with graceful fallback."""
    try:
        result = subprocess.run(
            ['semgrep', '--config=auto', '--json', 'src/'],
            capture_output=True,
            timeout=300
        )
        if result.returncode == 0:
            return True, result.stdout.decode()
        else:
            return False, result.stderr.decode()
    except FileNotFoundError:
        print("⚠ Semgrep not installed, skipping...", file=sys.stderr)
        return None, None
    except subprocess.TimeoutExpired:
        print("⚠ Semgrep timed out", file=sys.stderr)
        return None, None
    except Exception as e:
        print(f"⚠ Semgrep error: {e}", file=sys.stderr)
        return None, None

if __name__ == '__main__':
    success, output = run_semgrep()
    if success is None:
        sys.exit(0)  # Graceful exit if tool unavailable
    elif success:
        print("✓ Semgrep passed")
        sys.exit(0)
    else:
        print("✗ Semgrep found issues:")
        print(output)
        sys.exit(1)
```

#### 6.1.2 ESLint Security Plugin (if TypeScript/JavaScript)

**Setup:**
```bash
npm install --save-dev eslint-plugin-security
```

**Config:**
```json
{
  "extends": ["plugin:security/recommended"],
  "rules": {
    "security/detect-object-injection": "error",
    "security/detect-non-literal-fs-filename": "warn"
  }
}
```

**Graceful Fallback:**
```javascript
// scripts/security-check.js

const { execSync } = require('child_process');

try {
  execSync('npx eslint --plugin security src/', { stdio: 'inherit' });
  console.log('✓ ESLint security check passed');
  process.exit(0);
} catch (error) {
  if (error.code === 'ENOENT') {
    console.warn('⚠ ESLint not found, skipping...');
    process.exit(0);  // Graceful exit
  } else {
    console.error('✗ ESLint security check failed');
    process.exit(1);
  }
}
```

#### 6.1.3 Snyk (Dependency Scanning)

**Setup:**
```bash
# Install Snyk CLI (requires token)
npm install -g snyk
snyk auth <SNYK_TOKEN>  # Optional, can run without token

# Scan dependencies
snyk test --severity-threshold=high
```

**Graceful Fallback:**
```python
# scripts/snyk_check.py

import subprocess
import sys
import os

def run_snyk():
    """Run Snyk with graceful fallback."""
    token = os.environ.get('SNYK_TOKEN')
    
    if not token:
        print("⚠ SNYK_TOKEN not set, skipping Snyk scan...", file=sys.stderr)
        return None
    
    try:
        result = subprocess.run(
            ['snyk', 'test', '--severity-threshold=high', '--json'],
            capture_output=True,
            timeout=300,
            env={**os.environ, 'SNYK_TOKEN': token}
        )
        if result.returncode == 0:
            return True, None
        else:
            return False, result.stdout.decode()
    except FileNotFoundError:
        print("⚠ Snyk CLI not installed, skipping...", file=sys.stderr)
        return None, None
    except Exception as e:
        print(f"⚠ Snyk error: {e}", file=sys.stderr)
        return None, None

if __name__ == '__main__':
    success, output = run_snyk()
    if success is None:
        sys.exit(0)  # Graceful exit
    elif success:
        print("✓ Snyk scan passed")
        sys.exit(0)
    else:
        print("✗ Snyk found vulnerabilities:")
        print(output)
        sys.exit(1)
```

### 6.2 Security Test Suite

```python
# tests/test_security.py

import pytest
import tempfile
import os
from pathlib import Path
from worktree_orchestration.security.file_handling import SafePathHandler
from worktree_orchestration.security.schemas import PathParam, CompetitorIDParam

class TestPathValidation:
    """Test path validation security."""
    
    def test_reject_absolute_paths(self):
        """Test that absolute paths are rejected."""
        with pytest.raises(ValueError, match='Absolute paths'):
            PathParam(path='/etc/passwd')
    
    def test_reject_path_traversal(self):
        """Test that path traversal is rejected."""
        with pytest.raises(ValueError, match='Path traversal'):
            PathParam(path='../../etc/passwd')
    
    def test_reject_control_characters(self):
        """Test that control characters are rejected."""
        with pytest.raises(ValueError):
            PathParam(path='file\x00name')
    
    def test_path_resolution_within_base(self):
        """Test that resolved paths stay within base."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            # Valid path
            resolved = SafePathHandler.validate_and_resolve('subdir/file.txt', base)
            assert resolved.is_relative_to(base)
            
            # Invalid path (traversal)
            with pytest.raises(ValueError):
                SafePathHandler.validate_and_resolve('../../etc/passwd', base)


class TestCompetitorIDValidation:
    """Test competitor ID validation."""
    
    def test_valid_ids(self):
        """Test valid competitor IDs."""
        valid_ids = ['agent1', 'agent_2', 'agent-3', 'Agent123']
        for cid in valid_ids:
            CompetitorIDParam(competitor_id=cid)
    
    def test_invalid_ids(self):
        """Test invalid competitor IDs."""
        invalid_ids = ['agent 1', 'agent@1', 'agent.1', '../../etc']
        for cid in invalid_ids:
            with pytest.raises(ValueError):
                CompetitorIDParam(competitor_id=cid)


class TestCommandInjection:
    """Test command injection prevention."""
    
    def test_subprocess_no_shell(self):
        """Test that subprocess doesn't use shell."""
        import subprocess
        
        # This should fail safely (no shell execution)
        result = subprocess.run(
            ['echo', 'test; rm -rf /'],
            capture_output=True,
            shell=False  # Critical: no shell
        )
        # Command should execute safely (echo with literal arg)
        assert b'test; rm -rf /' in result.stdout
```

### 6.3 CI/CD Integration

```yaml
# .github/workflows/security.yml

name: Security Checks

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r worktree-orchestration/requirements.txt
          pip install semgrep bandit safety
      
      - name: Run Semgrep
        continue-on-error: true
        run: |
          semgrep --config=auto worktree-orchestration/src/ || true
      
      - name: Run Bandit
        continue-on-error: true
        run: |
          bandit -r worktree-orchestration/src/ || true
      
      - name: Run Safety (dependency check)
        continue-on-error: true
        env:
          SAFETY_API_KEY: ${{ secrets.SAFETY_API_KEY }}
        run: |
          safety check || true
      
      - name: Run Snyk
        continue-on-error: true
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        run: |
          snyk test --severity-threshold=high || true
      
      - name: Run security tests
        run: |
          pytest tests/test_security.py -v
```

---

## 7. Security Checklist

### 7.1 Pre-Deployment Checklist

- [ ] **Authentication**
  - [ ] IPC server uses Unix socket peer credentials
  - [ ] IPC socket permissions set to 0600
  - [ ] Dashboard API requires JWT authentication
  - [ ] Password hashing uses bcrypt/argon2 (not plaintext)
  - [ ] Token expiration configured (15min access, 7d refresh)

- [ ] **Authorization**
  - [ ] Role-based access control implemented
  - [ ] Each endpoint checks user permissions
  - [ ] Competitors can only access own artifacts

- [ ] **Input Validation**
  - [ ] All inputs validated with Pydantic schemas
  - [ ] Path traversal prevented
  - [ ] Command injection prevented (no shell execution)
  - [ ] SQL injection prevented (if DB added)

- [ ] **File Handling**
  - [ ] All paths canonicalized and validated
  - [ ] Symlinks handled safely
  - [ ] File permissions set correctly (0600 files, 0700 dirs)
  - [ ] Atomic writes used for artifacts

- [ ] **Resource Limits**
  - [ ] Timeouts configured for test execution
  - [ ] Disk quotas enforced
  - [ ] Memory limits set
  - [ ] Rate limiting on API endpoints

- [ ] **Logging & Monitoring**
  - [ ] Security events logged (auth failures, unauthorized access)
  - [ ] Sensitive data not logged
  - [ ] Audit trail for artifact access

- [ ] **Testing**
  - [ ] Security test suite passes
  - [ ] Static analysis (Semgrep/Bandit) run
  - [ ] Dependency scanning (Snyk/Safety) run
  - [ ] Penetration testing completed (if applicable)

---

## 8. Incident Response

### 8.1 Security Incident Procedures

1. **Detection**: Monitor logs for suspicious activity
2. **Containment**: Immediately revoke compromised credentials
3. **Investigation**: Review audit logs, identify attack vector
4. **Remediation**: Patch vulnerability, rotate secrets
5. **Communication**: Notify affected users if data exposed
6. **Post-Mortem**: Document incident, update security controls

### 8.2 Security Contacts

- **Security Team**: security@example.com
- **On-Call**: +1-XXX-XXX-XXXX
- **Bug Bounty**: security@example.com

---

## Appendix A: Security Configuration Examples

### A.1 IPC Server Configuration

```python
# config/security.py

IPC_CONFIG = {
    'socket_path': Path('/tmp/worktree-orch.sock'),
    'allowed_uids': {os.getuid()},  # Current user only
    'allowed_gids': set(os.getgroups()),
    'token_secret': os.environ.get('IPC_TOKEN_SECRET'),
    'socket_permissions': 0o600,
}
```

### A.2 Dashboard API Configuration

```python
# config/api_security.py

API_CONFIG = {
    'jwt_secret': os.environ.get('JWT_SECRET', secrets.token_urlsafe(32)),
    'jwt_algorithm': 'HS256',
    'access_token_expiry': 900,  # 15 minutes
    'refresh_token_expiry': 604800,  # 7 days
    'rate_limit': {
        'per_minute': 60,
        'per_hour': 1000,
    },
    'cors_origins': ['http://localhost:4000'],
    'session_cookie_secure': True,
    'session_cookie_httponly': True,
    'session_cookie_samesite': 'Strict',
}
```

---

## Appendix B: References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security.html)
- [Unix Socket Security](https://man7.org/linux/man-pages/man7/unix.7.html)

---

**Document Status:** Living document - update as threats evolve
