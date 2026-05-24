from typing import TypeVar, Generic, List, Dict, Any, Type, Callable, Optional
from functools import wraps
from neomodel import AsyncStructuredNode, adb
from tools.log import logger
from tools.neo4jtools import neo4j_manager

T = TypeVar('T', bound=AsyncStructuredNode)


class NeoModelRepositoryBase(Generic[T]):
    def __init__(self, model_cls: Type[T]):
        self.model_cls = model_cls
        if not neo4j_manager._initialized:
            neo4j_manager.initialize_ogm()

    @staticmethod
    def transactional(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def inner(self, *args, **kwargs):
            # Define an internal execution payload for adb to manage safely
            async def execution_wrapper():
                try:
                    return await func(self, *args, **kwargs)
                except Exception as e:
                    logger.error(
                        f"Transaction rollback triggered during "
                        f"{self.model_cls.__name__}.{func.__name__} execution: {e}"
                    )
                    raise e
            return await adb.transaction(execution_wrapper)()
        return inner

    @transactional
    async def bulk_upsert(self, batch: List[Dict[str, Any]]) -> None:
        if not batch:
            return
        await self.model_cls.create_or_update(*batch)