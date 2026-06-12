from neomodel import (
    StringProperty,
    ArrayProperty,
    AsyncRelationshipTo
)
from module.knowledge_graph.model.neo4j.relations import FoodNutrientRel, FoodCompoundRel
from module.knowledge_graph.model.neo4j.enum import RelationTypeName
from module.knowledge_graph.model.neo4j.base import StructuredNodeBaseClass


class Food(StructuredNodeBaseClass):
    food_id = StringProperty(unique_index=True, required=True)
    name = StringProperty(required=True, index=True)
    name_scientific = StringProperty(index=True)
    aliases = ArrayProperty(StringProperty(), default=[])
    description = StringProperty()
    food_group = StringProperty(index=True)
    food_subgroup = StringProperty()

    compounds = AsyncRelationshipTo(
        ('model.neo4j.compound.Compound'),
        RelationTypeName.CONTAINS_COMPOUND,
        model=FoodCompoundRel
    )

    nutrients = AsyncRelationshipTo(
        ('model.neo4j.nutrient.Nutrient'),
        RelationTypeName.HAS_NUTRIENT.value,
        model=FoodNutrientRel
    )
