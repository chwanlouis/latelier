from pydantic import BaseModel


class RegisterRequestModel(BaseModel):
    username: str
    password: str