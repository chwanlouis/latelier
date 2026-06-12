from module.knowledge_graph.model.neo4j.relations import EnzymeCompoundRel
from module.knowledge_graph.repository.neo4j.base import NeoModelRelationshipRepositoryBase


class CompoundEnzymeRepository(NeoModelRelationshipRepositoryBase[EnzymeCompoundRel]):
    def __init__(self):
        super().__init__(
            rel_cls=EnzymeCompoundRel,
            source_label="Compound",
            target_label="Enzyme",
            rel_type="INTERACTS_WITH_ENZYME"
        )


compound_enzyme_repository = CompoundEnzymeRepository()
