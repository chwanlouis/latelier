from typing import Optional
from model.neo4j.flavor import Flavor
from repository.neo4j.base import NeoModelRepositoryBase

_GUARD_TOKEN = object()

class FlavorRepository(NeoModelRepositoryBase[Flavor]):
    def __init__(self, *, _internal_token: Optional[object] = None):
        if _internal_token is not _GUARD_TOKEN:
            raise RuntimeError(
                "CRITICAL ARCHITECTURE VIOLATION: Direct instantiation of FlavorRepository is forbidden! "
                "You must import and use the pre-configured singleton instance: "
                "from repository.neo4j.flavor_repository import flavor_repository"
            )
        super().__init__(model_cls=Flavor)

flavor_repository = FlavorRepository(_internal_token=_GUARD_TOKEN)