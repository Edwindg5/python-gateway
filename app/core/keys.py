from app.core.config import settings


def get_secret() -> str:
    """Devuelve el secreto activo usado para validar JWT.

    Hoy solo existe un secreto (JWT_SECRET). Esta funcion es a proposito el
    unico punto de acceso al secreto: si en el futuro hay que soportar mas
    de uno (rotacion, distintos emisores, etc.), la logica para elegir cual
    usar se agrega aca adentro sin tener que tocar auth.py.
    """
    return settings.JWT_SECRET
