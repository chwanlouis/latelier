from neomodel import (
    AsyncStructuredNode,
    StringProperty,
    IntegerProperty,
    FloatProperty,
    AsyncRelationshipFrom
)
from neomodel import AsyncRelationshipTo
from model.neo4j.relations import FoodCompoundRel, FlavorCompoundRel


class Compound(AsyncStructuredNode):
    foodb_id = IntegerProperty(unique_index=True, required=True)
    compound_id = StringProperty(unique_index=True, required=True)
    name = StringProperty(required=True)
    state = StringProperty()
    annotation_quality = StringProperty()
    description = StringProperty()
    cas_number = StringProperty()
    smiles = StringProperty()
    inchi = StringProperty()
    inchikey = StringProperty()
    iupac_name = StringProperty()
    mono_mass = FloatProperty()
    kingdom = StringProperty()
    superklass = StringProperty()
    klass = StringProperty()
    subklass = StringProperty()

    foods = AsyncRelationshipFrom(
        "model.neo4j.food.Food",
        "CONTAINS_COMPOUND",
        model=FoodCompoundRel
    )

    flavors = AsyncRelationshipTo(
        "model.neo4j.flavor.Flavor",
        "HAS_FLAVOR",
        model=FlavorCompoundRel
    )