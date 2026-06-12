import jwt
import datetime
from typing import Optional
from fastapi import HTTPException, status
from passlib.hash import argon2
from passlib.context import CryptContext
from module.core.tools.settings import app_settings
from module.core.tools.log import logger


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("password must not be empty")
    logger.info(f"Password length in bytes: {len(password.encode('utf-8'))}")
    return argon2.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    try:
        return argon2.verify(plain_password, hashed_password)
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    to_encode = data.copy()
    now = datetime.datetime.utcnow()
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + datetime.timedelta(minutes=app_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": now})
    token = jwt.encode(to_encode, app_settings.SECRET_KEY, algorithm=app_settings.ALGORITHM)
    return token


def create_refresh_token(data: dict, expires_days: int = app_settings.REFRESH_TOKEN_EXPIRE_DAYS):
    to_encode = data.copy()
    now = datetime.datetime.utcnow()
    expire = now + datetime.timedelta(days=expires_days)
    to_encode.update({"exp": expire, "iat": now, "typ": "refresh"})
    token = jwt.encode(to_encode, app_settings.SECRET_KEY, algorithm=app_settings.ALGORITHM)
    return token


def decode_token(token: str):
    try:
        payload = jwt.decode(token, app_settings.SECRET_KEY, algorithms=[app_settings.ALGORITHM])
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
