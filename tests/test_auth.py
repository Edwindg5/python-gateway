import os
import time

os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("API_MOBILE_URL", "http://api-mobile:8080")
os.environ.setdefault("API_WEB_URL", "http://api-web:8000")

import jwt
import pytest

from app.core.auth import AuthError, authenticate

SECRET = os.environ["JWT_SECRET"]


def _make_token(payload: dict, secret: str = SECRET, exp_delta_seconds: int = 3600) -> str:
    data = {**payload, "exp": int(time.time()) + exp_delta_seconds}
    return jwt.encode(data, secret, algorithm="HS256")


def test_valid_web_token():
    token = _make_token({"sub": "user-1", "role": "admin"})

    context = authenticate(f"Bearer {token}")

    assert context.origen == "web"
    assert context.user_id == "user-1"
    assert context.rol == "admin"


def test_valid_mobile_token():
    token = _make_token({"user_id": 42, "rol": "operario"})

    context = authenticate(f"Bearer {token}")

    assert context.origen == "mobile"
    assert context.user_id == "42"
    assert context.rol == "operario"


def test_invalid_signature():
    token = _make_token({"sub": "user-1", "role": "admin"}, secret="otro-secreto")

    with pytest.raises(AuthError):
        authenticate(f"Bearer {token}")


def test_expired_token():
    token = _make_token({"sub": "user-1", "role": "admin"}, exp_delta_seconds=-3600)

    with pytest.raises(AuthError):
        authenticate(f"Bearer {token}")


def test_mixed_claims_rejected():
    token = _make_token({"sub": "user-1", "role": "admin", "user_id": 1, "rol": "operario"})

    with pytest.raises(AuthError):
        authenticate(f"Bearer {token}")


def test_unknown_shape_rejected():
    token = _make_token({"foo": "bar"})

    with pytest.raises(AuthError):
        authenticate(f"Bearer {token}")
