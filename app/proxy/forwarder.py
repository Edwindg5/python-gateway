import logging

import httpx
from fastapi import Request, Response

logger = logging.getLogger("kajve_gateway")

TIMEOUT_SECONDS = 10.0

# Headers de la respuesta del backend que no hay que reenviar tal cual:
# httpx ya descomprime el body al leer .content, asi que dejar
# content-encoding/content-length/transfer-encoding originales rompe al
# cliente (intentaria decodificar un body que ya viene decodificado).
EXCLUDED_RESPONSE_HEADERS = {"content-encoding", "content-length", "transfer-encoding", "connection"}


async def forward_request(
    request: Request,
    base_url: str,
    path: str,
    user_id: str | None = None,
    rol: str | None = None,
) -> Response:
    target_url = f"{base_url.rstrip('/')}/{path}"

    headers = dict(request.headers)
    headers.pop("host", None)
    if user_id is not None:
        headers["X-User-Id"] = user_id
    if rol is not None:
        headers["X-Role"] = rol

    body = await request.body()

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            backend_response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=request.query_params,
                content=body,
            )
    except (httpx.TimeoutException, httpx.ConnectError) as exc:
        logger.warning("Backend no respondio: %s %s -> %s", request.method, target_url, exc)
        return Response(
            content=f'{{"detail": "El backend no respondio: {base_url}"}}',
            status_code=502,
            media_type="application/json",
        )

    response_headers = {
        key: value
        for key, value in backend_response.headers.items()
        if key.lower() not in EXCLUDED_RESPONSE_HEADERS
    }

    return Response(
        content=backend_response.content,
        status_code=backend_response.status_code,
        headers=response_headers,
    )
