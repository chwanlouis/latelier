import os
import logging
from logging.handlers import TimedRotatingFileHandler
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from module.core.tools.settings import app_settings


os.makedirs(app_settings.LOG_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(app_settings.LOG_DIR, app_settings.LOG_FILE_NAME)


logger = logging.getLogger(app_settings.APPLICATION_NAME)
logger.setLevel(logging.INFO)
logger.propagate = True


# Formatter
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)


console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)


file_handler = TimedRotatingFileHandler(
    LOG_FILE_PATH, when="midnight", interval=1, backupCount=7, encoding="utf-8"
)
file_handler.setFormatter(formatter)

# Avoid duplicate handlers
if not logger.hasHandlers():
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", None):
    target_logger = logging.getLogger(logger_name)
    if not any(isinstance(h, TimedRotatingFileHandler) for h in target_logger.handlers):
        target_logger.addHandler(file_handler)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log request headers and parameters
        logger.info(f"Request URL: {request.url}")
        logger.info(f"Request Method: {request.method}")
        logger.info(f"Request Headers: {request.headers}")
        logger.info(f"Request Query Params: {request.query_params}")

        response = await call_next(request)

        logger.info(f"Response Status Code: {response.status_code}")
        return response
