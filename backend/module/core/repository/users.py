from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from module.core.model.sql.user import UserSQLModel, UserGroupEnum
from module.core.repository.base import RepositoryBaseClass
from module.core.tools.psqltools import db_session_manager
from module.core.tools.log import logger
from module.core.tools.login import hash_password


class UserRepository(RepositoryBaseClass[UserSQLModel]):
    def init(self):
        super().init(UserSQLModel)

    @db_session_manager
    async def get_user_by_id(self, user_id: int, *args, **kwargs) -> Optional[UserSQLModel]:
        db_session: AsyncSession = kwargs["db_session"]
        query = select(UserSQLModel).where(UserSQLModel.id == user_id)
        result = await db_session.execute(query)
        return result.scalar_one_or_none()

    @db_session_manager
    async def get_user_by_username(self, username: str, *args, **kwargs) -> Optional[UserSQLModel]:
        db_session: AsyncSession = kwargs["db_session"]
        query = select(UserSQLModel).where(UserSQLModel.username == username)
        result = await db_session.execute(query)
        return result.scalar_one_or_none()

    @db_session_manager
    async def insert_user(self, employee: UserSQLModel, *args, **kwargs) -> UserSQLModel:
        existing_user = await self.get_user_by_username(employee.username, *args, **kwargs)
        if existing_user:
            logger.warning(f"Registration failed: Username '{employee.username}' already exists.")
            raise ValueError(f"Username '{employee.username}' is already taken.")
        return await self.insert(employee, *args, **kwargs)

    @db_session_manager
    async def check_and_insert_user(self, employee: UserSQLModel, *args, **kwargs) -> Optional[UserSQLModel]:
        try:
            return await self.insert_user(employee, *args, **kwargs)
        except ValueError:
            logger.warning(f"User with username {employee.username} already exists.")
            return None

    @db_session_manager
    async def create_admin(self, username: str, password: str, email: str, *args, **kwargs) -> Optional[UserSQLModel]:
        existing_user = await self.get_user_by_username(username, *args, **kwargs)
        if existing_user:
            return None

        new_admin = UserSQLModel(
            username=username,
            hashed_password=hash_password(password),
            user_group=UserGroupEnum.admin,
            email=email
        )
        return await self.insert(new_admin, *args, **kwargs)

    @db_session_manager
    async def delete_user_by_username(self, username: str, *args, **kwargs) -> None:
        db_session: AsyncSession = kwargs["db_session"]
        user = await self.get_user_by_username(username, *args, **kwargs)
        if user:
            await db_session.delete(user)
            try:
                await db_session.commit()
                logger.info(f"Successfully deleted user: {username}")
            except Exception as e:
                logger.error(f"Error deleting user: {e}")
                await db_session.rollback()
                raise e
        else:
            logger.warning(f"User {username} not found for deletion.")

    @db_session_manager
    async def update_user(self, employee: UserSQLModel, *args, **kwargs) -> Optional[UserSQLModel]:
        logger.info(f"Updating {employee.username} in the database.")
        return await self.update(employee, *args, **kwargs)


user_repository = UserRepository()
