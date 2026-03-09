"""
API authentication and authorization for dashboard.
"""
import jwt
import secrets
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Callable
from functools import wraps


class APIAuthenticator:
    """JWT-based API authentication."""
    
    def __init__(self, secret_key: Optional[str] = None, algorithm: str = 'HS256'):
        """
        Args:
            secret_key: Secret key for JWT signing (default: from env or generate)
            algorithm: JWT algorithm (default: HS256)
        """
        self.secret_key = secret_key or os.environ.get('JWT_SECRET') or secrets.token_urlsafe(32)
        self.algorithm = algorithm
    
    def generate_token(self, user_id: str, roles: List[str],
                      expires_in: int = 900) -> str:
        """
        Generate JWT access token.
        
        Args:
            user_id: User identifier
            roles: List of user roles
            expires_in: Token expiration in seconds (default: 15 minutes)
        
        Returns:
            JWT token string
        """
        payload = {
            'user_id': user_id,
            'roles': roles,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow(),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def generate_refresh_token(self, user_id: str,
                              expires_in: int = 604800) -> str:
        """
        Generate refresh token.
        
        Args:
            user_id: User identifier
            expires_in: Token expiration in seconds (default: 7 days)
        
        Returns:
            Refresh token string
        """
        payload = {
            'user_id': user_id,
            'type': 'refresh',
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow(),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify JWT token.
        
        Args:
            token: JWT token string
        
        Returns:
            Decoded payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def require_auth(self, roles: Optional[List[str]] = None):
        """
        Decorator for requiring authentication.
        
        Usage (Flask):
            @app.route('/api/protected')
            @authenticator.require_auth(roles=['admin'])
            def protected_route():
                user_id = g.user_id
                return jsonify({'user': user_id})
        
        Usage (FastAPI):
            Use dependency injection instead
        """
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # This is a template - adapt to your web framework
                # For Flask:
                from flask import request, jsonify, g
                
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
                g.user_roles = payload.get('roles', [])
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator


class PasswordHasher:
    """Secure password hashing."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password using bcrypt.
        
        Args:
            password: Plaintext password
        
        Returns:
            Hashed password string
        """
        try:
            import bcrypt
            salt = bcrypt.gensalt()
            return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        except ImportError:
            # Fallback to hashlib (less secure, but works)
            import hashlib
            salt = secrets.token_hex(16)
            return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'),
                                     salt.encode('utf-8'), 100000).hex()
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            password: Plaintext password
            hashed: Hashed password
        
        Returns:
            True if password matches, False otherwise
        """
        try:
            import bcrypt
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except ImportError:
            # Fallback verification
            import hashlib
            parts = hashed.split(':')
            if len(parts) == 2:
                salt, hash_val = parts
                computed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'),
                                              salt.encode('utf-8'), 100000).hex()
                return secrets.compare_digest(computed, hash_val)
            return False
