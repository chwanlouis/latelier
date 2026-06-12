import jwt
import uuid
import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import (
    OAuth2PasswordRequestForm, OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
)
from module.core.tools.settings import app_settings
from module.core.tools.login import (
    hash_password,
    verify_password,
    decode_token,
    create_access_token,
    create_refresh_token,
)
from module.core.tools.redistools import async_redis_manager
from module.core.tools.log import logger
from module.core.tools.constants import api_constants
from module.core.model.request.auth import RegisterRequestModel
from module.core.model.response.auth import UserResponseModel, TokenResponseModel
from module.core.model.sql.user import UserSQLModel, UserGroupEnum
from module.core.repository.users import user_repository

security = HTTPBearer()
auth_router = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{api_constants.V1_PREFIX}/auth/token")


def get_user_group(payload: dict) -> Optional[str]:
    return payload.get("user_group") or payload.get("user_level")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Invalid authorization")
    try:
        token = credentials.credentials
        payload = jwt.decode(token, app_settings.SECRET_KEY, algorithms=[app_settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


class PermissionChecker:
    def __init__(self, req_admin: bool = False):
        self.req_admin = req_admin

    async def __call__(self, current_user: dict = Depends(get_current_user)) -> dict:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        user_level = get_user_group(current_user)
        user_id = current_user.get("user_id")

        logger.info(f"User {user_id} ({user_level}) authenticated successfully.")

        if self.req_admin and user_level != UserGroupEnum.admin.value:
            logger.warning(f"Access denied for User {user_id}: Admin role required.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin role required"
            )

        return current_user


async def _issue_and_store_refresh_token(payload: dict) -> str:
    refresh_payload = payload.copy()
    refresh_payload["jti"] = str(uuid.uuid4())
    refresh_token = create_refresh_token(refresh_payload)
    decoded = decode_token(refresh_token)
    jti = decoded.get("jti")
    if not jti:
        raise RuntimeError("Refresh token missing jti")
    key = f"refresh:{jti}"
    ttl_seconds = int(app_settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60)
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
    user: UserSQLModel = await user_repository.get_user_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")

    token_payload = {
        "user_id": user.id,
        "user_group": user.user_group.value
    }

    access_expires = datetime.timedelta(minutes=app_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(token_payload, expires_delta=access_expires)
    refresh_token = await _issue_and_store_refresh_token(token_payload)

    return TokenResponseModel(
        access_token=access_token,
        expires_at=(datetime.datetime.now(datetime.timezone.utc) + access_expires),
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

    token_payload = {
        "user_id": str(payload["user_id"]),
        "user_group": get_user_group(payload)
    }

    access_expires = datetime.timedelta(minutes=app_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(token_payload, expires_delta=access_expires)

    old_jti = payload.get("jti")
    if old_jti:
        await async_redis_manager.set(f"refresh:{old_jti}", "", ttl=1)

    new_refresh = await _issue_and_store_refresh_token(token_payload)

    return TokenResponseModel(
        access_token=access_token,
        expires_at=(datetime.datetime.now(datetime.timezone.utc) + access_expires),
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
async def read_me(current_user: dict = Depends(PermissionChecker())):
    if current_user.get("user_id", None) is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user_model: Optional[UserSQLModel] = await user_repository.get_user_by_id(current_user["user_id"])
    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponseModel(
        username=user_model.username,
        email=user_model.email
    )


@auth_router.post("/register", response_model=UserResponseModel,
                  dependencies=[Depends(PermissionChecker())])
async def register_user(payload: RegisterRequestModel, request: Request):
    existing = await user_repository.get_user_by_username(payload.username)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username exists")

    user = UserSQLModel(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        is_active=False,
        user_group=UserGroupEnum.basic
    )

    try:
        created: UserSQLModel = await user_repository.insert_user(user)
    except HTTPException as e:
        raise e
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="failed to create user") from exc
