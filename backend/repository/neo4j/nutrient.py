from typing import Optional
from model.neo4j.nutrient import Nutrient
from repository.neo4j.base import NeoModelRepositoryBase

_GUARD_TOKEN = object()

class NutrientRepository(NeoModelRepositoryBase[Nutrient]):
    def __init__(self, *, _internal_token: Optional[object] = None):
        if _internal_token is not _GUARD_TOKEN:
            raise RuntimeError(
                "CRITICAL ARCHITECTURE VIOLATION: Direct instantiation of NutrientRepository is forbidden! "
                "You must import and use the pre-configured singleton instance: "
                "from repository.neo4j.nutrient_repository import nutrient_repository"
            )
        super().__init__(model_cls=Nutrient)

nutrient_repository = NutrientRepository(_internal_token=_GUARD_TOKEN)