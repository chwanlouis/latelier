import jwt
import uuid
import datetime
from typing import Optional, List
from functools import wraps
from fastapi import APIRouter, Depends, HTTPException, Request, Security, status
from fastapi.security import (
    OAuth2PasswordRequestForm, OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
)
from utils.settings import settings
from utils.login import (
    hash_password,
    verify_password,
    decode_token,
    create_access_token,
    create_refresh_token,
)
from utils.redistools import async_redis_manager
from utils.log import logger
from model.request.auth import RegisterRequestModel
from model.response.auth import UserResponseModel, TokenResponseModel
from model.sql.user import UsersSQLModel, UserLevelEnum
from repository.auth.users import UserRepository


security = HTTPBearer()
auth_router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Invalid authorization")
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def has_permission(user_id: int, tag: str) -> bool:
    user_permitted_tags: List[str] = await UserRepository.get_all_permitted_tags_by_user_id(user_id)
    user_permitted_tags = [attr[0] for attr in user_permitted_tags]
    logger.info(f"User {user_id} has permissions: {user_permitted_tags}")
    logger.info(f"Checking if user {user_id} has permission for tag '{tag}'")
    logger.info(tag in user_permitted_tags)
    return tag in user_permitted_tags


def permission_required(tag: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get("request")
            if not request:
                raise HTTPException(status_code=400, detail="Request object is required")

            logger.info("*" * 100)
            user = kwargs.get("current_user") or get_current_user()
            logger.info(user)
            user_level = user.get("user_level")
            logger.info(user_level)

            if user_level == UserLevelEnum.SUPER_ADMIN.value or user_level == UserLevelEnum.ADMIN.value:
                return await func(*args, **kwargs)
            elif user_level == UserLevelEnum.BASIC.value:
                if not await has_permission(int(user["user_id"]), tag):
                    raise HTTPException(status_code=403, detail="Permission denied")
            return await func(*args, **kwargs)
        return wrapper
    return decorator


async def _issue_and_store_refresh_token(payload: dict) -> str:
    refresh_payload = payload.copy()
    refresh_payload["jti"] = str(uuid.uuid4())
    refresh_token = create_refresh_token(refresh_payload)
    decoded = decode_token(refresh_token)
    jti = decoded.get("jti")
    if not jti:
        raise RuntimeError("Refresh token missing jti")
    key = f"refresh:{jti}"
    ttl_seconds = int(settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60)
    await async_redis_manager.set(key, refresh_token, ttl=ttl_seconds)
    return refresh_token


async def _validate_refresh_token_in_redis(decoded_payload: dict, presented_token: str) -> None:
    jti = decoded_payload.get("jti")
    if not jti:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token (missing jti)")
    key = f"refresh:{jti}"
    stored = await async_redis_manager.get(key)
    if not stored:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked or unknown")
    if stored != presented_token:
        await async_redis_manager.set(key, "", ttl=1)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token invalid or reused")


@auth_router.post("/token", response_model=TokenResponseModel)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user: UsersSQLModel = await UserRepository.get_user_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    token_payload = {"user_id": str(user.id), "user_level": user.user_level}
    access_expires = datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(token_payload, expires_delta=access_expires)
    refresh_token = await _issue_and_store_refresh_token(token_payload)
    return TokenResponseModel(
        access_token=access_token,
        expires_at=(datetime.datetime.utcnow() + access_expires),
        refresh_token=refresh_token,
    )


@auth_router.post("/refresh", response_model=TokenResponseModel)
async def refresh_token(refresh_token: str):
    try:
        payload = decode_token(refresh_token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    if payload.get("typ") != "refresh":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not a refresh token")
    await _validate_refresh_token_in_redis(payload, refresh_token)
    token_payload = {"user_id": str(payload["user_id"]), "user_level": payload["user_level"]}
    access_expires = datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(token_payload, expires_delta=access_expires)
    old_jti = payload.get("jti")
    if old_jti:
        await async_redis_manager.set(f"refresh:{old_jti}", "", ttl=1)
    new_refresh = await _issue_and_store_refresh_token(token_payload)
    return TokenResponseModel(
        access_token=access_token,
        expires_at=(datetime.datetime.utcnow() + access_expires),
        refresh_token=new_refresh,
    )


@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(refresh_token: Optional[str] = None):
    if not refresh_token:
        return {}
    try:
        payload = decode_token(refresh_token)
    except Exception:
        return {}
    jti = payload.get("jti")
    if jti:
        await async_redis_manager.set(f"refresh:{jti}", "", ttl=1)
    return {}


@auth_router.get("/me", response_model=UserResponseModel)
async def read_me(current_user = Depends(get_current_user)):
    logger.info(current_user)
    return UserResponseModel(
        username=current_user["username"]
    )


@auth_router.post("/register", response_model=UserResponseModel)
async def register_user(payload: RegisterRequestModel, request: Request, dependency=Depends(permission_required)):
    existing = await UserRepository.get_user_by_username(payload.username)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username exists")
    user = UsersSQLModel(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        is_active=False,
        organisation_id=payload.organisation_id,
        user_level=UserLevelEnum.BASIC.value
    )
    try:
        created: UsersSQLModel = await UserRepository.insert_user(user)
    except HTTPException as e:
        raise e
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="failed to create user") from exc
    return UserResponseModel(
        username=payload.username,
        email=payload.email
    )
