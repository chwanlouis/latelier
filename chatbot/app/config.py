from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "Chatbot"
    app_version: str = "0.1.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # OpenAI (LLM backend)
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # MCP Server
    mcp_base_url: str = "https://localhost:8443"
    mcp_username: str = "admin"
    mcp_password: str = "admin123"
    # Path to CA bundle / server cert for TLS verification.
    # Set to "false" only in local development with self-signed certs.
    mcp_ssl_verify: str = "true"

    # Neo4j (direct connection for graph lookups)
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"

    # CORS — comma-separated list of allowed origins
    cors_origins: str = "http://localhost:3000"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
