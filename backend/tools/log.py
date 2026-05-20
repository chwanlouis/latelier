import os
import logging
from logging.handlers import TimedRotatingFileHandler
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "gma_opendoor_backend.log")


logger = logging.getLogger("gma_opendoor")
logger.setLevel(logging.INFO)


# Formatter
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Timed rotating file handler (new file every midnight, keep 7 days)
file_handler = TimedRotatingFileHandler(
    LOG_FILE, when="midnight", interval=1, backupCount=7, encoding="utf-8"
)
file_handler.setFormatter(formatter)

# Avoid duplicate handlers
if not logger.hasHandlers():
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


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