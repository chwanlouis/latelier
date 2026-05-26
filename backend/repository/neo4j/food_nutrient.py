from typing import Optional
from model.neo4j.relations import FoodNutrientRel  # Replace with your actual OGM class name if different
from repository.neo4j.base import NeoModelRelationshipRepositoryBase

_GUARD_TOKEN = object()

class FoodNutrientRepository(NeoModelRelationshipRepositoryBase[FoodNutrientRel]):
    def __init__(self, *, _internal_token: Optional[object] = None):
        if _internal_token is not _GUARD_TOKEN:
            raise RuntimeError(
                "CRITICAL ARCHITECTURE VIOLATION: Direct instantiation of FoodNutrientRepository is forbidden! "
                "You must import and use the pre-configured singleton instance: "
                "from repository.neo4j.food_nutrient_repository import food_nutrient_repository"
            )
        super().__init__(
            rel_cls=FoodNutrientRel,
            source_label="Food",
            target_label="Nutrient",
            rel_type="HAS_NUTRIENT"
        )

food_nutrient_repository = FoodNutrientRepository(_internal_token=_GUARD_TOKEN)