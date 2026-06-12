from neomodel import StringProperty, IntegerProperty, AsyncRelationshipFrom
from module.knowledge_graph.model.neo4j.relations import FlavorCompoundRel
from module.knowledge_graph.model.neo4j.enum import RelationTypeName
from module.knowledge_graph.model.neo4j.base import StructuredNodeBaseClass


class Flavor(StructuredNodeBaseClass):
    foodb_id = IntegerProperty(unique_index=True, required=True)
    name = StringProperty(required=True, index=True)
    flavor_group = StringProperty(index=True)
    category = StringProperty(index=True)

    compounds = AsyncRelationshipFrom(
        "model.neo4j.compound.Compound",
        RelationTypeName.HAS_FLAVOR.value,
        model=FlavorCompoundRel
    )