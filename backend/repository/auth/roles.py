from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from model.sql.role import RolesSQLModel
from utils.psqltools import db_session_manager
from repository.base import RepositoryBaseClass
from utils.log import logger


class RolesRepository(RepositoryBaseClass):
    @staticmethod
    @db_session_manager
    async def get_all_role(*args, **kwargs) -> Optional[RolesSQLModel]:
        db_session: AsyncSession = kwargs["db_session"]
        query = (
            select(RolesSQLModel)
        )
        result = await db_session.execute(query)
        return result.scalars().all()

    @staticmethod
    @db_session_manager
    async def get_role_by_name(name: str, *args, **kwargs) -> Optional[RolesSQLModel]:
        db_session: AsyncSession = kwargs["db_session"]
        query = (
            select(RolesSQLModel).where(RolesSQLModel.name == name)
        )
        result = await db_session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    @db_session_manager
    async def insert_role(role: RolesSQLModel, *args, **kwargs) -> RolesSQLModel:
        db_session: AsyncSession = kwargs["db_session"]
        logger.info(f"Attempting to insert role: {role.name}")
        db_session.add(role)
        try:
            await db_session.flush()
            await db_session.refresh(role)
            await db_session.commit()
            logger.info("Successfully inserted role.")
            return role
        except Exception as e:
            logger.error(f"Error inserting role: {e}")
            await db_session.rollback()

    @staticmethod
    @db_session_manager
    async def check_and_insert_role(role: RolesSQLModel, *args, **kwargs) -> Optional[RolesSQLModel]:
        existing_role = await RolesRepository.get_role_by_name(role.name)
        if existing_role:
            logger.warning(f"Role with name {role.name} already exists.")
            return None
        return await RolesRepository.insert_role(role)
