from sqlalchemy import text, update, inspect
from sqlalchemy.exc import SQLAlchemyError, NoSuchTableError
from sqlalchemy.ext.asyncio import AsyncSession, AsyncConnection
from typing import List, TypeVar, Any, Optional
from tools.psqltools import db_session_manager
from tools.log import logger


T = TypeVar('T')

class RepositoryBaseClass(object):
    @staticmethod
    @db_session_manager
    async def insert(item: T, *args, **kwargs) -> None:
        db_session: AsyncSession = kwargs["db_session"]
        logger.info(f"Inserting {item} into the database.")
        db_session.add(item)
        try:
            await db_session.commit()
            logger.info("Successfully inserted the record.")
        except Exception as e:
            logger.error(f"Error inserting record: {e}")
            await db_session.rollback()

    @staticmethod
    @db_session_manager
    async def insert_all(items: List[T], *args, **kwargs) -> None:
        db_session: AsyncSession = kwargs["db_session"]
        if not items:
            logger.warning("No items to insert.")
            return
        logger.info(f"Inserting {len(items)} records into the database.")
        db_session.add_all(items)
        try:
            await db_session.commit()
            logger.info("Successfully inserted records.")
        except Exception as e:
            logger.error(f"Error inserting records: {e}")
            await db_session.rollback()

    @staticmethod
    @db_session_manager
    async def update(item: T, *args, **kwargs) -> Optional[T]:
        db_session: AsyncSession = kwargs["db_session"]
        logger.info(f"Updating {item} in the database.")
        stmt = (
            update(item.__class__).where(item.__class__.id == item.id).values(item.to_dict())
        )
        try:
            await db_session.execute(stmt)
            await db_session.commit()
            logger.info(f"Successfully updated the record: {item.id}")
            return item
        except Exception as e:
            logger.error(f"Error updating record: {e}")
            await db_session.rollback()
            return None

    @staticmethod
    @db_session_manager
    async def update_all(items: List[T], *args, **kwargs) -> None:
        db_session: AsyncSession = kwargs["db_session"]
        if not items:
            logger.warning("No items to update.")
            return
        logger.info(f"Updating {len(items)} records in the database.")
        try:
            for item in items:
                await RepositoryBaseClass.update(item, db_session=db_session)
            logger.info("Successfully updated all records.")
        except Exception as e:
            logger.error(f"Error updating records: {e}")
            await db_session.rollback()

    @staticmethod
    @db_session_manager
    async def execute_raw_query(raw_query: str, *args, **kwargs) -> Optional[Any]:
        db_session: AsyncSession = kwargs["db_session"]
        logger.info(f"Executing raw SQL query: {raw_query}")
        try:
            result = await db_session.execute(text(raw_query))
            if result.returns_rows:
                rows = result.fetchall()
                logger.info(f"Raw query executed successfully, {len(rows)} rows returned.")
                return rows
            else:
                await db_session.commit()
                logger.info("Raw query executed successfully.")
                return None
        except SQLAlchemyError as e:
            logger.error(f"Database error occurred: {e}")
            await db_session.rollback()
            raise e
