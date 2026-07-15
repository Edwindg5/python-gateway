from dataclasses import dataclass

import jwt

from app.core.keys import get_secret

ALGORITHM = "HS256"


class AuthError(Exception):
    """Se lanza cuando el token es invalido, expiro, o su forma no se reconoce."""


@dataclass
class AuthContext:
    origen: str
    user_id: str
    rol: str


def _extract_bearer_token(authorization_header: str | None) -> str:
    if not authorization_header:
        raise AuthError("Falta el header Authorization")

    parts = authorization_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthError("El header Authorization debe tener el formato 'Bearer <token>'")

    return parts[1]


def _resolve_origin(payload: dict) -> str:
    is_web = "sub" in payload and "role" in payload
    is_mobile = "user_id" in payload and "rol" in payload

    if is_web and is_mobile:
        raise AuthError("Token con claims mezcladas de web y mobile, formato invalido")
    if is_web:
        return "web"
    if is_mobile:
        return "mobile"
    raise AuthError("Token con formato de payload desconocido")


def authenticate(authorization_header: str | None) -> AuthContext:
    token = _extract_bearer_token(authorization_header)

    try:
        payload = jwt.decode(token, get_secret(), algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise AuthError("Token expirado")
    except jwt.InvalidTokenError:
        raise AuthError("Token invalido")

    origen = _resolve_origin(payload)

    if origen == "web":
        user_id = payload["sub"]
        rol = payload["role"]
    else:
        user_id = payload["user_id"]
        rol = payload["rol"]

    return AuthContext(origen=origen, user_id=str(user_id), rol=str(rol))
