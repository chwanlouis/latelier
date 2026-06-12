from fastapi import APIRouter, Depends, Request
from module.core.router.auth_router import PermissionChecker


admin_service_router = APIRouter(
    prefix="/admin",
    tags=["AdminSystem"],
    dependencies=[Depends(PermissionChecker(req_admin=True))]
)


@admin_service_router.get(path="/healthCheck", tags=["Health"])
async def health_check(request: Request):
    return {"status": "ok", "message": "Service is healthy"}
