from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    JWT_SECRET: str
    API_MOBILE_URL: str
    API_WEB_URL: str
    PAGOS_URL: str
    PORT: int = 8090
    CORS_ALLOWED_ORIGIN: str = "*"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("JWT_SECRET")
    @classmethod
    def jwt_secret_must_not_be_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError(
                "JWT_SECRET no puede estar vacio. Definilo como variable de entorno antes de arrancar el gateway."
            )
        return value


settings = Settings()
