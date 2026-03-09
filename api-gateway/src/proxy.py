import httpx
from fastapi import Request, Response

_client: httpx.AsyncClient | None = None


async def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
    return _client


async def close_client():
    global _client
    if _client and not _client.is_closed:
        await _client.aclose()
        _client = None


async def proxy_request(request: Request, upstream_base: str, strip_prefix: str) -> Response:
    client = await get_client()

    path = request.url.path.removeprefix(strip_prefix)
    query = str(request.url.query)
    target = f"{upstream_base.rstrip('/')}{path}"
    if query:
        target += f"?{query}"

    headers = dict(request.headers)
    headers.pop("host", None)
    if hasattr(request.state, "correlation_id"):
        headers["X-Correlation-ID"] = request.state.correlation_id

    body = await request.body()

    try:
        upstream_resp = await client.request(
            method=request.method,
            url=target,
            headers=headers,
            content=body,
        )
    except httpx.ConnectError:
        return Response(
            content=f'{{"error": "Service unavailable", "upstream": "{strip_prefix}"}}',
            status_code=503,
            media_type="application/json",
        )

    return Response(
        content=upstream_resp.content,
        status_code=upstream_resp.status_code,
        headers=dict(upstream_resp.headers),
    )
