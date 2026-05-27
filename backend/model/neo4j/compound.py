from neomodel import (
    AsyncStructuredNode,
    StringProperty,
    IntegerProperty,
    FloatProperty,
    AsyncRelationshipFrom
)
from neomodel import AsyncRelationshipTo
from model.neo4j.relations import FoodCompoundRel, FlavorCompoundRel
from model.neo4j.enum import RelationTypeName
from model.neo4j.base import StructuredNodeBaseClass


class Compound(StructuredNodeBaseClass):
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
        RelationTypeName.CONTAINS_COMPOUND.value,
        model=FoodCompoundRel
    )

    flavors = AsyncRelationshipTo(
        "model.neo4j.flavor.Flavor",
        RelationTypeName.HAS_FLAVOR.value,
        model=FlavorCompoundRel
    )