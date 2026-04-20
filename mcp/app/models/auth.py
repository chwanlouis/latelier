from pydantic import BaseModel


class TokenRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInDB(BaseModel):
    username: str
    hashed_password: str
    disabled: bool = False
