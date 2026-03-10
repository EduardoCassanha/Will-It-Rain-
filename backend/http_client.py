import httpx

limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)

http_client = httpx.AsyncClient(
    limits=limits,
    timeout=httpx.Timeout(10.0, connect=5.0),
)
