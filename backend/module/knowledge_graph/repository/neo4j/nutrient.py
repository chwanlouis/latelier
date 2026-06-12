from module.knowledge_graph.model.neo4j.nutrient import Nutrient
from module.knowledge_graph.repository.neo4j.base import NeoModelRepositoryBase


class NutrientRepository(NeoModelRepositoryBase[Nutrient]):
    def __init__(self):
        super().__init__(model_cls=Nutrient)


nutrient_repository = NutrientRepository()
