from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    JWT_SECRET: str
    API_MOBILE_URL: str
    API_WEB_URL: str
    PAGOS_URL: str
    PORT: int = 8090
    CORS_ALLOWED_ORIGINS: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("JWT_SECRET")
    @classmethod
    def jwt_secret_must_not_be_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError(
                "JWT_SECRET no puede estar vacio. Definilo como variable de entorno antes de arrancar el gateway."
            )
        return value

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()]


settings = Settings()
