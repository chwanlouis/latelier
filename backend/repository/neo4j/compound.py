from typing import Optional
from model.neo4j.compound import Compound
from repository.neo4j.base import NeoModelRepositoryBase

_GUARD_TOKEN = object()

class CompoundRepository(NeoModelRepositoryBase[Compound]):
    def __init__(self, *, _internal_token: Optional[object] = None):
        if _internal_token is not _GUARD_TOKEN:
            raise RuntimeError(
                "CRITICAL ARCHITECTURE VIOLATION: Direct instantiation of CompoundRepository is forbidden! "
                "You must import and use the pre-configured singleton instance: "
                "from repository.neo4j.compound_repository import compound_repository"
            )
        super().__init__(model_cls=Compound)

compound_repository = CompoundRepository(_internal_token=_GUARD_TOKEN)