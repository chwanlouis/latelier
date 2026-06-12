from typing import TypeVar, Generic, List, Dict, Any, Type, Callable
from functools import wraps
from threading import Lock
from neomodel import AsyncStructuredNode, AsyncStructuredRel, adb
from module.core.tools.log import logger
from module.knowledge_graph.tools.neo4jtools import neo4j_manager


NodeType = TypeVar('NodeType', bound=AsyncStructuredNode)
RelType = TypeVar('RelType', bound=AsyncStructuredRel)


class RepositorySingletonMeta(type):
    _instances: Dict[Type[Any], Any] = {}
    _lock: Lock = Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class NeoModelRepositoryBase(Generic[NodeType], metaclass=RepositorySingletonMeta):
    def __init__(self, model_cls: Type[NodeType]):
        self.model_cls = model_cls

    @staticmethod
    def transactional(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def inner(self, *args, **kwargs):
            # Using the async context manager pattern is safer and handles exceptions perfectly
            async with adb.transaction:
                try:
                    return await func(self, *args, **kwargs)
                except Exception as e:
                    logger.error(
                        f"Transaction rollback triggered during "
                        f"{self.model_cls.__name__}.{func.__name__} execution: {e}"
                    )
                    raise e
        return inner

    @staticmethod
    def read_only_transactional(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def inner(self, *args, **kwargs):
            async with adb.read_transaction:
                try:
                    return await func(self, *args, **kwargs)
                except Exception as e:
                    logger.error(
                        f"read_only_transactional exception "
                        f"[{self.model_cls.__name__}.{func.__name__}]: {e}"
                    )
                    raise e
        return inner

    @transactional
    async def bulk_upsert(self, batch: List[Dict[str, Any]]) -> None:
        if not batch:
            return
        await self.model_cls.create_or_update(*batch)


class NeoModelRelationshipRepositoryBase(Generic[RelType], metaclass=RepositorySingletonMeta):
    def __init__(self, rel_cls: Type[RelType], source_label: str, target_label: str, rel_type: str):
        self.rel_cls = rel_cls
        self.source_label = source_label
        self.target_label = target_label
        self.rel_type = rel_type
        try:
            self.allowed_properties = list(rel_cls.defined_properties().keys())
        except AttributeError:
            self.allowed_properties = [
                p for p in dir(rel_cls)
                if not p.startswith('_') and not callable(getattr(rel_cls, p))
            ]

        set_clauses = [f"r.{p} = row.{p}" for p in self.allowed_properties if p != "id"]
        set_block = ",\n    ".join(set_clauses)

        self.bulk_link_query = f"""
        UNWIND $batch AS row
        MATCH (src:{self.source_label} {{foodb_id: row.source_id}})
        MATCH (tgt:{self.target_label} {{foodb_id: row.target_id}})
        MERGE (src)-[r:{self.rel_type}]->(tgt)
        SET {set_block}
        """

    @staticmethod
    def transactional(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def inner(self, *args, **kwargs):
            async with adb.transaction:
                try:
                    return await func(self, *args, **kwargs)
                except Exception as e:
                    logger.error(f"Transaction failure during relationship edge wiring: {e}")
                    raise e

        return inner

    @transactional
    async def bulk_link(self, batch: List[Dict[str, Any]]) -> None:
        if not batch:
            return
        # Using adb.cypher_query provides a purely non-blocking async execution
        # that shares the exact same connection pool context as your node repositories!
        await adb.cypher_query(self.bulk_link_query, {"batch": batch})