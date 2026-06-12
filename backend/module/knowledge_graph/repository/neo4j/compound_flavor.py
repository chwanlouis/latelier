from module.knowledge_graph.model.neo4j.relations import FlavorCompoundRel
from module.knowledge_graph.repository.neo4j.base import NeoModelRelationshipRepositoryBase


class CompoundFlavorRepository(NeoModelRelationshipRepositoryBase[FlavorCompoundRel]):
    def __init__(self):
        super().__init__(
            rel_cls=FlavorCompoundRel,
            source_label="Compound",
            target_label="Flavor",
            rel_type="HAS_FLAVOR"
        )


compound_flavor_repository = CompoundFlavorRepository()
