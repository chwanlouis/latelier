from neomodel import (
    StringProperty, IntegerProperty, AsyncRelationshipFrom
)
from module.knowledge_graph.model.neo4j.relations import EnzymeCompoundRel
from module.knowledge_graph.model.neo4j.enum import RelationTypeName
from module.knowledge_graph.model.neo4j.base import StructuredNodeBaseClass


class Enzyme(StructuredNodeBaseClass):
    foodb_id = IntegerProperty(unique_index=True, required=True)
    enzyme_id = StringProperty(unique_index=True, required=True)
    name = StringProperty(required=True, index=True)
    gene_name = StringProperty(index=True)
    description = StringProperty()
    go_classification = StringProperty()
    general_function = StringProperty()
    specific_function = StringProperty()
    pathway = StringProperty()
    reaction = StringProperty()
    cellular_location = StringProperty()
    uniprot_name = StringProperty()
    uniprot_id = StringProperty(index=True)

    compounds = AsyncRelationshipFrom(
        "model.neo4j.compound.Compound",
        RelationTypeName.INTERACTS_WITH_ENZYME.value,
        model=EnzymeCompoundRel
    )
