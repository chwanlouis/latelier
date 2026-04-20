from pydantic_settings import BaseSettings, field_validator
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "MCP Server"
    app_version: str = "0.1.0"
    debug: bool = False

    # HTTPS / SSL
    ssl_keyfile: str = "certs/key.pem"
    ssl_certfile: str = "certs/cert.pem"
    host: str = "0.0.0.0"
    port: int = 8443

    # JWT
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"

    # CORS — comma-separated list of allowed origins, e.g. "https://app.example.com"
    # Use "*" only for local development.
    cors_origins: str = "http://localhost:3000"

    @field_validator("secret_key")
    @classmethod
    def secret_key_must_be_set(cls, v: str) -> str:
        if not v:
            raise ValueError(
                "SECRET_KEY environment variable must be set to a strong random value"
            )
        return v

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
