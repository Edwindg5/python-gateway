from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.core.auth import AuthError, authenticate
from app.core.config import settings
from app.proxy.forwarder import forward_request

router = APIRouter()

FORWARD_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]

RUTAS_PUBLICAS = {
    "/mobile/auth/login",
    "/mobile/auth/register",
    "/mobile/auth/refresh",
    "/web/api/v1/auth/login",
}


@router.api_route("/mobile/{path:path}", methods=FORWARD_METHODS)
async def proxy_mobile(path: str, request: Request):
    if f"/mobile/{path}" in RUTAS_PUBLICAS:
        return await forward_request(
            request=request,
            base_url=settings.API_MOBILE_URL,
            path=path,
        )

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
    if f"/web/{path}" in RUTAS_PUBLICAS:
        return await forward_request(
            request=request,
            base_url=settings.API_WEB_URL,
            path=path,
        )

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


@router.api_route("/pagos/{path:path}", methods=FORWARD_METHODS)
async def proxy_pagos(path: str, request: Request):
    if path == "admin" or path.startswith("admin/"):
        try:
            auth_context = authenticate(request.headers.get("authorization"))
        except AuthError as exc:
            return JSONResponse(status_code=401, content={"detail": str(exc)})

        return await forward_request(
            request=request,
            base_url=settings.PAGOS_URL,
            path=path,
            user_id=auth_context.user_id,
            rol=auth_context.rol,
        )

    return await forward_request(
        request=request,
        base_url=settings.PAGOS_URL,
        path=path,
    )
