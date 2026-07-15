import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.middleware.logging import LoggingMiddleware
from app.proxy.router import router as proxy_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="kajve-gateway")

app.add_middleware(LoggingMiddleware)

# TODO: restringir a los dominios reales del frontend despues de la entrega.
# "*" es temporal para no bloquear el desarrollo/la demo final.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CORS_ALLOWED_ORIGIN],
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(proxy_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
