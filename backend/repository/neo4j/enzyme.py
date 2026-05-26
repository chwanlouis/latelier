from typing import Optional
from model.neo4j.enzyme import Enzyme
from repository.neo4j.base import NeoModelRepositoryBase

_GUARD_TOKEN = object()

class EnzymeRepository(NeoModelRepositoryBase[Enzyme]):
    def __init__(self, *, _internal_token: Optional[object] = None):
        if _internal_token is not _GUARD_TOKEN:
            raise RuntimeError(
                "CRITICAL ARCHITECTURE VIOLATION: Direct instantiation of EnzymeRepository is forbidden! "
                "You must import and use the pre-configured singleton instance: "
                "from repository.neo4j.enzyme_repository import enzyme_repository"
            )
        super().__init__(model_cls=Enzyme)

enzyme_repository = EnzymeRepository(_internal_token=_GUARD_TOKEN)