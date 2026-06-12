from module.knowledge_graph.model.neo4j.relations import FoodNutrientRel
from module.knowledge_graph.repository.neo4j.base import NeoModelRelationshipRepositoryBase


class FoodNutrientRepository(NeoModelRelationshipRepositoryBase[FoodNutrientRel]):
    def __init__(self):
        super().__init__(
            rel_cls=FoodNutrientRel,
            source_label="Food",
            target_label="Nutrient",
            rel_type="HAS_NUTRIENT"
        )


food_nutrient_repository = FoodNutrientRepository()
