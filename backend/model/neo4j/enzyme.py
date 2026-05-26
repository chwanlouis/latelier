from neomodel import AsyncStructuredNode, StringProperty, IntegerProperty, DateTimeProperty, AsyncRelationshipFrom
from model.neo4j.relations import EnzymeCompoundRel


class Enzyme(AsyncStructuredNode):
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

    created_at = DateTimeProperty()
    updated_at = DateTimeProperty()

    compounds = AsyncRelationshipFrom(
        "model.neo4j.compound.Compound",
        "INTERACTS_WITH_ENZYME",
        model=EnzymeCompoundRel
    )
