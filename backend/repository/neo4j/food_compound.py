from typing import Optional
from model.neo4j.relations import FoodCompoundRel  # Replace with your actual OGM class name if different
from repository.neo4j.base import NeoModelRelationshipRepositoryBase

_GUARD_TOKEN = object()

class FoodCompoundRepository(NeoModelRelationshipRepositoryBase[FoodCompoundRel]):
    def __init__(self, *, _internal_token: Optional[object] = None):
        if _internal_token is not _GUARD_TOKEN:
            raise RuntimeError(
                "CRITICAL ARCHITECTURE VIOLATION: Direct instantiation of FoodCompoundRepository is forbidden! "
                "You must import and use the pre-configured singleton instance: "
                "from repository.neo4j.food_compound_repository import food_compound_repository"
            )
        super().__init__(
            rel_cls=FoodCompoundRel,
            source_label="Food",
            target_label="Compound",
            rel_type="CONTAINS_COMPOUND"
        )

food_compound_repository = FoodCompoundRepository(_internal_token=_GUARD_TOKEN)