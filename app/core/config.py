from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_core.core_schema import FieldValidationInfo
from pydantic import PostgresDsn, field_validator, AnyHttpUrl
from typing import Any
from enum import Enum
import secrets


class ModeEnum(str, Enum):
    development = "development"
    production = "production"
    testing = "testing"


class Settings(BaseSettings):
    MODE: ModeEnum = ModeEnum.development
    # Database
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_NAME: str
    DATABASE_NAME_TEST: str
    # Token settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 1  # 1 hour
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 100  # 100 days
    ASYNC_DATABASE_URI: PostgresDsn | str = ""

    @field_validator("ASYNC_DATABASE_URI", mode="after")
    def assemble_db_connection(cls, v: str | None, info: FieldValidationInfo) -> Any:
        required_keys = ["DATABASE_USER", "DATABASE_PASSWORD", "DATABASE_HOST", "DATABASE_PORT", "DATABASE_NAME",
                         "DATABASE_NAME_TEST"]
        missing_keys = [key for key in required_keys if key not in info.data]
        if missing_keys:
            raise ValueError(f"Missing required settings: {', '.join(missing_keys)}")

        if isinstance(v, str):
            if v == "":
                return PostgresDsn.build(
                    scheme="postgresql+asyncpg",
                    username=info.data["DATABASE_USER"],
                    password=info.data["DATABASE_PASSWORD"],
                    host=info.data["DATABASE_HOST"],
                    port=info.data["DATABASE_PORT"],
                    path=info.data["DATABASE_NAME"] if info.data['MODE'] == ModeEnum.development else info.data[
                        "DATABASE_NAME_TEST"],
                )
        return v

    SECRET_KEY: str = secrets.token_urlsafe(32)
    ENCRYPT_KEY: str = secrets.token_urlsafe(32)
    BACKEND_CORS_ORIGINS: list[str] | list[AnyHttpUrl] | None = None

    @field_validator("BACKEND_CORS_ORIGINS")
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


def get_settings() -> Settings:
    """Returns the settings instance, loading environment variables first."""
    return Settings(_env_file=".env", _env_file_encoding="utf-8")


settings = Settings()
