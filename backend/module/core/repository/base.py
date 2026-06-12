from sqlalchemy import text, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, TypeVar, Any, Optional, Generic, Type
from module.core.tools.psqltools import db_session_manager

T = TypeVar('T')

class ImplementationError(Exception):
    pass


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls in cls._instances:
            raise ImplementationError(
                f"{cls.__name__} has already been instantiated. Multiple instantiations are forbidden."
            )
        cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class RepositoryBaseClass(Generic[T], metaclass=SingletonMeta):
    def init(self, model_class: Type[T]):
        self.model_class = model_class

    @db_session_manager
    async def insert(self, item: T, *args, **kwargs) -> T:
        db_session: AsyncSession = kwargs["db_session"]
        db_session.add(item)
        try:
            await db_session.flush()
            await db_session.commit()
            return item
        except Exception as e:
            await db_session.rollback()
            raise e

    @db_session_manager
    async def insert_all(self, items: List[T], *args, **kwargs) -> None:
        db_session: AsyncSession = kwargs["db_session"]
        if not items:
            return
        db_session.add_all(items)
        try:
            await db_session.commit()
        except Exception as e:
            await db_session.rollback()
            raise e

    @db_session_manager
    async def update(self, item: T, *args, **kwargs) -> Optional[T]:
        db_session: AsyncSession = kwargs["db_session"]
        stmt = (
            update(self.model_class)
            .where(self.model_class.id == item.id)
            .values(item.to_dict())
        )
        try:
            await db_session.execute(stmt)
            await db_session.commit()
            return item
        except Exception as e:
            await db_session.rollback()
            return None

    @db_session_manager
    async def update_all(self, items: List[T], *args, **kwargs) -> None:
        db_session: AsyncSession = kwargs["db_session"]
        if not items:
            return
        try:
            for item in items:
                stmt = (
                    update(self.model_class)
                    .where(self.model_class.id == item.id)
                    .values(item.to_dict())
                )
                await db_session.execute(stmt)
            await db_session.commit()
        except Exception as e:
            await db_session.rollback()
            raise e

    @db_session_manager
    async def execute_raw_query(self, raw_query: str, *args, **kwargs) -> Optional[Any]:
        db_session: AsyncSession = kwargs["db_session"]
        try:
            result = await db_session.execute(text(raw_query))
            if result.returns_rows:
                return result.fetchall()
            else:
                await db_session.commit()
                return None
        except SQLAlchemyError as e:
            await db_session.rollback()
            raise e
