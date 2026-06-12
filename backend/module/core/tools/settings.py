import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    APPLICATION_NAME: str = "L'atelier"
    VERSION: str = "0.0.1b"
    ENV: str = Field("dev", env="ENV")
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent

    SECRET_KEY: str = Field("dev-secret-change-me", env="SECRET_KEY")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS")

    INIT_ADMIN_USERNAME: str = Field("", env="INIT_ADMIN_USERNAME")
    INIT_ADMIN_PASSWORD: str = Field("", env="INIT_ADMIN_PASSWORD")
    INIT_ADMIN_EMAIL: str = Field("", env="INIT_ADMIN_EMAIL")
    BACKEND_PORT: int = Field(8000, env="BACKEND_PORT")
    FRONTEND_PORT: int = Field(3000, env="FRONTEND_PORT")

    REDIS_URL: Optional[str] = Field(None, env="REDIS_URL")
    REDIS_PASSWORD: Optional[str] = Field(None, env="REDIS_PASSWORD")
    REDIS_HOST: str = Field("", env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")
    REDIS_DB: int = Field(0, env="REDIS_DB")

    DATABASE_URL: Optional[str] = Field(None, env="DATABASE_URL")
    POSTGRES_USER: str = Field("", env="POSTGRES_USER")
    POSTGRES_PASSWORD: Optional[str] = Field("", env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field("", env="POSTGRES_DB")
    POSTGRES_HOST: str = Field("", env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(5432, env="POSTGRES_PORT")

    SQLITE_FILE_NAME: str = "fallback_local.db"

    NEO4J_HOST: str = Field("", env="NEO4J_HOST")
    NEO4J_PORT: int = Field(0, env="NEO4J_PORT")
    NEO4J_USERNAME: str = Field("", env="NEO4J_USERNAME")
    NEO4J_PASSWORD: str = Field("", env="NEO4J_PASSWORD")

    CLOUD_BASE_URL: str = Field("", env="CLOUD_BASE_URL")
    TOKEN_TTL: int = Field(120, env="TOKEN_TTL")

    LOG_DIR: Path = BASE_DIR / "logs"
    LOG_FILE_NAME: str = "latelier-backend.log"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="forbid",
    )

    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def _build_redis_url(cls, v, info):
        if v:
            return v
        data = info.data or {}
        pwd = data.get("REDIS_PASSWORD") or os.getenv("REDIS_PASSWORD")
        host = data.get("REDIS_HOST") or os.getenv("REDIS_HOST", "redis")
        port = str(data.get("REDIS_PORT") or os.getenv("REDIS_PORT", 6379))
        db = str(data.get("REDIS_DB") or os.getenv("REDIS_DB", 0))

        if pwd:
            return f"redis://:{pwd}@{host}:{port}/{db}"
        return f"redis://{host}:{port}/{db}"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _build_database_url(cls, v, info):
        if v:
            return v
        data = info.data or {}
        user = data.get("POSTGRES_USER") or os.getenv("POSTGRES_USER")
        pwd = data.get("POSTGRES_PASSWORD") or os.getenv("POSTGRES_PASSWORD")
        db = data.get("POSTGRES_DB") or os.getenv("POSTGRES_DB")
        host = data.get("POSTGRES_HOST") or os.getenv("POSTGRES_HOST")
        port = data.get("POSTGRES_PORT") or os.getenv("POSTGRES_PORT")
        if pwd:
            return f"postgresql+asyncpg://{user}:{pwd}@{host}:{port}/{db}"
        return f"postgresql+asyncpg://{user}@{host}:{port}/{db}"

    @field_validator("SECRET_KEY")
    @classmethod
    def _validate_secret_key(cls, v, info):
        env = info.data.get("ENV") or os.getenv("ENV", "development")
        if env == "production" and v in (None, "", "dev-secret-change-me"):
            raise ValueError("SECRET_KEY must be set to a secure value in production")
        return v

    @property
    def FALLBACK_DATABASE_URL(self) -> str:
        abs_db_path = self.BASE_DIR / self.SQLITE_FILE_NAME
        return f"sqlite+aiosqlite:///{abs_db_path.as_posix()}"

    @property
    def NEO4J_URL(self) -> str:
        if self.NEO4J_PASSWORD:
            return f"bolt://{self.NEO4J_USERNAME}:{self.NEO4J_PASSWORD}@{self.NEO4J_HOST}:{self.NEO4J_PORT}"
        return f"bolt://{self.NEO4J_USERNAME}@{self.NEO4J_HOST}:{self.NEO4J_PORT}"


app_settings = Settings()
