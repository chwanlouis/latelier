from typing import Optional
from model.neo4j.relations import EnzymeCompoundRel
from repository.neo4j.base import NeoModelRelationshipRepositoryBase

_GUARD_TOKEN = object()

class CompoundEnzymeRepository(NeoModelRelationshipRepositoryBase[EnzymeCompoundRel]):
    def __init__(self, *, _internal_token: Optional[object] = None):
        if _internal_token is not _GUARD_TOKEN:
            raise RuntimeError(
                "CRITICAL ARCHITECTURE VIOLATION: Direct instantiation of CompoundEnzymeRepository is forbidden! "
                "You must import and use the pre-configured singleton instance: "
                "from repository.neo4j.compound_enzyme_repository import compound_enzyme_repository"
            )
        super().__init__(
            rel_cls=EnzymeCompoundRel,
            source_label="Compound",
            target_label="Enzyme",
            rel_type="INTERACTS_WITH_ENZYME"
        )


compound_enzyme_repository = CompoundEnzymeRepository(_internal_token=_GUARD_TOKEN)