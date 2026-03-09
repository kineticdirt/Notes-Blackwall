import jwt
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

EXEMPT_PATHS = {"/health", "/docs", "/openapi.json"}


class JWTAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, secret: str, algorithm: str = "HS256"):
        super().__init__(app)
        self.secret = secret
        self.algorithm = algorithm

    async def dispatch(self, request: Request, call_next):
        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

        token = auth_header.removeprefix("Bearer ").strip()
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            request.state.user = payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

        return await call_next(request)
