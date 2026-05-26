# backend/model/neo4j/flavor.py
from neomodel import AsyncStructuredNode, StringProperty, IntegerProperty, DateTimeProperty, AsyncRelationshipFrom
from model.neo4j.relations import FlavorCompoundRel

class Flavor(AsyncStructuredNode):
    foodb_id = IntegerProperty(unique_index=True, required=True)
    name = StringProperty(required=True, index=True)
    flavor_group = StringProperty(index=True)  # E.g., "vegetable", "fruit", "berry"
    category = StringProperty(index=True)      # E.g., "odor", "taste"

    created_at = DateTimeProperty()
    updated_at = DateTimeProperty()

    # Incoming links from chemical compounds that express this specific flavor node
    compounds = AsyncRelationshipFrom(
        "model.neo4j.compound.Compound",
        "HAS_FLAVOR",
        model=FlavorCompoundRel
    )