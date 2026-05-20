from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from model.sql.user import UsersSQLModel, UserLevelEnum
from model.sql.user_role import UserRoleSQLModel
from model.sql.role import RolesSQLModel
from model.sql.role_permission import RolePermissionSQLModel
from model.sql.permission import PermissionSQLModel
from utils.psqltools import db_session_manager
from repository.base import RepositoryBaseClass
from utils.log import logger


class UserRepository(RepositoryBaseClass):
    @staticmethod
    @db_session_manager
    async def get_user_by_id(user_id: int, *args, **kwargs) -> Optional[UsersSQLModel]:
        db_session: AsyncSession = kwargs["db_session"]
        query = (
            select(UsersSQLModel)
            .where(UsersSQLModel.id == user_id)
        )
        result = await db_session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    @db_session_manager
    async def get_user_by_username(username: str, *args, **kwargs) -> Optional[UsersSQLModel]:
        db_session: AsyncSession = kwargs["db_session"]
        query = (
            select(UsersSQLModel)
            .where(UsersSQLModel.username == username)
        )
        result = await db_session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    @db_session_manager
    async def insert_user(employee: UsersSQLModel, *args, **kwargs) -> UsersSQLModel:
        db_session: AsyncSession = kwargs["db_session"]
        logger.info(f"Attempting to insert user: {employee.username}")
        db_session.add(employee)
        try:
            await db_session.flush()
            await db_session.refresh(employee)
            await db_session.commit()
            logger.info("Successfully inserted user.")
            return employee
        except Exception as e:
            logger.error(f"Error inserting user: {e}")
            await db_session.rollback()

    @staticmethod
    @db_session_manager
    async def check_and_insert_user(employee: UsersSQLModel, *args, **kwargs) -> Optional[UsersSQLModel]:
        existing_user = await UserRepository.get_user_by_username(employee.username)
        if existing_user:
            logger.warning(f"User with username {employee.username} already exists.")
            return None
        return await UserRepository.insert_user(employee)

    @staticmethod
    @db_session_manager
    async def delete_user_by_username(
            username: str,
            *args, **kwargs
    ) -> None:
        db_session: AsyncSession = kwargs["db_session"]
        user = await UserRepository.get_user_by_username(db_session, username)
        if user:
            await db_session.delete(user)
            try:
                await db_session.commit()
                logger.info(f"Successfully deleted user: {username}")
            except Exception as e:
                logger.error(f"Error deleting user: {e}")
                await db_session.rollback()
        else:
            logger.warning(f"User {username} not found for deletion.")

    @staticmethod
    @db_session_manager
    async def update_user(
            employee: UsersSQLModel,
            *args, **kwargs
        ):
        db_session: AsyncSession = kwargs["db_session"]
        logger.info(f"Updating {employee.username} in the database.")
        stmt = (
            update(UsersSQLModel).where(UsersSQLModel.id == employee.id).values(employee.to_dict())
        )
        try:
            await db_session.execute(stmt)
            await db_session.commit()
            logger.info(f"Successfully updated the record: {employee.username}")
        except Exception as e:
            logger.error(f"Error updating record: {e}")
            await db_session.rollback()

    @staticmethod
    @db_session_manager
    async def get_all_permitted_tags_by_user_id(user_id: int, *args, **kwargs):
        db_session: AsyncSession = kwargs["db_session"]
        query = (
            select(
                PermissionSQLModel.tag
            )
            .select_from(UsersSQLModel)
            .outerjoin(UserRoleSQLModel, UserRoleSQLModel.user_id == UsersSQLModel.id)
            .outerjoin(RolesSQLModel, RolesSQLModel.id == UserRoleSQLModel.role_id)
            .outerjoin(RolePermissionSQLModel, RolePermissionSQLModel.role_id == RolesSQLModel.id)
            .outerjoin(PermissionSQLModel, RolePermissionSQLModel.permission_id == PermissionSQLModel.id)
            .where(UsersSQLModel.id == user_id)
            .distinct()
        )
        try:
            results = await db_session.execute(query)
            logger.info(f"Successfully retrieved permitted tags for user ID: {user_id}")
            return results.fetchall()
        except Exception as e:
            logger.error(f"Error updating record: {e}")
            await db_session.rollback()
