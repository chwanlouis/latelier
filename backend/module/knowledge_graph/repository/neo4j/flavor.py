from module.knowledge_graph.model.neo4j.flavor import Flavor
from module.knowledge_graph.repository.neo4j.base import NeoModelRepositoryBase


class FlavorRepository(NeoModelRepositoryBase[Flavor]):
    def __init__(self):
        super().__init__(model_cls=Flavor)


flavor_repository = FlavorRepository()
