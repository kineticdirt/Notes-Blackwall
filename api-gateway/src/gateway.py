import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response

from .config import Settings, ROUTES
from .proxy import proxy_request, close_client
from .middleware.rate_limiter import RateLimitMiddleware
from .middleware.correlation import CorrelationIDMiddleware


settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_client()


app = FastAPI(
    title="Cequence BlackWall API Gateway",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(CorrelationIDMiddleware)
app.add_middleware(RateLimitMiddleware, rpm=settings.rate_limit_rpm)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "api-gateway"}


@app.api_route("/api/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def route(service: str, path: str, request: Request) -> Response:
    prefix = f"/api/{service}"
    route_attr = ROUTES.get(prefix)
    if not route_attr:
        return Response(
            content=f'{{"error": "Unknown service: {service}"}}',
            status_code=404,
            media_type="application/json",
        )
    upstream_base = getattr(settings, route_attr)
    return await proxy_request(request, upstream_base, prefix)


def main():
    uvicorn.run(
        "src.gateway:app",
        host=settings.gateway_host,
        port=settings.gateway_port,
        log_level=settings.log_level,
        reload=True,
    )


if __name__ == "__main__":
    main()
