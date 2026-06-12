from module.knowledge_graph.model.neo4j.compound import Compound
from module.knowledge_graph.repository.neo4j.base import NeoModelRepositoryBase


class CompoundRepository(NeoModelRepositoryBase[Compound]):
    def __init__(self):
        super().__init__(model_cls=Compound)


compound_repository = CompoundRepository()
