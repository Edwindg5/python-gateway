import logging

from fastapi import FastAPI

from app.middleware.logging import LoggingMiddleware
from app.proxy.router import router as proxy_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="kajve-gateway")

app.add_middleware(LoggingMiddleware)

app.include_router(proxy_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
