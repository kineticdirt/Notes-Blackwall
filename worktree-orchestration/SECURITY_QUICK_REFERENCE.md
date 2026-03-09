# Security Quick Reference

**Quick implementation guide for secure-by-default worktree orchestration.**

---

## 1. IPC Server Setup (Unix Socket)

### Basic Setup

```python
from pathlib import Path
from src.security.ipc_auth import IPCAuthenticator, IPCAuthorizer
from src.ipc.server import IPCServer

# Create authenticator (allows current user only by default)
authenticator = IPCAuthenticator()

# Create authorizer (current user = admin by default)
authorizer = IPCAuthorizer()

# Define handlers
def handle_start_round(params, uid=None):
    round_num = params['round_num']
    # ... your logic
    return {'status': 'started', 'round_num': round_num}

handlers = {
    'start_round': handle_start_round,
    # ... other handlers
}

# Start server
server = IPCServer(
    socket_path=Path('/tmp/worktree-orch.sock'),
    authenticator=authenticator,
    authorizer=authorizer,
    handlers=handlers
)
server.start()
```

### Secure Socket Permissions

```python
# Socket is automatically created with 0600 permissions
# Only owner can read/write
```

---

## 2. Dashboard API Setup (Port 4000)

### Flask Example

```python
from flask import Flask, request, jsonify, g
from src.security.api_auth import APIAuthenticator, PasswordHasher

app = Flask(__name__)
authenticator = APIAuthenticator()

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    
    # Verify credentials (implement your user lookup)
    user = get_user(username)
    if not user or not PasswordHasher.verify_password(password, user.password_hash):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Generate tokens
    access_token = authenticator.generate_token(user.id, user.roles)
    refresh_token = authenticator.generate_refresh_token(user.id)
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
    })

@app.route('/api/rounds', methods=['GET'])
@authenticator.require_auth(roles=['admin', 'viewer'])
def list_rounds():
    user_id = g.user_id
    # ... your logic
    return jsonify({'rounds': []})
```

---

## 3. Input Validation

### Using Schemas

```python
from src.security.schemas import (
    SubmitSolutionRequest,
    PathParam,
    CompetitorIDParam,
)

# Validate request
try:
    request = SubmitSolutionRequest(**request_data)
except ValueError as e:
    return {'error': str(e)}, 400

# Use validated data
competitor_id = request.competitor_id
round_num = request.round_num
solution_path = request.solution_path.resolve(base_dir)
```

---

## 4. Safe File Handling

### Path Validation

```python
from src.security.file_handling import SafePathHandler
from pathlib import Path

base_dir = Path('/safe/base')

# Validate and resolve path
try:
    resolved = SafePathHandler.validate_and_resolve(
        'subdir/file.txt',
        base_dir,
        follow_symlinks=False
    )
except ValueError as e:
    # Handle error
    pass
```

### Atomic Writes

```python
from src.security.file_handling import SafePathHandler

# Atomic write with safe permissions
content = b'Hello, World!'
SafePathHandler.safe_write(file_path, content, mode=0o600)
```

---

## 5. Security Testing

### Run Security Checks

```bash
# Make script executable
chmod +x scripts/security_check.py

# Run all checks (graceful fallbacks if tools missing)
python scripts/security_check.py
```

### Run Security Tests

```bash
pytest tests/test_security.py -v
```

---

## 6. Environment Variables

### Required for Production

```bash
# JWT secret (generate: python -c "import secrets; print(secrets.token_urlsafe(32))")
export JWT_SECRET="your-secret-key-here"

# Optional: IPC token secret (for multi-user IPC)
export IPC_TOKEN_SECRET="your-ipc-secret"

# Optional: Security scanning tokens
export SNYK_TOKEN="your-snyk-token"
export SAFETY_API_KEY="your-safety-key"
```

---

## 7. Common Security Patterns

### Command Execution (NO SHELL)

```python
# ✅ CORRECT: No shell, explicit args
subprocess.run(['python', 'test.py'], shell=False)

# ❌ WRONG: Shell execution (vulnerable to injection)
subprocess.run(f'python test.py {user_input}', shell=True)
```

### Path Handling

```python
# ✅ CORRECT: Validate and resolve
path = SafePathHandler.validate_and_resolve(user_path, base_dir)

# ❌ WRONG: Direct path usage
path = base_dir / user_path  # Vulnerable to traversal
```

### Authentication

```python
# ✅ CORRECT: Check authentication before authorization
peer_info = authenticator.authenticate_peer(sock)
if not peer_info:
    return error('Unauthorized')

if not authorizer.authorize(peer_info['uid'], operation):
    return error('Forbidden')

# ❌ WRONG: Skip authentication
# Directly execute operation
```

---

## 8. Security Checklist

Before deploying:

- [ ] IPC socket permissions set to 0600
- [ ] JWT secret configured (not default)
- [ ] All inputs validated with schemas
- [ ] Path traversal prevented
- [ ] Command injection prevented (no shell)
- [ ] File permissions set correctly
- [ ] Security tests pass
- [ ] Static analysis run (Semgrep/Bandit)
- [ ] Dependencies scanned (Snyk/Safety)

---

## 9. Quick Fixes

### Fix Missing Import

```python
# If hashlib missing in arena.py
import hashlib
```

### Fix Socket Permissions

```python
# Ensure socket has correct permissions
os.chmod(socket_path, 0o600)
```

### Fix Path Validation

```python
# Always use SafePathHandler
from src.security.file_handling import SafePathHandler
path = SafePathHandler.validate_and_resolve(user_path, base_dir)
```

---

## 10. Getting Help

- **Full Documentation**: See `SECURITY.md`
- **Security Issues**: security@example.com
- **Threat Model**: See `SECURITY.md` Section 1

---

**Last Updated:** 2026-01-30
