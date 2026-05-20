import datetime
from typing import Optional
from pydantic import BaseModel


class TokenResponseModel(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime.datetime
    refresh_token: Optional[str] = None


class UserResponseModel(BaseModel):
    username: str
    email: str