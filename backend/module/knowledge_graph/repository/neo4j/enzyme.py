from module.knowledge_graph.model.neo4j.enzyme import Enzyme
from module.knowledge_graph.repository.neo4j.base import NeoModelRepositoryBase


class EnzymeRepository(NeoModelRepositoryBase[Enzyme]):
    def __init__(self):
        super().__init__(model_cls=Enzyme)


enzyme_repository = EnzymeRepository()
