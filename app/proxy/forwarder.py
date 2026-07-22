import json
import logging
from urllib.parse import quote

import httpx
from fastapi import Request, Response

logger = logging.getLogger("kajve_gateway")

TIMEOUT_SECONDS = 10.0

# Headers de la respuesta del backend que no hay que reenviar tal cual:
# httpx ya descomprime el body al leer .content, asi que dejar
# content-encoding/content-length/transfer-encoding originales rompe al
# cliente (intentaria decodificar un body que ya viene decodificado).
EXCLUDED_RESPONSE_HEADERS = {"content-encoding", "content-length", "transfer-encoding", "connection"}


def _is_valid_path(path: str) -> bool:
    return ".." not in path and path.isprintable()


def _inject_user_id_into_body(body: bytes, user_id: str) -> bytes:
    """Fuerza "id_usuario" en el body JSON, pisando lo que haya mandado el cliente.

    Si el body esta vacio (ej. GET /dispositivos/{id}) o no es un objeto JSON,
    se devuelve tal cual: hay endpoints de ML sin body y no hay nada que inyectar.
    """
    if not body:
        return body

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return body

    if not isinstance(data, dict):
        return body

    data["id_usuario"] = user_id
    return json.dumps(data).encode("utf-8")


async def forward_request(
    request: Request,
    base_url: str,
    path: str,
    user_id: str | None = None,
    rol: str | None = None,
    internal_api_key: str | None = None,
    inject_user_id_in_body: bool = False,
) -> Response:
    if not _is_valid_path(path):
        return Response(
            content='{"detail": "Ruta inválida"}',
            status_code=400,
            media_type="application/json",
        )

    target_url = f"{base_url.rstrip('/')}/{quote(path, safe='/')}"

    headers = dict(request.headers)
    headers.pop("host", None)
    if user_id is not None:
        headers["X-User-Id"] = user_id
    if rol is not None:
        headers["X-Role"] = rol
    if internal_api_key is not None:
        headers["X-Internal-Api-Key"] = internal_api_key

    body = await request.body()

    if inject_user_id_in_body and user_id is not None:
        body = _inject_user_id_into_body(body, user_id)
        # el body pudo haber cambiado de tamano: si dejamos el content-length
        # original, el backend puede truncar o rechazar el request.
        headers.pop("content-length", None)

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
            content='{"detail": "El servicio no está disponible en este momento. Intenta de nuevo más tarde."}',
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
