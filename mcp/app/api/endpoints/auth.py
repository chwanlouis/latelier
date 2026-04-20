from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.jwt import create_access_token, hash_password, verify_password
from app.models.auth import Token

router = APIRouter(prefix="/auth", tags=["auth"])

# In-memory user store for demonstration — replace with DB lookup in production
_FAKE_USERS_DB: dict[str, str] = {
    "admin": hash_password("admin123"),
}


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    hashed = _FAKE_USERS_DB.get(form_data.username)
    if not hashed or not verify_password(form_data.password, hashed):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token({"sub": form_data.username})
    return Token(access_token=token)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(username: str, password: str):
    if username in _FAKE_USERS_DB:
        raise HTTPException(status_code=400, detail="Username already registered")
    _FAKE_USERS_DB[username] = hash_password(password)
    return {"message": "User created", "username": username}
