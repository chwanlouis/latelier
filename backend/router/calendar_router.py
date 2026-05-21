from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from router.auth import get_current_user, permission_required
from repository.auth.users import UserRepository
from repository.auth.roles import RolesRepository


calendar_router = APIRouter(prefix="/calendar", tags=["auth"])


@calendar_router.get(
    path="/getAllEmployee",
    status_code=status.HTTP_200_OK,
)
@permission_required(tag="healthCheck:admin")
async def get_all_employee(request: Request, current_user = Depends(get_current_user)):
    if current_user["role"] == "admin":
        return await UserRepository.get_employees_by_usergroup([UserGroupEnum.manager, UserGroupEnum.supervisor,
                                                                UserGroupEnum.employee])
    elif current_user["role"] == "manager":
        return await UserRepository.get_employees_by_usergroup([UserGroupEnum.supervisor, UserGroupEnum.employee])
    elif current_user["role"] == "supervisor":
        return await UserRepository.get_employees_by_usergroup([UserGroupEnum.employee])
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted for your role")


@calendar_router.get(
    path="/getRoles",
    dependencies=[
        Depends(require_roles(UserGroupEnum.admin, UserGroupEnum.manager, UserGroupEnum.supervisor))
    ],
    status_code=status.HTTP_200_OK,
)
async def get_all_roles():
    return await RolesRepository.get_all_roles()


@calendar_router.post(
    path="/addDuties",
    dependencies=[Depends(require_roles("admin", "manager", "supervisor"))],
    status_code=status.HTTP_201_CREATED,
)
def add_duties(duty_list: List[DutiesSQLModel]):
    for duty in duty_list:
        UserRepository.insert_duty(duty)