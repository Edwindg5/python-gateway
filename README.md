# kajve-gateway

Punto único de entrada que valida el JWT de cada request antes de reenviarla al backend correcto (`api-mobile` o `api-web`). No persiste nada.

## Variables de entorno

Copiar `.env.example` a `.env` y completar:

| Variable | Descripción |
|---|---|
| `JWT_SECRET` | Secreto usado para validar la firma HS256 de los JWT (mobile y web). No puede estar vacío. |
| `API_MOBILE_URL` | URL base del backend `api-mobile`. Todo lo que llega a `/mobile/*` se reenvía ahí. |
| `API_WEB_URL` | URL base del backend `api-web`. Todo lo que llega a `/web/*` se reenvía ahí. |
| `PORT` | Puerto en el que escucha el gateway. |

## Correr local

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash / PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

cp .env.example .env   # completar JWT_SECRET, API_MOBILE_URL, API_WEB_URL

uvicorn app.main:app --reload --port 8090
```

## Probar

```bash
curl http://localhost:8090/health

curl -H "Authorization: Bearer <token>" http://localhost:8090/mobile/perfil
curl -H "Authorization: Bearer <token>" http://localhost:8090/web/algun-endpoint
```

## Tests

```bash
pytest
```

## Docker

```bash
docker build -t kajve-gateway .
docker run --env-file .env -p 8090:8090 kajve-gateway
```
