from pydantic import BaseModel


class RegisterRequestModel(BaseModel):
    username: str
    email: str
    password: str
    organisation_id: int
