from typing import Optional
from model.neo4j.relations import FlavorCompoundRel
from repository.neo4j.base import NeoModelRelationshipRepositoryBase

_GUARD_TOKEN = object()

class CompoundFlavorRepository(NeoModelRelationshipRepositoryBase[FlavorCompoundRel]):
    def __init__(self, *, _internal_token: Optional[object] = None):
        if _internal_token is not _GUARD_TOKEN:
            raise RuntimeError(
                "CRITICAL ARCHITECTURE VIOLATION: Direct instantiation of CompoundFlavorRepository is forbidden! "
                "You must import and use the pre-configured singleton instance: "
                "from repository.neo4j.compound_flavor_repository import compound_flavor_repository"
            )
        super().__init__(
            rel_cls=FlavorCompoundRel,
            source_label="Compound",
            target_label="Flavor",
            rel_type="HAS_FLAVOR"
        )


compound_flavor_repository = CompoundFlavorRepository(_internal_token=_GUARD_TOKEN)