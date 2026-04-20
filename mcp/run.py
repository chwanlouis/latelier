import uvicorn

from app.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        ssl_keyfile=settings.ssl_keyfile,
        ssl_certfile=settings.ssl_certfile,
        reload=settings.debug,
    )
