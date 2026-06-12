from module.knowledge_graph.model.neo4j.relations import FoodCompoundRel
from module.knowledge_graph.repository.neo4j.base import NeoModelRelationshipRepositoryBase


class FoodCompoundRepository(NeoModelRelationshipRepositoryBase[FoodCompoundRel]):
    def __init__(self):
        super().__init__(
            rel_cls=FoodCompoundRel,
            source_label="Food",
            target_label="Compound",
            rel_type="CONTAINS_COMPOUND"
        )


food_compound_repository = FoodCompoundRepository()
