from typing import Optional, AsyncGenerator, Tuple
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from tools.log import logger
from tools.settings import settings


class PSQLManager(object):
    def __init__(self):
        self.db_engine = None
        self.session_maker = None

    def get_engine(self, database_url: Optional[str] = None):
        if self.db_engine is not None:
            return self.db_engine
        if database_url is None:
            raise Exception
        engine = create_async_engine(database_url, echo=True)
        self.db_engine = engine
        return engine

    def get_session_maker(self):
        if self.session_maker is not None:
            return self.session_maker
        engine = self.db_engine
        session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        self.session_maker = session_maker
        return session_maker

    async def get_db_session(self) -> AsyncSession:
        async_session = self.get_session_maker()
        async with async_session() as session:
            yield session

    async def get_db_session_and_engine(self):
        engine = self.get_engine()
        async_session = self.get_session_maker()
        async with async_session() as session:
            yield session, engine


psql_manager = PSQLManager()
logger.info(settings.DATABASE_URL)
psql_manager.get_engine(settings.DATABASE_URL)
psql_manager.get_session_maker()


def db_session_manager(func):
    async def inner_function(*args, **kwargs):
        async for db_session in psql_manager.get_db_session():
            try:
                kwargs["db_session"] = db_session
                result = await func(*args, **kwargs)
                await db_session.commit()
                return result
            except Exception as e:
                await db_session.rollback()
                raise e
    return inner_function
