from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.core.auth import AuthError, authenticate
from app.core.config import settings
from app.proxy.forwarder import forward_request

router = APIRouter()

FORWARD_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]


@router.api_route("/mobile/{path:path}", methods=FORWARD_METHODS)
async def proxy_mobile(path: str, request: Request):
    try:
        auth_context = authenticate(request.headers.get("authorization"))
    except AuthError as exc:
        return JSONResponse(status_code=401, content={"detail": str(exc)})

    return await forward_request(
        request=request,
        base_url=settings.API_MOBILE_URL,
        path=path,
        user_id=auth_context.user_id,
        rol=auth_context.rol,
    )


@router.api_route("/web/{path:path}", methods=FORWARD_METHODS)
async def proxy_web(path: str, request: Request):
    try:
        auth_context = authenticate(request.headers.get("authorization"))
    except AuthError as exc:
        return JSONResponse(status_code=401, content={"detail": str(exc)})

    return await forward_request(
        request=request,
        base_url=settings.API_WEB_URL,
        path=path,
        user_id=auth_context.user_id,
        rol=auth_context.rol,
    )
