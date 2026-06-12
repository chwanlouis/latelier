from pydantic import BaseModel


class ApiVersionSettings(BaseModel):
    V1_PREFIX: str = "/api/v1"


api_constants = ApiVersionSettings()
