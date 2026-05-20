from sqlalchemy.ext.asyncio import AsyncSession
from model.sql.duty import DutySQLModel
from utils.psqltools import db_session_manager
from repository.base import RepositoryBaseClass
from utils.log import logger


class DutiesRepository(RepositoryBaseClass):
    @staticmethod
    @db_session_manager
    async def insert_role(duty: DutySQLModel, *args, **kwargs) -> DutySQLModel:
        db_session: AsyncSession = kwargs["db_session"]
        db_session.add(duty)
        try:
            await db_session.flush()
            await db_session.refresh(duty)
            await db_session.commit()
            logger.info(f"Successfully inserted duty: {duty.duty_date} from {duty.start_time} to {duty.end_time} "
                        f"Employee ID = {duty.employee_id} Role ID = {duty.role_id}")
            return duty
        except Exception as e:
            logger.error(f"Error inserting duty: {e}")
            await db_session.rollback()
